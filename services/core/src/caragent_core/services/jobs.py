from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from caragent_core.enums import (
    ArtifactKind,
    DesignVersionStatus,
    ExportStatus,
    FailureCategory,
    FeedbackApprovalState,
    JobEventType,
    JobStatus,
    ModelRunStatus,
)
from caragent_core.models import (
    Artifact,
    DesignVersion,
    ExportRecord,
    Feedback,
    GenerationJob,
    JobEvent,
    ModelRun,
    utc_now,
)
from caragent_core.repositories import jobs as job_repository
from caragent_core.services import workspaces

JsonObject = dict[str, object]
SUPPORTED_CONCEPT_EXPORT_FORMATS = {"jpeg", "jpg", "png"}
CONCEPT_EXPORT_DISCLAIMER = "Concept preview only, not print-ready."


class JobNotFoundError(LookupError):
    pass


class JobValidationError(ValueError):
    pass


class ModelRunNotFoundError(LookupError):
    pass


@dataclass(frozen=True)
class JobCreationResult:
    job: GenerationJob
    idempotent_reused: bool


def _normalize_required(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise JobValidationError(f"{field_name} is required")
    return normalized


def _validate_choice(value: str, allowed: set[str], field_name: str) -> str:
    normalized = _normalize_required(value, field_name).lower()
    if normalized not in allowed:
        raise JobValidationError(f"Unsupported {field_name}: {value}")
    return normalized


def _sanitize_error(message: str | None, *, secrets: Sequence[str] = ()) -> str | None:
    if message is None:
        return None
    sanitized = message.replace("\n", " ").replace("\r", " ")
    for secret in secrets:
        if secret:
            sanitized = sanitized.replace(secret, "[redacted]")
    return sanitized[:1000]


def _sanitize_metadata_value(value: object, *, secrets: Sequence[str]) -> object:
    if isinstance(value, str):
        return _sanitize_error(value, secrets=secrets)
    if isinstance(value, list):
        return [_sanitize_metadata_value(item, secrets=secrets) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _sanitize_metadata_value(item, secrets=secrets)
            for key, item in value.items()
        }
    return value


def _sanitize_event_metadata(
    metadata: JsonObject | None,
    *,
    secrets: Sequence[str] = (),
) -> JsonObject | None:
    if metadata is None:
        return None

    sanitized = {
        str(key): _sanitize_metadata_value(value, secrets=secrets)
        for key, value in metadata.items()
    }
    category = sanitized.get("failure_category")
    if category is not None:
        sanitized["failure_category"] = _validate_choice(
            str(category),
            {item.value for item in FailureCategory},
            "failure_category",
        )
    return sanitized


async def _get_workspace_version(
    session: AsyncSession,
    workspace_id: UUID,
    version_id: UUID,
) -> DesignVersion:
    version = await session.get(DesignVersion, version_id)
    if version is None or version.workspace_id != workspace_id:
        raise JobValidationError("Version not found for workspace")
    return version


async def _get_workspace_artifact(
    session: AsyncSession,
    workspace_id: UUID,
    artifact_id: UUID,
    *,
    version_id: UUID | None = None,
) -> Artifact:
    artifact = await session.get(Artifact, artifact_id)
    if artifact is None or artifact.workspace_id != workspace_id:
        raise JobValidationError("Artifact not found for workspace")
    if version_id is not None and artifact.version_id != version_id:
        raise JobValidationError("Artifact not found for version")
    return artifact


async def create_job(
    session: AsyncSession,
    workspace_id: UUID,
    *,
    idempotency_key: str,
    operation: str,
    brief_id: UUID | None = None,
    requested_by: str | None = None,
    provider: str | None = None,
    model: str | None = None,
    estimated_cost: Decimal | None = None,
    metadata: JsonObject | None = None,
) -> JobCreationResult:
    await workspaces.get_workspace(session, workspace_id)

    normalized_key = _normalize_required(idempotency_key, "idempotency_key")
    normalized_operation = _normalize_required(operation, "operation")
    existing = await job_repository.find_job_by_idempotency_key(
        session,
        workspace_id,
        normalized_key,
    )
    if existing is not None:
        return JobCreationResult(job=existing, idempotent_reused=True)

    job = GenerationJob(
        brief_id=brief_id,
        estimated_cost=estimated_cost,
        idempotency_key=normalized_key,
        metadata_json=metadata or {},
        model=model,
        operation=normalized_operation,
        provider=provider,
        requested_by=requested_by,
        status=JobStatus.QUEUED.value,
        workspace_id=workspace_id,
    )
    session.add(job)
    await session.flush()
    await append_event(
        session,
        job.id,
        event_type=JobEventType.CREATED.value,
        status=JobStatus.QUEUED.value,
        message="Job queued.",
        source="api",
    )
    return JobCreationResult(job=job, idempotent_reused=False)


async def get_job(session: AsyncSession, job_id: UUID) -> GenerationJob:
    job = await job_repository.get_job(session, job_id)
    if job is None:
        raise JobNotFoundError(f"Job not found: {job_id}")
    return job


async def list_workspace_jobs(session: AsyncSession, workspace_id: UUID) -> list[GenerationJob]:
    await workspaces.get_workspace(session, workspace_id)
    return await job_repository.list_workspace_jobs(session, workspace_id)


async def get_workspace_version(
    session: AsyncSession,
    workspace_id: UUID,
    version_id: UUID,
) -> DesignVersion:
    await workspaces.get_workspace(session, workspace_id)
    return await _get_workspace_version(session, workspace_id, version_id)


async def append_event(
    session: AsyncSession,
    job_id: UUID,
    *,
    event_type: str,
    status: str | None = None,
    message: str | None = None,
    progress: Decimal | None = None,
    source: str | None = None,
    metadata: JsonObject | None = None,
) -> JobEvent:
    await get_job(session, job_id)
    normalized_event_type = _validate_choice(
        event_type,
        {item.value for item in JobEventType},
        "event_type",
    )
    normalized_status = (
        _validate_choice(status, {item.value for item in JobStatus}, "status")
        if status is not None
        else None
    )
    event = JobEvent(
        event_type=normalized_event_type,
        job_id=job_id,
        message=message,
        metadata_json=metadata or {},
        progress=progress,
        sequence=await job_repository.next_event_sequence(session, job_id),
        source=source,
        status=normalized_status,
    )
    session.add(event)
    await session.flush()
    return event


async def transition_job_status(
    session: AsyncSession,
    job_id: UUID,
    *,
    status: str,
    message: str | None = None,
    metadata: JsonObject | None = None,
    source: str | None = None,
    latest_error: str | None = None,
    secrets: Sequence[str] = (),
) -> GenerationJob:
    job = await get_job(session, job_id)
    normalized_status = _validate_choice(status, {item.value for item in JobStatus}, "status")
    job.status = normalized_status
    job.latest_error = _sanitize_error(latest_error, secrets=secrets)
    event_metadata = _sanitize_event_metadata(metadata, secrets=secrets)
    if event_metadata is not None and normalized_status in {
        JobStatus.CANCELED.value,
        JobStatus.FAILED.value,
        JobStatus.SUCCEEDED.value,
    }:
        job.metadata_json = {
            **(job.metadata_json or {}),
            "operations": event_metadata,
        }

    event_type = JobEventType.STATUS.value
    if normalized_status == JobStatus.SUCCEEDED.value:
        event_type = JobEventType.COMPLETED.value
    elif normalized_status == JobStatus.FAILED.value:
        event_type = JobEventType.ERROR.value

    await append_event(
        session,
        job_id,
        event_type=event_type,
        status=normalized_status,
        message=message,
        metadata=event_metadata,
        source=source,
    )
    await session.flush()
    return job


async def update_job_costs(
    session: AsyncSession,
    job_id: UUID,
    *,
    estimated_cost: Decimal | None = None,
    actual_cost: Decimal | None = None,
) -> GenerationJob:
    job = await get_job(session, job_id)
    job.estimated_cost = estimated_cost
    job.actual_cost = actual_cost
    await session.flush()
    return job


async def cancel_job(
    session: AsyncSession,
    job_id: UUID,
    *,
    reason: str | None = None,
    requested_by: str | None = None,
    source: str | None = None,
) -> GenerationJob:
    job = await get_job(session, job_id)
    if job.status not in {JobStatus.QUEUED.value, JobStatus.RUNNING.value}:
        raise JobValidationError("Only queued or running jobs can be canceled")

    metadata: JsonObject = {"failure_category": FailureCategory.CANCELED.value}
    if reason:
        metadata["reason"] = reason
    if requested_by:
        metadata["requested_by"] = requested_by
    return await transition_job_status(
        session,
        job_id,
        status=JobStatus.CANCELED.value,
        message=(
            "Cancellation requested for running job."
            if job.status == JobStatus.RUNNING.value
            else "Job canceled."
        ),
        metadata=metadata,
        source=source,
    )


async def list_job_events(session: AsyncSession, job_id: UUID) -> list[JobEvent]:
    await get_job(session, job_id)
    return await job_repository.list_job_events(session, job_id)


async def create_design_version(
    session: AsyncSession,
    workspace_id: UUID,
    *,
    parent_version_id: UUID | None = None,
    job_id: UUID | None = None,
    brief_id: UUID | None = None,
    status: str = DesignVersionStatus.DRAFT.value,
    title: str | None = None,
    summary: str | None = None,
    parameters: JsonObject | None = None,
) -> DesignVersion:
    await workspaces.get_workspace(session, workspace_id)
    normalized_status = _validate_choice(
        status,
        {item.value for item in DesignVersionStatus},
        "version status",
    )
    lineage_depth = 0
    if parent_version_id is not None:
        parent = await session.get(DesignVersion, parent_version_id)
        if parent is None or parent.workspace_id != workspace_id:
            raise JobValidationError(f"Parent version not found: {parent_version_id}")
        lineage_depth = parent.lineage_depth + 1

    version = DesignVersion(
        brief_id=brief_id,
        job_id=job_id,
        lineage_depth=lineage_depth,
        parameters=parameters or {},
        parent_version_id=parent_version_id,
        status=normalized_status,
        summary=summary,
        title=title,
        workspace_id=workspace_id,
    )
    session.add(version)
    await session.flush()
    return version


async def create_artifact(
    session: AsyncSession,
    workspace_id: UUID,
    *,
    object_key: str,
    kind: str,
    job_id: UUID | None = None,
    version_id: UUID | None = None,
    asset_id: UUID | None = None,
    content_type: str | None = None,
    byte_size: int | None = None,
    checksum_sha256: str | None = None,
    width: int | None = None,
    height: int | None = None,
    metadata: JsonObject | None = None,
) -> Artifact:
    await workspaces.get_workspace(session, workspace_id)
    normalized_kind = _validate_choice(kind, {item.value for item in ArtifactKind}, "artifact kind")
    normalized_key = _normalize_required(object_key, "object_key")
    artifact = Artifact(
        asset_id=asset_id,
        byte_size=byte_size,
        checksum_sha256=checksum_sha256,
        content_type=content_type,
        height=height,
        job_id=job_id,
        kind=normalized_kind,
        metadata_json=metadata or {},
        object_key=normalized_key,
        version_id=version_id,
        width=width,
        workspace_id=workspace_id,
    )
    session.add(artifact)
    await session.flush()
    return artifact


async def create_model_run(
    session: AsyncSession,
    job_id: UUID,
    *,
    provider: str | None = None,
    model: str | None = None,
    status: str = ModelRunStatus.PLANNED.value,
    parameters: JsonObject | None = None,
    prompt_text: str | None = None,
    prompt_payload: JsonObject | None = None,
    estimated_cost: Decimal | None = None,
    actual_cost: Decimal | None = None,
    input_artifact_ids: list[str] | None = None,
    output_artifact_id: UUID | None = None,
) -> ModelRun:
    await get_job(session, job_id)
    normalized_status = _validate_choice(
        status,
        {item.value for item in ModelRunStatus},
        "model run status",
    )
    model_run = ModelRun(
        actual_cost=actual_cost,
        estimated_cost=estimated_cost,
        input_artifact_ids=input_artifact_ids or [],
        job_id=job_id,
        model=model,
        output_artifact_id=output_artifact_id,
        parameters=parameters or {},
        prompt_payload=prompt_payload or {},
        prompt_text=prompt_text,
        provider=provider,
        status=normalized_status,
    )
    session.add(model_run)
    await session.flush()
    return model_run


async def get_model_run(session: AsyncSession, model_run_id: UUID) -> ModelRun:
    model_run = await session.get(ModelRun, model_run_id)
    if model_run is None:
        raise ModelRunNotFoundError(f"Model run not found: {model_run_id}")
    return model_run


async def complete_model_run(
    session: AsyncSession,
    model_run_id: UUID,
    *,
    output_artifact_id: UUID,
    actual_cost: Decimal | None = None,
) -> ModelRun:
    model_run = await get_model_run(session, model_run_id)
    model_run.status = ModelRunStatus.SUCCEEDED.value
    model_run.output_artifact_id = output_artifact_id
    model_run.actual_cost = actual_cost
    model_run.completed_at = utc_now()
    model_run.error_message = None
    await session.flush()
    return model_run


async def fail_model_run(
    session: AsyncSession,
    model_run_id: UUID,
    *,
    error_message: str,
    actual_cost: Decimal | None = None,
    secrets: Sequence[str] = (),
) -> ModelRun:
    model_run = await get_model_run(session, model_run_id)
    model_run.status = ModelRunStatus.FAILED.value
    model_run.actual_cost = actual_cost
    model_run.completed_at = utc_now()
    model_run.error_message = _sanitize_error(error_message, secrets=secrets)
    await session.flush()
    return model_run


async def record_feedback(
    session: AsyncSession,
    workspace_id: UUID,
    version_id: UUID,
    *,
    rating: int | None = None,
    approval_state: str = FeedbackApprovalState.NONE.value,
    comment: str | None = None,
    metadata: JsonObject | None = None,
) -> Feedback:
    await workspaces.get_workspace(session, workspace_id)
    await _get_workspace_version(session, workspace_id, version_id)
    normalized_state = _validate_choice(
        approval_state,
        {item.value for item in FeedbackApprovalState},
        "approval state",
    )
    if rating is not None and not 1 <= rating <= 5:
        raise JobValidationError("Feedback rating must be between 1 and 5")
    feedback = Feedback(
        approval_state=normalized_state,
        comment=comment,
        metadata_json=metadata or {},
        rating=rating,
        version_id=version_id,
        workspace_id=workspace_id,
    )
    session.add(feedback)
    await session.flush()
    return feedback


async def record_export(
    session: AsyncSession,
    workspace_id: UUID,
    version_id: UUID,
    *,
    export_format: str,
    artifact_id: UUID | None = None,
    status: str = ExportStatus.REQUESTED.value,
    concept_label: str = "concept_preview",
    manifest: JsonObject | None = None,
) -> ExportRecord:
    await workspaces.get_workspace(session, workspace_id)
    version = await _get_workspace_version(session, workspace_id, version_id)
    artifact = (
        await _get_workspace_artifact(
            session,
            workspace_id,
            artifact_id,
            version_id=version_id,
        )
        if artifact_id is not None
        else None
    )
    normalized_format = _normalize_required(export_format, "export_format").lower()
    if normalized_format not in SUPPORTED_CONCEPT_EXPORT_FORMATS:
        raise JobValidationError(f"Unsupported export format: {export_format}")
    normalized_status = _validate_choice(
        status,
        {item.value for item in ExportStatus},
        "export status",
    )
    normalized_label = _normalize_required(concept_label, "concept_label")
    export_manifest: JsonObject = {
        **(manifest or {}),
        "brief_id": str(version.brief_id) if version.brief_id is not None else None,
        "concept_label": normalized_label,
        "disclaimer": CONCEPT_EXPORT_DISCLAIMER,
        "format": normalized_format,
        "parameters": version.parameters,
        "parent_version_id": (
            str(version.parent_version_id) if version.parent_version_id is not None else None
        ),
        "source_artifact_id": str(artifact.id) if artifact is not None else None,
        "source_artifact_object_key": artifact.object_key if artifact is not None else None,
        "version_id": str(version_id),
        "workspace_id": str(workspace_id),
    }
    export = ExportRecord(
        artifact_id=artifact_id,
        concept_label=normalized_label,
        format=normalized_format,
        manifest=export_manifest,
        status=normalized_status,
        version_id=version_id,
        workspace_id=workspace_id,
    )
    session.add(export)
    await session.flush()
    return export


async def list_workspace_versions(session: AsyncSession, workspace_id: UUID) -> list[DesignVersion]:
    await workspaces.get_workspace(session, workspace_id)
    return await job_repository.list_workspace_versions(session, workspace_id)


async def list_workspace_artifacts(session: AsyncSession, workspace_id: UUID) -> list[Artifact]:
    await workspaces.get_workspace(session, workspace_id)
    return await job_repository.list_workspace_artifacts(session, workspace_id)


async def list_job_model_runs(session: AsyncSession, job_id: UUID) -> list[ModelRun]:
    await get_job(session, job_id)
    return await job_repository.list_job_model_runs(session, job_id)


async def list_workspace_feedback(session: AsyncSession, workspace_id: UUID) -> list[Feedback]:
    await workspaces.get_workspace(session, workspace_id)
    return await job_repository.list_workspace_feedback(session, workspace_id)


async def list_workspace_exports(session: AsyncSession, workspace_id: UUID) -> list[ExportRecord]:
    await workspaces.get_workspace(session, workspace_id)
    return await job_repository.list_workspace_exports(session, workspace_id)
