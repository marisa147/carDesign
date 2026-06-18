from __future__ import annotations

import asyncio
import json
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from caragent_core.database import session_scope
from caragent_core.enums import JobStatus
from caragent_core.models import metadata
from caragent_core.services import jobs, workspaces
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncEngine

from caragent_api.config import ApiSettings
from caragent_api.main import create_app
from caragent_api.queue import QueuedGenerationTask, QueueInspection


class FakeQueueClient:
    def __init__(
        self,
        *,
        detail: str | None = "No worker replied.",
        raise_error: Exception | None = None,
        status: str = "unavailable",
    ) -> None:
        self.detail = detail
        self.raise_error = raise_error
        self.status = status

    async def enqueue_generation_job(self, job_id: UUID) -> QueuedGenerationTask:
        return QueuedGenerationTask(
            job_id=job_id,
            task_id="fake-task-id",
            task_name="caragent_worker.generate_2d_concept_job",
        )

    async def inspect_generation_queue(self) -> dict[str, Any]:
        if self.raise_error is not None:
            raise self.raise_error
        return {
            "active_tasks": 0,
            "active_workers": 0,
            "detail": self.detail,
            "generation_queue": "caragent.default",
            "registered_tasks": [],
            "reserved_tasks": 0,
            "status": self.status,
        }


class DataclassQueueClient(FakeQueueClient):
    async def inspect_generation_queue(self) -> QueueInspection:
        return QueueInspection(
            active_tasks=1,
            active_workers=1,
            detail=None,
            generation_queue="caragent.default",
            registered_tasks=["caragent_worker.generate_2d_concept_job"],
            reserved_tasks=0,
            status="ok",
        )


def create_operations_client(
    tmp_path: Path,
    *,
    queue_client: FakeQueueClient | None = None,
    settings: ApiSettings | None = None,
) -> tuple[TestClient, Any]:
    database_path = tmp_path / "operations.db"
    active_settings = settings or ApiSettings(
        database_url=f"sqlite+aiosqlite:///{database_path.as_posix()}",
    )
    app = create_app(active_settings)
    app.state.queue_client = queue_client or FakeQueueClient()
    asyncio.run(create_schema(app.state.database_engine))
    return TestClient(app), app


async def create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)


def test_operations_provider_status_reports_local_disabled_provider(tmp_path: Path) -> None:
    client, _app = create_operations_client(tmp_path)

    response = client.get("/operations/provider-status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["api_version"] == "0.1.0"
    assert payload["runtime_mode"] == "local"
    provider = payload["provider"]
    assert provider["active_mode"] == "local-deterministic"
    assert provider["bfl_key_configured"] is False
    assert provider["calls_enabled"] is False
    assert provider["default_provider"] == "disabled"
    assert provider["guard_state"]["hosted_quota_guard_enabled"] is False
    assert provider["hosted_calls_blocked_reason"] is None
    assert provider["hosted_daily_call_limit"] is None
    assert provider["hosted_provider_configured"] is False
    assert provider["hosted_quota_guard_enabled"] is False
    assert provider["hosted_rate_limit_per_minute"] is None
    assert provider["max_estimated_cost_per_job"] is None
    assert provider["supported_providers"] == ["local-deterministic", "bfl"]
    assert payload["queue"]["status"] == "unavailable"
    assert payload["queue"]["generation_queue"] == "caragent.default"
    assert payload["worker"]["status"] == "unavailable"
    assert payload["worker"]["task_name"] == "caragent_worker.generate_2d_concept_job"
    assert payload["recent_failures"] == []


def test_operations_provider_status_reports_hosted_config_without_secret(
    tmp_path: Path,
) -> None:
    settings = ApiSettings(
        ai_provider_bfl_api_key=SecretStr("bfl-secret"),
        ai_provider_calls_enabled=True,
        ai_provider_default="bfl",
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'hosted.db').as_posix()}",
    )
    client, _app = create_operations_client(tmp_path, settings=settings)

    response = client.get("/operations/provider-status")

    assert response.status_code == 200
    provider = response.json()["provider"]
    assert provider["active_mode"] == "local-deterministic"
    assert provider["bfl_key_configured"] is True
    assert provider["calls_enabled"] is True
    assert provider["default_provider"] == "bfl"
    assert provider["hosted_provider_configured"] is True
    assert provider["hosted_quota_guard_enabled"] is False
    assert "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED is disabled" in provider[
        "hosted_calls_blocked_reason"
    ]
    assert "Hosted quota/rate/cost guards are incomplete" in provider[
        "hosted_calls_blocked_reason"
    ]
    assert "bfl-secret" not in response.text


def test_operations_provider_status_reports_hosted_quota_guards(
    tmp_path: Path,
) -> None:
    settings = ApiSettings(
        ai_hosted_daily_call_limit=25,
        ai_hosted_rate_limit_per_minute=4,
        ai_max_estimated_cost_per_job=Decimal("0.7500"),
        ai_provider_bfl_api_key=SecretStr("bfl-secret"),
        ai_provider_calls_enabled=True,
        ai_provider_default="bfl",
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'hosted-guarded.db').as_posix()}",
        v2_hosted_provider_rollout_enabled=True,
    )
    client, _app = create_operations_client(tmp_path, settings=settings)

    response = client.get("/operations/provider-status")

    assert response.status_code == 200
    provider = response.json()["provider"]
    assert provider["hosted_calls_blocked_reason"] is None
    assert provider["hosted_daily_call_limit"] == 25
    assert provider["hosted_quota_guard_enabled"] is True
    assert provider["hosted_rate_limit_per_minute"] == 4
    assert provider["max_estimated_cost_per_job"] == "0.7500"
    assert "bfl-secret" not in response.text


def test_operations_provider_status_exposes_safe_capabilities_and_guard_state(
    tmp_path: Path,
) -> None:
    settings = ApiSettings(
        ai_hosted_daily_call_limit=25,
        ai_hosted_rate_limit_per_minute=4,
        ai_max_estimated_cost_per_job=Decimal("0.7500"),
        ai_provider_bfl_api_key=SecretStr("bfl-secret"),
        ai_provider_calls_enabled=True,
        ai_provider_default="bfl",
        ai_provider_model="flux-2-pro-preview",
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'hosted-capabilities.db').as_posix()}",
        v2_hosted_provider_rollout_enabled=True,
    )
    client, _app = create_operations_client(tmp_path, settings=settings)

    response = client.get("/operations/provider-status")

    assert response.status_code == 200
    provider = response.json()["provider"]
    assert provider["guard_state"] == {
        "daily_call_limit": 25,
        "hosted_quota_guard_enabled": True,
        "max_estimated_cost_per_job": "0.7500",
        "rate_limit_per_minute": 4,
    }
    capabilities = {item["provider"]: item for item in provider["capabilities"]}
    assert set(capabilities) == {"local-deterministic", "bfl"}
    assert capabilities["local-deterministic"]["enabled"] is True
    assert capabilities["local-deterministic"]["credential_required"] is False
    assert capabilities["bfl"]["enabled"] is True
    assert capabilities["bfl"]["credential_configured"] is True
    assert capabilities["bfl"]["default_model"] == "flux-2-pro-preview"
    assert capabilities["bfl"]["blocked_reasons"] == []
    rendered = json.dumps(provider, sort_keys=True)
    assert "bfl-secret" not in rendered
    assert "api_key" not in rendered.lower()
    assert "token" not in rendered.lower()


def test_operations_provider_status_blocks_bfl_without_secrets_or_guards(
    tmp_path: Path,
) -> None:
    settings = ApiSettings(
        ai_provider_calls_enabled=True,
        ai_provider_default="bfl",
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'blocked-capabilities.db').as_posix()}",
        v2_hosted_provider_rollout_enabled=True,
    )
    client, _app = create_operations_client(tmp_path, settings=settings)

    response = client.get("/operations/provider-status")

    assert response.status_code == 200
    provider = response.json()["provider"]
    bfl = next(item for item in provider["capabilities"] if item["provider"] == "bfl")
    assert bfl["enabled"] is False
    assert bfl["credential_configured"] is False
    assert "AI_PROVIDER_BFL_API_KEY is missing" in bfl["blocked_reasons"]
    assert "Hosted quota/rate/cost guards are incomplete" in bfl["blocked_reasons"]
    assert provider["guard_state"]["hosted_quota_guard_enabled"] is False
    assert "secret" not in response.text.lower()


def test_operations_provider_status_degrades_when_queue_probe_raises(
    tmp_path: Path,
) -> None:
    queue_client = FakeQueueClient(raise_error=RuntimeError("redis-secret unreachable"))
    client, _app = create_operations_client(tmp_path, queue_client=queue_client)

    response = client.get("/operations/provider-status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["queue"]["status"] == "unavailable"
    assert payload["worker"]["status"] == "unavailable"
    assert "redis-secret" not in response.text


def test_operations_provider_status_accepts_queue_inspection_dataclass(
    tmp_path: Path,
) -> None:
    client, _app = create_operations_client(tmp_path, queue_client=DataclassQueueClient())

    response = client.get("/operations/provider-status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["queue"]["status"] == "ok"
    assert payload["queue"]["active_tasks"] == 1
    assert payload["queue"]["active_workers"] == 1
    assert payload["queue"]["registered_tasks"] == [
        "caragent_worker.generate_2d_concept_job",
    ]
    assert payload["worker"]["status"] == "ok"


def test_operations_provider_status_lists_recent_classified_failures(
    tmp_path: Path,
) -> None:
    client, app = create_operations_client(tmp_path)

    async def seed_failure() -> str:
        async with session_scope(app.state.session_factory) as session:
            workspace = await workspaces.create_workspace(session, title="Operations")
            created = await jobs.create_job(
                session,
                workspace.id,
                idempotency_key="ops-failed-001",
                operation="generate_2d_concept",
            )
            await jobs.transition_job_status(
                session,
                created.job.id,
                status=JobStatus.FAILED.value,
                latest_error="Provider timeout",
                message="Generation failed.",
                metadata={
                    "failure_category": "provider",
                    "model": "flux-pro",
                    "provider": "bfl",
                    "stage": "provider_generate",
                },
                source="worker-generation",
            )
            return str(created.job.id)

    job_id = asyncio.run(seed_failure())

    response = client.get("/operations/provider-status")

    assert response.status_code == 200
    failure = response.json()["recent_failures"][0]
    assert failure["created_at"]
    assert failure == {
        "created_at": failure["created_at"],
        "failure_category": "provider",
        "job_id": job_id,
        "message": "Provider timeout",
        "model": "flux-pro",
        "provider": "bfl",
        "stage": "provider_generate",
        "status": "failed",
    }


def test_operations_recent_failures_fall_back_to_unknown_without_metadata(
    tmp_path: Path,
) -> None:
    client, app = create_operations_client(tmp_path)

    async def seed_failures() -> tuple[str, str]:
        async with session_scope(app.state.session_factory) as session:
            workspace = await workspaces.create_workspace(session, title="Legacy failures")
            categorized = await jobs.create_job(
                session,
                workspace.id,
                idempotency_key="ops-categorized-failed-001",
                operation="generate_2d_concept",
            )
            await jobs.transition_job_status(
                session,
                categorized.job.id,
                status=JobStatus.FAILED.value,
                latest_error="bfl-secret\nupstream failed",
                message="Generation failed.",
                metadata={
                    "failure_category": "provider",
                    "provider": "bfl",
                    "stage": "provider_generate",
                },
                secrets=("bfl-secret",),
                source="worker-generation",
            )
            legacy = await jobs.create_job(
                session,
                workspace.id,
                idempotency_key="ops-legacy-failed-001",
                operation="generate_2d_concept",
            )
            await jobs.transition_job_status(
                session,
                legacy.job.id,
                status=JobStatus.FAILED.value,
                latest_error="Legacy failure",
                message="Generation failed.",
                source="worker-generation",
            )
            return str(categorized.job.id), str(legacy.job.id)

    categorized_job_id, legacy_job_id = asyncio.run(seed_failures())

    response = client.get("/operations/provider-status")

    assert response.status_code == 200
    recent_failures = response.json()["recent_failures"]
    assert [failure["job_id"] for failure in recent_failures[:2]] == [
        legacy_job_id,
        categorized_job_id,
    ]
    assert recent_failures[0]["failure_category"] == "unknown"
    assert recent_failures[0]["message"] == "Legacy failure"
    assert recent_failures[1]["failure_category"] == "provider"
    assert recent_failures[1]["message"] == "[redacted] upstream failed"
    assert "bfl-secret" not in response.text
