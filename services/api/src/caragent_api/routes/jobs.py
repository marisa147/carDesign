from __future__ import annotations

from typing import Annotated
from uuid import UUID

from caragent_core.services import jobs, workspaces
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_api.dependencies import get_db_session, get_queue_client
from caragent_api.queue import QueueClient
from caragent_api.schemas import (
    ArtifactResponse,
    DesignVersionResponse,
    ExportCreateRequest,
    ExportResponse,
    FeedbackCreateRequest,
    FeedbackResponse,
    GenerationJobCancelRequest,
    GenerationJobCancelResponse,
    GenerationJobResponse,
    JobCreateRequest,
    JobCreateResponse,
    JobEventResponse,
    ModelRunResponse,
    QueueRevokeResponse,
)

router = APIRouter(tags=["jobs"])

SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]
QueueDependency = Annotated[QueueClient, Depends(get_queue_client)]


def workspace_not_found(error: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workspace not found")


def job_not_found(error: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")


def job_validation_failed(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=str(error),
    )


def create_response(result: jobs.JobCreationResult) -> JobCreateResponse:
    payload = GenerationJobResponse.model_validate(result.job).model_dump()
    return JobCreateResponse(**payload, idempotent_reused=result.idempotent_reused)


@router.post(
    "/workspaces/{workspace_id}/jobs",
    response_model=JobCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job(
    workspace_id: UUID,
    payload: JobCreateRequest,
    session: SessionDependency,
) -> JobCreateResponse:
    try:
        result = await jobs.create_job(
            session,
            workspace_id,
            brief_id=payload.brief_id,
            estimated_cost=payload.estimated_cost,
            idempotency_key=payload.idempotency_key,
            metadata=payload.metadata,
            model=payload.model,
            operation=payload.operation,
            provider=payload.provider,
            requested_by=payload.requested_by,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except jobs.JobValidationError as error:
        raise job_validation_failed(error) from error
    return create_response(result)


@router.get("/workspaces/{workspace_id}/jobs", response_model=list[GenerationJobResponse])
async def list_jobs(
    workspace_id: UUID,
    session: SessionDependency,
) -> list[GenerationJobResponse]:
    try:
        job_rows = await jobs.list_workspace_jobs(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [GenerationJobResponse.model_validate(job) for job in job_rows]


@router.get("/jobs/{job_id}", response_model=GenerationJobResponse)
async def get_job(job_id: UUID, session: SessionDependency) -> GenerationJobResponse:
    try:
        job = await jobs.get_job(session, job_id)
    except jobs.JobNotFoundError as error:
        raise job_not_found(error) from error
    return GenerationJobResponse.model_validate(job)


@router.post("/jobs/{job_id}/cancel", response_model=GenerationJobCancelResponse)
async def cancel_job(
    job_id: UUID,
    payload: GenerationJobCancelRequest,
    session: SessionDependency,
    queue: QueueDependency,
) -> GenerationJobCancelResponse:
    try:
        existing = await jobs.get_job(session, job_id)
        task_id = _extract_queue_task_id(existing.metadata_json)
        canceled = await jobs.cancel_job(
            session,
            job_id,
            reason=payload.reason,
            requested_by=payload.requested_by,
            source="api",
        )
    except jobs.JobNotFoundError as error:
        raise job_not_found(error) from error
    except jobs.JobValidationError as error:
        raise job_validation_failed(error) from error

    try:
        revoke_result = await queue.revoke_generation_task(task_id)
        queue_revoke = QueueRevokeResponse.model_validate(revoke_result)
    except Exception:
        queue_revoke = QueueRevokeResponse(
            detail="Queue revoke failed.",
            status="failed",
            task_id=task_id,
        )

    return GenerationJobCancelResponse(
        job=GenerationJobResponse.model_validate(canceled),
        queue_revoke=queue_revoke,
    )


@router.get("/jobs/{job_id}/events", response_model=list[JobEventResponse])
async def list_events(job_id: UUID, session: SessionDependency) -> list[JobEventResponse]:
    try:
        event_rows = await jobs.list_job_events(session, job_id)
    except jobs.JobNotFoundError as error:
        raise job_not_found(error) from error
    return [JobEventResponse.model_validate(event) for event in event_rows]


@router.get("/workspaces/{workspace_id}/versions", response_model=list[DesignVersionResponse])
async def list_versions(
    workspace_id: UUID,
    session: SessionDependency,
) -> list[DesignVersionResponse]:
    try:
        rows = await jobs.list_workspace_versions(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [DesignVersionResponse.model_validate(row) for row in rows]


@router.get("/workspaces/{workspace_id}/artifacts", response_model=list[ArtifactResponse])
async def list_artifacts(
    workspace_id: UUID,
    session: SessionDependency,
) -> list[ArtifactResponse]:
    try:
        rows = await jobs.list_workspace_artifacts(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [ArtifactResponse.model_validate(row) for row in rows]


@router.get("/jobs/{job_id}/model-runs", response_model=list[ModelRunResponse])
async def list_model_runs(job_id: UUID, session: SessionDependency) -> list[ModelRunResponse]:
    try:
        rows = await jobs.list_job_model_runs(session, job_id)
    except jobs.JobNotFoundError as error:
        raise job_not_found(error) from error
    return [ModelRunResponse.model_validate(row) for row in rows]


@router.get("/workspaces/{workspace_id}/feedback", response_model=list[FeedbackResponse])
async def list_feedback(
    workspace_id: UUID,
    session: SessionDependency,
) -> list[FeedbackResponse]:
    try:
        rows = await jobs.list_workspace_feedback(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [FeedbackResponse.model_validate(row) for row in rows]


@router.post(
    "/workspaces/{workspace_id}/versions/{version_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_feedback(
    workspace_id: UUID,
    version_id: UUID,
    payload: FeedbackCreateRequest,
    session: SessionDependency,
) -> FeedbackResponse:
    try:
        row = await jobs.record_feedback(
            session,
            workspace_id,
            version_id,
            approval_state=payload.approval_state,
            comment=payload.comment,
            metadata=payload.metadata,
            rating=payload.rating,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except jobs.JobValidationError as error:
        raise job_validation_failed(error) from error
    return FeedbackResponse.model_validate(row)


@router.get("/workspaces/{workspace_id}/exports", response_model=list[ExportResponse])
async def list_exports(
    workspace_id: UUID,
    session: SessionDependency,
) -> list[ExportResponse]:
    try:
        rows = await jobs.list_workspace_exports(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [ExportResponse.model_validate(row) for row in rows]


@router.post(
    "/workspaces/{workspace_id}/versions/{version_id}/exports",
    response_model=ExportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_export(
    workspace_id: UUID,
    version_id: UUID,
    payload: ExportCreateRequest,
    session: SessionDependency,
) -> ExportResponse:
    try:
        row = await jobs.record_export(
            session,
            workspace_id,
            version_id,
            artifact_id=payload.artifact_id,
            concept_label=payload.concept_label,
            export_format=payload.format,
            manifest=payload.manifest,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except jobs.JobValidationError as error:
        raise job_validation_failed(error) from error
    return ExportResponse.model_validate(row)


def _extract_queue_task_id(metadata: object) -> str | None:
    if not isinstance(metadata, dict):
        return None
    queue_metadata = metadata.get("queue")
    if not isinstance(queue_metadata, dict):
        return None
    task_id = queue_metadata.get("task_id")
    return task_id if isinstance(task_id, str) and task_id else None
