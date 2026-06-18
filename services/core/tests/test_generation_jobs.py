from __future__ import annotations

from collections.abc import AsyncIterator
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from caragent_core.database import create_engine, create_session_factory, session_scope
from caragent_core.enums import ArtifactKind, ModelRunStatus
from caragent_core.models import metadata
from caragent_core.services import jobs, workspaces


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)

    yield create_session_factory(engine)

    await engine.dispose()


async def test_model_run_completion_helpers_store_output_and_timestamps(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Generation")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="generation-001",
            operation="generate_2d_concept",
        )
        model_run = await jobs.create_model_run(
            session,
            created.job.id,
            model="local-concept-v1",
            provider="local-deterministic",
            status=ModelRunStatus.RUNNING.value,
        )
        artifact = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=512,
            checksum_sha256="a" * 64,
            content_type="image/png",
            height=768,
            job_id=created.job.id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace.id}/generated/concept.png",
            width=1536,
        )

        completed = await jobs.complete_model_run(
            session,
            model_run.id,
            actual_cost=Decimal("0.0000"),
            output_artifact_id=artifact.id,
        )

    assert completed.status == ModelRunStatus.SUCCEEDED.value
    assert completed.output_artifact_id == artifact.id
    assert completed.actual_cost == Decimal("0.0000")
    assert completed.completed_at is not None
    assert completed.error_message is None


async def test_model_run_failure_helper_sanitizes_error_text(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Generation")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="generation-002",
            operation="generate_2d_concept",
        )
        model_run = await jobs.create_model_run(
            session,
            created.job.id,
            model="local-concept-v1",
            provider="local-deterministic",
            status=ModelRunStatus.RUNNING.value,
        )

        failed = await jobs.fail_model_run(
            session,
            model_run.id,
            error_message="provider-secret\nfailed",
            secrets=["provider-secret"],
        )

    assert failed.status == ModelRunStatus.FAILED.value
    assert failed.completed_at is not None
    assert failed.error_message == "[redacted] failed"
    assert "provider-secret" not in failed.error_message


async def test_mask_artifact_metadata_can_be_stored_without_binary_payload(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Targeted edit")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="targeted-edit-001",
            operation="generate_2d_concept",
            metadata={
                "edit_intent": {
                    "mode": "targeted_edit",
                    "route_preference": "deterministic_recomposition",
                    "schema_version": 1,
                },
            },
        )
        artifact = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=256,
            content_type="image/png",
            height=768,
            job_id=created.job.id,
            kind="mask",
            metadata={
                "edit_region": {
                    "height": 0.2,
                    "type": "rectangle",
                    "unit": "normalized",
                    "width": 0.4,
                    "x": 0.2,
                    "y": 0.35,
                },
                "parent_version_id": "22222222-2222-2222-2222-222222222222",
                "target": {"id": "door-main", "type": "safe_zone"},
            },
            object_key=f"workspaces/{workspace.id}/masks/door-main.png",
            width=1536,
        )

    assert artifact.kind == "mask"
    assert artifact.metadata_json["target"] == {"id": "door-main", "type": "safe_zone"}
    assert "mask_bytes" not in artifact.metadata_json
