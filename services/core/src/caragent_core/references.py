from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from caragent_core.enums import ReferenceRole


class ReferenceAssignment(BaseModel):
    asset_id: UUID
    enabled: bool = True
    role: ReferenceRole
    schema_version: int = Field(default=1, ge=1, le=1)


class ReferenceRightsSnapshot(BaseModel):
    asset_id: UUID
    checksum_sha256: str | None = None
    content_type: str
    object_key: str
    original_filename: str
    rights_confirmed_at: datetime | None = None
    rights_notes: str | None = None
    rights_status: str
    schema_version: int = Field(default=1, ge=1, le=1)
    source_label: str | None = None
    source_url: str | None = None


class ReferenceUsageItem(BaseModel):
    asset_id: UUID
    enabled: bool = True
    rights: ReferenceRightsSnapshot | None = None
    role: ReferenceRole
    schema_version: int = Field(default=1, ge=1, le=1)


class ReferenceUsageSnapshot(BaseModel):
    items: list[ReferenceUsageItem] = Field(default_factory=list)
    schema_version: int = Field(default=1, ge=1, le=1)


__all__ = [
    "ReferenceAssignment",
    "ReferenceRightsSnapshot",
    "ReferenceRole",
    "ReferenceUsageItem",
    "ReferenceUsageSnapshot",
]
