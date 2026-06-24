from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import httpx
import pytest
from caragent_core.database import session_scope
from caragent_core.enums import ArtifactKind, DesignVersionStatus, JobStatus
from caragent_core.generation import MVP_COUPE_TEMPLATE_ID
from caragent_core.models import DesignVersion, GenerationJob, JobDispatchOutbox, metadata
from caragent_core.services import jobs
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from caragent_api.config import ApiSettings
from caragent_api.main import create_app
from caragent_api.queue import QueuedGenerationTask


class FakeQueueClient:
    enqueued: list[dict[str, Any]]
    revoked: list[str | None]

    def __init__(self) -> None:
        self.enqueued = []
        self.revoked = []

    async def enqueue_generation_job(self, job_id: UUID) -> QueuedGenerationTask:
        task_id = f"task-{len(self.enqueued) + 1}"
        payload = {
            "args": [str(job_id)],
            "job_id": str(job_id),
            "kwargs": {},
            "task_id": task_id,
            "task_name": "caragent_worker.generate_2d_concept_job",
        }
        self.enqueued.append(payload)
        return QueuedGenerationTask(
            job_id=job_id,
            task_id=task_id,
            task_name="caragent_worker.generate_2d_concept_job",
        )

    async def inspect_generation_queue(self) -> dict[str, Any]:
        return {
            "active_tasks": 0,
            "active_workers": 0,
            "detail": "not inspected in generation tests",
            "generation_queue": "caragent.default",
            "registered_tasks": [],
            "reserved_tasks": 0,
            "status": "unavailable",
        }

    async def revoke_generation_task(self, task_id: str | None) -> dict[str, Any]:
        self.revoked.append(task_id)
        return {
            "detail": None if task_id else "No Celery task id is available for this job.",
            "status": "revoked" if task_id else "not_available",
            "task_id": task_id,
        }

@dataclass
class CommitVisibleQueueClient(FakeQueueClient):
    def __init__(self, session_factory: async_sessionmaker[Any]) -> None:
        super().__init__()
        self.session_factory = session_factory

    async def enqueue_generation_job(self, job_id: UUID) -> QueuedGenerationTask:
        async with session_scope(self.session_factory) as session:
            committed_job = await session.get(GenerationJob, job_id)
            assert committed_job is not None
            assert committed_job.status == JobStatus.QUEUED.value
        return await super().enqueue_generation_job(job_id)


def create_generation_client(
    tmp_path: Path,
    *,
    settings: ApiSettings | None = None,
) -> tuple[TestClient, Any, FakeQueueClient]:
    database_path = tmp_path / "generation-api.db"
    active_settings = settings or ApiSettings(
        database_url=f"sqlite+aiosqlite:///{database_path.as_posix()}",
    )
    app = create_app(active_settings)
    fake_queue = FakeQueueClient()
    app.state.queue_client = fake_queue
    asyncio.run(create_schema(app.state.database_engine))
    return TestClient(app), app, fake_queue


async def create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)


def test_create_and_update_structured_generation_brief(tmp_path: Path) -> None:
    client, _app, _queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Generation"}).json()["id"]

    created = client.post(
        f"/workspaces/{workspace_id}/generation/briefs",
        json={
            "character_focus": "large heroine portrait across door and rear quarter",
            "character_theme": "Sakura heroine",
            "color_harmony": "white base with teal accents and silver separators",
            "coverage": "full side coverage",
            "original_request": (
                "White RX-7 with Sakura heroine, teal accents, and MOON DRIVE text."
            ),
            "overlay_logo_asset_ids": [],
            "palette": ["white", "teal"],
            "racing_cues": ["number panel", "tow arrow"],
            "reference_asset_ids": [],
            "style": "clean racing itasha",
            "supporting_graphics": ["teal ribbon", "sakura petals"],
            "text": ["MOON DRIVE"],
            "typography_intent": "bold readable door lettering",
            "vehicle_template_id": "mazda-rx7",
            "view": "rear",
        },
    )

    assert created.status_code == 201
    payload = created.json()["payload"]
    assert payload["character_focus"] == "large heroine portrait across door and rear quarter"
    assert payload["character_theme"] == "Sakura heroine"
    assert payload["color_harmony"] == "white base with teal accents and silver separators"
    assert payload["overlay_logo_asset_ids"] == []
    assert payload["racing_cues"] == ["number panel", "tow arrow"]
    assert payload["supporting_graphics"] == ["teal ribbon", "sakura petals"]
    assert payload["typography_intent"] == "bold readable door lettering"
    assert payload["vehicle_template_id"] == MVP_COUPE_TEMPLATE_ID
    assert payload["view"] == "side"
    assert "Unsupported vehicle template" in " ".join(payload["warnings"])
    assert "Unsupported view" in " ".join(payload["warnings"])

    updated = client.patch(
        f"/generation/briefs/{created.json()['id']}",
        json={
            "character_focus": "rear quarter chibi plus door typography",
            "color_harmony": "teal dominant with white negative space",
            "coverage": "rear quarter emphasis",
            "overlay_logo_asset_ids": ["11111111-1111-1111-1111-111111111111"],
            "palette": ["white", "teal", "silver"],
            "racing_cues": ["side skirt stripe"],
            "supporting_graphics": ["speed line"],
            "text": ["MOON DRIVE", "SAKURA"],
            "typography_intent": "stacked block type",
        },
    )

    assert updated.status_code == 200
    assert updated.json()["id"] == created.json()["id"]
    assert updated.json()["payload"]["coverage"] == "rear quarter emphasis"
    assert updated.json()["payload"]["character_focus"] == "rear quarter chibi plus door typography"
    assert updated.json()["payload"]["color_harmony"] == "teal dominant with white negative space"
    assert updated.json()["payload"]["overlay_logo_asset_ids"] == [
        "11111111-1111-1111-1111-111111111111",
    ]
    assert updated.json()["payload"]["palette"] == ["white", "teal", "silver"]
    assert updated.json()["payload"]["racing_cues"] == ["side skirt stripe"]
    assert updated.json()["payload"]["supporting_graphics"] == ["speed line"]
    assert updated.json()["payload"]["text"] == ["MOON DRIVE", "SAKURA"]
    assert updated.json()["payload"]["typography_intent"] == "stacked block type"



def test_create_generation_brief_uses_openai_structured_parser_when_enabled(
    tmp_path: Path,
) -> None:
    settings = api_settings(
        tmp_path,
        ai_brief_parser_provider="openai",
        ai_provider_calls_enabled=True,
        ai_provider_openai_api_key=SecretStr("openai-secret"),
        ai_provider_openai_text_model="gpt-5.5",
    )
    client, app, _queue = create_generation_client(tmp_path, settings=settings)
    workspace_id = client.post("/workspaces", json={"title": "GPT parser"}).json()["id"]
    submitted_payloads: list[dict[str, object]] = []

    def handler(http_request: httpx.Request) -> httpx.Response:
        submitted_payloads.append(json.loads(http_request.content))
        assert http_request.headers.get("Authorization") == "Bearer openai-secret"
        return httpx.Response(
            200,
            json={
                "id": "resp-brief-1",
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {
                                "type": "output_text",
                                "text": json.dumps(
                                    {
                                        "character_theme": "Miku racing heroine",
                                        "coverage": "full side coverage",
                                        "original_request": (
                                            "白色双门车，初音未来主题，门板文字 MIKU DRIVE。"
                                        ),
                                        "palette": ["white", "cyan", "black"],
                                        "style": "clean GPT itasha concept",
                                        "text": ["MIKU DRIVE"],
                                        "vehicle_template_id": MVP_COUPE_TEMPLATE_ID,
                                        "view": "side",
                                    },
                                ),
                            },
                        ],
                    },
                ],
            },
        )

    parser_client = httpx.AsyncClient(
        base_url="https://api.openai.test/v1",
        transport=httpx.MockTransport(handler),
    )
    app.state.openai_brief_parser_client = parser_client

    try:
        response = client.post(
            f"/workspaces/{workspace_id}/generation/briefs",
            json={"original_request": "白色双门车，初音未来主题，门板文字 MIKU DRIVE。"},
        )
    finally:
        asyncio.run(parser_client.aclose())

    assert response.status_code == 201
    payload = response.json()["payload"]
    assert payload["character_theme"] == "Miku racing heroine"
    assert payload["style"] == "clean GPT itasha concept"
    assert payload["palette"] == ["white", "cyan", "black"]
    assert payload["text"] == ["MIKU DRIVE"]
    assert submitted_payloads
    assert submitted_payloads[0]["model"] == "gpt-5.5"
    assert (
        "infer and complete missing visual design details"
        in submitted_payloads[0]["input"][0]["content"]
    )
    assert submitted_payloads[0]["text"]["format"]["type"] == "json_schema"
    assert "openai-secret" not in response.text

def test_create_generation_brief_supports_openai_chat_completions_parser(
    tmp_path: Path,
) -> None:
    settings = api_settings(
        tmp_path,
        ai_brief_parser_provider="openai",
        ai_provider_calls_enabled=True,
        ai_provider_openai_api_key=SecretStr("openai-secret"),
        ai_provider_openai_responses_path="/chat/completions",
        ai_provider_openai_text_model="gpt-5.5",
    )
    client, app, _queue = create_generation_client(tmp_path, settings=settings)
    workspace_id = client.post("/workspaces", json={"title": "Codex relay parser"}).json()["id"]
    submitted_payloads: list[dict[str, object]] = []

    def handler(http_request: httpx.Request) -> httpx.Response:
        assert http_request.url.path.endswith("/chat/completions")
        submitted_payload = json.loads(http_request.content)
        submitted_payloads.append(submitted_payload)
        assert http_request.headers.get("Authorization") == "Bearer openai-secret"
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-brief-1",
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "```json\n"
                            + json.dumps(
                                {
                                    "character_focus": "large Miku portrait on door",
                                    "character_theme": "Hatsune Miku racing theme",
                                    "coverage": "balanced side coverage",
                                    "original_request": (
                                        "白色双门车，初音未来主题，门板文字 MIKU RACING。"
                                    ),
                                    "palette": ["white", "cyan", "black"],
                                    "style": "clean racing itasha",
                                    "text": ["MIKU RACING"],
                                    "vehicle_template_id": MVP_COUPE_TEMPLATE_ID,
                                    "view": "side",
                                },
                            )
                            + "\n```",
                        },
                    },
                ],
            },
        )

    parser_client = httpx.AsyncClient(
        base_url="https://api.openai.test/v1",
        transport=httpx.MockTransport(handler),
    )
    app.state.openai_brief_parser_client = parser_client

    try:
        response = client.post(
            f"/workspaces/{workspace_id}/generation/briefs",
            json={"original_request": "白色双门车，初音未来主题，门板文字 MIKU RACING。"},
        )
    finally:
        asyncio.run(parser_client.aclose())

    assert response.status_code == 201
    payload = response.json()["payload"]
    assert payload["character_theme"] == "Hatsune Miku racing theme"
    assert payload["character_focus"] == "large Miku portrait on door"
    assert payload["style"] == "clean racing itasha"
    assert payload["palette"] == ["white", "cyan", "black"]
    assert payload["text"] == ["MIKU RACING"]
    assert submitted_payloads
    assert submitted_payloads[0]["model"] == "gpt-5.5"
    assert "messages" in submitted_payloads[0]
    assert (
        "infer and complete missing visual design details"
        in submitted_payloads[0]["messages"][0]["content"]
    )
    assert submitted_payloads[0]["response_format"] == {"type": "json_object"}
    assert "openai-secret" not in response.text
def test_update_generation_brief_accepts_explicit_clears(tmp_path: Path) -> None:
    client, _app, _queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Generation clears"}).json()["id"]
    original_request = "White coupe with Sakura heroine and MOON DRIVE text."
    created = client.post(
        f"/workspaces/{workspace_id}/generation/briefs",
        json={
            "character_theme": "Sakura heroine",
            "coverage": "full side coverage",
            "original_request": original_request,
            "palette": ["white", "teal"],
            "reference_asset_ids": ["22222222-2222-2222-2222-222222222222"],
            "reference_usage": [
                {
                    "asset_id": "22222222-2222-2222-2222-222222222222",
                    "enabled": True,
                    "role": "character",
                },
            ],
            "style": "clean racing itasha",
            "text": ["MOON DRIVE"],
            "vehicle_template_id": MVP_COUPE_TEMPLATE_ID,
            "view": "side",
        },
    )
    assert created.status_code == 201

    updated = client.patch(
        f"/generation/briefs/{created.json()['id']}",
        json={
            "character_theme": "",
            "coverage": "",
            "palette": [],
            "reference_asset_ids": [],
            "reference_usage": [],
            "style": "",
            "text": [],
        },
    )

    assert updated.status_code == 200
    payload = updated.json()["payload"]
    assert payload["character_theme"] == original_request
    assert payload["coverage"] == "balanced side coverage"
    assert payload["palette"] == []
    assert payload["reference_asset_ids"] == []
    assert payload["reference_usage"] == []
    assert payload["style"] == "itasha concept"
    assert payload["text"] == []


def test_update_generation_brief_archives_and_blocks_generation(tmp_path: Path) -> None:
    client, _app, _queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Archive brief"}).json()["id"]
    brief_id = create_brief(client, workspace_id)

    archived = client.patch(
        f"/generation/briefs/{brief_id}",
        json={"status": "archived"},
    )
    generation = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={
            "brief_id": brief_id,
            "idempotency_key": "archived-brief-generation",
            "requested_by": "web-workbench",
        },
    )

    assert archived.status_code == 200
    assert archived.json()["status"] == "archived"
    assert generation.status_code == 422
    assert "archived" in generation.json()["detail"]


def test_workspace_brief_list_omits_archived_generation_briefs(tmp_path: Path) -> None:
    client, _app, _queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Resume active brief"}).json()["id"]
    archived_brief_id = create_brief(client, workspace_id)
    active_brief_id = create_brief(client, workspace_id, original_request="Active concept")

    archived = client.patch(
        f"/generation/briefs/{archived_brief_id}",
        json={"status": "archived"},
    )
    listed = client.get(f"/workspaces/{workspace_id}/briefs")

    assert archived.status_code == 200
    assert [brief["id"] for brief in listed.json()] == [active_brief_id]

def test_update_generation_brief_recomputes_selected_template(tmp_path: Path) -> None:
    client, _app, _queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Template update"}).json()["id"]
    brief_id = create_brief(client, workspace_id)

    updated = client.patch(
        f"/generation/briefs/{brief_id}",
        json={"vehicle_template_id": "generic_van_side_v1", "view": "side"},
    )
    unsupported = client.patch(
        f"/generation/briefs/{brief_id}",
        json={"vehicle_template_id": "not-a-template", "view": "rear"},
    )

    assert updated.status_code == 200
    payload = updated.json()["payload"]
    assert payload["vehicle_template_id"] == "generic_van_side_v1"
    assert payload["vehicle_template_label"] == "Generic van side-view"
    assert payload["template_readiness"]["catalog_eligible"] is True
    assert payload["template_readiness"]["missing_asset_slots"] == []
    assert {zone["id"] for zone in payload["safe_zones"]} >= {"door-main", "rear-quarter"}

    assert unsupported.status_code == 200
    unsupported_payload = unsupported.json()["payload"]
    assert unsupported_payload["vehicle_template_id"] == MVP_COUPE_TEMPLATE_ID
    assert "Unsupported vehicle template" in " ".join(unsupported_payload["warnings"])
    assert "Unsupported view" in " ".join(unsupported_payload["warnings"])


def test_update_generation_brief_recomputes_quality_warnings(tmp_path: Path) -> None:
    client, _app, _queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Generation"}).json()["id"]
    brief_id = create_brief(client, workspace_id)

    updated = client.patch(
        f"/generation/briefs/{brief_id}",
        json={"text": ["MOON DRIVE SUPER LONG LETTERING"]},
    )

    assert updated.status_code == 200
    assert any(
        "Text may be hard to read" in warning
        for warning in updated.json()["payload"]["warnings"]
    )


def test_generation_brief_reference_usage_round_trips_through_api(tmp_path: Path) -> None:
    client, _app, _queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "References"}).json()["id"]
    character_asset_id = str(uuid4())
    palette_asset_id = str(uuid4())
    legacy_asset_id = str(uuid4())

    created = client.post(
        f"/workspaces/{workspace_id}/generation/briefs",
        json={
            "character_theme": "Sakura heroine",
            "original_request": "White coupe with Sakura heroine and teal palette.",
            "palette": ["white", "teal"],
            "reference_asset_ids": [legacy_asset_id],
            "reference_usage": [
                {
                    "asset_id": character_asset_id,
                    "enabled": True,
                    "role": "character",
                },
                {
                    "asset_id": palette_asset_id,
                    "enabled": False,
                    "role": "palette",
                },
            ],
            "text": ["MOON DRIVE"],
        },
    )

    assert created.status_code == 201
    payload = created.json()["payload"]
    assert payload["reference_asset_ids"] == [legacy_asset_id]
    assert payload["reference_usage"] == [
        {
            "asset_id": character_asset_id,
            "enabled": True,
            "role": "character",
            "schema_version": 1,
        },
        {
            "asset_id": palette_asset_id,
            "enabled": False,
            "role": "palette",
            "schema_version": 1,
        },
    ]

    updated = client.patch(
        f"/generation/briefs/{created.json()['id']}",
        json={
            "reference_asset_ids": [],
            "reference_usage": [
                {
                    "asset_id": legacy_asset_id,
                    "enabled": True,
                    "role": "style",
                },
            ],
        },
    )

    assert updated.status_code == 200
    assert updated.json()["payload"]["reference_asset_ids"] == []
    assert updated.json()["payload"]["reference_usage"] == [
        {
            "asset_id": legacy_asset_id,
            "enabled": True,
            "role": "style",
            "schema_version": 1,
        },
    ]

    legacy = client.post(
        f"/workspaces/{workspace_id}/generation/briefs",
        json={
            "character_theme": "Sakura heroine",
            "original_request": "White coupe with only legacy references.",
            "reference_asset_ids": [legacy_asset_id],
        },
    )
    assert legacy.status_code == 201
    assert legacy.json()["payload"]["reference_asset_ids"] == [legacy_asset_id]
    assert legacy.json()["payload"]["reference_usage"] == []


def test_submit_generation_job_enqueues_worker_task_and_reuses_idempotency(
    tmp_path: Path,
) -> None:
    client, _app, queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Generation"}).json()["id"]
    brief_id = create_brief(client, workspace_id)

    first = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={
            "brief_id": brief_id,
            "idempotency_key": "submit-001",
            "requested_by": "local-user",
        },
    )
    duplicate = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={
            "brief_id": brief_id,
            "idempotency_key": "submit-001",
            "requested_by": "local-user",
        },
    )

    assert first.status_code == 201
    assert duplicate.status_code == 201
    assert first.json()["job"]["operation"] == "generate_2d_concept"
    assert first.json()["job"]["provider"] is None
    assert first.json()["job"]["model"] is None
    assert first.json()["job"]["estimated_cost"] is None
    assert first.json()["job"]["status"] == "queued"
    assert first.json()["job"]["metadata"]["queue"] == {
        "task_id": "task-1",
        "task_name": "caragent_worker.generate_2d_concept_job",
        "queue": "caragent.default",
    }
    assert first.json()["job"]["metadata"]["vehicle_template"]["id"] == MVP_COUPE_TEMPLATE_ID
    assert first.json()["job"]["metadata"]["vehicle_template"]["source"]["source_type"] == (
        "internal_original"
    )
    assert first.json()["job"]["metadata"]["vehicle_template"]["readiness"]["catalog_eligible"] is (
        True
    )
    assert first.json()["idempotent_reused"] is False
    assert duplicate.json()["job"]["id"] == first.json()["job"]["id"]
    assert duplicate.json()["idempotent_reused"] is True
    assert len(queue.enqueued) == 1
    assert queue.enqueued[0]["job_id"] == first.json()["job"]["id"]
    assert "secret" not in str(queue.enqueued[0]).lower()


def test_submit_generation_job_dispatches_only_after_commit_and_marks_outbox(
    tmp_path: Path,
) -> None:
    client, app, _queue = create_generation_client(tmp_path)
    queue = CommitVisibleQueueClient(app.state.session_factory)
    app.state.queue_client = queue
    workspace_id = client.post("/workspaces", json={"title": "Committed dispatch"}).json()["id"]
    brief_id = create_brief(client, workspace_id)

    response = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={
            "brief_id": brief_id,
            "idempotency_key": "dispatch-after-commit",
            "requested_by": "local-user",
        },
    )

    assert response.status_code == 201
    job_id = UUID(response.json()["job"]["id"])
    dispatches = asyncio.run(read_dispatch_outbox(app.state.session_factory))

    assert len(queue.enqueued) == 1
    assert queue.enqueued[0]["job_id"] == str(job_id)
    assert len(dispatches) == 1
    assert dispatches[0].job_id == job_id
    assert dispatches[0].status == jobs.DISPATCH_DISPATCHED
    assert dispatches[0].task_id == "task-1"
    assert dispatches[0].attempts == 1
    assert dispatches[0].dispatched_at is not None

@pytest.mark.parametrize(
    ("settings_kwargs", "expected_reason"),
    [
        ({}, "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED is disabled"),
        (
            {"v2_hosted_provider_rollout_enabled": True},
            "AI_PROVIDER_CALLS_ENABLED is disabled",
        ),
        (
            {
                "ai_provider_calls_enabled": True,
                "v2_hosted_provider_rollout_enabled": True,
            },
            "AI_PROVIDER_BFL_API_KEY is missing",
        ),
        (
            {
                "ai_provider_bfl_api_key": SecretStr("bfl-secret"),
                "ai_provider_calls_enabled": True,
                "v2_hosted_provider_rollout_enabled": True,
            },
            "Hosted quota/rate/cost guards are incomplete",
        ),
    ],
)
def test_submit_hosted_generation_blocks_unmet_preflight(
    tmp_path: Path,
    settings_kwargs: dict[str, Any],
    expected_reason: str,
) -> None:
    client, _app, queue = create_generation_client(
        tmp_path,
        settings=api_settings(tmp_path, **settings_kwargs),
    )
    workspace_id = client.post("/workspaces", json={"title": "Generation"}).json()["id"]
    brief_id = create_brief(client, workspace_id)

    response = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={
            "brief_id": brief_id,
            "idempotency_key": f"hosted-blocked-{expected_reason}",
            "model": "flux-2-pro-preview",
            "provider": "bfl",
            "provider_parameters": {"output_format": "png"},
            "requested_by": "local-user",
        },
    )

    assert response.status_code == 422
    assert expected_reason in response.json()["detail"]
    assert queue.enqueued == []
    assert "bfl-secret" not in response.text


def test_submit_hosted_generation_rejects_unsupported_model_before_enqueue(
    tmp_path: Path,
) -> None:
    client, _app, queue = create_generation_client(
        tmp_path,
        settings=hosted_api_settings(tmp_path),
    )
    workspace_id = client.post("/workspaces", json={"title": "Generation"}).json()["id"]
    brief_id = create_brief(client, workspace_id)

    response = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={
            "brief_id": brief_id,
            "idempotency_key": "hosted-unsupported-model",
            "model": "flux-1-dev",
            "provider": "bfl",
            "requested_by": "local-user",
        },
    )

    assert response.status_code == 422
    assert "Unsupported model for provider bfl" in response.json()["detail"]
    assert queue.enqueued == []


def test_submit_hosted_generation_persists_provider_intent_when_allowed(
    tmp_path: Path,
) -> None:
    client, app, queue = create_generation_client(
        tmp_path,
        settings=hosted_api_settings(tmp_path),
    )
    workspace_id = client.post("/workspaces", json={"title": "Generation"}).json()["id"]
    brief_id = create_brief(client, workspace_id)

    response = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={
            "brief_id": brief_id,
            "estimated_cost": "99.9900",
            "idempotency_key": "hosted-allowed",
            "model": "flux-2-pro-preview",
            "provider": "bfl",
            "provider_parameters": {
                "aspect_ratio": "16:9",
                "output_format": "png",
            },
            "requested_by": "local-user",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["job"]["provider"] == "bfl"
    assert payload["job"]["model"] == "flux-2-pro-preview"
    assert payload["job"]["estimated_cost"] is None
    assert payload["job"]["metadata"]["provider_intent"] == {
        "model": "flux-2-pro-preview",
        "parameters": {
            "aspect_ratio": "16:9",
            "output_format": "png",
        },
        "provider": "bfl",
    }
    assert payload["job"]["metadata"]["source"] == "generation-api"
    assert len(queue.enqueued) == 1
    assert queue.enqueued[0]["job_id"] == payload["job"]["id"]
    assert "bfl-secret" not in response.text

    stored_job = asyncio.run(read_job(app.state.session_factory, UUID(payload["job"]["id"])))
    assert stored_job.provider == "bfl"
    assert stored_job.model == "flux-2-pro-preview"
    assert stored_job.estimated_cost is None
    assert stored_job.metadata_json["provider_intent"]["provider"] == "bfl"


def test_submit_hosted_generation_records_unsupported_reference_warnings(
    tmp_path: Path,
) -> None:
    client, _app, queue = create_generation_client(
        tmp_path,
        settings=hosted_api_settings(tmp_path),
    )
    workspace_id = client.post("/workspaces", json={"title": "Reference warnings"}).json()["id"]
    reference_asset_id = str(uuid4())
    brief = client.post(
        f"/workspaces/{workspace_id}/generation/briefs",
        json={
            "character_theme": "Sakura heroine",
            "original_request": "White coupe with a character reference.",
            "reference_usage": [
                {
                    "asset_id": reference_asset_id,
                    "enabled": True,
                    "role": "character",
                },
            ],
        },
    )
    assert brief.status_code == 201

    response = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={
            "brief_id": brief.json()["id"],
            "idempotency_key": "hosted-reference-warning",
            "model": "flux-2-pro-preview",
            "provider": "bfl",
            "requested_by": "local-user",
        },
    )

    assert response.status_code == 201
    metadata = response.json()["job"]["metadata"]
    assert metadata["reference_usage"] == {
        "included_reference_asset_ids": [],
        "omitted_reference_asset_ids": [reference_asset_id],
        "reference_warning_count": 1,
        "reference_warnings": [
            {
                "asset_id": reference_asset_id,
                "reason": "unsupported_by_provider",
                "role": "character",
            },
        ],
        "unsupported_reference_roles": ["character"],
    }
    assert len(queue.enqueued) == 1
    assert "bfl-secret" not in response.text


def test_cancel_generation_job_marks_canceled_and_revokes_queue_task(
    tmp_path: Path,
) -> None:
    client, _app, queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Generation"}).json()["id"]
    brief_id = create_brief(client, workspace_id)
    submitted = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={
            "brief_id": brief_id,
            "idempotency_key": "cancel-001",
            "requested_by": "local-user",
        },
    ).json()
    job_id = submitted["job"]["id"]

    canceled = client.post(
        f"/jobs/{job_id}/cancel",
        json={"reason": "user_request", "requested_by": "local-user"},
    )
    fetched = client.get(f"/jobs/{job_id}")

    assert canceled.status_code == 200
    assert canceled.json()["job"]["status"] == "canceled"
    assert canceled.json()["job"]["latest_error"] is None
    assert canceled.json()["queue_revoke"] == {
        "detail": None,
        "status": "revoked",
        "task_id": "task-1",
    }
    assert fetched.json()["metadata"]["operations"] == {
        "failure_category": "canceled",
        "reason": "user_request",
        "requested_by": "local-user",
    }
    assert queue.revoked == ["task-1"]


def test_cancel_generation_job_rejects_terminal_status(tmp_path: Path) -> None:
    client, app, queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Generation"}).json()["id"]
    brief_id = create_brief(client, workspace_id)
    submitted = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={"brief_id": brief_id, "idempotency_key": "cancel-terminal-001"},
    ).json()
    job_id = submitted["job"]["id"]
    asyncio.run(mark_job_succeeded(app.state.session_factory, UUID(job_id)))

    canceled = client.post(
        f"/jobs/{job_id}/cancel",
        json={"reason": "user_request", "requested_by": "local-user"},
    )

    assert canceled.status_code == 422
    assert queue.revoked == []


def test_generation_routes_reject_missing_brief_or_request_data(tmp_path: Path) -> None:
    client, _app, queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Generation"}).json()["id"]

    missing_request = client.post(
        f"/workspaces/{workspace_id}/generation/briefs",
        json={"character_theme": "Sakura"},
    )
    missing_brief = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={"idempotency_key": "submit-001"},
    )

    assert missing_request.status_code == 422
    assert missing_brief.status_code == 422
    assert queue.enqueued == []


def test_retry_failed_generation_creates_new_job_without_overwriting_failed_job(
    tmp_path: Path,
) -> None:
    client, app, queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Generation"}).json()["id"]
    brief_id = create_brief(client, workspace_id)
    failed = client.post(
        f"/workspaces/{workspace_id}/generation/jobs",
        json={"brief_id": brief_id, "idempotency_key": "failed-001"},
    ).json()["job"]
    asyncio.run(mark_job_failed(app.state.session_factory, UUID(failed["id"])))

    retry = client.post(
        f"/jobs/{failed['id']}/retry",
        json={"idempotency_key": "retry-001", "requested_by": "local-user"},
    )
    original = client.get(f"/jobs/{failed['id']}")

    assert retry.status_code == 201
    assert retry.json()["job"]["id"] != failed["id"]
    assert retry.json()["job"]["brief_id"] == brief_id
    assert retry.json()["job"]["operation"] == "generate_2d_concept"
    assert retry.json()["job"]["status"] == "queued"
    assert retry.json()["retry_of_job_id"] == failed["id"]
    assert original.json()["status"] == "failed"
    assert len(queue.enqueued) == 2
    assert queue.enqueued[-1]["job_id"] == retry.json()["job"]["id"]


def test_retry_targeted_iteration_preserves_edit_intent_and_provider_intent(
    tmp_path: Path,
) -> None:
    client, app, queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Retry targeted"}).json()["id"]
    brief_id = create_brief(client, workspace_id)
    parent_version_id, parent_artifact_id = asyncio.run(
        create_parent_version_with_artifact(
            app.state.session_factory,
            workspace_id,
            brief_id,
        ),
    )
    edit_intent = targeted_edit_intent_payload(mask_artifact_id=parent_artifact_id)

    failed = client.post(
        f"/workspaces/{workspace_id}/versions/{parent_version_id}/iterations",
        json={
            "brief_id": brief_id,
            "change_request": "Move the selected door text.",
            "edit_intent": edit_intent,
            "idempotency_key": "targeted-retry-source",
            "provider": "local-deterministic",
            "provider_parameters": {"quality": "concept"},
        },
    ).json()["job"]
    asyncio.run(
        mark_job_failed(
            app.state.session_factory,
            UUID(failed["id"]),
            metadata={
                "failure_category": "provider",
                "retry_eligible": True,
                "retry_route": "deterministic_recomposition",
            },
        ),
    )

    retry = client.post(
        f"/jobs/{failed['id']}/retry",
        json={"idempotency_key": "targeted-retry-001", "requested_by": "local-user"},
    )

    assert retry.status_code == 201
    retry_job = retry.json()["job"]
    assert retry_job["provider"] == "local-deterministic"
    assert retry_job["model"] == "local-concept-v1"
    assert retry_job["metadata"]["retry_of_job_id"] == failed["id"]
    assert retry_job["metadata"]["parent_version_id"] == str(parent_version_id)
    assert retry_job["metadata"]["edit_intent"] == edit_intent | {
        "parent_version_id": str(parent_version_id),
    }
    assert retry_job["metadata"]["provider_intent"] == {
        "model": "local-concept-v1",
        "parameters": {"quality": "concept"},
        "provider": "local-deterministic",
    }
    assert retry.json()["retry_of_job_id"] == failed["id"]
    assert len(queue.enqueued) == 2
    assert queue.enqueued[-1]["job_id"] == retry_job["id"]


def test_retry_targeted_iteration_rejects_non_retryable_failure(
    tmp_path: Path,
) -> None:
    client, app, queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Retry blocked"}).json()["id"]
    brief_id = create_brief(client, workspace_id)
    parent_version_id, parent_artifact_id = asyncio.run(
        create_parent_version_with_artifact(
            app.state.session_factory,
            workspace_id,
            brief_id,
        ),
    )
    failed = client.post(
        f"/workspaces/{workspace_id}/versions/{parent_version_id}/iterations",
        json={
            "brief_id": brief_id,
            "change_request": "Move a missing layer.",
            "edit_intent": targeted_edit_intent_payload(mask_artifact_id=parent_artifact_id),
            "idempotency_key": "targeted-retry-blocked",
        },
    ).json()["job"]
    asyncio.run(
        mark_job_failed(
            app.state.session_factory,
            UUID(failed["id"]),
            metadata={
                "blocked_reason": "target not found",
                "failure_category": "targeted_edit_invalid",
                "retry_eligible": False,
                "retry_route": "deterministic_recomposition",
            },
        ),
    )

    retry = client.post(
        f"/jobs/{failed['id']}/retry",
        json={"idempotency_key": "targeted-retry-blocked-again"},
    )

    assert retry.status_code == 422
    assert "target not found" in retry.json()["detail"]
    assert len(queue.enqueued) == 1


def test_submit_iteration_job_records_parent_metadata_without_overwriting_parent(
    tmp_path: Path,
) -> None:
    client, app, queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Generation"}).json()["id"]
    brief_id = create_brief(client, workspace_id)
    parent_version_id = asyncio.run(
        create_parent_version(app.state.session_factory, workspace_id, brief_id),
    )

    first = client.post(
        f"/workspaces/{workspace_id}/versions/{parent_version_id}/iterations",
        json={
            "brief_id": brief_id,
            "change_request": "Increase pink accents and keep the door text.",
            "idempotency_key": "iterate-001",
            "parameter_overrides": {"palette": ["white", "pink"]},
            "requested_by": "local-user",
        },
    )
    duplicate = client.post(
        f"/workspaces/{workspace_id}/versions/{parent_version_id}/iterations",
        json={
            "brief_id": brief_id,
            "change_request": "Increase pink accents and keep the door text.",
            "idempotency_key": "iterate-001",
            "parameter_overrides": {"palette": ["white", "pink"]},
            "requested_by": "local-user",
        },
    )

    assert first.status_code == 201
    assert duplicate.status_code == 201
    assert first.json()["job"]["operation"] == "generate_2d_concept"
    assert first.json()["job"]["brief_id"] == brief_id
    assert first.json()["idempotent_reused"] is False
    assert duplicate.json()["job"]["id"] == first.json()["job"]["id"]
    assert duplicate.json()["idempotent_reused"] is True
    assert len(queue.enqueued) == 1
    assert queue.enqueued[0]["job_id"] == first.json()["job"]["id"]

    stored_job = asyncio.run(read_job(app.state.session_factory, UUID(first.json()["job"]["id"])))
    parent = asyncio.run(read_version(app.state.session_factory, parent_version_id))
    metadata_without_template = {
        key: value for key, value in stored_job.metadata_json.items() if key != "vehicle_template"
    }
    assert metadata_without_template == {
        "change_request": "Increase pink accents and keep the door text.",
        "iteration": True,
        "parameter_overrides": {"palette": ["white", "pink"]},
        "parent_version_id": str(parent_version_id),
        "queue": {
            "queue": "caragent.default",
            "task_id": "task-1",
            "task_name": "caragent_worker.generate_2d_concept_job",
        },
        "source": "generation-iteration-api",
    }
    assert stored_job.metadata_json["vehicle_template"]["id"] == MVP_COUPE_TEMPLATE_ID
    assert parent.parent_version_id is None
    assert parent.lineage_depth == 0
    assert parent.parameters == {"concept_label": "parent_preview"}


def test_submit_targeted_iteration_records_edit_intent_metadata(
    tmp_path: Path,
) -> None:
    client, app, queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Targeted edit"}).json()["id"]
    brief_id = create_brief(client, workspace_id)
    parent_version_id = asyncio.run(
        create_parent_version(app.state.session_factory, workspace_id, brief_id),
    )
    spoofed_parent_id = uuid4()
    mask_artifact_id = uuid4()

    response = client.post(
        f"/workspaces/{workspace_id}/versions/{parent_version_id}/iterations",
        json={
            "brief_id": brief_id,
            "change_request": "Move the door typography upward without changing the character.",
            "edit_intent": targeted_edit_intent_payload(
                mask_artifact_id=mask_artifact_id,
                parent_version_id=spoofed_parent_id,
            ),
            "idempotency_key": "targeted-edit-001",
            "parameter_overrides": {"coverage": "door focus"},
            "provider": "local-deterministic",
            "provider_parameters": {"quality": "concept"},
            "requested_by": "local-user",
        },
    )

    assert response.status_code == 201
    assert len(queue.enqueued) == 1

    stored_job = asyncio.run(
        read_job(app.state.session_factory, UUID(response.json()["job"]["id"])),
    )
    assert stored_job.metadata_json["parent_version_id"] == str(parent_version_id)
    assert stored_job.metadata_json["edit_intent"] == {
        "mask": {
            "artifact_id": str(mask_artifact_id),
            "content_type": "image/png",
            "height": 768,
            "width": 1536,
        },
        "mode": "targeted_edit",
        "parent_version_id": str(parent_version_id),
        "prompt_delta": {
            "instructions": ["Move door typography upward."],
            "summary": "Move the selected door text layer.",
        },
        "region": {
            "height": 0.2,
            "type": "rectangle",
            "unit": "normalized",
            "width": 0.4,
            "x": 0.2,
            "y": 0.35,
        },
        "route_preference": "deterministic_recomposition",
        "schema_version": 1,
        "target": {
            "id": "door-main",
            "type": "safe_zone",
        },
    }
    assert stored_job.metadata_json["provider_intent"] == {
        "model": "local-concept-v1",
        "parameters": {"quality": "concept"},
        "provider": "local-deterministic",
    }


def test_submit_provider_masked_iteration_rejects_unsupported_provider_route(
    tmp_path: Path,
) -> None:
    client, app, queue = create_generation_client(
        tmp_path,
        settings=hosted_api_settings(tmp_path, v2_targeted_regeneration_enabled=True),
    )
    workspace_id = client.post("/workspaces", json={"title": "Provider mask"}).json()["id"]
    brief_id = create_brief(client, workspace_id)
    parent_version_id = asyncio.run(
        create_parent_version(app.state.session_factory, workspace_id, brief_id),
    )

    response = client.post(
        f"/workspaces/{workspace_id}/versions/{parent_version_id}/iterations",
        json={
            "brief_id": brief_id,
            "change_request": "Repaint just the selected door text.",
            "edit_intent": targeted_edit_intent_payload(
                route_preference="provider_masked_generation",
            ),
            "idempotency_key": "provider-mask-unsupported",
            "model": "flux-2-pro-preview",
            "provider": "bfl",
            "provider_parameters": {"output_format": "png"},
            "requested_by": "local-user",
        },
    )

    assert response.status_code == 422
    assert "provider_masked_generation" in response.json()["detail"]
    assert "does not support" in response.json()["detail"]
    assert queue.enqueued == []
    assert "bfl-secret" not in response.text


def targeted_edit_intent_payload(
    *,
    mask_artifact_id: UUID | None = None,
    parent_version_id: UUID | None = None,
    prompt_delta: dict[str, Any] | None = None,
    region: dict[str, Any] | None = None,
    route_preference: str = "deterministic_recomposition",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "mask": {
            "artifact_id": str(mask_artifact_id or uuid4()),
            "content_type": "image/png",
            "height": 768,
            "width": 1536,
        },
        "mode": "targeted_edit",
        "prompt_delta": prompt_delta
        if prompt_delta is not None
        else {
            "instructions": ["Move door typography upward."],
            "summary": "Move the selected door text layer.",
        },
        "region": region
        if region is not None
        else {
            "height": 0.2,
            "type": "rectangle",
            "unit": "normalized",
            "width": 0.4,
            "x": 0.2,
            "y": 0.35,
        },
        "route_preference": route_preference,
        "schema_version": 1,
        "target": {
            "id": "door-main",
            "type": "safe_zone",
        },
    }
    if parent_version_id is not None:
        payload["parent_version_id"] = str(parent_version_id)
    return payload


@pytest.mark.parametrize(
    ("edit_intent", "expected_detail"),
    [
        (
            targeted_edit_intent_payload(
                region={
                    "height": 0.2,
                    "type": "rectangle",
                    "unit": "normalized",
                    "width": 0.4,
                    "x": -0.1,
                    "y": 0.35,
                },
            ),
            "region",
        ),
        (
            targeted_edit_intent_payload(route_preference="full_regeneration"),
            "route",
        ),
        (
            targeted_edit_intent_payload(prompt_delta={"instructions": []}),
            "prompt_delta",
        ),
        (
            {
                key: value
                for key, value in targeted_edit_intent_payload().items()
                if key != "mask"
            },
            "mask",
        ),
    ],
)
def test_submit_targeted_iteration_validates_edit_intent(
    tmp_path: Path,
    edit_intent: dict[str, Any],
    expected_detail: str,
) -> None:
    client, app, queue = create_generation_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Invalid targeted edit"}).json()["id"]
    brief_id = create_brief(client, workspace_id)
    parent_version_id = asyncio.run(
        create_parent_version(app.state.session_factory, workspace_id, brief_id),
    )

    response = client.post(
        f"/workspaces/{workspace_id}/versions/{parent_version_id}/iterations",
        json={
            "brief_id": brief_id,
            "change_request": "Try a targeted edit.",
            "edit_intent": edit_intent,
            "idempotency_key": f"targeted-invalid-{expected_detail}",
        },
    )

    assert response.status_code == 422
    assert expected_detail in response.text
    assert queue.enqueued == []


def test_submit_iteration_job_rejects_missing_or_wrong_workspace_parent_version(
    tmp_path: Path,
) -> None:
    client, app, queue = create_generation_client(tmp_path)
    first_workspace_id = client.post("/workspaces", json={"title": "First"}).json()["id"]
    second_workspace_id = client.post("/workspaces", json={"title": "Second"}).json()["id"]
    first_brief_id = create_brief(client, first_workspace_id)
    second_brief_id = create_brief(client, second_workspace_id)
    parent_version_id = asyncio.run(
        create_parent_version(app.state.session_factory, first_workspace_id, first_brief_id),
    )

    missing_parent = client.post(
        f"/workspaces/{first_workspace_id}/versions/{uuid4()}/iterations",
        json={
            "brief_id": first_brief_id,
            "change_request": "Try a cleaner side stripe.",
            "idempotency_key": "iterate-missing",
        },
    )
    wrong_workspace_parent = client.post(
        f"/workspaces/{second_workspace_id}/versions/{parent_version_id}/iterations",
        json={
            "brief_id": second_brief_id,
            "change_request": "Try a cleaner side stripe.",
            "idempotency_key": "iterate-wrong-workspace",
        },
    )

    assert missing_parent.status_code == 422
    assert wrong_workspace_parent.status_code == 422
    assert queue.enqueued == []


def test_api_generation_boundary_does_not_import_worker_or_provider_code() -> None:
    forbidden = (
        re.compile(r"^\s*import\s+caragent_worker\b", re.MULTILINE),
        re.compile(r"^\s*from\s+caragent_worker\b", re.MULTILINE),
        re.compile(r"^\s*from\s+caragent_worker\.providers\b", re.MULTILINE),
        re.compile(r"\bfal_client\b"),
    )
    violations = [
        f"{source_file}: {pattern.pattern}"
        for source_file in Path("src/caragent_api").rglob("*.py")
        for pattern in forbidden
        if pattern.search(source_file.read_text(encoding="utf-8"))
    ]

    assert violations == []


def create_brief(
    client: TestClient,
    workspace_id: str,
    *,
    original_request: str = "White coupe with Sakura heroine and MOON DRIVE text.",
) -> str:
    response = client.post(
        f"/workspaces/{workspace_id}/generation/briefs",
        json={
            "character_theme": "Sakura heroine",
            "original_request": original_request,
            "palette": ["white", "teal"],
            "text": ["MOON DRIVE"],
        },
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def api_settings(tmp_path: Path, **overrides: Any) -> ApiSettings:
    return ApiSettings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'generation-api.db').as_posix()}",
        **overrides,
    )


def hosted_api_settings(tmp_path: Path, **overrides: Any) -> ApiSettings:
    settings: dict[str, Any] = {
        "ai_hosted_daily_call_limit": 10,
        "ai_hosted_rate_limit_per_minute": 5,
        "ai_max_estimated_cost_per_job": Decimal("0.5000"),
        "ai_provider_bfl_api_key": SecretStr("bfl-secret"),
        "ai_provider_calls_enabled": True,
        "ai_provider_default": "bfl",
        "ai_provider_model": "flux-2-pro-preview",
        "v2_hosted_provider_rollout_enabled": True,
    }
    settings.update(overrides)
    return api_settings(tmp_path, **settings)


async def mark_job_failed(
    session_factory: async_sessionmaker[Any],
    job_id: UUID,
    *,
    metadata: dict[str, object] | None = None,
) -> None:
    async with session_scope(session_factory) as session:
        await jobs.transition_job_status(
            session,
            job_id,
            latest_error="forced failure",
            metadata=metadata,
            message="Forced failed state.",
            source="test",
            status=JobStatus.FAILED.value,
        )


async def mark_job_succeeded(
    session_factory: async_sessionmaker[Any],
    job_id: UUID,
) -> None:
    async with session_scope(session_factory) as session:
        await jobs.transition_job_status(
            session,
            job_id,
            message="Forced succeeded state.",
            source="test",
            status=JobStatus.SUCCEEDED.value,
        )


async def create_parent_version(
    session_factory: async_sessionmaker[Any],
    workspace_id: str,
    brief_id: str,
) -> UUID:
    async with session_scope(session_factory) as session:
        version = await jobs.create_design_version(
            session,
            UUID(workspace_id),
            brief_id=UUID(brief_id),
            parameters={"concept_label": "parent_preview"},
            status=DesignVersionStatus.GENERATED.value,
            summary="Parent concept.",
            title="Parent concept",
        )
        return version.id


async def create_parent_version_with_artifact(
    session_factory: async_sessionmaker[Any],
    workspace_id: str,
    brief_id: str,
) -> tuple[UUID, UUID]:
    async with session_scope(session_factory) as session:
        version = await jobs.create_design_version(
            session,
            UUID(workspace_id),
            brief_id=UUID(brief_id),
            parameters={"concept_label": "parent_preview"},
            status=DesignVersionStatus.GENERATED.value,
            summary="Parent concept.",
            title="Parent concept",
        )
        artifact = await jobs.create_artifact(
            session,
            UUID(workspace_id),
            byte_size=len(b"parent-preview"),
            content_type="image/png",
            height=768,
            job_id=None,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            metadata={"concept_label": "parent_preview"},
            object_key=f"workspaces/{workspace_id}/generated/{version.id}/parent.png",
            version_id=version.id,
            width=1536,
        )
        return version.id, artifact.id


async def read_dispatch_outbox(
    session_factory: async_sessionmaker[Any],
) -> list[JobDispatchOutbox]:
    async with session_scope(session_factory) as session:
        result = await session.scalars(
            select(JobDispatchOutbox).order_by(JobDispatchOutbox.created_at.asc()),
        )
        return list(result)

async def read_job(
    session_factory: async_sessionmaker[Any],
    job_id: UUID,
) -> GenerationJob:
    async with session_scope(session_factory) as session:
        return await jobs.get_job(session, job_id)


async def read_version(
    session_factory: async_sessionmaker[Any],
    version_id: UUID,
) -> DesignVersion:
    async with session_scope(session_factory) as session:
        version = await session.get(DesignVersion, version_id)
        assert version is not None
        return version
