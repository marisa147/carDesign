from __future__ import annotations

import asyncio
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Annotated

from caragent_core.enums import FailureCategory, JobStatus
from caragent_core.models import GenerationJob
from caragent_core.provider_capabilities import (
    BFL_ALIASES,
    BFL_PROVIDER,
    OPENAI_ALIASES,
    OPENAI_PROVIDER,
    provider_capabilities_as_list,
)
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_api.config import ApiSettings
from caragent_api.dependencies import get_db_session, get_queue_client
from caragent_api.queue import GENERATE_2D_CONCEPT_TASK, GENERATION_QUEUE, QueueClient
from caragent_api.schemas import (
    BflSettingsResponse,
    BflSettingsUpdateRequest,
    OpenAISettingsResponse,
    OpenAISettingsUpdateRequest,
    OperationsProviderStatusResponse,
    ProviderOperationsSummary,
    QueueOperationsSummary,
    RecentFailureResponse,
    WorkerOperationsSummary,
)

router = APIRouter(tags=["operations"])

SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]
QueueDependency = Annotated[QueueClient, Depends(get_queue_client)]

SUPPORTED_PROVIDERS = ["local-deterministic", "bfl", "openai"]

BFL_ENV_DEFAULTS = {
    "AI_PROVIDER_DEFAULT": "disabled",
    "AI_PROVIDER_CALLS_ENABLED": "false",
    "AI_PROVIDER_MODEL": "flux-2-pro-preview",
    "AI_PROVIDER_BFL_BASE_URL": "https://api.bfl.ai",
    "AI_PROVIDER_BFL_SUBMIT_PATH": "/v1/flux-2-pro-preview",
    "AI_PROVIDER_BFL_RESULT_PATH": "/v1/get_result",
    "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED": "false",
    "AI_HOSTED_DAILY_CALL_LIMIT": "3",
    "AI_HOSTED_RATE_LIMIT_PER_MINUTE": "1",
    "AI_MAX_ESTIMATED_COST_PER_JOB": "0.2500",
    "AI_PROVIDER_BFL_API_KEY": "",
}

COMMON_BFL_ENV_KEYS = {
    "AI_PROVIDER_DEFAULT",
    "AI_PROVIDER_CALLS_ENABLED",
    "AI_PROVIDER_MODEL",
    "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED",
    "AI_HOSTED_DAILY_CALL_LIMIT",
    "AI_HOSTED_RATE_LIMIT_PER_MINUTE",
    "AI_MAX_ESTIMATED_COST_PER_JOB",
    "AI_PROVIDER_BFL_API_KEY",
}

WORKER_ONLY_BFL_ENV_KEYS = {
    "AI_PROVIDER_BFL_BASE_URL",
    "AI_PROVIDER_BFL_SUBMIT_PATH",
    "AI_PROVIDER_BFL_RESULT_PATH",
}

OPENAI_ENV_DEFAULTS = {
    "AI_PROVIDER_DEFAULT": "disabled",
    "AI_PROVIDER_CALLS_ENABLED": "false",
    "AI_PROVIDER_OPENAI_IMAGE_MODEL": "gpt-image-2",
    "AI_PROVIDER_OPENAI_BASE_URL": "https://api.openai.com/v1",
    "AI_PROVIDER_OPENAI_IMAGE_PATH": "/images/generations",
    "AI_PROVIDER_OPENAI_RESPONSES_PATH": "/responses",
    "AI_PROVIDER_OPENAI_TEXT_MODEL": "gpt-5.5",
    "AI_BRIEF_PARSER_PROVIDER": "deterministic",
    "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED": "false",
    "AI_HOSTED_DAILY_CALL_LIMIT": "6",
    "AI_HOSTED_RATE_LIMIT_PER_MINUTE": "2",
    "AI_MAX_ESTIMATED_COST_PER_JOB": "0.9000",
    "AI_PROVIDER_OPENAI_API_KEY": "",
}

COMMON_OPENAI_ENV_KEYS = {
    "AI_PROVIDER_DEFAULT",
    "AI_PROVIDER_CALLS_ENABLED",
    "AI_PROVIDER_OPENAI_IMAGE_MODEL",
    "AI_PROVIDER_OPENAI_BASE_URL",
    "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED",
    "AI_HOSTED_DAILY_CALL_LIMIT",
    "AI_HOSTED_RATE_LIMIT_PER_MINUTE",
    "AI_MAX_ESTIMATED_COST_PER_JOB",
    "AI_PROVIDER_OPENAI_API_KEY",
}

API_ONLY_OPENAI_ENV_KEYS = {
    "AI_PROVIDER_OPENAI_RESPONSES_PATH",
    "AI_PROVIDER_OPENAI_TEXT_MODEL",
    "AI_BRIEF_PARSER_PROVIDER",
}

WORKER_ONLY_OPENAI_ENV_KEYS = {
    "AI_PROVIDER_OPENAI_IMAGE_PATH",
}

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




@router.get(
    "/operations/bfl-settings",
    response_model=BflSettingsResponse,
)
def get_bfl_settings(request: Request) -> BflSettingsResponse:
    settings = _settings_from_request(request)
    _require_local_settings_write(settings)
    api_env_path, worker_env_path = _bfl_env_paths(request)
    return _bfl_settings_response(
        _merged_bfl_env(api_env_path, worker_env_path),
        restart_required=False,
    )


@router.post(
    "/operations/bfl-settings",
    response_model=BflSettingsResponse,
)
def update_bfl_settings(
    request: Request,
    payload: BflSettingsUpdateRequest,
) -> BflSettingsResponse:
    settings = _settings_from_request(request)
    _require_local_settings_write(settings)
    api_env_path, worker_env_path = _bfl_env_paths(request)
    existing = _merged_bfl_env(api_env_path, worker_env_path)
    updates = _bfl_env_updates(
        payload,
        existing_api_key=existing.get("AI_PROVIDER_BFL_API_KEY", ""),
    )
    _upsert_env_file(
        api_env_path,
        {key: value for key, value in updates.items() if key in COMMON_BFL_ENV_KEYS},
    )
    _upsert_env_file(worker_env_path, updates)
    return _bfl_settings_response(
        _merged_bfl_env(api_env_path, worker_env_path),
        restart_required=True,
    )


@router.get(
    "/operations/openai-settings",
    response_model=OpenAISettingsResponse,
)
def get_openai_settings(request: Request) -> OpenAISettingsResponse:
    settings = _settings_from_request(request)
    _require_local_settings_write(settings)
    api_env_path, worker_env_path = _openai_env_paths(request)
    return _openai_settings_response(
        _merged_openai_env(api_env_path, worker_env_path),
        restart_required=False,
    )


@router.post(
    "/operations/openai-settings",
    response_model=OpenAISettingsResponse,
)
def update_openai_settings(
    request: Request,
    payload: OpenAISettingsUpdateRequest,
) -> OpenAISettingsResponse:
    settings = _settings_from_request(request)
    _require_local_settings_write(settings)
    api_env_path, worker_env_path = _openai_env_paths(request)
    existing = _merged_openai_env(api_env_path, worker_env_path)
    updates = _openai_env_updates(
        payload,
        existing_api_key=existing.get("AI_PROVIDER_OPENAI_API_KEY", ""),
    )
    api_updates = {
        key: value
        for key, value in updates.items()
        if key in COMMON_OPENAI_ENV_KEYS | API_ONLY_OPENAI_ENV_KEYS
    }
    worker_updates = {
        key: value
        for key, value in updates.items()
        if key in COMMON_OPENAI_ENV_KEYS | WORKER_ONLY_OPENAI_ENV_KEYS
    }
    _upsert_env_file(api_env_path, api_updates)
    _upsert_env_file(worker_env_path, worker_updates)
    return _openai_settings_response(
        _merged_openai_env(api_env_path, worker_env_path),
        restart_required=True,
    )

def _settings_from_request(request: Request) -> ApiSettings:
    settings = getattr(request.app.state, "settings", None)
    if isinstance(settings, ApiSettings):
        return settings
    return ApiSettings()


def _provider_summary(settings: ApiSettings) -> ProviderOperationsSummary:
    default_provider = settings.ai_provider_default.strip().lower() or "disabled"
    capabilities = settings.provider_capability_map()
    bfl = capabilities[BFL_PROVIDER]
    openai = capabilities[OPENAI_PROVIDER]
    bfl_key_configured = bool(bfl["credential_configured"])
    openai_key_configured = bool(openai["credential_configured"])

    hosted_capability: dict[str, object] | None = None
    active_mode = "local-deterministic"
    if default_provider in BFL_ALIASES:
        hosted_capability = bfl
        if bfl["enabled"]:
            active_mode = BFL_PROVIDER
    elif default_provider in OPENAI_ALIASES:
        hosted_capability = openai
        if openai["enabled"]:
            active_mode = OPENAI_PROVIDER

    raw_blocked_reasons = (
        hosted_capability.get("blocked_reasons") if hosted_capability is not None else []
    )
    blocked_reasons = (
        [str(reason) for reason in raw_blocked_reasons]
        if isinstance(raw_blocked_reasons, list)
        else []
    )
    hosted_provider_configured = bool(
        settings.ai_provider_calls_enabled
        and hosted_capability is not None
        and hosted_capability.get("credential_configured")
    )
    guard_state = (
        hosted_capability.get("guard_state")
        if hosted_capability is not None
        else bfl["guard_state"]
    )
    if not isinstance(guard_state, dict):
        guard_state = {}
    hosted_quota_guard_enabled = bool(guard_state.get("hosted_quota_guard_enabled"))

    return ProviderOperationsSummary(
        active_mode=active_mode,
        bfl_key_configured=bfl_key_configured,
        openai_key_configured=openai_key_configured,
        calls_enabled=settings.ai_provider_calls_enabled,
        capabilities=provider_capabilities_as_list(capabilities),
        default_provider=default_provider,
        guard_state=guard_state,
        hosted_calls_blocked_reason=(
            "; ".join(blocked_reasons) if blocked_reasons else None
        ),
        hosted_daily_call_limit=settings.ai_hosted_daily_call_limit,
        hosted_provider_configured=hosted_provider_configured,
        hosted_quota_guard_enabled=hosted_quota_guard_enabled,
        hosted_rate_limit_per_minute=settings.ai_hosted_rate_limit_per_minute,
        max_estimated_cost_per_job=settings.ai_max_estimated_cost_per_job,
        supported_providers=SUPPORTED_PROVIDERS,
    )

async def _inspect_queue(
    queue: QueueClient,
    *,
    timeout_seconds: float = 3.0,
) -> QueueOperationsSummary:
    try:
        inspection = await asyncio.wait_for(
            asyncio.to_thread(lambda: asyncio.run(queue.inspect_generation_queue())),
            timeout=timeout_seconds,
        )
    except TimeoutError:
        return QueueOperationsSummary(
            active_tasks=0,
            active_workers=0,
            detail="Queue inspection timed out.",
            generation_queue=GENERATION_QUEUE,
            registered_tasks=[],
            reserved_tasks=0,
            status="unavailable",
        )
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
        provider_failure_kind=_optional_metadata_string(metadata.get("provider_failure_kind")),
        provider_status=_optional_metadata_string(metadata.get("provider_status")),
        stage=_optional_metadata_string(metadata.get("stage")),
        status=job.status,
    )


def _optional_metadata_string(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _require_local_settings_write(settings: ApiSettings) -> None:
    if settings.runtime_mode != "local":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hosted provider settings can only be edited in local development mode.",
        )


def _bfl_env_paths(request: Request) -> tuple[Path, Path]:
    override = getattr(request.app.state, "bfl_settings_env_paths", None)
    if isinstance(override, dict):
        api_path = override.get("api")
        worker_path = override.get("worker")
        if api_path and worker_path:
            return Path(api_path), Path(worker_path)

    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "services" / "api" / ".env", repo_root / "services" / "worker" / ".env"


def _merged_bfl_env(api_env_path: Path, worker_env_path: Path) -> dict[str, str]:
    api_values = _read_env_file(api_env_path)
    worker_values = _read_env_file(worker_env_path)
    merged = BFL_ENV_DEFAULTS.copy()
    merged.update({key: value for key, value in api_values.items() if key in COMMON_BFL_ENV_KEYS})
    merged.update(
        {
            key: value
            for key, value in worker_values.items()
            if key in COMMON_BFL_ENV_KEYS | WORKER_ONLY_BFL_ENV_KEYS
        },
    )
    if not merged.get("AI_PROVIDER_BFL_API_KEY"):
        merged["AI_PROVIDER_BFL_API_KEY"] = api_values.get("AI_PROVIDER_BFL_API_KEY", "")
    return merged


def _bfl_env_updates(
    payload: BflSettingsUpdateRequest,
    *,
    existing_api_key: str,
) -> dict[str, str]:
    api_key = existing_api_key if payload.api_key is None else payload.api_key.strip()
    return {
        "AI_PROVIDER_DEFAULT": payload.default_provider,
        "AI_PROVIDER_CALLS_ENABLED": _bool_env(payload.calls_enabled),
        "AI_PROVIDER_MODEL": payload.model.strip() or "flux-2-pro-preview",
        "AI_PROVIDER_BFL_BASE_URL": _normalize_base_url(payload.base_url),
        "AI_PROVIDER_BFL_SUBMIT_PATH": _normalize_path(payload.submit_path),
        "AI_PROVIDER_BFL_RESULT_PATH": _normalize_path(payload.result_path),
        "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED": _bool_env(payload.rollout_enabled),
        "AI_HOSTED_DAILY_CALL_LIMIT": _optional_int_env(payload.daily_call_limit),
        "AI_HOSTED_RATE_LIMIT_PER_MINUTE": _optional_int_env(payload.rate_limit_per_minute),
        "AI_MAX_ESTIMATED_COST_PER_JOB": _optional_decimal_env(payload.max_estimated_cost_per_job),
        "AI_PROVIDER_BFL_API_KEY": api_key,
    }


def _bfl_settings_response(
    values: dict[str, str],
    *,
    restart_required: bool,
) -> BflSettingsResponse:
    base_url = _normalize_base_url(values["AI_PROVIDER_BFL_BASE_URL"])
    submit_path = _normalize_path(values["AI_PROVIDER_BFL_SUBMIT_PATH"])
    result_path = _normalize_path(values["AI_PROVIDER_BFL_RESULT_PATH"])
    api_key = values.get("AI_PROVIDER_BFL_API_KEY", "").strip()
    return BflSettingsResponse(
        api_key_configured=bool(api_key),
        api_key_masked=_mask_secret(api_key),
        base_url=base_url,
        calls_enabled=_env_bool(values["AI_PROVIDER_CALLS_ENABLED"]),
        daily_call_limit=_optional_int(values.get("AI_HOSTED_DAILY_CALL_LIMIT")),
        default_provider=values["AI_PROVIDER_DEFAULT"].strip().lower() or "disabled",
        max_estimated_cost_per_job=_optional_decimal(values.get("AI_MAX_ESTIMATED_COST_PER_JOB")),
        model=values["AI_PROVIDER_MODEL"].strip() or "flux-2-pro-preview",
        rate_limit_per_minute=_optional_int(values.get("AI_HOSTED_RATE_LIMIT_PER_MINUTE")),
        restart_required=restart_required,
        result_path=result_path,
        rollout_enabled=_env_bool(values["V2_HOSTED_PROVIDER_ROLLOUT_ENABLED"]),
        submit_path=submit_path,
        submit_url=f"{base_url}{submit_path}",
    )



def _openai_env_paths(request: Request) -> tuple[Path, Path]:
    override = getattr(request.app.state, "openai_settings_env_paths", None)
    if isinstance(override, dict):
        api_path = override.get("api")
        worker_path = override.get("worker")
        if api_path and worker_path:
            return Path(api_path), Path(worker_path)

    repo_root = Path(__file__).resolve().parents[5]
    return repo_root / "services" / "api" / ".env", repo_root / "services" / "worker" / ".env"


def _merged_openai_env(api_env_path: Path, worker_env_path: Path) -> dict[str, str]:
    api_values = _read_env_file(api_env_path)
    worker_values = _read_env_file(worker_env_path)
    merged = OPENAI_ENV_DEFAULTS.copy()
    merged.update(
        {
            key: value
            for key, value in api_values.items()
            if key in COMMON_OPENAI_ENV_KEYS | API_ONLY_OPENAI_ENV_KEYS
        },
    )
    merged.update(
        {
            key: value
            for key, value in worker_values.items()
            if key in COMMON_OPENAI_ENV_KEYS | WORKER_ONLY_OPENAI_ENV_KEYS
        },
    )
    if not merged.get("AI_PROVIDER_OPENAI_API_KEY"):
        merged["AI_PROVIDER_OPENAI_API_KEY"] = api_values.get("AI_PROVIDER_OPENAI_API_KEY", "")
    return merged


def _openai_env_updates(
    payload: OpenAISettingsUpdateRequest,
    *,
    existing_api_key: str,
) -> dict[str, str]:
    api_key = existing_api_key if payload.api_key is None else payload.api_key.strip()
    return {
        "AI_PROVIDER_DEFAULT": payload.default_provider,
        "AI_PROVIDER_CALLS_ENABLED": _bool_env(payload.calls_enabled),
        "AI_PROVIDER_OPENAI_IMAGE_MODEL": payload.image_model.strip() or "gpt-image-2",
        "AI_PROVIDER_OPENAI_BASE_URL": _normalize_base_url(
            payload.base_url,
            default="https://api.openai.com/v1",
        ),
        "AI_PROVIDER_OPENAI_IMAGE_PATH": _normalize_path(payload.image_path),
        "AI_PROVIDER_OPENAI_RESPONSES_PATH": _normalize_path(payload.responses_path),
        "AI_PROVIDER_OPENAI_TEXT_MODEL": payload.text_model.strip() or "gpt-5.5",
        "AI_BRIEF_PARSER_PROVIDER": "openai" if payload.parser_enabled else "deterministic",
        "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED": _bool_env(payload.rollout_enabled),
        "AI_HOSTED_DAILY_CALL_LIMIT": _optional_int_env(payload.daily_call_limit),
        "AI_HOSTED_RATE_LIMIT_PER_MINUTE": _optional_int_env(payload.rate_limit_per_minute),
        "AI_MAX_ESTIMATED_COST_PER_JOB": _optional_decimal_env(payload.max_estimated_cost_per_job),
        "AI_PROVIDER_OPENAI_API_KEY": api_key,
    }


def _openai_settings_response(
    values: dict[str, str],
    *,
    restart_required: bool,
) -> OpenAISettingsResponse:
    base_url = _normalize_base_url(
        values["AI_PROVIDER_OPENAI_BASE_URL"],
        default="https://api.openai.com/v1",
    )
    image_path = _normalize_path(values["AI_PROVIDER_OPENAI_IMAGE_PATH"])
    responses_path = _normalize_path(values["AI_PROVIDER_OPENAI_RESPONSES_PATH"])
    api_key = values.get("AI_PROVIDER_OPENAI_API_KEY", "").strip()
    return OpenAISettingsResponse(
        api_key_configured=bool(api_key),
        api_key_masked=_mask_secret(api_key),
        base_url=base_url,
        calls_enabled=_env_bool(values["AI_PROVIDER_CALLS_ENABLED"]),
        daily_call_limit=_optional_int(values.get("AI_HOSTED_DAILY_CALL_LIMIT")),
        default_provider=values["AI_PROVIDER_DEFAULT"].strip().lower() or "disabled",
        image_model=values["AI_PROVIDER_OPENAI_IMAGE_MODEL"].strip() or "gpt-image-2",
        image_path=image_path,
        image_url=f"{base_url}{image_path}",
        max_estimated_cost_per_job=_optional_decimal(values.get("AI_MAX_ESTIMATED_COST_PER_JOB")),
        parser_enabled=(
            values.get("AI_BRIEF_PARSER_PROVIDER", "").strip().lower()
            in {"openai", "gpt"}
        ),
        rate_limit_per_minute=_optional_int(values.get("AI_HOSTED_RATE_LIMIT_PER_MINUTE")),
        responses_path=responses_path,
        restart_required=restart_required,
        rollout_enabled=_env_bool(values["V2_HOSTED_PROVIDER_ROLLOUT_ENABLED"]),
        text_model=values["AI_PROVIDER_OPENAI_TEXT_MODEL"].strip() or "gpt-5.5",
    )

def _read_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = _unquote_env_value(value.strip())
    return values


def _upsert_env_file(path: Path, updates: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    seen: set[str] = set()
    next_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            next_lines.append(line)
            continue
        key, _value = stripped.split("=", 1)
        env_key = key.strip()
        if env_key in updates:
            next_lines.append(f"{env_key}={_env_file_value(updates[env_key])}")
            seen.add(env_key)
        else:
            next_lines.append(line)
    for key, value in updates.items():
        if key not in seen:
            next_lines.append(f"{key}={_env_file_value(value)}")
    path.write_text("\n".join(next_lines) + "\n", encoding="utf-8")


def _normalize_base_url(value: str, *, default: str = "https://api.bfl.ai") -> str:
    normalized = value.strip().rstrip("/")
    return normalized or default


def _normalize_path(value: str) -> str:
    normalized = value.strip() or "/"
    return normalized if normalized.startswith("/") else f"/{normalized}"


def _bool_env(value: bool) -> str:
    return "true" if value else "false"


def _env_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _optional_int_env(value: int | None) -> str:
    return "" if value is None else str(value)


def _optional_decimal_env(value: Decimal | None) -> str:
    return "" if value is None else str(value)


def _optional_int(value: str | None) -> int | None:
    if not value or not value.strip():
        return None
    return int(value)


def _optional_decimal(value: str | None) -> Decimal | None:
    if not value or not value.strip():
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def _mask_secret(value: str) -> str | None:
    if not value:
        return None
    if len(value) <= 4:
        return "********"
    return f"********{value[-4:]}"


def _unquote_env_value(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _env_file_value(value: str) -> str:
    if not value:
        return ""
    if any(char.isspace() for char in value) or "#" in value:
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value

