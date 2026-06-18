from __future__ import annotations

from typing import Annotated

from caragent_core.enums import FailureCategory, JobStatus
from caragent_core.models import GenerationJob
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_api.config import ApiSettings
from caragent_api.dependencies import get_db_session, get_queue_client
from caragent_api.queue import GENERATE_2D_CONCEPT_TASK, GENERATION_QUEUE, QueueClient
from caragent_api.schemas import (
    OperationsProviderStatusResponse,
    ProviderOperationsSummary,
    QueueOperationsSummary,
    RecentFailureResponse,
    WorkerOperationsSummary,
)

router = APIRouter(tags=["operations"])

SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]
QueueDependency = Annotated[QueueClient, Depends(get_queue_client)]

SUPPORTED_PROVIDERS = ["local-deterministic", "bfl"]


@router.get(
    "/operations/provider-status",
    response_model=OperationsProviderStatusResponse,
)
async def provider_status(
    request: Request,
    session: SessionDependency,
    queue: QueueDependency,
) -> OperationsProviderStatusResponse:
    settings = _settings_from_request(request)
    queue_summary = await _inspect_queue(queue)
    return OperationsProviderStatusResponse(
        api_version=settings.api_version,
        provider=_provider_summary(settings),
        queue=queue_summary,
        recent_failures=await _recent_failures(session),
        runtime_mode=settings.runtime_mode,
        worker=WorkerOperationsSummary(
            active_workers=queue_summary.active_workers,
            detail=queue_summary.detail,
            status=queue_summary.status,
            task_name=GENERATE_2D_CONCEPT_TASK,
        ),
    )


def _settings_from_request(request: Request) -> ApiSettings:
    settings = getattr(request.app.state, "settings", None)
    if isinstance(settings, ApiSettings):
        return settings
    return ApiSettings()


def _provider_summary(settings: ApiSettings) -> ProviderOperationsSummary:
    default_provider = settings.ai_provider_default.strip().lower() or "disabled"
    bfl_key_configured = bool(
        settings.ai_provider_bfl_api_key
        and settings.ai_provider_bfl_api_key.get_secret_value()
    )
    hosted_provider_configured = (
        settings.ai_provider_calls_enabled
        and default_provider in {"bfl", "black-forest-labs"}
        and bfl_key_configured
    )
    active_mode = "bfl" if hosted_provider_configured else "local-deterministic"
    hosted_quota_guard_enabled = (
        settings.ai_hosted_daily_call_limit is not None
        and settings.ai_hosted_rate_limit_per_minute is not None
        and settings.ai_max_estimated_cost_per_job is not None
    )
    return ProviderOperationsSummary(
        active_mode=active_mode,
        bfl_key_configured=bfl_key_configured,
        calls_enabled=settings.ai_provider_calls_enabled,
        default_provider=default_provider,
        hosted_calls_blocked_reason=(
            None
            if not settings.ai_provider_calls_enabled or hosted_quota_guard_enabled
            else "Hosted calls require daily, per-minute, and per-job cost limits."
        ),
        hosted_daily_call_limit=settings.ai_hosted_daily_call_limit,
        hosted_provider_configured=hosted_provider_configured,
        hosted_quota_guard_enabled=hosted_quota_guard_enabled,
        hosted_rate_limit_per_minute=settings.ai_hosted_rate_limit_per_minute,
        max_estimated_cost_per_job=settings.ai_max_estimated_cost_per_job,
        supported_providers=SUPPORTED_PROVIDERS,
    )


async def _inspect_queue(queue: QueueClient) -> QueueOperationsSummary:
    try:
        inspection = await queue.inspect_generation_queue()
    except Exception:
        return QueueOperationsSummary(
            active_tasks=0,
            active_workers=0,
            detail="Queue inspection unavailable.",
            generation_queue=GENERATION_QUEUE,
            registered_tasks=[],
            reserved_tasks=0,
            status="unavailable",
        )

    return QueueOperationsSummary.model_validate(inspection)


async def _recent_failures(session: AsyncSession) -> list[RecentFailureResponse]:
    result = await session.execute(
        select(GenerationJob)
        .where(GenerationJob.status == JobStatus.FAILED.value)
        .order_by(GenerationJob.updated_at.desc())
        .limit(5),
    )
    return [_failure_response(job) for job in result.scalars()]


def _failure_response(job: GenerationJob) -> RecentFailureResponse:
    operations = job.metadata_json.get("operations") if isinstance(job.metadata_json, dict) else {}
    metadata = operations if isinstance(operations, dict) else {}
    return RecentFailureResponse(
        created_at=job.updated_at,
        failure_category=str(
            metadata.get("failure_category") or FailureCategory.UNKNOWN.value,
        ),
        job_id=job.id,
        message=job.latest_error,
        model=_optional_metadata_string(metadata.get("model")) or job.model,
        provider=_optional_metadata_string(metadata.get("provider")) or job.provider,
        stage=_optional_metadata_string(metadata.get("stage")),
        status=job.status,
    )


def _optional_metadata_string(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None
