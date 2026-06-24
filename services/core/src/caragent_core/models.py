from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import Uuid

from caragent_core.enums import (
    ArtifactKind,
    AssetKind,
    DesignBriefStatus,
    DesignVersionStatus,
    ExportStatus,
    FeedbackApprovalState,
    JobEventType,
    JobStatus,
    MessageRole,
    ModelRunStatus,
    RightsStatus,
    WorkspaceStatus,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class IdMixin:
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


JsonObject = dict[str, Any]


class Workspace(IdMixin, TimestampMixin, Base):
    __tablename__ = "workspaces"

    owner_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(160), default="Untitled workspace", nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default=WorkspaceStatus.ACTIVE.value,
        nullable=False,
        index=True,
    )
    metadata_json: Mapped[JsonObject] = mapped_column("metadata", JSON, default=dict)


class Message(IdMixin, TimestampMixin, Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("workspace_id", "sequence", name="uq_messages_workspace_sequence"),
        Index("ix_messages_workspace_created", "workspace_id", "created_at"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(32), default=MessageRole.USER.value, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[JsonObject] = mapped_column("metadata", JSON, default=dict)


class DesignBrief(IdMixin, TimestampMixin, Base):
    __tablename__ = "design_briefs"
    __table_args__ = (Index("ix_design_briefs_workspace_created", "workspace_id", "created_at"),)

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_message_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        default=DesignBriefStatus.DRAFT.value,
        nullable=False,
    )
    payload: Mapped[JsonObject] = mapped_column(JSON, default=dict, nullable=False)


class Asset(IdMixin, TimestampMixin, Base):
    __tablename__ = "assets"
    __table_args__ = (Index("ix_assets_workspace_created", "workspace_id", "created_at"),)

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    kind: Mapped[str] = mapped_column(String(32), default=AssetKind.REFERENCE.value, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    thumbnail_object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    rights_status: Mapped[str] = mapped_column(
        String(32),
        default=RightsStatus.MISSING.value,
        nullable=False,
        index=True,
    )
    rights_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rights_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[JsonObject] = mapped_column("metadata", JSON, default=dict)


class GenerationJob(IdMixin, TimestampMixin, Base):
    __tablename__ = "generation_jobs"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "idempotency_key",
            name="uq_generation_jobs_workspace_idempotency",
        ),
        Index("ix_generation_jobs_workspace_status", "workspace_id", "status"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    brief_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("design_briefs.id", ondelete="SET NULL"),
    )
    idempotency_key: Mapped[str] = mapped_column(String(160), nullable=False)
    operation: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default=JobStatus.QUEUED.value,
        nullable=False,
        index=True,
    )
    requested_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    actual_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    latest_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    state_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    metadata_json: Mapped[JsonObject] = mapped_column("metadata", JSON, default=dict)


class JobDispatchOutbox(IdMixin, TimestampMixin, Base):
    __tablename__ = "job_dispatch_outbox"
    __table_args__ = (
        UniqueConstraint("job_id", "task_name", name="uq_job_dispatch_outbox_job_task"),
        Index("ix_job_dispatch_outbox_status_created", "status", "created_at"),
    )

    job_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("generation_jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_name: Mapped[str] = mapped_column(String(160), nullable=False)
    queue_name: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    task_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_json: Mapped[JsonObject] = mapped_column("metadata", JSON, default=dict)


class JobEvent(IdMixin, TimestampMixin, Base):
    __tablename__ = "job_events"
    __table_args__ = (
        UniqueConstraint("job_id", "sequence", name="uq_job_events_job_sequence"),
        Index("ix_job_events_job_created", "job_id", "created_at"),
    )

    job_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("generation_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(
        String(32),
        default=JobEventType.STATUS.value,
        nullable=False,
    )
    status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    progress: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    source: Mapped[str | None] = mapped_column(String(80), nullable=True)
    metadata_json: Mapped[JsonObject] = mapped_column("metadata", JSON, default=dict)


class DesignVersion(IdMixin, TimestampMixin, Base):
    __tablename__ = "design_versions"
    __table_args__ = (Index("ix_design_versions_workspace_created", "workspace_id", "created_at"),)

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_version_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("design_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("generation_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    brief_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("design_briefs.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default=DesignVersionStatus.DRAFT.value,
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    lineage_depth: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    parameters: Mapped[JsonObject] = mapped_column(JSON, default=dict)


class Artifact(IdMixin, TimestampMixin, Base):
    __tablename__ = "artifacts"
    __table_args__ = (Index("ix_artifacts_workspace_created", "workspace_id", "created_at"),)

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("generation_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    version_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("design_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    asset_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("assets.id", ondelete="SET NULL"),
        nullable=True,
    )
    kind: Mapped[str] = mapped_column(String(40), default=ArtifactKind.UPLOAD.value, nullable=False)
    object_key: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    byte_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[JsonObject] = mapped_column("metadata", JSON, default=dict)


class ModelRun(IdMixin, TimestampMixin, Base):
    __tablename__ = "model_runs"
    __table_args__ = (Index("ix_model_runs_job_created", "job_id", "created_at"),)

    job_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("generation_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    provider: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        default=ModelRunStatus.PLANNED.value,
        nullable=False,
    )
    parameters: Mapped[JsonObject] = mapped_column(JSON, default=dict)
    prompt_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt_payload: Mapped[JsonObject] = mapped_column(JSON, default=dict)
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    actual_cost: Mapped[Decimal | None] = mapped_column(Numeric(12, 4), nullable=True)
    input_artifact_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    output_artifact_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)


class Feedback(IdMixin, TimestampMixin, Base):
    __tablename__ = "feedback"
    __table_args__ = (Index("ix_feedback_workspace_created", "workspace_id", "created_at"),)

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("design_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    approval_state: Mapped[str] = mapped_column(
        String(32),
        default=FeedbackApprovalState.NONE.value,
        nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[JsonObject] = mapped_column("metadata", JSON, default=dict)


class ExportRecord(IdMixin, TimestampMixin, Base):
    __tablename__ = "exports"
    __table_args__ = (Index("ix_exports_workspace_created", "workspace_id", "created_at"),)

    workspace_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("design_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    artifact_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("artifacts.id", ondelete="SET NULL"),
        nullable=True,
    )
    format: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        default=ExportStatus.REQUESTED.value,
        nullable=False,
    )
    concept_label: Mapped[str] = mapped_column(
        String(80),
        default="concept_preview",
        nullable=False,
    )
    manifest: Mapped[JsonObject] = mapped_column(JSON, default=dict)
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


metadata = Base.metadata
