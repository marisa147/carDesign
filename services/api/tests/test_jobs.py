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
from caragent_core.models import Artifact, DesignVersion, metadata
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
            metadata={
                "actual_cost": "0.0300",
                "model": "flux-2-pro-preview",
                "provider": "bfl",
                "provider_status": "ready",
            },
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


async def create_targeted_edit_records(
    session_factory: async_sessionmaker[Any],
    workspace_id: UUID,
    job_id: UUID,
) -> dict[str, str]:
    async with session_scope(session_factory) as session:
        parent = await jobs.create_design_version(
            session,
            workspace_id,
            job_id=job_id,
            parameters={"concept_label": "parent_preview", "preview_spec": parent_preview_spec()},
            status=DesignVersionStatus.GENERATED.value,
            title="Parent concept",
        )
        parent_artifact = await jobs.create_artifact(
            session,
            workspace_id,
            job_id=job_id,
            version_id=parent.id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace_id}/generated/{parent.id}/parent.png",
            content_type="image/png",
            byte_size=128,
            metadata={"concept_label": "parent_preview", "preview_spec": parent_preview_spec()},
            height=768,
            width=1536,
        )
        trace_metadata = targeted_edit_trace_metadata(parent, parent_artifact)
        child = await jobs.create_design_version(
            session,
            workspace_id,
            job_id=job_id,
            parent_version_id=parent.id,
            parameters={
                "concept_label": "targeted_recomposition",
                "preview_spec": parent_preview_spec(),
                **trace_metadata,
            },
            status=DesignVersionStatus.GENERATED.value,
            title="Targeted recomposition preview",
        )
        child_artifact = await jobs.create_artifact(
            session,
            workspace_id,
            job_id=job_id,
            version_id=child.id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace_id}/generated/{child.id}/concept.png",
            content_type="image/png",
            byte_size=144,
            metadata=trace_metadata,
            height=768,
            width=1536,
        )
        model_run = await jobs.create_model_run(
            session,
            job_id,
            provider="deterministic-recomposition",
            model="preview-spec-recomposer-v1",
            status=ModelRunStatus.SUCCEEDED.value,
            parameters=trace_metadata,
            prompt_payload={"mask_edit": trace_metadata},
            prompt_text="Move selected door text.",
            estimated_cost=Decimal("0.0000"),
            actual_cost=Decimal("0.0000"),
            input_artifact_ids=[str(parent_artifact.id)],
            output_artifact_id=child_artifact.id,
        )
        await jobs.transition_job_status(
            session,
            job_id,
            status=JobStatus.SUCCEEDED.value,
            message="Generation completed.",
            metadata={**trace_metadata, "stage": "completed"},
            source="worker-generation",
        )

    return {
        "child_artifact_id": str(child_artifact.id),
        "child_version_id": str(child.id),
        "model_run_id": str(model_run.id),
        "parent_artifact_id": str(parent_artifact.id),
        "parent_version_id": str(parent.id),
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
    assert artifacts.json()[0]["metadata"] == {
        "actual_cost": "0.0300",
        "model": "flux-2-pro-preview",
        "provider": "bfl",
        "provider_status": "ready",
    }
    assert [item["id"] for item in model_runs.json()] == [records["model_run_id"]]
    assert [item["id"] for item in feedback.json()] == [records["feedback_id"]]
    assert [item["id"] for item in exports.json()] == [records["export_id"]]


def test_targeted_edit_records_are_readable_through_api(tmp_path: Path) -> None:
    client, app = create_job_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Targeted evidence"}).json()["id"]
    job_id = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"idempotency_key": "targeted-api-001", "operation": "generate_2d_concept"},
    ).json()["id"]
    records = asyncio.run(
        create_targeted_edit_records(
            app.state.session_factory,
            UUID(workspace_id),
            UUID(job_id),
        ),
    )

    fetched_job = client.get(f"/jobs/{job_id}")
    events = client.get(f"/jobs/{job_id}/events")
    versions = client.get(f"/workspaces/{workspace_id}/versions")
    artifacts = client.get(f"/workspaces/{workspace_id}/artifacts")
    model_runs = client.get(f"/jobs/{job_id}/model-runs")

    assert fetched_job.json()["metadata"]["operations"]["edit_route"] == (
        "deterministic_recomposition"
    )
    assert events.json()[-1]["metadata"]["target"] == {
        "id": "text-1",
        "type": "overlay_layer",
    }
    parent, child = versions.json()
    assert parent["id"] == records["parent_version_id"]
    assert child["id"] == records["child_version_id"]
    assert child["parent_version_id"] == records["parent_version_id"]
    assert child["parameters"]["edit_route"] == "deterministic_recomposition"
    assert child["parameters"]["mask_artifact_id"] == records["parent_artifact_id"]
    assert child["parameters"]["prompt_delta"]["summary"] == "Move selected door text."

    parent_artifact, child_artifact = artifacts.json()
    assert parent_artifact["id"] == records["parent_artifact_id"]
    assert child_artifact["id"] == records["child_artifact_id"]
    assert child_artifact["metadata"]["region"]["unit"] == "normalized"
    assert child_artifact["metadata"]["target"]["id"] == "text-1"

    model_run = model_runs.json()[0]
    assert model_run["id"] == records["model_run_id"]
    assert model_run["input_artifact_ids"] == [records["parent_artifact_id"]]
    assert model_run["parameters"]["edit_route"] == "deterministic_recomposition"
    assert model_run["prompt_payload"]["mask_edit"]["mask_artifact_id"] == (
        records["parent_artifact_id"]
    )


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


def parent_preview_spec() -> dict[str, object]:
    return {
        "overlay_layers": [
            {"id": "text-1", "kind": "text", "text": "MOON DRIVE", "zone_id": "door-main"},
        ],
        "safe_zones": [
            {
                "height": 0.24,
                "id": "door-main",
                "kind": "body",
                "label": "Door / main side panel",
                "width": 0.34,
                "x": 0.32,
                "y": 0.47,
            },
        ],
    }


def targeted_edit_trace_metadata(
    parent: DesignVersion,
    parent_artifact: Artifact,
) -> dict[str, object]:
    parent_id = str(parent.id)
    parent_artifact_id = str(parent_artifact.id)
    return {
        "changed_fields": ["text", "y"],
        "edit_route": "deterministic_recomposition",
        "external_calls": False,
        "mask_artifact_id": parent_artifact_id,
        "mask_content_type": "image/png",
        "mask_height": 768,
        "mask_width": 1536,
        "parent_artifact_id": parent_artifact_id,
        "parent_version_id": parent_id,
        "prompt_delta": {
            "instructions": ["Move selected door text."],
            "summary": "Move selected door text.",
        },
        "region": {
            "height": 0.24,
            "type": "rectangle",
            "unit": "normalized",
            "width": 0.34,
            "x": 0.32,
            "y": 0.47,
        },
        "target": {"id": "text-1", "type": "overlay_layer"},
    }
