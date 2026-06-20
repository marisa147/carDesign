from __future__ import annotations

import json
import zipfile
from collections.abc import AsyncIterator
from decimal import Decimal
from io import BytesIO
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from caragent_core import enums
from caragent_core.database import create_engine, create_session_factory, session_scope
from caragent_core.enums import (
    ArtifactKind,
    DesignVersionStatus,
    FeedbackApprovalState,
    JobEventType,
    JobStatus,
    ModelRunStatus,
)
from caragent_core.models import GenerationJob, metadata
from caragent_core.production_preflight import REQUIRED_PRODUCTION_EVIDENCE_IDS
from caragent_core.services import jobs, workspaces


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)

    yield create_session_factory(engine)

    await engine.dispose()


async def test_create_job_is_idempotent_per_workspace(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Jobs")

        first = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="brief-001",
            operation="generate_concept",
            requested_by="local-user",
        )
        duplicate = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="brief-001",
            operation="generate_concept",
            requested_by="local-user",
        )
        initial_estimated_cost = first.job.estimated_cost
        initial_actual_cost = first.job.actual_cost
        job_count = await session.scalar(select(func.count()).select_from(GenerationJob))
        updated = await jobs.update_job_costs(
            session,
            first.job.id,
            estimated_cost=Decimal("1.2500"),
            actual_cost=Decimal("0.7500"),
        )

    assert first.idempotent_reused is False
    assert duplicate.idempotent_reused is True
    assert duplicate.job.id == first.job.id
    assert job_count == 1
    assert initial_estimated_cost is None
    assert initial_actual_cost is None
    assert updated.estimated_cost == Decimal("1.2500")
    assert updated.actual_cost == Decimal("0.7500")


async def test_job_events_order_and_status_persist_across_sessions(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Events")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="events-001",
            operation="generate_concept",
        )
        await jobs.transition_job_status(
            session,
            created.job.id,
            status=JobStatus.RUNNING.value,
            message="Worker claimed job.",
            source="worker",
        )
        await jobs.transition_job_status(
            session,
            created.job.id,
            status=JobStatus.SUCCEEDED.value,
            message="Local simulation completed.",
            source="worker",
        )

    async with session_scope(session_factory) as session:
        persisted = await jobs.get_job(session, created.job.id)
        events = await jobs.list_job_events(session, created.job.id)

    assert persisted.status == JobStatus.SUCCEEDED.value
    assert [event.sequence for event in events] == [1, 2, 3]
    assert [event.status for event in events] == [
        JobStatus.QUEUED.value,
        JobStatus.RUNNING.value,
        JobStatus.SUCCEEDED.value,
    ]
    assert [event.event_type for event in events] == [
        JobEventType.CREATED.value,
        JobEventType.STATUS.value,
        JobEventType.COMPLETED.value,
    ]


def test_failure_category_enum_covers_current_operations_taxonomy() -> None:
    assert {item.value for item in enums.FailureCategory} == {
        "canceled",
        "provider",
        "provider_configuration",
        "queue_worker",
        "storage",
        "targeted_edit_conflict",
        "targeted_edit_invalid",
        "targeted_edit_unsupported",
        "timeout",
        "unknown",
        "validation_rights",
    }


async def test_transition_job_status_records_operational_failure_metadata(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Operations")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="ops-failure-001",
            metadata={"iteration": True},
            operation="generate_concept",
        )
        failed = await jobs.transition_job_status(
            session,
            created.job.id,
            status=JobStatus.FAILED.value,
            latest_error="provider-secret\nfailed upstream",
            message="Generation failed.",
            metadata={
                "error": "provider-secret\nfailed upstream",
                "failure_category": "provider",
                "model": "flux-pro",
                "provider": "bfl",
                "stage": "provider_generate",
            },
            secrets=("provider-secret",),
            source="worker-generation",
        )
        events = await jobs.list_job_events(session, created.job.id)

    assert failed.latest_error == "[redacted] failed upstream"
    assert failed.metadata_json["iteration"] is True
    assert failed.metadata_json["operations"] == {
        "error": "[redacted] failed upstream",
        "failure_category": "provider",
        "model": "flux-pro",
        "provider": "bfl",
        "stage": "provider_generate",
    }
    assert events[-1].event_type == JobEventType.ERROR.value
    assert events[-1].metadata_json == failed.metadata_json["operations"]


async def test_transition_job_status_records_canceled_operational_metadata(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Cancellation")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="ops-cancel-001",
            metadata={"queue": {"task_id": "task-1"}},
            operation="generate_concept",
        )
        canceled = await jobs.transition_job_status(
            session,
            created.job.id,
            status=JobStatus.CANCELED.value,
            message="Job canceled.",
            metadata={
                "failure_category": "canceled",
                "reason": "user_request",
                "requested_by": "web-workbench",
            },
            source="api",
        )
        events = await jobs.list_job_events(session, created.job.id)

    assert canceled.latest_error is None
    assert canceled.metadata_json["queue"] == {"task_id": "task-1"}
    assert canceled.metadata_json["operations"] == {
        "failure_category": "canceled",
        "reason": "user_request",
        "requested_by": "web-workbench",
    }
    assert events[-1].status == JobStatus.CANCELED.value
    assert events[-1].metadata_json == canceled.metadata_json["operations"]


async def test_cancel_job_transitions_queued_and_running_jobs(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Cancel")
        queued = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="cancel-queued-001",
            metadata={"queue": {"task_id": "task-queued"}},
            operation="generate_concept",
        )
        running = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="cancel-running-001",
            operation="generate_concept",
        )
        await jobs.transition_job_status(
            session,
            running.job.id,
            status=JobStatus.RUNNING.value,
            message="Worker started.",
            source="worker",
        )

        canceled_queued = await jobs.cancel_job(
            session,
            queued.job.id,
            reason="user_request",
            requested_by="web-workbench",
            source="api",
        )
        canceled_running = await jobs.cancel_job(
            session,
            running.job.id,
            reason="user_request",
            requested_by="web-workbench",
            source="api",
        )
        queued_events = await jobs.list_job_events(session, queued.job.id)

    assert canceled_queued.status == JobStatus.CANCELED.value
    assert canceled_queued.latest_error is None
    assert canceled_queued.metadata_json["queue"] == {"task_id": "task-queued"}
    assert canceled_queued.metadata_json["operations"] == {
        "failure_category": "canceled",
        "reason": "user_request",
        "requested_by": "web-workbench",
    }
    assert canceled_running.status == JobStatus.CANCELED.value
    assert queued_events[-1].status == JobStatus.CANCELED.value
    assert queued_events[-1].metadata_json == canceled_queued.metadata_json["operations"]


async def test_cancel_job_rejects_terminal_jobs(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Cancel terminal")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="cancel-terminal-001",
            operation="generate_concept",
        )
        await jobs.transition_job_status(
            session,
            created.job.id,
            status=JobStatus.SUCCEEDED.value,
            message="Done.",
            source="worker",
        )

        with pytest.raises(jobs.JobValidationError, match="Only queued or running jobs"):
            await jobs.cancel_job(
                session,
                created.job.id,
                reason="user_request",
                requested_by="web-workbench",
                source="api",
            )


async def test_job_support_records_for_local_simulation_outputs(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Simulation")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="simulation-001",
            operation="generate_concept",
        )
        version = await jobs.create_design_version(
            session,
            workspace.id,
            job_id=created.job.id,
            status=DesignVersionStatus.GENERATED.value,
            title="Local simulation",
            parameters={"palette": ["pink", "white"]},
        )
        artifact = await jobs.create_artifact(
            session,
            workspace.id,
            job_id=created.job.id,
            version_id=version.id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace.id}/generated/{version.id}/concept.png",
            content_type="image/png",
            byte_size=256,
        )
        model_run = await jobs.create_model_run(
            session,
            created.job.id,
            provider="local-simulation",
            model="phase-2-no-provider",
            status=ModelRunStatus.SUCCEEDED.value,
            parameters={"seed": 7},
            prompt_text="pink itasha concept",
            estimated_cost=Decimal("0.0000"),
            actual_cost=Decimal("0.0000"),
            output_artifact_id=artifact.id,
        )
        feedback = await jobs.record_feedback(
            session,
            workspace.id,
            version.id,
            approval_state=FeedbackApprovalState.APPROVED.value,
            comment="Good first direction.",
            rating=5,
        )
        export = await jobs.record_export(
            session,
            workspace.id,
            version.id,
            artifact_id=artifact.id,
            export_format="png",
            manifest={"concept_label": "concept_preview"},
        )

        versions = await jobs.list_workspace_versions(session, workspace.id)
        artifacts = await jobs.list_workspace_artifacts(session, workspace.id)
        model_runs = await jobs.list_job_model_runs(session, created.job.id)
        feedback_rows = await jobs.list_workspace_feedback(session, workspace.id)
        exports = await jobs.list_workspace_exports(session, workspace.id)

    assert versions == [version]
    assert artifacts == [artifact]
    assert model_runs == [model_run]
    assert feedback_rows == [feedback]
    assert exports == [export]
    assert artifact.object_key.endswith("/concept.png")
    assert model_run.output_artifact_id == artifact.id
    assert feedback.approval_state == FeedbackApprovalState.APPROVED.value
    assert export.concept_label == "concept_preview"


async def test_in_memory_object_storage_can_read_written_objects() -> None:
    from caragent_core.storage import InMemoryObjectStorage

    storage = InMemoryObjectStorage()
    await storage.put_object(
        "workspaces/workspace-1/export/package/concept-handoff.zip",
        b"zip-content",
        "application/zip",
    )

    stored = await storage.get_object(
        "workspaces/workspace-1/export/package/concept-handoff.zip",
    )

    assert stored.content == b"zip-content"
    assert stored.content_type == "application/zip"

    with pytest.raises(FileNotFoundError):
        await storage.get_object("workspaces/workspace-1/export/package/missing.zip")


async def test_feedback_and_export_require_version_to_belong_to_workspace(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        source_workspace = await workspaces.create_workspace(session, title="Source")
        other_workspace = await workspaces.create_workspace(session, title="Other")
        version = await jobs.create_design_version(
            session,
            source_workspace.id,
            status=DesignVersionStatus.GENERATED.value,
            title="Source version",
        )

        with pytest.raises(jobs.JobValidationError, match="Version not found for workspace"):
            await jobs.record_feedback(
                session,
                other_workspace.id,
                version.id,
                approval_state=FeedbackApprovalState.APPROVED.value,
                rating=4,
            )

        with pytest.raises(jobs.JobValidationError, match="Version not found for workspace"):
            await jobs.record_export(
                session,
                other_workspace.id,
                version.id,
                export_format="png",
            )


async def test_export_rejects_unsupported_format(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Export")
        version = await jobs.create_design_version(
            session,
            workspace.id,
            status=DesignVersionStatus.GENERATED.value,
            title="Export source",
        )

        with pytest.raises(jobs.JobValidationError, match="Unsupported export format"):
            await jobs.record_export(
                session,
                workspace.id,
                version.id,
                export_format="pdf",
            )


async def test_phase_13_handoff_package_zip_contains_reports_and_assets(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    from caragent_core.handoff import (
        ENHANCED_HANDOFF_PACKAGE_FORMAT,
        build_handoff_package_zip,
    )
    from caragent_core.storage import InMemoryObjectStorage

    storage = InMemoryObjectStorage()
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Handoff ZIP")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="handoff-zip-001",
            operation="generate_concept",
        )
        version = await jobs.create_design_version(
            session,
            workspace.id,
            job_id=created.job.id,
            parameters=_handoff_parameters(),
            title="Package source",
        )
        concept = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=11,
            checksum_sha256="a" * 64,
            content_type="image/png",
            height=768,
            job_id=created.job.id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace.id}/generated/{version.id}/concept.png",
            version_id=version.id,
            width=1536,
        )
        screenshot = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=14,
            checksum_sha256="b" * 64,
            content_type="image/png",
            height=720,
            job_id=created.job.id,
            kind=ArtifactKind.PREVIEW_3D_SCREENSHOT.value,
            metadata={"preview_3d_screenshot": {"warning_ids": ["uv_not_verified"]}},
            object_key=f"workspaces/{workspace.id}/preview_3d_screenshot/{version.id}/capture.png",
            version_id=version.id,
            width=1280,
        )
        model_run = await jobs.create_model_run(
            session,
            created.job.id,
            input_artifact_ids=["66666666-6666-6666-6666-666666666666"],
            model="local-concept-v1",
            output_artifact_id=concept.id,
            prompt_text="Review package prompt api_key=secret image_base64 C:\\tmp\\concept.png",
            provider="local-simulation",
            status=ModelRunStatus.SUCCEEDED.value,
        )

        await storage.put_object(concept.object_key, b"concept-png", "image/png")
        await storage.put_object(screenshot.object_key, b"screenshot-png", "image/png")

        result = await build_handoff_package_zip(
            model_runs=[model_run],
            package_object_key=f"workspaces/{workspace.id}/exports/{version.id}/concept-handoff.zip",
            review_notes=["Approved for concept discussion."],
            screenshot_artifacts=[screenshot],
            source_artifact=concept,
            storage=storage,
            version=version,
        )

    assert result.content_type == "application/zip"
    assert result.byte_size == len(result.content)
    assert len(result.checksum_sha256) == 64

    with zipfile.ZipFile(BytesIO(result.content)) as archive:
        names = set(archive.namelist())
        assert {
            "manifest.json",
            "handoff-notes.md",
            "warnings.md",
            "production-readiness-preflight.json",
            "template-validation.json",
            "prompt-trace.md",
            "references.json",
            "images/concept.png",
            f"screenshots/{screenshot.id}.png",
        } <= names
        assert archive.read("images/concept.png") == b"concept-png"
        assert archive.read(f"screenshots/{screenshot.id}.png") == b"screenshot-png"

        manifest = json.loads(archive.read("manifest.json"))
        assert manifest["format"] == ENHANCED_HANDOFF_PACKAGE_FORMAT
        assert manifest["schema_version"] == 1
        assert manifest["source_artifact"]["id"] == str(concept.id)
        assert manifest["production_readiness_preflight"]["status"] == "concept_only"
        assert manifest["production_readiness_preflight"]["print_ready_allowed"] is False
        assert manifest["template_validation"]["source_type"] == "internal_original"
        preflight = json.loads(archive.read("production-readiness-preflight.json"))
        template_validation = json.loads(archive.read("template-validation.json"))
        assert set(REQUIRED_PRODUCTION_EVIDENCE_IDS) <= set(preflight["missing_evidence"])
        assert template_validation["license_status"] == "approved"

        rendered_text = "\n".join(
            archive.read(name).decode("utf-8").lower()
            for name in [
                "manifest.json",
                "handoff-notes.md",
                "warnings.md",
                "production-readiness-preflight.json",
                "template-validation.json",
                "prompt-trace.md",
                "references.json",
            ]
        )
        assert "api_key" not in rendered_text
        assert "secret" not in rendered_text
        assert "image_base64" not in rendered_text
        assert "c:\\" not in rendered_text


async def test_phase_13_handoff_package_zip_requires_source_concept_bytes(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    from caragent_core.handoff import HandoffPackageBuildError, build_handoff_package_zip
    from caragent_core.storage import InMemoryObjectStorage

    storage = InMemoryObjectStorage()
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Missing concept")
        version = await jobs.create_design_version(
            session,
            workspace.id,
            parameters=_handoff_parameters(),
            title="Missing source",
        )
        concept = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=11,
            content_type="image/png",
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace.id}/generated/{version.id}/missing.png",
            version_id=version.id,
        )

        with pytest.raises(HandoffPackageBuildError, match="source concept image"):
            await build_handoff_package_zip(
                package_object_key=f"workspaces/{workspace.id}/exports/{version.id}/missing.zip",
                source_artifact=concept,
                storage=storage,
                version=version,
            )


async def test_phase_13_handoff_package_zip_warns_for_missing_optional_screenshot(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    from caragent_core.handoff import build_handoff_package_zip
    from caragent_core.storage import InMemoryObjectStorage

    storage = InMemoryObjectStorage()
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Missing screenshot")
        version = await jobs.create_design_version(
            session,
            workspace.id,
            parameters=_handoff_parameters(),
            title="Missing screenshot source",
        )
        concept = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=11,
            content_type="image/png",
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace.id}/generated/{version.id}/concept.png",
            version_id=version.id,
        )
        screenshot = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=14,
            content_type="image/png",
            kind=ArtifactKind.PREVIEW_3D_SCREENSHOT.value,
            object_key=f"workspaces/{workspace.id}/preview_3d_screenshot/{version.id}/missing.png",
            version_id=version.id,
        )
        await storage.put_object(concept.object_key, b"concept-png", "image/png")

        result = await build_handoff_package_zip(
            package_object_key=f"workspaces/{workspace.id}/exports/{version.id}/missing-screenshot.zip",
            screenshot_artifacts=[screenshot],
            source_artifact=concept,
            storage=storage,
            version=version,
        )

    with zipfile.ZipFile(BytesIO(result.content)) as archive:
        assert f"screenshots/{screenshot.id}.png" not in archive.namelist()
        manifest = json.loads(archive.read("manifest.json"))

    assert any(
        item["id"] == "preview_3d_screenshot_missing_object"
        for item in manifest["warnings"]["items"]
    )


def test_phase_19_production_preflight_report_names_missing_evidence() -> None:
    from caragent_core.production_preflight import (
        build_production_readiness_preflight_report,
    )

    source_artifact = SimpleNamespace(id=uuid4())
    version = SimpleNamespace(
        id=uuid4(),
        parameters=_handoff_parameters(),
        workspace_id=uuid4(),
    )

    report = build_production_readiness_preflight_report(
        source_artifact=source_artifact,
        version=version,
    )

    assert report.status == "concept_only"
    assert report.print_ready_allowed is False
    assert set(REQUIRED_PRODUCTION_EVIDENCE_IDS) <= set(report.missing_evidence)
    assert "print_ready_export_blocked" in report.blockers
    assert report.template_validation.source_type == "internal_original"
    assert report.template_validation.license_status == "approved"
    assert "not print-ready" in report.disclaimer


@pytest.mark.parametrize(
    "rights_variant",
    ["missing_snapshot", "rejected", "missing_source"],
)
async def test_phase_13_handoff_package_zip_blocks_missing_reference_rights_source(
    session_factory: async_sessionmaker[AsyncSession],
    rights_variant: str,
) -> None:
    from caragent_core.handoff import HandoffPackageBuildError, build_handoff_package_zip
    from caragent_core.storage import InMemoryObjectStorage

    storage = InMemoryObjectStorage()
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title=f"Blocked {rights_variant}")
        version = await jobs.create_design_version(
            session,
            workspace.id,
            parameters=_handoff_parameters_with_rights_variant(rights_variant),
            title="Blocked handoff source",
        )
        concept = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=11,
            content_type="image/png",
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace.id}/generated/{version.id}/concept.png",
            version_id=version.id,
        )
        await storage.put_object(concept.object_key, b"concept-png", "image/png")

        with pytest.raises(HandoffPackageBuildError, match="rights/source metadata"):
            await build_handoff_package_zip(
                package_object_key=f"workspaces/{workspace.id}/exports/{version.id}/blocked.zip",
                source_artifact=concept,
                storage=storage,
                version=version,
            )


def _handoff_parameters() -> dict[str, object]:
    reference_asset_id = "66666666-6666-6666-6666-666666666666"
    return {
        "included_reference_asset_ids": [reference_asset_id],
        "omitted_reference_asset_ids": [],
        "preview_3d": {
            "warnings": [
                {
                    "id": "non_production_preview",
                    "message": "Lightweight 3D preview is concept-only.",
                    "severity": "warning",
                },
                {
                    "id": "uv_not_verified",
                    "message": "Vehicle-specific UV mapping has not been verified.",
                    "severity": "warning",
                },
            ],
        },
        "preview_spec": {
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
            "template": {
                "id": "generic-side-coupe",
                "label": "Generic side-view coupe",
                "readiness": {"catalog_eligible": True},
                "source": {
                    "license_status": "approved",
                    "source_type": "internal_original",
                },
                "view": "side",
            },
        },
        "reference_roles": {"character": [reference_asset_id]},
        "reference_warning_count": 0,
        "rights_snapshot": {
            reference_asset_id: {
                "rights_status": "confirmed",
                "source_label": "User upload",
            },
        },
        "unsupported_reference_roles": [],
    }


def _handoff_parameters_with_rights_variant(variant: str) -> dict[str, object]:
    parameters = _handoff_parameters()
    reference_asset_id = parameters["included_reference_asset_ids"][0]
    rights_snapshot = dict(parameters["rights_snapshot"])
    rights = dict(rights_snapshot[reference_asset_id])
    if variant == "missing_snapshot":
        parameters["rights_snapshot"] = {}
        return parameters
    if variant == "rejected":
        rights["rights_status"] = "rejected"
    elif variant == "missing_source":
        rights["source_label"] = None
        rights["source_url"] = None
    else:
        raise AssertionError(f"Unknown rights variant: {variant}")
    rights_snapshot[reference_asset_id] = rights
    parameters["rights_snapshot"] = rights_snapshot
    return parameters
