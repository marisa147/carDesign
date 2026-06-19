from __future__ import annotations

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
    assert len(side_response.json()) == 5
    assert rear_response.status_code == 200
    assert rear_response.json() == []


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
