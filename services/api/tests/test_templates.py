from __future__ import annotations

import json
import zipfile
from io import BytesIO

from fastapi.testclient import TestClient

from caragent_api.main import create_app


def test_list_templates_exposes_catalog_ready_mvp_pack() -> None:
    client = TestClient(create_app())

    response = client.get("/templates")

    assert response.status_code == 200
    templates = response.json()
    assert [item["id"] for item in templates] == [
        "generic_coupe_side_v1",
        "generic_sedan_side_v1",
        "generic_hatchback_side_v1",
        "generic_suv_side_v1",
        "generic_van_side_v1",
        "toyota_gr86_brz_v1",
    ]
    assert all(item["thumbnail_url"].endswith("/thumbnail.png") for item in templates)
    assert all(item["source"]["source_type"] == "internal_original" for item in templates)
    assert all(item["source"]["license_status"] == "approved" for item in templates)
    assert all(item["readiness"]["catalog_eligible"] is True for item in templates)
    assert all(item["readiness"]["missing_asset_slots"] == [] for item in templates)
    assert all(item["safe_zone_summary"] for item in templates)


def test_list_templates_filters_by_view_and_readiness() -> None:
    client = TestClient(create_app())

    side_response = client.get("/templates", params={"view": "side", "catalog_eligible": True})
    rear_response = client.get("/templates", params={"view": "rear"})

    assert side_response.status_code == 200
    front_response = client.get("/templates", params={"view": "front"})

    assert len(side_response.json()) == 6
    assert rear_response.status_code == 200
    assert [item["id"] for item in rear_response.json()] == ["toyota_gr86_brz_v1"]
    assert front_response.status_code == 200
    assert [item["id"] for item in front_response.json()] == ["toyota_gr86_brz_v1"]


def test_get_template_detail_resolves_legacy_alias() -> None:
    client = TestClient(create_app())

    response = client.get("/templates/generic-side-coupe")

    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == "generic_coupe_side_v1"
    assert detail["aliases"] == ["generic-side-coupe"]
    assert detail["asset_slots"]["thumbnail"] == "thumbnail.png"
    assert {zone["id"] for zone in detail["safe_zones"]} >= {"door-main", "rear-quarter"}


def test_template_thumbnail_returns_png_without_filesystem_paths() -> None:
    client = TestClient(create_app())

    response = client.get("/templates/generic_van_side_v1/thumbnail.png")
    missing = client.get("/templates/not-a-template/thumbnail.png")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(b"\x89PNG\r\n\x1a\n")
    assert missing.status_code == 404
    assert "D:" not in missing.text


def test_get_gr86_brz_template_detail_exposes_construction_metadata() -> None:
    client = TestClient(create_app())

    response = client.get("/templates/toyota_gr86_brz_v1")

    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == "toyota_gr86_brz_v1"
    assert detail["supported_views"] == ["side", "front", "rear", "top"]
    assert set(detail["view_assets"]) == {"side", "front", "rear", "top"}
    assert detail["dimensions"]["overall_length"] == 4265
    assert detail["scale"]["unit"] == "mm_per_canvas_px"
    assert set(detail["export_config"]["formats"]) == {"svg", "pdf", "png"}
    assert detail["authorization"]["source"] == "internal_generated"
    assert {section["id"] for section in detail["sections"]} >= {"door-left", "hood", "roof"}
    assert {zone["id"] for zone in detail["forbidden_zones"]} >= {"side-window", "front-windshield"}


def test_validate_template_package_accepts_svg_png_json_zip() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/templates/validate-package",
        files={"package": ("valid-template.zip", _template_package_zip(), "application/zip")},
    )

    assert response.status_code == 200
    report = response.json()
    assert report["accepted"] is True
    assert report["template_id"] == "user_gr86_demo_v1"
    assert report["source_class"] == "user_provided"
    assert report["authorization"]["authorization_file"] == "authorization.md"
    assert report["issues"] == []
    assert "template.json" in report["files_checked"]


def test_validate_template_package_reports_missing_authorization_fields() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/templates/validate-package",
        files={
            "package": (
                "missing-auth.zip",
                _template_package_zip(authorization={"source": "user"}),
                "application/zip",
            )
        },
    )

    assert response.status_code == 200
    report = response.json()
    assert report["accepted"] is False
    assert {issue["code"] for issue in report["issues"]} >= {"missing_authorization_field"}
    assert {issue["path"] for issue in report["issues"]} == {"template.json"}


def test_validate_template_package_rejects_unsafe_zip_paths() -> None:
    client = TestClient(create_app())
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("../template.json", "{}")

    response = client.post(
        "/templates/validate-package",
        files={"package": ("unsafe.zip", buffer.getvalue(), "application/zip")},
    )

    assert response.status_code == 200
    report = response.json()
    assert report["accepted"] is False
    assert report["issues"] == [
        {
            "code": "unsafe_path",
            "message": "Package contains an unsafe file path.",
            "path": "../template.json",
            "severity": "error",
        }
    ]


def _template_package_zip(authorization: dict[str, object] | None = None) -> bytes:
    template = {
        "id": "user_gr86_demo_v1",
        "label": "User GR86 demo",
        "supported_views": ["side", "front"],
        "source": {"source_type": "user_provided_with_rights"},
        "view_assets": {
            "side": {"base": "views/side.png", "panel_lines": "views/side-lines.svg"},
            "front": {"base": "views/front.png", "panel_lines": "views/front-lines.svg"},
        },
        "dimensions": {"overall_length": 4265},
        "export_config": {"formats": ["svg", "pdf", "png"]},
        "authorization": authorization
        if authorization is not None
        else {
            "source": "user_uploaded",
            "authorization_file": "authorization.md",
            "scope": "workspace_and_export",
            "expires_at": None,
            "commercial_use": True,
            "reviewer": "owner",
            "version_history": [{"version": "1.0.0", "reviewed_at": "2026-06-23"}],
        },
    }
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("template.json", json.dumps(template))
        archive.writestr("safe_zones.json", json.dumps([]))
        archive.writestr("sections.json", json.dumps([]))
        archive.writestr("forbidden_zones.json", json.dumps([]))
        archive.writestr("authorization.md", "owner authorization")
        archive.writestr("views/side.png", b"\x89PNG\r\n\x1a\n")
        archive.writestr("views/front.png", b"\x89PNG\r\n\x1a\n")
        archive.writestr("views/side-lines.svg", "<svg xmlns='http://www.w3.org/2000/svg'/>")
        archive.writestr("views/front-lines.svg", "<svg xmlns='http://www.w3.org/2000/svg'/>")
    return buffer.getvalue()
