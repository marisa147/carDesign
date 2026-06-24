from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, Any
from uuid import UUID

from caragent_core.enums import DesignBriefStatus, JobStatus
from caragent_core.generation import (
    BriefDraft,
    BriefParserInput,
    GenerationBriefPayload,
    create_generation_brief,
    create_generation_brief_from_draft,
    refresh_generation_brief_warnings,
)
from caragent_core.models import Artifact, DesignBrief, GenerationJob
from caragent_core.provider_capabilities import (
    BFL_ALIASES,
    BFL_PROVIDER,
    LOCAL_DEFAULT_MODEL,
    LOCAL_PROVIDER,
    OPENAI_ALIASES,
    OPENAI_PROVIDER,
    PROVIDER_MASKED_GENERATION_ROUTE,
    normalize_provider_name,
)
from caragent_core.references import plan_reference_usage
from caragent_core.services import jobs, workspaces
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_api.config import ApiSettings
from caragent_api.dependencies import (
    CurrentUser,
    CurrentUserDependency,
    OwnedWorkspaceDependency,
    SessionDependency,
    get_queue_client,
    require_workspace_owner,
)
from caragent_api.openai_brief_parser import parse_openai_brief
from caragent_api.queue import (
    GENERATE_2D_CONCEPT_TASK,
    GENERATION_QUEUE,
    QueueClient,
    QueuedGenerationTask,
)
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


async def _require_workspace_owner_by_id(
    session: AsyncSession,
    workspace_id: UUID,
    current_user: CurrentUser,
) -> None:
    try:
        workspace = await workspaces.get_workspace(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    require_workspace_owner(workspace, current_user)


async def _require_brief_owner(
    session: AsyncSession,
    brief: DesignBrief,
    current_user: CurrentUser,
) -> None:
    await _require_workspace_owner_by_id(session, brief.workspace_id, current_user)


async def _get_owned_generation_job(
    session: AsyncSession,
    job_id: UUID,
    current_user: CurrentUser,
) -> GenerationJob:
    try:
        job = await jobs.get_job(session, job_id)
    except jobs.JobNotFoundError as error:
        raise job_not_found(error) from error
    await _require_workspace_owner_by_id(session, job.workspace_id, current_user)
    return job


@router.post(
    "/workspaces/{workspace_id}/generation/briefs",
    response_model=GenerationBriefResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_generation_brief_route(
    workspace_id: UUID,
    payload: GenerationBriefCreateRequest,
    request: Request,
    session: SessionDependency,
    _workspace: OwnedWorkspaceDependency,
) -> GenerationBriefResponse:
    try:
        brief_payload = await _brief_payload_from_create_request(payload, request)
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
    current_user: CurrentUserDependency,
) -> GenerationBriefResponse:
    brief = await session.get(DesignBrief, brief_id)
    if brief is None:
        raise brief_not_found()
    await _require_brief_owner(session, brief, current_user)

    try:
        current = GenerationBriefPayload.model_validate(brief.payload)
        update_payload = payload.model_dump(exclude_unset=True)
        next_status = update_payload.pop("status", None)
        if not update_payload and next_status is None:
            raise ValueError("At least one brief field is required")
        updated = _updated_brief_payload(current, update_payload) if update_payload else current
        if next_status is not None:
            brief.status = _normalized_brief_status(str(next_status))
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
    current_user: CurrentUserDependency,
    _workspace: OwnedWorkspaceDependency,
) -> GenerationJobSubmissionResponse:
    brief = await _get_workspace_brief(session, workspace_id, payload.brief_id)
    brief_payload = GenerationBriefPayload.model_validate(brief.payload)
    provider_intent = _provider_intent_from_submission(payload, _settings_from_request(request))
    metadata: dict[str, Any] = {
        "source": "generation-api",
        "vehicle_template": _brief_template_metadata(brief_payload),
    }
    if provider_intent is not None:
        metadata["provider_intent"] = provider_intent.metadata
    reference_metadata = _reference_usage_metadata(
        brief_payload,
        provider_intent.provider if provider_intent is not None else LOCAL_PROVIDER,
    )
    if reference_metadata is not None:
        metadata["reference_usage"] = reference_metadata
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
            requested_by=current_user.id,
        )
    except (workspaces.WorkspaceNotFoundError, jobs.JobValidationError) as error:
        raise generation_validation_failed(error) from error

    queued = None
    if not result.idempotent_reused:
        queued = await _dispatch_created_generation_job(session, queue, result.job)

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
    current_user: CurrentUserDependency,
    _workspace: OwnedWorkspaceDependency,
) -> GenerationJobSubmissionResponse:
    brief = await _get_workspace_brief(session, workspace_id, payload.brief_id)
    brief_payload = GenerationBriefPayload.model_validate(brief.payload)
    settings = _settings_from_request(request)
    provider_intent = _provider_intent_from_submission(payload, settings)
    try:
        parent_version = await jobs.get_workspace_version(session, workspace_id, version_id)
        _validate_provider_mask_route(payload, provider_intent, settings)
        metadata: dict[str, Any] = {
            "change_request": payload.change_request,
            "iteration": True,
            "parameter_overrides": payload.parameter_overrides,
            "source": "generation-iteration-api",
            "vehicle_template": _brief_template_metadata(brief_payload),
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
            requested_by=current_user.id,
        )
    except (workspaces.WorkspaceNotFoundError, jobs.JobValidationError) as error:
        raise generation_validation_failed(error) from error

    queued = None
    if not result.idempotent_reused:
        queued = await _dispatch_created_generation_job(session, queue, result.job)

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
    current_user: CurrentUserDependency,
) -> GenerationJobRetryResponse:
    failed_job = await _get_owned_generation_job(session, job_id, current_user)

    if failed_job.status != JobStatus.FAILED.value:
        raise generation_validation_failed(ValueError("Only failed generation jobs can be retried"))
    if failed_job.brief_id is None:
        raise generation_validation_failed(ValueError("Failed job has no design brief to retry"))

    retry_metadata = await _retry_metadata_from_failed_job(session, failed_job)
    provider_intent = _provider_intent_from_metadata(retry_metadata)
    result = await jobs.create_job(
        session,
        failed_job.workspace_id,
        brief_id=failed_job.brief_id,
        idempotency_key=payload.idempotency_key,
        metadata=retry_metadata,
        model=provider_intent.model if provider_intent is not None else failed_job.model,
        operation=failed_job.operation,
        provider=(
            provider_intent.provider if provider_intent is not None else failed_job.provider
        ),
        requested_by=current_user.id,
    )

    queued = None
    if not result.idempotent_reused:
        queued = await _dispatch_created_generation_job(session, queue, result.job)

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
    if brief.status == DesignBriefStatus.ARCHIVED.value:
        raise generation_validation_failed(
            ValueError("archived brief cannot be used for generation."),
        )
    return brief


async def _dispatch_created_generation_job(
    session: AsyncSession,
    queue: QueueClient,
    job: GenerationJob,
) -> GenerationQueuedTaskResponse:
    dispatch = await jobs.create_job_dispatch_outbox(
        session,
        job.id,
        metadata={"source": "generation-api"},
        queue_name=GENERATION_QUEUE,
        task_name=GENERATE_2D_CONCEPT_TASK,
    )
    await session.commit()

    try:
        queued_task = await queue.enqueue_generation_job(job.id)
    except Exception as error:
        await jobs.mark_job_dispatch_failed(
            session,
            dispatch.dispatch.id,
            error_message=str(error),
        )
        await session.commit()
        raise

    await _persist_queued_task_metadata(session, job, queued_task)
    await jobs.mark_job_dispatch_dispatched(
        session,
        dispatch.dispatch.id,
        task_id=queued_task.task_id,
    )
    await session.commit()
    return GenerationQueuedTaskResponse.model_validate(queued_task)

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



def _brief_parser_input(payload: GenerationBriefCreateRequest) -> BriefParserInput:
    return BriefParserInput.model_validate(
        payload.model_dump(
            include=set(BriefDraft.model_fields),
            mode="python",
        ),
    )


async def _brief_payload_from_create_request(
    payload: GenerationBriefCreateRequest,
    request: Request,
) -> GenerationBriefPayload:
    settings = _settings_from_request(request)
    parser_input = _brief_parser_input(payload)
    if settings.ai_brief_parser_provider.strip().lower() in OPENAI_ALIASES:
        parser_client = getattr(request.app.state, "openai_brief_parser_client", None)
        draft = await parse_openai_brief(
            parser_input,
            client=parser_client,
            settings=settings,
        )
        return create_generation_brief_from_draft(draft)

    return create_generation_brief_from_draft(BriefDraft.model_validate(parser_input))

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
    if provider in OPENAI_ALIASES:
        return _openai_provider_intent(payload, settings)
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


def _openai_provider_intent(
    payload: GenerationJobSubmissionRequest | GenerationIterationSubmissionRequest,
    settings: ApiSettings,
) -> ProviderIntent:
    capability = settings.provider_capability_map()[OPENAI_PROVIDER]
    blocked_reasons = [str(reason) for reason in capability["blocked_reasons"]]
    if blocked_reasons:
        raise generation_validation_failed(ValueError("; ".join(blocked_reasons)))

    model = _requested_model(payload.model, default=str(capability["default_model"]))
    allowed_models = {str(model_name) for model_name in capability.get("allowed_models", [])}
    if model not in allowed_models:
        raise generation_validation_failed(
            ValueError(f"Unsupported model for provider openai: {model}"),
        )
    return ProviderIntent(
        model=model,
        parameters=dict(payload.provider_parameters),
        provider=OPENAI_PROVIDER,
    )



def _normalized_brief_status(value: str) -> str:
    normalized_status = value.strip().lower()
    allowed_statuses = {item.value for item in DesignBriefStatus}
    if normalized_status not in allowed_statuses:
        raise ValueError(f"Unsupported brief status: {value}")
    return normalized_status


def _requested_model(value: str | None, *, default: str) -> str:
    model = (value or "").strip()
    return model or default


async def _retry_metadata_from_failed_job(
    session: AsyncSession,
    failed_job: GenerationJob,
) -> dict[str, Any]:
    source_metadata = failed_job.metadata_json if isinstance(failed_job.metadata_json, dict) else {}
    operations = source_metadata.get("operations")
    if isinstance(operations, dict) and operations.get("retry_eligible") is False:
        blocked_reason = operations.get("blocked_reason")
        reason = str(blocked_reason) if blocked_reason else "Failed job is not retryable."
        raise generation_validation_failed(ValueError(reason))

    retry_metadata: dict[str, Any] = {
        key: value
        for key, value in source_metadata.items()
        if key not in {"operations", "queue", "retry_of_job_id"}
    }
    retry_metadata["retry_of_job_id"] = str(failed_job.id)
    retry_metadata["source"] = "generation-retry-api"

    edit_intent = retry_metadata.get("edit_intent")
    if isinstance(edit_intent, dict):
        await _validate_targeted_retry_prerequisites(session, failed_job, edit_intent)
    return retry_metadata


async def _validate_targeted_retry_prerequisites(
    session: AsyncSession,
    failed_job: GenerationJob,
    edit_intent: dict[str, Any],
) -> None:
    parent_version_id = edit_intent.get("parent_version_id") or (
        failed_job.metadata_json.get("parent_version_id")
        if isinstance(failed_job.metadata_json, dict)
        else None
    )
    if not parent_version_id:
        raise generation_validation_failed(
            ValueError("Targeted edit retry requires a parent version."),
        )
    try:
        parent_uuid = UUID(str(parent_version_id))
    except ValueError as error:
        raise generation_validation_failed(
            ValueError("Targeted edit retry parent version is invalid."),
        ) from error
    await jobs.get_workspace_version(
        session,
        failed_job.workspace_id,
        parent_uuid,
    )

    mask = edit_intent.get("mask")
    mask_artifact_id = mask.get("artifact_id") if isinstance(mask, dict) else None
    if not mask_artifact_id:
        raise generation_validation_failed(
            ValueError("Targeted edit retry requires a mask artifact."),
        )
    try:
        mask_uuid = UUID(str(mask_artifact_id))
    except ValueError as error:
        raise generation_validation_failed(
            ValueError("Targeted edit retry mask artifact is invalid."),
        ) from error
    mask_artifact = await session.get(Artifact, mask_uuid)
    if mask_artifact is None or mask_artifact.workspace_id != failed_job.workspace_id:
        raise generation_validation_failed(
            ValueError("Targeted edit retry mask artifact is no longer available."),
        )


def _provider_intent_from_metadata(metadata: dict[str, Any]) -> ProviderIntent | None:
    raw_intent = metadata.get("provider_intent")
    if not isinstance(raw_intent, dict):
        return None
    provider = raw_intent.get("provider")
    model = raw_intent.get("model")
    parameters = raw_intent.get("parameters")
    if not isinstance(provider, str) or not isinstance(model, str):
        return None
    return ProviderIntent(
        model=model,
        parameters=dict(parameters) if isinstance(parameters, dict) else {},
        provider=provider,
    )


def _reference_usage_metadata(
    brief_payload: GenerationBriefPayload,
    provider: str,
) -> dict[str, Any] | None:
    reference_plan = plan_reference_usage(
        provider=provider,
        reference_asset_ids=brief_payload.reference_asset_ids,
        reference_usage=brief_payload.reference_usage,
    )
    if reference_plan.reference_warning_count == 0:
        return None
    return reference_plan.warning_metadata()


def _updated_brief_payload(
    current: GenerationBriefPayload,
    update_payload: dict[str, Any],
) -> GenerationBriefPayload:
    merged: dict[str, Any] = current.model_dump(mode="json") | update_payload
    should_normalize_with_fallbacks = (
        "vehicle_template_id" in update_payload
        or "view" in update_payload
        or _has_empty_required_brief_fields(update_payload)
    )
    if not should_normalize_with_fallbacks:
        return refresh_generation_brief_warnings(GenerationBriefPayload(**merged))

    return create_generation_brief(
        character_focus=_optional_string(merged.get("character_focus")),
        character_theme=_optional_string(merged.get("character_theme")),
        color_harmony=_optional_string(merged.get("color_harmony")),
        coverage=_optional_string(merged.get("coverage")),
        overlay_logo_asset_ids=_string_list(merged.get("overlay_logo_asset_ids")),
        original_request=str(merged["original_request"]),
        palette=_string_list(merged.get("palette")),
        racing_cues=_string_list(merged.get("racing_cues")),
        reference_asset_ids=_string_list(merged.get("reference_asset_ids")),
        reference_usage=_sequence_or_none(merged.get("reference_usage")),
        style=_optional_string(merged.get("style")),
        supporting_graphics=_string_list(merged.get("supporting_graphics")),
        text=_string_list(merged.get("text")),
        typography_intent=_optional_string(merged.get("typography_intent")),
        vehicle_template_id=_optional_string(merged.get("vehicle_template_id")),
        view=_optional_string(merged.get("view")),
    )


_REQUIRED_BRIEF_FALLBACK_FIELDS = {"character_theme", "coverage", "style"}


def _has_empty_required_brief_fields(update_payload: dict[str, Any]) -> bool:
    return any(
        isinstance(update_payload.get(field), str) and update_payload[field].strip() == ""
        for field in _REQUIRED_BRIEF_FALLBACK_FIELDS
    )


def _brief_template_metadata(brief_payload: GenerationBriefPayload) -> dict[str, Any]:
    return {
        "id": brief_payload.vehicle_template_id,
        "label": brief_payload.vehicle_template_label,
        "readiness": brief_payload.template_readiness.model_dump(mode="json"),
        "source": brief_payload.template_source.model_dump(mode="json"),
        "view": brief_payload.view,
    }


def _optional_string(value: object) -> str | None:
    return value if isinstance(value, str) else None


def _string_list(value: object) -> list[str] | None:
    if not isinstance(value, list):
        return None
    return [item for item in value if isinstance(item, str)]


def _sequence_or_none(value: object) -> list[Any] | None:
    return value if isinstance(value, list) else None


def _validate_provider_mask_route(
    payload: GenerationIterationSubmissionRequest,
    provider_intent: ProviderIntent | None,
    settings: ApiSettings,
) -> None:
    edit_intent = payload.edit_intent
    if edit_intent is None or edit_intent.route_preference != PROVIDER_MASKED_GENERATION_ROUTE:
        return
    if not settings.v2_targeted_regeneration_enabled:
        raise generation_validation_failed(
            ValueError("V2_TARGETED_REGENERATION_ENABLED is disabled."),
        )
    if provider_intent is None:
        raise generation_validation_failed(
            ValueError("provider_masked_generation requires a selected provider."),
        )

    provider_key = _capability_provider_key(provider_intent.provider)
    capability = settings.provider_capability_map().get(provider_key)
    if capability is None:
        raise generation_validation_failed(
            ValueError(
                f"Provider {provider_intent.provider} does not support "
                f"{PROVIDER_MASKED_GENERATION_ROUTE}.",
            ),
    )

    supported_routes = {str(route) for route in capability.get("supported_edit_routes", [])}
    raw_supports = capability.get("supports")
    supports = raw_supports if isinstance(raw_supports, dict) else {}
    raw_mask_input = capability.get("mask_input")
    mask_input = raw_mask_input if isinstance(raw_mask_input, dict) else {}
    if (
        PROVIDER_MASKED_GENERATION_ROUTE not in supported_routes
        or not bool(supports.get("mask_aware_generation"))
        or not bool(mask_input.get("accepted"))
    ):
        blocked_reason = str(
            mask_input.get("blocked_reason")
            or f"Route {PROVIDER_MASKED_GENERATION_ROUTE} is not enabled.",
        )
        raise generation_validation_failed(
            ValueError(
                f"Provider {provider_key} does not support "
                f"{PROVIDER_MASKED_GENERATION_ROUTE}: {blocked_reason}",
            ),
        )


def _capability_provider_key(provider_name: str) -> str:
    provider = provider_name.strip().lower()
    if provider in LOCAL_PROVIDER_NAMES:
        return LOCAL_PROVIDER
    if provider in BFL_ALIASES:
        return BFL_PROVIDER
    if provider in OPENAI_ALIASES:
        return OPENAI_PROVIDER
    return provider
