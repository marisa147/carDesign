from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_core.models import (
    Artifact,
    DesignVersion,
    ExportRecord,
    Feedback,
    GenerationJob,
    JobEvent,
    ModelRun,
)


async def get_job(session: AsyncSession, job_id: UUID) -> GenerationJob | None:
    return cast(GenerationJob | None, await session.get(GenerationJob, job_id))


async def find_job_by_idempotency_key(
    session: AsyncSession,
    workspace_id: UUID,
    idempotency_key: str,
) -> GenerationJob | None:
    return cast(
        GenerationJob | None,
        await session.scalar(
            select(GenerationJob).where(
                GenerationJob.workspace_id == workspace_id,
                GenerationJob.idempotency_key == idempotency_key,
            ),
        ),
    )


async def list_workspace_jobs(session: AsyncSession, workspace_id: UUID) -> list[GenerationJob]:
    result = await session.scalars(
        select(GenerationJob)
        .where(GenerationJob.workspace_id == workspace_id)
        .order_by(GenerationJob.created_at.asc()),
    )
    return list(result)


async def next_event_sequence(session: AsyncSession, job_id: UUID) -> int:
    value = await session.scalar(
        select(func.max(JobEvent.sequence)).where(JobEvent.job_id == job_id),
    )
    return (value or 0) + 1


async def list_job_events(session: AsyncSession, job_id: UUID) -> list[JobEvent]:
    result = await session.scalars(
        select(JobEvent)
        .where(JobEvent.job_id == job_id)
        .order_by(JobEvent.sequence.asc(), JobEvent.created_at.asc()),
    )
    return list(result)


async def list_job_model_runs(session: AsyncSession, job_id: UUID) -> list[ModelRun]:
    result = await session.scalars(
        select(ModelRun)
        .where(ModelRun.job_id == job_id)
        .order_by(ModelRun.created_at.asc()),
    )
    return list(result)


async def list_workspace_versions(session: AsyncSession, workspace_id: UUID) -> list[DesignVersion]:
    result = await session.scalars(
        select(DesignVersion)
        .where(DesignVersion.workspace_id == workspace_id)
        .order_by(DesignVersion.created_at.asc()),
    )
    return list(result)


async def list_workspace_artifacts(session: AsyncSession, workspace_id: UUID) -> list[Artifact]:
    result = await session.scalars(
        select(Artifact)
        .where(Artifact.workspace_id == workspace_id)
        .order_by(Artifact.created_at.asc()),
    )
    return list(result)


async def list_workspace_feedback(session: AsyncSession, workspace_id: UUID) -> list[Feedback]:
    result = await session.scalars(
        select(Feedback)
        .where(Feedback.workspace_id == workspace_id)
        .order_by(Feedback.created_at.asc()),
    )
    return list(result)


async def list_workspace_exports(session: AsyncSession, workspace_id: UUID) -> list[ExportRecord]:
    result = await session.scalars(
        select(ExportRecord)
        .where(ExportRecord.workspace_id == workspace_id)
        .order_by(ExportRecord.created_at.asc()),
    )
    return list(result)
