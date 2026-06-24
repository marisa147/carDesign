from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from caragent_core.editing import EditIntent
from caragent_core.enums import MessageRole
from caragent_core.generation import (
    GenerationBriefPayload,
    TemplateReadinessReport,
    TemplateSourceMetadata,
)
from caragent_core.preview3d import Preview3DScreenshotMetadata, Preview3DSpec
from caragent_core.production_preflight import ProductionReadinessPreflightReport
from caragent_core.references import ReferenceAssignment
from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    reference_usage: list[ReferenceAssignment] | None = None
    overlay_logo_asset_ids: list[str] | None = None
    source_message_id: UUID | None = None
    title: str | None = Field(default=None, max_length=160)


class GenerationBriefUpdateRequest(BaseModel):
    vehicle_template_id: str | None = Field(default=None, min_length=1, max_length=120)
    view: str | None = Field(default=None, min_length=1, max_length=40)
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
    reference_usage: list[ReferenceAssignment] | None = None
    overlay_logo_asset_ids: list[str] | None = None
    status: str | None = Field(default=None, min_length=1, max_length=32)


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


class TemplateSafeZoneSummaryResponse(BaseModel):
    id: str
    label: str
    kind: str
    x: float
    y: float
    width: float
    height: float


class TemplateCatalogItemResponse(BaseModel):
    id: str
    label: str
    view: str
    supported_views: list[str]
    aliases: list[str] = Field(default_factory=list)
    canvas_width: int
    canvas_height: int
    thumbnail_url: str
    source: TemplateSourceMetadata
    readiness: TemplateReadinessReport
    safe_zone_summary: list[TemplateSafeZoneSummaryResponse]


class TemplateDetailResponse(TemplateCatalogItemResponse):
    asset_slots: dict[str, str | None]
    safe_zones: list[dict[str, Any]]
    view_assets: dict[str, dict[str, str]] = Field(default_factory=dict)
    sections: list[dict[str, Any]] = Field(default_factory=list)
    forbidden_zones: list[dict[str, Any]] = Field(default_factory=list)
    dimensions: dict[str, Any] | None = None
    scale: dict[str, Any] | None = None
    export_config: dict[str, Any] | None = None
    authorization: dict[str, Any] | None = None


class TemplatePackageValidationIssue(BaseModel):
    severity: str = Field(pattern="^(error|warning)$")
    code: str
    message: str
    path: str | None = None


class TemplatePackageValidationResponse(BaseModel):
    accepted: bool
    template_id: str | None = None
    label: str | None = None
    source_class: str | None = None
    authorization: dict[str, Any] | None = None
    files_checked: list[str] = Field(default_factory=list)
    issues: list[TemplatePackageValidationIssue] = Field(default_factory=list)


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
    edit_intent: EditIntent | None = None
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
    openai_key_configured: bool
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


class BflSettingsUpdateRequest(BaseModel):
    api_key: str | None = None
    base_url: str = Field(default="https://api.bfl.ai", max_length=512)
    calls_enabled: bool = False
    daily_call_limit: int | None = Field(default=None, ge=0)
    default_provider: str = Field(default="disabled", max_length=80)
    max_estimated_cost_per_job: Decimal | None = None
    model: str = Field(default="flux-2-pro-preview", max_length=120)
    rate_limit_per_minute: int | None = Field(default=None, ge=0)
    result_path: str = Field(default="/v1/get_result", max_length=255)
    rollout_enabled: bool = False
    submit_path: str = Field(default="/v1/flux-2-pro-preview", max_length=255)


class BflSettingsResponse(BaseModel):
    api_key_configured: bool
    api_key_masked: str | None
    base_url: str
    calls_enabled: bool
    daily_call_limit: int | None
    default_provider: str
    max_estimated_cost_per_job: Decimal | None
    model: str
    rate_limit_per_minute: int | None
    restart_required: bool
    result_path: str
    rollout_enabled: bool
    submit_path: str
    submit_url: str


class OpenAISettingsUpdateRequest(BaseModel):
    api_key: str | None = None
    base_url: str = Field(default="https://api.openai.com/v1", max_length=512)
    calls_enabled: bool = False
    daily_call_limit: int | None = Field(default=None, ge=0)
    default_provider: str = Field(default="disabled", max_length=80)
    image_model: str = Field(default="gpt-image-2", max_length=120)
    image_path: str = Field(default="/images/generations", max_length=255)
    max_estimated_cost_per_job: Decimal | None = None
    parser_enabled: bool = False
    rate_limit_per_minute: int | None = Field(default=None, ge=0)
    responses_path: str = Field(default="/responses", max_length=255)
    rollout_enabled: bool = False
    text_model: str = Field(default="gpt-5.5", max_length=120)


class OpenAISettingsResponse(BaseModel):
    api_key_configured: bool
    api_key_masked: str | None
    base_url: str
    calls_enabled: bool
    daily_call_limit: int | None
    default_provider: str
    image_model: str
    image_path: str
    image_url: str
    max_estimated_cost_per_job: Decimal | None
    parser_enabled: bool
    rate_limit_per_minute: int | None
    responses_path: str
    restart_required: bool
    rollout_enabled: bool
    text_model: str


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
    preview_3d: Preview3DSpec | None = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def derive_preview_3d(self) -> DesignVersionResponse:
        if self.preview_3d is not None:
            return self
        candidate = self.parameters.get("preview_3d")
        if isinstance(candidate, dict):
            try:
                self.preview_3d = Preview3DSpec.model_validate(candidate)
            except ValueError:
                self.preview_3d = None
        return self


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
    content_url: str | None = None
    byte_size: int | None
    checksum_sha256: str | None
    metadata: dict[str, Any] = Field(default_factory=dict, validation_alias="metadata_json")
    preview_3d_screenshot: Preview3DScreenshotMetadata | None = None
    width: int | None
    height: int | None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def derive_preview_3d_screenshot(self) -> ArtifactResponse:
        if self.preview_3d_screenshot is not None:
            return self
        candidate = self.metadata.get("preview_3d_screenshot")
        if isinstance(candidate, dict):
            try:
                self.preview_3d_screenshot = Preview3DScreenshotMetadata.model_validate(candidate)
            except ValueError:
                self.preview_3d_screenshot = None
        return self


class Preview3DScreenshotCreateRequest(BaseModel):
    content_type: str = Field(min_length=1, max_length=80)
    filename: str = Field(default="preview-3d-screenshot.png", min_length=1, max_length=160)
    height: int = Field(gt=0, le=8192)
    image_base64: str = Field(min_length=1)
    preview_3d: Preview3DSpec
    width: int = Field(gt=0, le=8192)


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
    format: str = Field(min_length=1, max_length=64)
    artifact_id: UUID | None = None
    concept_label: str = Field(default="concept_preview", min_length=1, max_length=120)
    manifest: dict[str, Any] = Field(default_factory=dict)


class ProductionReadinessPreflightResponse(BaseModel):
    export: ExportResponse
    report: ProductionReadinessPreflightReport
