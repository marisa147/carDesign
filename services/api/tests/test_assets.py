from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from caragent_core.models import metadata
from caragent_core.storage import MAX_UPLOAD_BYTES, InMemoryObjectStorage
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine

from caragent_api.config import ApiSettings
from caragent_api.main import create_app


def create_asset_client(tmp_path: Path) -> tuple[TestClient, Any, InMemoryObjectStorage]:
    database_path = tmp_path / "assets.db"
    settings = ApiSettings(database_url=f"sqlite+aiosqlite:///{database_path.as_posix()}")
    app = create_app(settings)
    storage = InMemoryObjectStorage()
    app.state.object_storage = storage
    asyncio.run(create_schema(app.state.database_engine))
    return TestClient(app), app, storage


async def create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)


def test_upload_list_and_update_asset_rights(tmp_path: Path) -> None:
    client, _app, storage = create_asset_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Assets"}).json()["id"]

    upload = client.post(
        f"/workspaces/{workspace_id}/assets",
        data={"kind": "reference"},
        files={"file": ("reference.png", b"\x89PNG\r\n\x1a\nimage-bytes", "image/png")},
    )

    assert upload.status_code == 201
    asset = upload.json()
    asset_id = asset["id"]
    assert asset["rights_status"] == "missing"
    assert asset["object_key"] in storage.objects

    rights = client.patch(
        f"/assets/{asset_id}/rights",
        json={
            "rights_notes": "User confirmed usage rights.",
            "rights_status": "confirmed",
            "source_label": "User-provided reference",
            "source_url": "https://example.test/reference",
        },
    )
    listed = client.get(f"/workspaces/{workspace_id}/assets")

    assert rights.status_code == 200
    assert rights.json()["rights_status"] == "confirmed"
    assert rights.json()["rights_confirmed_at"] is not None
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [asset_id]


def test_get_asset_metadata(tmp_path: Path) -> None:
    client, _app, _storage = create_asset_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Assets"}).json()["id"]
    uploaded = client.post(
        f"/workspaces/{workspace_id}/assets",
        data={"kind": "reference"},
        files={"file": ("reference.png", b"\x89PNG\r\n\x1a\nimage-bytes", "image/png")},
    ).json()

    response = client.get(f"/assets/{uploaded['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == uploaded["id"]
    assert response.json()["object_key"] == uploaded["object_key"]
    assert "credentials" not in response.text


def test_upload_rejects_unsupported_content_type(tmp_path: Path) -> None:
    client, _app, _storage = create_asset_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Assets"}).json()["id"]

    upload = client.post(
        f"/workspaces/{workspace_id}/assets",
        data={"kind": "reference"},
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )

    assert upload.status_code == 422


def test_upload_rejects_too_large_content(tmp_path: Path) -> None:
    client, _app, storage = create_asset_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Assets"}).json()["id"]

    upload = client.post(
        f"/workspaces/{workspace_id}/assets",
        data={"kind": "reference"},
        files={"file": ("large.png", b"x" * (MAX_UPLOAD_BYTES + 1), "image/png")},
    )

    assert upload.status_code == 422
    assert storage.objects == {}
