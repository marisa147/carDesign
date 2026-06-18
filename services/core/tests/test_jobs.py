from __future__ import annotations

from collections.abc import AsyncIterator
from decimal import Decimal

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
