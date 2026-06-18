from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any
from uuid import UUID

from caragent_core.enums import JobStatus
from caragent_core.generation import (
    GenerationBriefPayload,
    create_generation_brief,
    refresh_generation_brief_warnings,
)
from caragent_core.models import DesignBrief, GenerationJob
from caragent_core.provider_capabilities import (
    BFL_ALIASES,
    BFL_PROVIDER,
    LOCAL_DEFAULT_MODEL,
    LOCAL_PROVIDER,
    normalize_provider_name,
)
from caragent_core.services import jobs, workspaces
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_api.config import ApiSettings
from caragent_api.dependencies import get_db_session, get_queue_client
from caragent_api.queue import GENERATION_QUEUE, QueueClient, QueuedGenerationTask
from caragent_api.schemas import (
    GenerationBriefCreateRequest,
    GenerationBriefResponse,
    GenerationBriefUpdateRequest,
    GenerationIterationSubmissionRequest,
    GenerationJobResponse,
    GenerationJobRetryRequest,
    GenerationJobRetryResponse,
    GenerationJobSubmissionRequest,
    GenerationJobSubmissionResponse,
    GenerationQueuedTaskResponse,
)

GENERATION_OPERATION = "generate_2d_concept"

router = APIRouter(tags=["generation"])

SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]
QueueDependency = Annotated[QueueClient, Depends(get_queue_client)]
LOCAL_PROVIDER_NAMES = {"local", LOCAL_PROVIDER}


@dataclass(frozen=True, slots=True)
class ProviderIntent:
    provider: str
    model: str
    parameters: dict[str, Any]

    @property
    def metadata(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "parameters": dict(self.parameters),
            "provider": self.provider,
        }


def workspace_not_found(error: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workspace not found")


def brief_not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="brief not found")


def job_not_found(error: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")


def generation_validation_failed(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=str(error),
    )


@router.post(
    "/workspaces/{workspace_id}/generation/briefs",
    response_model=GenerationBriefResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_generation_brief_route(
    workspace_id: UUID,
    payload: GenerationBriefCreateRequest,
    session: SessionDependency,
) -> GenerationBriefResponse:
    try:
        brief_payload = create_generation_brief(
            character_focus=payload.character_focus,
            character_theme=payload.character_theme,
            color_harmony=payload.color_harmony,
            coverage=payload.coverage,
            overlay_logo_asset_ids=payload.overlay_logo_asset_ids,
            original_request=payload.original_request,
            palette=payload.palette,
            racing_cues=payload.racing_cues,
            reference_asset_ids=payload.reference_asset_ids,
            style=payload.style,
            supporting_graphics=payload.supporting_graphics,
            text=payload.text,
            typography_intent=payload.typography_intent,
            vehicle_template_id=payload.vehicle_template_id,
            view=payload.view,
        )
        brief = await workspaces.create_design_brief(
            session,
            workspace_id,
            payload=brief_payload.model_dump(mode="json"),
            title=payload.title,
            source_message_id=payload.source_message_id,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except (ValueError, workspaces.WorkspaceValidationError) as error:
        raise generation_validation_failed(error) from error

    return GenerationBriefResponse.model_validate(brief)


@router.patch("/generation/briefs/{brief_id}", response_model=GenerationBriefResponse)
async def update_generation_brief_route(
    brief_id: UUID,
    payload: GenerationBriefUpdateRequest,
    session: SessionDependency,
) -> GenerationBriefResponse:
    brief = await session.get(DesignBrief, brief_id)
    if brief is None:
        raise brief_not_found()

    try:
        current = GenerationBriefPayload.model_validate(brief.payload)
        update_payload = payload.model_dump(exclude_unset=True)
        if not update_payload:
            raise ValueError("At least one brief field is required")
        updated = refresh_generation_brief_warnings(
            GenerationBriefPayload(**(current.model_dump() | update_payload)),
        )
    except ValueError as error:
        raise generation_validation_failed(error) from error

    brief.payload = updated.model_dump(mode="json")
    await session.flush()
    return GenerationBriefResponse.model_validate(brief)


@router.post(
    "/workspaces/{workspace_id}/generation/jobs",
    response_model=GenerationJobSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_generation_job(
    workspace_id: UUID,
    payload: GenerationJobSubmissionRequest,
    request: Request,
    session: SessionDependency,
    queue: QueueDependency,
) -> GenerationJobSubmissionResponse:
    brief = await _get_workspace_brief(session, workspace_id, payload.brief_id)
    provider_intent = _provider_intent_from_submission(payload, _settings_from_request(request))
    metadata: dict[str, Any] = {"source": "generation-api"}
    if provider_intent is not None:
        metadata["provider_intent"] = provider_intent.metadata
    try:
        result = await jobs.create_job(
            session,
            workspace_id,
            brief_id=brief.id,
            idempotency_key=payload.idempotency_key,
            metadata=metadata,
            model=provider_intent.model if provider_intent is not None else None,
            operation=GENERATION_OPERATION,
            provider=provider_intent.provider if provider_intent is not None else None,
            requested_by=payload.requested_by,
        )
    except (workspaces.WorkspaceNotFoundError, jobs.JobValidationError) as error:
        raise generation_validation_failed(error) from error

    queued = None
    if not result.idempotent_reused:
        queued_task = await queue.enqueue_generation_job(result.job.id)
        await _persist_queued_task_metadata(session, result.job, queued_task)
        queued = GenerationQueuedTaskResponse.model_validate(queued_task)

    return GenerationJobSubmissionResponse(
        idempotent_reused=result.idempotent_reused,
        job=GenerationJobResponse.model_validate(result.job),
        queued=queued,
    )


@router.post(
    "/workspaces/{workspace_id}/versions/{version_id}/iterations",
    response_model=GenerationJobSubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_generation_iteration_job(
    workspace_id: UUID,
    version_id: UUID,
    payload: GenerationIterationSubmissionRequest,
    request: Request,
    session: SessionDependency,
    queue: QueueDependency,
) -> GenerationJobSubmissionResponse:
    brief = await _get_workspace_brief(session, workspace_id, payload.brief_id)
    provider_intent = _provider_intent_from_submission(payload, _settings_from_request(request))
    try:
        parent_version = await jobs.get_workspace_version(session, workspace_id, version_id)
        metadata: dict[str, Any] = {
            "change_request": payload.change_request,
            "iteration": True,
            "parameter_overrides": payload.parameter_overrides,
            "source": "generation-iteration-api",
        }
        if payload.edit_intent is not None:
            edit_intent = payload.edit_intent.model_copy(
                update={"parent_version_id": parent_version.id},
            )
            metadata["edit_intent"] = edit_intent.model_dump(mode="json")
        if provider_intent is not None:
            metadata["provider_intent"] = provider_intent.metadata
        metadata["parent_version_id"] = str(parent_version.id)
        result = await jobs.create_job(
            session,
            workspace_id,
            brief_id=brief.id,
            idempotency_key=payload.idempotency_key,
            metadata=metadata,
            model=provider_intent.model if provider_intent is not None else None,
            operation=GENERATION_OPERATION,
            provider=provider_intent.provider if provider_intent is not None else None,
            requested_by=payload.requested_by,
        )
    except (workspaces.WorkspaceNotFoundError, jobs.JobValidationError) as error:
        raise generation_validation_failed(error) from error

    queued = None
    if not result.idempotent_reused:
        queued_task = await queue.enqueue_generation_job(result.job.id)
        await _persist_queued_task_metadata(session, result.job, queued_task)
        queued = GenerationQueuedTaskResponse.model_validate(queued_task)

    return GenerationJobSubmissionResponse(
        idempotent_reused=result.idempotent_reused,
        job=GenerationJobResponse.model_validate(result.job),
        queued=queued,
    )


@router.post(
    "/jobs/{job_id}/retry",
    response_model=GenerationJobRetryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def retry_generation_job(
    job_id: UUID,
    payload: GenerationJobRetryRequest,
    session: SessionDependency,
    queue: QueueDependency,
) -> GenerationJobRetryResponse:
    try:
        failed_job = await jobs.get_job(session, job_id)
    except jobs.JobNotFoundError as error:
        raise job_not_found(error) from error

    if failed_job.status != JobStatus.FAILED.value:
        raise generation_validation_failed(ValueError("Only failed generation jobs can be retried"))
    if failed_job.brief_id is None:
        raise generation_validation_failed(ValueError("Failed job has no design brief to retry"))

    result = await jobs.create_job(
        session,
        failed_job.workspace_id,
        brief_id=failed_job.brief_id,
        idempotency_key=payload.idempotency_key,
        metadata={"retry_of_job_id": str(failed_job.id)},
        operation=failed_job.operation,
        requested_by=payload.requested_by,
    )

    queued = None
    if not result.idempotent_reused:
        queued_task = await queue.enqueue_generation_job(result.job.id)
        await _persist_queued_task_metadata(session, result.job, queued_task)
        queued = GenerationQueuedTaskResponse.model_validate(queued_task)

    return GenerationJobRetryResponse(
        idempotent_reused=result.idempotent_reused,
        job=GenerationJobResponse.model_validate(result.job),
        queued=queued,
        retry_of_job_id=failed_job.id,
    )


async def _get_workspace_brief(
    session: AsyncSession,
    workspace_id: UUID,
    brief_id: UUID,
) -> DesignBrief:
    await workspaces.get_workspace(session, workspace_id)
    brief = await session.get(DesignBrief, brief_id)
    if brief is None or brief.workspace_id != workspace_id:
        raise brief_not_found()
    return brief


async def _persist_queued_task_metadata(
    session: AsyncSession,
    job: GenerationJob,
    queued_task: QueuedGenerationTask,
) -> None:
    job.metadata_json = {
        **(job.metadata_json or {}),
        "queue": {
            "queue": GENERATION_QUEUE,
            "task_id": queued_task.task_id,
            "task_name": queued_task.task_name,
        },
    }
    await session.flush()


def _settings_from_request(request: Request) -> ApiSettings:
    settings = getattr(request.app.state, "settings", None)
    if isinstance(settings, ApiSettings):
        return settings
    return ApiSettings()


def _provider_intent_from_submission(
    payload: GenerationJobSubmissionRequest | GenerationIterationSubmissionRequest,
    settings: ApiSettings,
) -> ProviderIntent | None:
    provider = normalize_provider_name(payload.provider)
    if provider == "disabled":
        return None
    if provider in LOCAL_PROVIDER_NAMES:
        model = _requested_model(payload.model, default=LOCAL_DEFAULT_MODEL)
        if model != LOCAL_DEFAULT_MODEL:
            raise generation_validation_failed(
                ValueError(f"Unsupported model for provider {LOCAL_PROVIDER}: {model}"),
            )
        return ProviderIntent(
            model=LOCAL_DEFAULT_MODEL,
            parameters=dict(payload.provider_parameters),
            provider=LOCAL_PROVIDER,
        )
    if provider in BFL_ALIASES:
        return _bfl_provider_intent(payload, settings)
    raise generation_validation_failed(ValueError(f"Unsupported provider: {provider}"))


def _bfl_provider_intent(
    payload: GenerationJobSubmissionRequest | GenerationIterationSubmissionRequest,
    settings: ApiSettings,
) -> ProviderIntent:
    capability = settings.provider_capability_map()[BFL_PROVIDER]
    blocked_reasons = [str(reason) for reason in capability["blocked_reasons"]]
    if blocked_reasons:
        raise generation_validation_failed(ValueError("; ".join(blocked_reasons)))

    model = _requested_model(payload.model, default=str(capability["default_model"]))
    allowed_models = {str(model_name) for model_name in capability.get("allowed_models", [])}
    if model not in allowed_models:
        raise generation_validation_failed(
            ValueError(f"Unsupported model for provider bfl: {model}"),
        )
    return ProviderIntent(
        model=model,
        parameters=dict(payload.provider_parameters),
        provider=BFL_PROVIDER,
    )


def _requested_model(value: str | None, *, default: str) -> str:
    model = (value or "").strip()
    return model or default
