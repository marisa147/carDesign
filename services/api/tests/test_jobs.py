from __future__ import annotations

import asyncio
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID

from caragent_core.database import session_scope
from caragent_core.enums import (
    ArtifactKind,
    DesignVersionStatus,
    FeedbackApprovalState,
    JobEventType,
    JobStatus,
    ModelRunStatus,
)
from caragent_core.models import metadata
from caragent_core.services import jobs
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from caragent_api.config import ApiSettings
from caragent_api.main import create_app


def create_job_client(tmp_path: Path) -> tuple[TestClient, Any]:
    database_path = tmp_path / "jobs.db"
    settings = ApiSettings(database_url=f"sqlite+aiosqlite:///{database_path.as_posix()}")
    app = create_app(settings)
    asyncio.run(create_schema(app.state.database_engine))
    return TestClient(app), app


async def create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)


async def mark_job_succeeded(
    session_factory: async_sessionmaker[Any],
    job_id: UUID,
) -> None:
    async with session_scope(session_factory) as session:
        await jobs.transition_job_status(
            session,
            job_id,
            status=JobStatus.SUCCEEDED.value,
            message="Local simulation completed.",
            source="worker",
        )


async def create_simulation_records(
    session_factory: async_sessionmaker[Any],
    workspace_id: UUID,
    job_id: UUID,
) -> dict[str, str]:
    async with session_scope(session_factory) as session:
        version = await jobs.create_design_version(
            session,
            workspace_id,
            job_id=job_id,
            status=DesignVersionStatus.GENERATED.value,
            title="Local simulation",
        )
        artifact = await jobs.create_artifact(
            session,
            workspace_id,
            job_id=job_id,
            version_id=version.id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace_id}/generated/{version.id}/concept.png",
            content_type="image/png",
            byte_size=128,
        )
        model_run = await jobs.create_model_run(
            session,
            job_id,
            provider="local-simulation",
            model="phase-2-no-provider",
            status=ModelRunStatus.SUCCEEDED.value,
            estimated_cost=Decimal("0.0000"),
            actual_cost=Decimal("0.0000"),
            output_artifact_id=artifact.id,
        )
        feedback = await jobs.record_feedback(
            session,
            workspace_id,
            version.id,
            approval_state=FeedbackApprovalState.APPROVED.value,
            rating=5,
        )
        export = await jobs.record_export(
            session,
            workspace_id,
            version.id,
            artifact_id=artifact.id,
            export_format="png",
        )

    return {
        "artifact_id": str(artifact.id),
        "export_id": str(export.id),
        "feedback_id": str(feedback.id),
        "model_run_id": str(model_run.id),
        "version_id": str(version.id),
    }


def test_create_job_requires_idempotency_and_reuses_duplicate_key(tmp_path: Path) -> None:
    client, _app = create_job_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Jobs"}).json()["id"]

    missing_key = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"operation": "generate_concept"},
    )
    first = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={
            "idempotency_key": "brief-001",
            "operation": "generate_concept",
            "requested_by": "local-user",
        },
    )
    duplicate = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={
            "idempotency_key": "brief-001",
            "operation": "generate_concept",
            "requested_by": "local-user",
        },
    )

    assert missing_key.status_code == 422
    assert first.status_code == 201
    assert duplicate.status_code == 201
    assert duplicate.json()["id"] == first.json()["id"]
    assert first.json()["idempotent_reused"] is False
    assert duplicate.json()["idempotent_reused"] is True
    assert first.json()["estimated_cost"] is None
    assert first.json()["actual_cost"] is None


def test_job_reads_status_and_events_from_durable_storage(tmp_path: Path) -> None:
    client, app = create_job_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Jobs"}).json()["id"]
    created = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"idempotency_key": "status-001", "operation": "generate_concept"},
    ).json()
    job_id = created["id"]

    asyncio.run(mark_job_succeeded(app.state.session_factory, UUID(job_id)))

    with TestClient(app) as resumed_client:
        listed = resumed_client.get(f"/workspaces/{workspace_id}/jobs")
        fetched = resumed_client.get(f"/jobs/{job_id}")
        events = resumed_client.get(f"/jobs/{job_id}/events")

    assert listed.status_code == 200
    assert [job["id"] for job in listed.json()] == [job_id]
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "succeeded"
    assert events.status_code == 200
    assert [event["status"] for event in events.json()] == ["queued", "succeeded"]


def test_job_and_event_responses_expose_operational_metadata(tmp_path: Path) -> None:
    client, app = create_job_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Operations"}).json()["id"]
    created = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={
            "idempotency_key": "ops-response-001",
            "metadata": {
                "operations": {
                    "failure_category": "provider",
                    "provider": "bfl",
                    "stage": "provider_generate",
                },
            },
            "operation": "generate_concept",
        },
    ).json()
    job_id = created["id"]

    async def append_operational_event() -> None:
        async with session_scope(app.state.session_factory) as session:
            await jobs.append_event(
                session,
                UUID(job_id),
                event_type=JobEventType.ERROR.value,
                message="Generation failed.",
                metadata={
                    "failure_category": "provider",
                    "provider": "bfl",
                    "stage": "provider_generate",
                },
                source="worker-generation",
                status=JobStatus.FAILED.value,
            )

    asyncio.run(append_operational_event())

    fetched = client.get(f"/jobs/{job_id}")
    events = client.get(f"/jobs/{job_id}/events")

    assert fetched.status_code == 200
    assert fetched.json()["metadata"] == {
        "operations": {
            "failure_category": "provider",
            "provider": "bfl",
            "stage": "provider_generate",
        },
    }
    assert events.status_code == 200
    assert events.json()[-1]["metadata"] == {
        "failure_category": "provider",
        "provider": "bfl",
        "stage": "provider_generate",
    }


def test_simulation_records_are_readable_through_api(tmp_path: Path) -> None:
    client, app = create_job_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Simulation"}).json()["id"]
    job_id = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"idempotency_key": "simulation-001", "operation": "generate_concept"},
    ).json()["id"]
    records = asyncio.run(
        create_simulation_records(app.state.session_factory, UUID(workspace_id), UUID(job_id)),
    )

    versions = client.get(f"/workspaces/{workspace_id}/versions")
    artifacts = client.get(f"/workspaces/{workspace_id}/artifacts")
    model_runs = client.get(f"/jobs/{job_id}/model-runs")
    feedback = client.get(f"/workspaces/{workspace_id}/feedback")
    exports = client.get(f"/workspaces/{workspace_id}/exports")

    assert [item["id"] for item in versions.json()] == [records["version_id"]]
    assert [item["id"] for item in artifacts.json()] == [records["artifact_id"]]
    assert [item["id"] for item in model_runs.json()] == [records["model_run_id"]]
    assert [item["id"] for item in feedback.json()] == [records["feedback_id"]]
    assert [item["id"] for item in exports.json()] == [records["export_id"]]


def test_feedback_and_concept_export_can_be_created_through_api(tmp_path: Path) -> None:
    client, app = create_job_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Iteration"}).json()["id"]
    job_id = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"idempotency_key": "iteration-001", "operation": "generate_concept"},
    ).json()["id"]
    records = asyncio.run(
        create_simulation_records(app.state.session_factory, UUID(workspace_id), UUID(job_id)),
    )

    feedback = client.post(
        f"/workspaces/{workspace_id}/versions/{records['version_id']}/feedback",
        json={
            "approval_state": "approved",
            "comment": "Good concept direction.",
            "rating": 4,
        },
    )
    export = client.post(
        f"/workspaces/{workspace_id}/versions/{records['version_id']}/exports",
        json={
            "artifact_id": records["artifact_id"],
            "format": "png",
        },
    )

    assert feedback.status_code == 201
    assert feedback.json()["version_id"] == records["version_id"]
    assert feedback.json()["approval_state"] == "approved"
    assert feedback.json()["rating"] == 4
    assert feedback.json()["comment"] == "Good concept direction."

    assert export.status_code == 201
    export_payload = export.json()
    assert export_payload["version_id"] == records["version_id"]
    assert export_payload["artifact_id"] == records["artifact_id"]
    assert export_payload["format"] == "png"
    assert export_payload["concept_label"] == "concept_preview"
    assert export_payload["manifest"]["version_id"] == records["version_id"]
    assert export_payload["manifest"]["source_artifact_id"] == records["artifact_id"]
    assert export_payload["manifest"]["format"] == "png"
    assert "not print-ready" in export_payload["manifest"]["disclaimer"]


def test_feedback_and_export_creation_validate_inputs(tmp_path: Path) -> None:
    client, app = create_job_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Validation"}).json()["id"]
    other_workspace_id = client.post("/workspaces", json={"title": "Other"}).json()["id"]
    job_id = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"idempotency_key": "validation-001", "operation": "generate_concept"},
    ).json()["id"]
    records = asyncio.run(
        create_simulation_records(app.state.session_factory, UUID(workspace_id), UUID(job_id)),
    )

    bad_rating = client.post(
        f"/workspaces/{workspace_id}/versions/{records['version_id']}/feedback",
        json={"approval_state": "approved", "rating": 6},
    )
    wrong_workspace = client.post(
        f"/workspaces/{other_workspace_id}/versions/{records['version_id']}/feedback",
        json={"approval_state": "approved", "rating": 4},
    )
    bad_export_format = client.post(
        f"/workspaces/{workspace_id}/versions/{records['version_id']}/exports",
        json={"artifact_id": records["artifact_id"], "format": "pdf"},
    )

    assert bad_rating.status_code == 422
    assert wrong_workspace.status_code == 422
    assert bad_export_format.status_code == 422
