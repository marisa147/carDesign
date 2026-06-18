from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from caragent_core.models import metadata
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine

from caragent_api.config import ApiSettings
from caragent_api.main import create_app


def create_workspace_client(tmp_path: Path) -> tuple[TestClient, Any]:
    database_path = tmp_path / "workspaces.db"
    settings = ApiSettings(database_url=f"sqlite+aiosqlite:///{database_path.as_posix()}")
    app = create_app(settings)
    asyncio.run(create_schema(app.state.database_engine))
    return TestClient(app), app


async def create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)


def test_workspace_message_and_brief_routes_persist_across_clients(tmp_path: Path) -> None:
    client, app = create_workspace_client(tmp_path)

    workspace_response = client.post("/workspaces", json={"title": "Sakura GT86"})

    assert workspace_response.status_code == 201
    workspace = workspace_response.json()
    workspace_id = workspace["id"]
    assert workspace["title"] == "Sakura GT86"

    first_message = client.post(
        f"/workspaces/{workspace_id}/messages",
        json={"content": "Make a pink racing itasha.", "role": "user"},
    )
    second_message = client.post(
        f"/workspaces/{workspace_id}/messages",
        json={"content": "Drafting a structured brief.", "role": "assistant"},
    )
    brief_response = client.post(
        f"/workspaces/{workspace_id}/briefs",
        json={
            "payload": {"vehicle": "GT86", "palette": ["pink", "white"]},
            "title": "Initial brief",
        },
    )

    assert first_message.status_code == 201
    assert second_message.status_code == 201
    assert brief_response.status_code == 201

    with TestClient(app) as resumed_client:
        resumed_workspace = resumed_client.get(f"/workspaces/{workspace_id}")
        messages = resumed_client.get(f"/workspaces/{workspace_id}/messages")
        briefs = resumed_client.get(f"/workspaces/{workspace_id}/briefs")

    assert resumed_workspace.status_code == 200
    assert resumed_workspace.json()["id"] == workspace_id
    assert [message["sequence"] for message in messages.json()] == [1, 2]
    assert [message["content"] for message in messages.json()] == [
        "Make a pink racing itasha.",
        "Drafting a structured brief.",
    ]
    assert briefs.json()[0]["payload"] == {"vehicle": "GT86", "palette": ["pink", "white"]}


def test_missing_workspace_returns_404(tmp_path: Path) -> None:
    client, _app = create_workspace_client(tmp_path)

    response = client.get("/workspaces/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
