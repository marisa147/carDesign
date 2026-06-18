from __future__ import annotations

from enum import StrEnum


class WorkspaceStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class DesignBriefStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    ARCHIVED = "archived"


class AssetKind(StrEnum):
    REFERENCE = "reference"
    LOGO = "logo"
    CAR_PHOTO = "car_photo"
    INSPIRATION = "inspiration"


class RightsStatus(StrEnum):
    MISSING = "missing"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELED = "canceled"


class FailureCategory(StrEnum):
    PROVIDER = "provider"
    PROVIDER_CONFIGURATION = "provider_configuration"
    VALIDATION_RIGHTS = "validation_rights"
    STORAGE = "storage"
    QUEUE_WORKER = "queue_worker"
    CANCELED = "canceled"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class JobEventType(StrEnum):
    CREATED = "created"
    STATUS = "status"
    PROGRESS = "progress"
    ERROR = "error"
    COMPLETED = "completed"


class DesignVersionStatus(StrEnum):
    DRAFT = "draft"
    GENERATED = "generated"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPORTED = "exported"


class ArtifactKind(StrEnum):
    UPLOAD = "upload"
    MASK = "mask"
    THUMBNAIL = "thumbnail"
    GENERATED_IMAGE = "generated_image"
    PREVIEW = "preview"
    EXPORT = "export"


class ModelRunStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class FeedbackApprovalState(StrEnum):
    NONE = "none"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExportStatus(StrEnum):
    REQUESTED = "requested"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
