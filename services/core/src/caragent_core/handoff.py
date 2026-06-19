from __future__ import annotations

from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

HANDOFF_PACKAGE_SCHEMA_VERSION = 1
ENHANCED_HANDOFF_PACKAGE_TYPE = "enhanced_concept_handoff"
ENHANCED_HANDOFF_PACKAGE_FORMAT = "enhanced_concept_handoff_zip"
HANDOFF_CONCEPT_ONLY_DISCLAIMER = (
    "Concept handoff package for review only; not print-ready production artwork."
)

JsonObject = dict[str, object]


class HandoffBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HandoffPackageFile(HandoffBaseModel):
    kind: str = Field(min_length=1)
    path: str = Field(min_length=1)
    required: bool = True


class HandoffSourceArtifact(HandoffBaseModel):
    byte_size: int | None = Field(default=None, ge=0)
    checksum_sha256: str | None = None
    content_type: str = Field(min_length=1)
    height: int | None = Field(default=None, ge=1)
    id: UUID
    object_key: str = Field(min_length=1)
    width: int | None = Field(default=None, ge=1)


class HandoffPackageArtifact(HandoffBaseModel):
    byte_size: int | None = Field(default=None, ge=0)
    checksum_sha256: str | None = None
    content_type: str = Field(min_length=1)
    object_key: str = Field(min_length=1)


class HandoffPromptTrace(HandoffBaseModel):
    model_run_ids: list[str] = Field(default_factory=list)
    schema_version: int = Field(default=HANDOFF_PACKAGE_SCHEMA_VERSION, ge=1, le=1)
    summary: str | None = None


class HandoffProviderTrace(HandoffBaseModel):
    actual_cost: Decimal | None = None
    estimated_cost: Decimal | None = None
    model: str | None = None
    provider: str | None = None
    schema_version: int = Field(default=HANDOFF_PACKAGE_SCHEMA_VERSION, ge=1, le=1)
    status: str | None = None


class HandoffWarningReport(HandoffBaseModel):
    blocked: list[JsonObject] = Field(default_factory=list)
    items: list[JsonObject] = Field(default_factory=list)
    optional_missing: list[JsonObject] = Field(default_factory=list)
    schema_version: int = Field(default=HANDOFF_PACKAGE_SCHEMA_VERSION, ge=1, le=1)


class HandoffReferenceManifest(HandoffBaseModel):
    included_reference_asset_ids: list[str] = Field(default_factory=list)
    omitted_reference_asset_ids: list[str] = Field(default_factory=list)
    reference_roles: dict[str, list[str]] = Field(default_factory=dict)
    reference_warning_count: int = Field(default=0, ge=0)
    rights_snapshot: dict[str, JsonObject] = Field(default_factory=dict)
    schema_version: int = Field(default=HANDOFF_PACKAGE_SCHEMA_VERSION, ge=1, le=1)
    unsupported_reference_roles: list[str] = Field(default_factory=list)


class HandoffPackageManifest(HandoffBaseModel):
    brief_id: UUID | None = None
    disclaimer: str = HANDOFF_CONCEPT_ONLY_DISCLAIMER
    files: list[HandoffPackageFile] = Field(min_length=1)
    format: Literal["enhanced_concept_handoff_zip"]
    package_artifact: HandoffPackageArtifact
    package_type: Literal["enhanced_concept_handoff"]
    parent_version_id: UUID | None = None
    preview_3d: JsonObject = Field(default_factory=dict)
    preview_spec: JsonObject = Field(default_factory=dict)
    prompt_trace: HandoffPromptTrace
    provider_trace: HandoffProviderTrace
    references: HandoffReferenceManifest
    review_notes: list[str] = Field(default_factory=list)
    schema_version: int = Field(default=HANDOFF_PACKAGE_SCHEMA_VERSION, ge=1, le=1)
    source_artifact: HandoffSourceArtifact
    template: JsonObject = Field(default_factory=dict)
    version_id: UUID
    warnings: HandoffWarningReport
    workspace_id: UUID


__all__ = [
    "ENHANCED_HANDOFF_PACKAGE_FORMAT",
    "ENHANCED_HANDOFF_PACKAGE_TYPE",
    "HANDOFF_CONCEPT_ONLY_DISCLAIMER",
    "HANDOFF_PACKAGE_SCHEMA_VERSION",
    "HandoffPackageArtifact",
    "HandoffPackageFile",
    "HandoffPackageManifest",
    "HandoffPromptTrace",
    "HandoffProviderTrace",
    "HandoffReferenceManifest",
    "HandoffSourceArtifact",
    "HandoffWarningReport",
]
