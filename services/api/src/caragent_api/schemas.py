from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from caragent_core.enums import MessageRole
from caragent_core.generation import GenerationBriefPayload
from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreateRequest(BaseModel):
    owner_id: str | None = Field(default=None, max_length=128)
    title: str | None = Field(default=None, max_length=160)


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: str | None
    title: str
    status: str
    created_at: datetime
    updated_at: datetime


class MessageCreateRequest(BaseModel):
    role: str = Field(default=MessageRole.USER.value)
    content: str = Field(min_length=1)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    sequence: int
    role: str
    content: str
    created_at: datetime
    updated_at: datetime


class DesignBriefCreateRequest(BaseModel):
    payload: dict[str, Any] = Field(min_length=1)
    source_message_id: UUID | None = None
    title: str | None = Field(default=None, max_length=160)


class DesignBriefResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    source_message_id: UUID | None
    title: str | None
    status: str
    payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class GenerationBriefCreateRequest(BaseModel):
    original_request: str = Field(min_length=1)
    vehicle_template_id: str | None = None
    view: str | None = None
    character_theme: str | None = None
    character_focus: str | None = None
    style: str | None = None
    palette: list[str] | None = None
    text: list[str] | None = None
    supporting_graphics: list[str] | None = None
    racing_cues: list[str] | None = None
    typography_intent: str | None = None
    color_harmony: str | None = None
    coverage: str | None = None
    reference_asset_ids: list[str] | None = None
    overlay_logo_asset_ids: list[str] | None = None
    source_message_id: UUID | None = None
    title: str | None = Field(default=None, max_length=160)


class GenerationBriefUpdateRequest(BaseModel):
    character_theme: str | None = None
    character_focus: str | None = None
    style: str | None = None
    palette: list[str] | None = None
    text: list[str] | None = None
    supporting_graphics: list[str] | None = None
    racing_cues: list[str] | None = None
    typography_intent: str | None = None
    color_harmony: str | None = None
    coverage: str | None = None
    reference_asset_ids: list[str] | None = None
    overlay_logo_asset_ids: list[str] | None = None


class GenerationBriefResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    source_message_id: UUID | None
    title: str | None
    status: str
    payload: GenerationBriefPayload
    created_at: datetime
    updated_at: datetime


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    kind: str
    original_filename: str
    content_type: str
    byte_size: int
    checksum_sha256: str | None
    object_key: str
    thumbnail_object_key: str | None
    rights_status: str
    source_label: str | None
    source_url: str | None
    rights_notes: str | None
    rights_confirmed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AssetRightsUpdateRequest(BaseModel):
    rights_status: str
    source_label: str | None = Field(default=None, max_length=255)
    source_url: str | None = Field(default=None, max_length=1024)
    rights_notes: str | None = None


class JobCreateRequest(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=160)
    operation: str = Field(min_length=1, max_length=80)
    brief_id: UUID | None = None
    requested_by: str | None = Field(default=None, max_length=128)
    provider: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=120)
    estimated_cost: Decimal | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class GenerationJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    brief_id: UUID | None
    idempotency_key: str
    operation: str
    status: str
    requested_by: str | None
    provider: str | None
    model: str | None
    estimated_cost: Decimal | None
    actual_cost: Decimal | None
    latest_error: str | None
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_json")
    created_at: datetime
    updated_at: datetime


class JobCreateResponse(GenerationJobResponse):
    idempotent_reused: bool


class GenerationQueuedTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    task_id: str | None = None
    task_name: str


class GenerationJobSubmissionRequest(BaseModel):
    brief_id: UUID
    idempotency_key: str = Field(min_length=1, max_length=160)
    model: str | None = Field(default=None, max_length=120)
    provider: str | None = Field(default=None, max_length=80)
    provider_parameters: dict[str, Any] = Field(default_factory=dict)
    requested_by: str | None = Field(default=None, max_length=128)


class GenerationIterationSubmissionRequest(BaseModel):
    brief_id: UUID
    change_request: str = Field(min_length=1)
    idempotency_key: str = Field(min_length=1, max_length=160)
    parameter_overrides: dict[str, Any] = Field(default_factory=dict)
    model: str | None = Field(default=None, max_length=120)
    provider: str | None = Field(default=None, max_length=80)
    provider_parameters: dict[str, Any] = Field(default_factory=dict)
    requested_by: str | None = Field(default=None, max_length=128)


class GenerationJobSubmissionResponse(BaseModel):
    job: GenerationJobResponse
    idempotent_reused: bool
    queued: GenerationQueuedTaskResponse | None


class GenerationJobRetryRequest(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=160)
    requested_by: str | None = Field(default=None, max_length=128)


class GenerationJobRetryResponse(GenerationJobSubmissionResponse):
    retry_of_job_id: UUID


class GenerationJobCancelRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=160)
    requested_by: str | None = Field(default=None, max_length=128)


class QueueRevokeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    detail: str | None = None
    status: str
    task_id: str | None = None


class GenerationJobCancelResponse(BaseModel):
    job: GenerationJobResponse
    queue_revoke: QueueRevokeResponse


class JobEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    sequence: int
    event_type: str
    status: str | None
    message: str | None
    progress: Decimal | None
    source: str | None
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_json")
    created_at: datetime
    updated_at: datetime


class ProviderOperationsSummary(BaseModel):
    active_mode: str
    bfl_key_configured: bool
    calls_enabled: bool
    capabilities: list[dict[str, Any]] = Field(default_factory=list)
    default_provider: str
    guard_state: dict[str, Any] = Field(default_factory=dict)
    hosted_calls_blocked_reason: str | None = None
    hosted_daily_call_limit: int | None = None
    hosted_provider_configured: bool
    hosted_quota_guard_enabled: bool
    hosted_rate_limit_per_minute: int | None = None
    max_estimated_cost_per_job: Decimal | None = None
    supported_providers: list[str]


class QueueOperationsSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    active_tasks: int
    active_workers: int
    detail: str | None = None
    generation_queue: str
    registered_tasks: list[str]
    reserved_tasks: int
    status: str


class WorkerOperationsSummary(BaseModel):
    active_workers: int
    detail: str | None = None
    status: str
    task_name: str


class RecentFailureResponse(BaseModel):
    created_at: datetime
    failure_category: str
    job_id: UUID
    message: str | None
    model: str | None
    provider: str | None
    provider_failure_kind: str | None = None
    provider_status: str | None = None
    stage: str | None
    status: str


class OperationsProviderStatusResponse(BaseModel):
    api_version: str
    provider: ProviderOperationsSummary
    queue: QueueOperationsSummary
    recent_failures: list[RecentFailureResponse]
    runtime_mode: str
    worker: WorkerOperationsSummary


class DesignVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    parent_version_id: UUID | None
    job_id: UUID | None
    brief_id: UUID | None
    status: str
    title: str | None
    summary: str | None
    lineage_depth: int
    parameters: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    job_id: UUID | None
    version_id: UUID | None
    asset_id: UUID | None
    kind: str
    object_key: str
    content_type: str | None
    byte_size: int | None
    checksum_sha256: str | None
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_json")
    width: int | None
    height: int | None
    created_at: datetime
    updated_at: datetime


class ModelRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    provider: str | None
    model: str | None
    status: str
    parameters: dict[str, Any]
    prompt_text: str | None
    prompt_payload: dict[str, Any]
    estimated_cost: Decimal | None
    actual_cost: Decimal | None
    input_artifact_ids: list[str]
    output_artifact_id: UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    version_id: UUID
    rating: int | None
    approval_state: str
    comment: str | None
    created_at: datetime
    updated_at: datetime


class FeedbackCreateRequest(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    approval_state: str = Field(default="none", max_length=40)
    comment: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ExportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    version_id: UUID
    artifact_id: UUID | None
    format: str
    status: str
    concept_label: str
    manifest: dict[str, Any]
    requested_at: datetime
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ExportCreateRequest(BaseModel):
    format: str = Field(min_length=1, max_length=20)
    artifact_id: UUID | None = None
    concept_label: str = Field(default="concept_preview", min_length=1, max_length=120)
    manifest: dict[str, Any] = Field(default_factory=dict)
