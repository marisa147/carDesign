from __future__ import annotations

import base64
import binascii
import hashlib
from typing import Annotated
from uuid import UUID, uuid4

from caragent_core.enums import ArtifactKind
from caragent_core.models import Artifact
from caragent_core.preview3d import Preview3DScreenshotArtifactMetadata
from caragent_core.services import jobs, workspaces
from caragent_core.storage import ObjectStorage, build_object_key, validate_upload
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_api.config import ApiSettings
from caragent_api.dependencies import get_db_session, get_object_storage, get_queue_client
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
    Preview3DScreenshotCreateRequest,
    QueueRevokeResponse,
)

router = APIRouter(tags=["jobs"])

SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]
QueueDependency = Annotated[QueueClient, Depends(get_queue_client)]
StorageDependency = Annotated[ObjectStorage, Depends(get_object_storage)]

SCREENSHOT_CONTENT_TYPES = {"image/png", "image/webp"}
MAX_PREVIEW_3D_SCREENSHOT_BYTES = 5 * 1024 * 1024


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


@router.post(
    "/workspaces/{workspace_id}/versions/{version_id}/preview-3d-screenshots",
    response_model=ArtifactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_preview_3d_screenshot(
    workspace_id: UUID,
    version_id: UUID,
    payload: Preview3DScreenshotCreateRequest,
    request: Request,
    session: SessionDependency,
    storage: StorageDependency,
) -> ArtifactResponse:
    settings = _settings_from_request(request)
    if not settings.v2_lightweight_3d_preview_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED is disabled.",
        )

    try:
        version = await jobs.get_workspace_version(session, workspace_id, version_id)
        await _validate_preview_3d_source_artifact(session, workspace_id, version_id, payload)
        screenshot_bytes = _decode_screenshot_bytes(payload.image_base64)
        _validate_screenshot_upload(payload, len(screenshot_bytes))
        metadata = _preview_3d_screenshot_metadata(payload)
        object_key = build_object_key(
            workspace_id=workspace_id,
            kind=ArtifactKind.PREVIEW_3D_SCREENSHOT.value,
            record_id=uuid4(),
            filename=payload.filename,
        )
        await storage.put_object(object_key, screenshot_bytes, payload.content_type)
        artifact = await jobs.create_artifact(
            session,
            workspace_id,
            byte_size=len(screenshot_bytes),
            checksum_sha256=hashlib.sha256(screenshot_bytes).hexdigest(),
            content_type=payload.content_type,
            height=payload.height,
            job_id=version.job_id,
            kind=ArtifactKind.PREVIEW_3D_SCREENSHOT.value,
            metadata=metadata.model_dump(mode="json"),
            object_key=object_key,
            version_id=version.id,
            width=payload.width,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except (ValueError, jobs.JobValidationError) as error:
        raise job_validation_failed(error) from error

    return ArtifactResponse.model_validate(artifact)


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


def _settings_from_request(request: Request) -> ApiSettings:
    settings = getattr(request.app.state, "settings", None)
    if isinstance(settings, ApiSettings):
        return settings
    raise RuntimeError("API settings are not configured")


async def _validate_preview_3d_source_artifact(
    session: AsyncSession,
    workspace_id: UUID,
    version_id: UUID,
    payload: Preview3DScreenshotCreateRequest,
) -> None:
    source = payload.preview_3d.source
    if source.workspace_id != workspace_id:
        raise jobs.JobValidationError("Preview3D source workspace does not match request")
    if source.version_id != version_id:
        raise jobs.JobValidationError("Preview3D source version does not match request")

    source_artifact = await session.get(Artifact, source.artifact_id)
    if source_artifact is None or source_artifact.workspace_id != workspace_id:
        raise jobs.JobValidationError("Preview3D source artifact not found for workspace")
    if source_artifact.version_id != version_id:
        raise jobs.JobValidationError("Preview3D source artifact not found for version")


def _decode_screenshot_bytes(image_base64: str) -> bytes:
    try:
        return base64.b64decode(image_base64, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ValueError("Screenshot image_base64 is invalid") from error


def _validate_screenshot_upload(
    payload: Preview3DScreenshotCreateRequest,
    byte_size: int,
) -> None:
    if payload.content_type not in SCREENSHOT_CONTENT_TYPES:
        raise ValueError(f"Unsupported screenshot content type: {payload.content_type}")
    validate_upload(
        byte_size=byte_size,
        content_type=payload.content_type,
        filename=payload.filename,
        max_upload_bytes=MAX_PREVIEW_3D_SCREENSHOT_BYTES,
    )


def _preview_3d_screenshot_metadata(
    payload: Preview3DScreenshotCreateRequest,
) -> Preview3DScreenshotArtifactMetadata:
    warning_ids = [
        warning.id
        for warning in payload.preview_3d.warnings
        if warning.id in {"non_production_preview", "uv_not_verified"}
    ]
    return Preview3DScreenshotArtifactMetadata.model_validate(
        {
            "preview_3d_screenshot": {
                "camera": payload.preview_3d.camera.model_dump(mode="json"),
                "preview_3d": payload.preview_3d.model_dump(mode="json"),
                "shell_id": payload.preview_3d.compatibility.shell_id,
                "source_artifact_id": payload.preview_3d.source.artifact_id,
                "warning_ids": warning_ids,
            },
        },
    )
