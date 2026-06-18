from __future__ import annotations

import asyncio
import base64
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
from caragent_core.preview3d import (
    Preview3DScreenshotArtifactMetadata,
    Preview3DSpec,
    build_preview_3d_spec,
    required_preview_3d_warning_ids,
)
from caragent_core.services import jobs
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from caragent_api.config import ApiSettings
from caragent_api.main import create_app

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 32


def create_job_client(
    tmp_path: Path,
    *,
    settings_overrides: dict[str, Any] | None = None,
) -> tuple[TestClient, Any]:
    database_path = tmp_path / "jobs.db"
    settings = ApiSettings(
        database_url=f"sqlite+aiosqlite:///{database_path.as_posix()}",
        **(settings_overrides or {}),
    )
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


async def create_reference_trace_records(
    session_factory: async_sessionmaker[Any],
    workspace_id: UUID,
    job_id: UUID,
) -> dict[str, Any]:
    trace = reference_trace_metadata()
    async with session_scope(session_factory) as session:
        version = await jobs.create_design_version(
            session,
            workspace_id,
            job_id=job_id,
            parameters={
                "concept_label": "concept_preview",
                **trace,
            },
            status=DesignVersionStatus.GENERATED.value,
            title="Reference concept",
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
            metadata=trace,
        )
    return {
        "artifact_id": str(artifact.id),
        "reference_trace": trace,
        "version_id": str(version.id),
    }


async def create_preview_3d_records(
    session_factory: async_sessionmaker[Any],
    workspace_id: UUID,
    job_id: UUID,
) -> dict[str, str]:
    spec = preview_3d_spec()
    async with session_scope(session_factory) as session:
        version = await jobs.create_design_version(
            session,
            workspace_id,
            job_id=job_id,
            parameters={"preview_3d": spec.model_dump(mode="json")},
            status=DesignVersionStatus.GENERATED.value,
            title="3D preview source",
        )
        artifact = await jobs.create_artifact(
            session,
            workspace_id,
            byte_size=1024,
            checksum_sha256="b" * 64,
            content_type="image/png",
            height=720,
            job_id=job_id,
            kind=ArtifactKind.PREVIEW_3D_SCREENSHOT.value,
            metadata=preview_3d_screenshot_metadata().model_dump(mode="json"),
            object_key=f"workspaces/{workspace_id}/preview_3d_screenshot/{version.id}/capture.png",
            version_id=version.id,
            width=1280,
        )
    return {"artifact_id": str(artifact.id), "version_id": str(version.id)}


async def create_preview_3d_source_records(
    session_factory: async_sessionmaker[Any],
    workspace_id: UUID,
    job_id: UUID,
) -> dict[str, str]:
    async with session_scope(session_factory) as session:
        version = await jobs.create_design_version(
            session,
            workspace_id,
            job_id=job_id,
            parameters={"concept_label": "preview_3d_source"},
            status=DesignVersionStatus.GENERATED.value,
            title="3D preview source",
        )
        source_artifact = await jobs.create_artifact(
            session,
            workspace_id,
            byte_size=1024,
            content_type="image/png",
            height=768,
            job_id=job_id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace_id}/generated_image/{version.id}/concept.png",
            version_id=version.id,
            width=1536,
        )
        spec = build_preview_3d_spec(
            artifact_id=source_artifact.id,
            artifact_object_key=source_artifact.object_key,
            preview_spec={
                **parent_preview_spec(),
                "template": {
                    "id": "generic-side-coupe",
                    "label": "Generic side-view coupe",
                    "view": "side",
                },
            },
            version_id=version.id,
            workspace_id=workspace_id,
        )
        version.parameters = {
            **version.parameters,
            "preview_3d": spec.model_dump(mode="json"),
        }
        await session.flush()
    return {
        "source_artifact_id": str(source_artifact.id),
        "source_artifact_object_key": source_artifact.object_key,
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


def test_concept_export_manifest_includes_reference_trace_source(
    tmp_path: Path,
) -> None:
    client, app = create_job_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "Reference export"}).json()["id"]
    job_id = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"idempotency_key": "reference-export-001", "operation": "generate_concept"},
    ).json()["id"]
    records = asyncio.run(
        create_reference_trace_records(
            app.state.session_factory,
            UUID(workspace_id),
            UUID(job_id),
        ),
    )

    export = client.post(
        f"/workspaces/{workspace_id}/versions/{records['version_id']}/exports",
        json={
            "artifact_id": records["artifact_id"],
            "format": "png",
            "manifest": {"requested_by": "api-test"},
        },
    )

    assert export.status_code == 201
    manifest = export.json()["manifest"]
    trace = records["reference_trace"]
    for key in (
        "included_reference_asset_ids",
        "omitted_reference_asset_ids",
        "reference_roles",
        "reference_usage",
        "reference_warning_count",
        "rights_snapshot",
        "unsupported_reference_roles",
    ):
        assert manifest[key] == trace[key]
    rendered_manifest = str(manifest).lower()
    assert "image_bytes" not in rendered_manifest
    assert "api_key" not in rendered_manifest
    assert "secret" not in rendered_manifest


def test_preview_3d_screenshot_artifacts_are_readable_through_api(tmp_path: Path) -> None:
    client, app = create_job_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "3D preview"}).json()["id"]
    job_id = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"idempotency_key": "preview-3d-api-001", "operation": "generate_concept"},
    ).json()["id"]
    records = asyncio.run(
        create_preview_3d_records(app.state.session_factory, UUID(workspace_id), UUID(job_id)),
    )

    versions = client.get(f"/workspaces/{workspace_id}/versions")
    artifacts = client.get(f"/workspaces/{workspace_id}/artifacts")

    assert versions.status_code == 200
    assert versions.json()[0]["parameters"]["preview_3d"]["schema_version"] == 1
    assert versions.json()[0]["preview_3d"]["schema_version"] == 1
    assert versions.json()[0]["parameters"]["preview_3d"]["compatibility"] == {
        "reason": None,
        "shell_id": "generic-side-coupe-lightweight-v1",
        "status": "compatible",
    }

    assert artifacts.status_code == 200
    artifact = artifacts.json()[0]
    assert artifact["id"] == records["artifact_id"]
    assert artifact["kind"] == "preview_3d_screenshot"
    assert artifact["version_id"] == records["version_id"]
    assert artifact["metadata"]["preview_3d_screenshot"]["shell_id"] == (
        "generic-side-coupe-lightweight-v1"
    )
    assert artifact["preview_3d_screenshot"]["schema_version"] == 1
    assert artifact["preview_3d_screenshot"]["warning_ids"] == [
        "non_production_preview",
        "uv_not_verified",
    ]
    rendered = str(artifact["metadata"]).lower()
    assert "base64" not in rendered
    assert "image_bytes" not in rendered
    assert "binary" not in rendered


def test_preview_3d_screenshot_can_be_created_through_api(tmp_path: Path) -> None:
    client, app = create_job_client(
        tmp_path,
        settings_overrides={"v2_lightweight_3d_preview_enabled": True},
    )
    workspace_id = client.post("/workspaces", json={"title": "3D capture"}).json()["id"]
    job_id = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"idempotency_key": "preview-3d-capture-001", "operation": "generate_concept"},
    ).json()["id"]
    records = asyncio.run(
        create_preview_3d_source_records(
            app.state.session_factory,
            UUID(workspace_id),
            UUID(job_id),
        ),
    )

    created = client.post(
        f"/workspaces/{workspace_id}/versions/{records['version_id']}/preview-3d-screenshots",
        json=preview_3d_screenshot_create_payload(
            source_artifact_id=records["source_artifact_id"],
            source_artifact_object_key=records["source_artifact_object_key"],
            version_id=records["version_id"],
            workspace_id=workspace_id,
        ),
    )

    assert created.status_code == 201
    payload = created.json()
    assert payload["kind"] == "preview_3d_screenshot"
    assert payload["version_id"] == records["version_id"]
    assert payload["content_type"] == "image/png"
    assert payload["byte_size"] == len(PNG_BYTES)
    assert payload["width"] == 640
    assert payload["height"] == 360
    assert payload["object_key"].endswith("/preview-3d-screenshot.png")
    assert payload["metadata"]["preview_3d_screenshot"]["shell_id"] == (
        "generic-side-coupe-lightweight-v1"
    )
    assert payload["metadata"]["preview_3d_screenshot"]["source_artifact_id"] == (
        records["source_artifact_id"]
    )
    assert payload["preview_3d_screenshot"]["warning_ids"] == [
        "non_production_preview",
        "uv_not_verified",
    ]
    rendered = str(payload["metadata"]).lower()
    assert "base64" not in rendered
    assert "image_bytes" not in rendered
    assert "binary" not in rendered


def test_preview_3d_screenshot_creation_is_feature_gated(tmp_path: Path) -> None:
    client, app = create_job_client(tmp_path)
    workspace_id = client.post("/workspaces", json={"title": "3D capture off"}).json()["id"]
    job_id = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"idempotency_key": "preview-3d-capture-off", "operation": "generate_concept"},
    ).json()["id"]
    records = asyncio.run(
        create_preview_3d_source_records(
            app.state.session_factory,
            UUID(workspace_id),
            UUID(job_id),
        ),
    )

    response = client.post(
        f"/workspaces/{workspace_id}/versions/{records['version_id']}/preview-3d-screenshots",
        json=preview_3d_screenshot_create_payload(
            source_artifact_id=records["source_artifact_id"],
            source_artifact_object_key=records["source_artifact_object_key"],
            version_id=records["version_id"],
            workspace_id=workspace_id,
        ),
    )

    assert response.status_code == 403
    assert "V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED is disabled" in response.json()["detail"]


def test_preview_3d_screenshot_creation_validates_payload_and_ownership(
    tmp_path: Path,
) -> None:
    client, app = create_job_client(
        tmp_path,
        settings_overrides={"v2_lightweight_3d_preview_enabled": True},
    )
    workspace_id = client.post("/workspaces", json={"title": "3D capture validation"}).json()[
        "id"
    ]
    other_workspace_id = client.post("/workspaces", json={"title": "Other"}).json()["id"]
    job_id = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"idempotency_key": "preview-3d-capture-validation", "operation": "generate_concept"},
    ).json()["id"]
    records = asyncio.run(
        create_preview_3d_source_records(
            app.state.session_factory,
            UUID(workspace_id),
            UUID(job_id),
        ),
    )
    payload = preview_3d_screenshot_create_payload(
        source_artifact_id=records["source_artifact_id"],
        source_artifact_object_key=records["source_artifact_object_key"],
        version_id=records["version_id"],
        workspace_id=workspace_id,
    )

    unsupported_type = client.post(
        f"/workspaces/{workspace_id}/versions/{records['version_id']}/preview-3d-screenshots",
        json={**payload, "content_type": "image/gif"},
    )
    wrong_workspace = client.post(
        f"/workspaces/{other_workspace_id}/versions/{records['version_id']}/preview-3d-screenshots",
        json=payload,
    )
    wrong_version = client.post(
        f"/workspaces/{workspace_id}/versions/22222222-2222-2222-2222-222222222222/preview-3d-screenshots",
        json=payload,
    )

    assert unsupported_type.status_code == 422
    assert wrong_workspace.status_code == 422
    assert wrong_version.status_code == 422


def test_preview_3d_screenshot_creation_restores_required_warning_metadata(
    tmp_path: Path,
) -> None:
    client, app = create_job_client(
        tmp_path,
        settings_overrides={"v2_lightweight_3d_preview_enabled": True},
    )
    workspace_id = client.post("/workspaces", json={"title": "3D warning restore"}).json()["id"]
    job_id = client.post(
        f"/workspaces/{workspace_id}/jobs",
        json={"idempotency_key": "preview-3d-warning-restore", "operation": "generate_concept"},
    ).json()["id"]
    records = asyncio.run(
        create_preview_3d_source_records(
            app.state.session_factory,
            UUID(workspace_id),
            UUID(job_id),
        ),
    )
    payload = preview_3d_screenshot_create_payload(
        source_artifact_id=records["source_artifact_id"],
        source_artifact_object_key=records["source_artifact_object_key"],
        version_id=records["version_id"],
        workspace_id=workspace_id,
    )
    preview_3d = payload["preview_3d"]
    assert isinstance(preview_3d, dict)
    preview_3d["warnings"] = []

    created = client.post(
        f"/workspaces/{workspace_id}/versions/{records['version_id']}/preview-3d-screenshots",
        json=payload,
    )

    assert created.status_code == 201
    assert created.json()["preview_3d_screenshot"]["warning_ids"] == (
        required_preview_3d_warning_ids()
    )


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


def reference_trace_metadata() -> dict[str, object]:
    reference_id = "11111111-1111-1111-1111-111111111111"
    rights = {
        "asset_id": reference_id,
        "checksum_sha256": "a" * 64,
        "content_type": "image/png",
        "object_key": f"workspaces/workspace-1/reference/{reference_id}/reference.png",
        "original_filename": "reference.png",
        "rights_confirmed_at": "2026-06-17T00:10:00Z",
        "rights_notes": "User confirmed use.",
        "rights_status": "confirmed",
        "schema_version": 1,
        "source_label": "User source",
        "source_url": None,
    }
    return {
        "included_reference_asset_ids": [reference_id],
        "omitted_reference_asset_ids": [],
        "reference_roles": {"character": [reference_id]},
        "reference_usage": {
            "items": [
                {
                    "asset_id": reference_id,
                    "enabled": True,
                    "rights": rights,
                    "role": "character",
                    "schema_version": 1,
                },
            ],
            "schema_version": 1,
        },
        "reference_warning_count": 0,
        "rights_snapshot": {reference_id: rights},
        "unsupported_reference_roles": [],
    }


def preview_3d_spec() -> Preview3DSpec:
    return Preview3DSpec.model_validate(
        {
            "camera": {
                "preset_id": "front-left-default",
                "position": {"x": 2.8, "y": 1.4, "z": 4.2},
                "target": {"x": 0.0, "y": 0.4, "z": 0.0},
                "zoom": 1.0,
            },
            "compatibility": {
                "shell_id": "generic-side-coupe-lightweight-v1",
                "status": "compatible",
            },
            "materials": {
                "decal_strategy": "preview_spec_projection",
                "overlay_layers": [
                    {"id": "text-1", "slot": "side-decal-plane", "text": "MOON DRIVE"},
                ],
                "safe_zone_overlays": [
                    {
                        "height": 0.24,
                        "id": "door-main",
                        "slot": "side-decal-plane",
                        "width": 0.34,
                        "x": 0.32,
                        "y": 0.47,
                    },
                ],
                "source_artifact_id": "33333333-3333-3333-3333-333333333333",
                "source_kind": "preview_spec",
            },
            "mode": "lightweight_shell",
            "shell": {
                "dimensions": {"height": 1.4, "length": 4.4, "width": 1.8},
                "id": "generic-side-coupe-lightweight-v1",
                "label": "Generic side coupe lightweight shell",
                "material_slots": ["body", "side-decal-plane", "glass", "wheel"],
                "template_id": "generic-side-coupe",
            },
            "source": {
                "artifact_id": "33333333-3333-3333-3333-333333333333",
                "artifact_object_key": "workspaces/ws/generated_image/artifact/concept.png",
                "preview_spec_template_id": "generic-side-coupe",
                "preview_spec_view": "side",
                "version_id": "22222222-2222-2222-2222-222222222222",
                "workspace_id": "11111111-1111-1111-1111-111111111111",
            },
        },
    )


def preview_3d_screenshot_metadata() -> Preview3DScreenshotArtifactMetadata:
    spec = preview_3d_spec()
    dumped = spec.model_dump(mode="json")
    return Preview3DScreenshotArtifactMetadata.model_validate(
        {
            "preview_3d_screenshot": {
                "camera": dumped["camera"],
                "preview_3d": dumped,
                "shell_id": "generic-side-coupe-lightweight-v1",
                "source_artifact_id": "33333333-3333-3333-3333-333333333333",
                "warning_ids": ["non_production_preview", "uv_not_verified"],
            },
        },
    )


def preview_3d_screenshot_create_payload(
    *,
    source_artifact_id: str,
    source_artifact_object_key: str,
    version_id: str,
    workspace_id: str,
    content_type: str = "image/png",
) -> dict[str, object]:
    spec = build_preview_3d_spec(
        artifact_id=source_artifact_id,
        artifact_object_key=source_artifact_object_key,
        preview_spec={
            **parent_preview_spec(),
            "template": {
                "id": "generic-side-coupe",
                "label": "Generic side-view coupe",
                "view": "side",
            },
        },
        version_id=version_id,
        workspace_id=workspace_id,
    )
    return {
        "content_type": content_type,
        "filename": "preview-3d-screenshot.png",
        "height": 360,
        "image_base64": base64.b64encode(PNG_BYTES).decode("ascii"),
        "preview_3d": spec.model_dump(mode="json"),
        "width": 640,
    }
