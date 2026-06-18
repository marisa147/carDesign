from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from caragent_core.enums import ReferenceRole

REFERENCE_SCHEMA_VERSION = 1
DEFAULT_LEGACY_REFERENCE_ROLE = ReferenceRole.INSPIRATION
BFL_REFERENCE_UNSUPPORTED_PROVIDERS = {"bfl", "black-forest-labs"}
REFERENCE_TRACE_METADATA_KEYS = (
    "included_reference_asset_ids",
    "omitted_reference_asset_ids",
    "reference_roles",
    "reference_usage",
    "reference_warning_count",
    "rights_snapshot",
    "unsupported_reference_roles",
)


class ReferenceAssignment(BaseModel):
    asset_id: UUID
    enabled: bool = True
    role: ReferenceRole
    schema_version: int = Field(default=REFERENCE_SCHEMA_VERSION, ge=1, le=1)


class ReferenceRightsSnapshot(BaseModel):
    asset_id: UUID
    checksum_sha256: str | None = None
    content_type: str
    object_key: str
    original_filename: str
    rights_confirmed_at: datetime | None = None
    rights_notes: str | None = None
    rights_status: str
    schema_version: int = Field(default=REFERENCE_SCHEMA_VERSION, ge=1, le=1)
    source_label: str | None = None
    source_url: str | None = None


class ReferenceUsageItem(BaseModel):
    asset_id: UUID
    enabled: bool = True
    rights: ReferenceRightsSnapshot | None = None
    role: ReferenceRole
    schema_version: int = Field(default=REFERENCE_SCHEMA_VERSION, ge=1, le=1)


class ReferenceUsageSnapshot(BaseModel):
    items: list[ReferenceUsageItem] = Field(default_factory=list)
    schema_version: int = Field(default=REFERENCE_SCHEMA_VERSION, ge=1, le=1)


class ReferenceWarning(BaseModel):
    asset_id: UUID
    reason: Literal["disabled", "unsupported_by_provider"]
    role: ReferenceRole


class ReferenceUsagePlan(BaseModel):
    included_reference_asset_ids: list[str] = Field(default_factory=list)
    omitted_reference_asset_ids: list[str] = Field(default_factory=list)
    reference_usage: dict[str, object] = Field(default_factory=dict)
    reference_warning_count: int = 0
    reference_warnings: list[ReferenceWarning] = Field(default_factory=list)
    unsupported_reference_roles: list[ReferenceRole] = Field(default_factory=list)

    def prompt_payload_fields(self) -> dict[str, object]:
        dumped = self.model_dump(mode="json")
        return {
            "included_reference_asset_ids": dumped["included_reference_asset_ids"],
            "omitted_reference_asset_ids": dumped["omitted_reference_asset_ids"],
            "reference_usage": dumped["reference_usage"],
            "reference_warning_count": dumped["reference_warning_count"],
            "reference_warnings": dumped["reference_warnings"],
            "unsupported_reference_roles": dumped["unsupported_reference_roles"],
        }

    def warning_metadata(self) -> dict[str, object]:
        dumped = self.model_dump(mode="json")
        return {
            "included_reference_asset_ids": dumped["included_reference_asset_ids"],
            "omitted_reference_asset_ids": dumped["omitted_reference_asset_ids"],
            "reference_warning_count": dumped["reference_warning_count"],
            "reference_warnings": dumped["reference_warnings"],
            "unsupported_reference_roles": dumped["unsupported_reference_roles"],
        }


def normalize_reference_assignments(
    *,
    reference_asset_ids: list[str],
    reference_usage: list[ReferenceAssignment],
) -> list[ReferenceAssignment]:
    normalized: list[ReferenceAssignment] = []
    seen: set[tuple[str, ReferenceRole]] = set()

    for assignment in reference_usage:
        _append_unique_assignment(normalized, seen, assignment)

    for asset_id in reference_asset_ids:
        _append_unique_assignment(
            normalized,
            seen,
            ReferenceAssignment(
                asset_id=UUID(str(asset_id)),
                enabled=True,
                role=DEFAULT_LEGACY_REFERENCE_ROLE,
            ),
        )

    return normalized


def plan_reference_usage(
    *,
    provider: str,
    reference_asset_ids: list[str],
    reference_usage: list[ReferenceAssignment],
) -> ReferenceUsagePlan:
    requested = normalize_reference_assignments(
        reference_asset_ids=reference_asset_ids,
        reference_usage=reference_usage,
    )
    unsupported_roles = _unsupported_roles_for_provider(provider)
    included_ids: list[str] = []
    omitted_ids: list[str] = []
    warnings: list[ReferenceWarning] = []
    unsupported_warning_roles: list[ReferenceRole] = []

    for assignment in requested:
        asset_id = str(assignment.asset_id)
        if not assignment.enabled:
            _append_unique_value(omitted_ids, asset_id)
            warnings.append(
                ReferenceWarning(
                    asset_id=assignment.asset_id,
                    reason="disabled",
                    role=assignment.role,
                ),
            )
            continue

        if assignment.role in unsupported_roles:
            _append_unique_value(omitted_ids, asset_id)
            _append_unique_value(unsupported_warning_roles, assignment.role)
            warnings.append(
                ReferenceWarning(
                    asset_id=assignment.asset_id,
                    reason="unsupported_by_provider",
                    role=assignment.role,
                ),
            )
            continue

        _append_unique_value(included_ids, asset_id)

    return ReferenceUsagePlan(
        included_reference_asset_ids=included_ids,
        omitted_reference_asset_ids=omitted_ids,
        reference_usage={
            "requested": [assignment.model_dump(mode="json") for assignment in requested],
            "schema_version": REFERENCE_SCHEMA_VERSION,
        },
        reference_warning_count=len(warnings),
        reference_warnings=warnings,
        unsupported_reference_roles=unsupported_warning_roles,
    )


def build_reference_trace_metadata(
    snapshot: ReferenceUsageSnapshot,
    *,
    included_reference_asset_ids: list[str],
    omitted_reference_asset_ids: list[str],
    reference_warning_count: int,
    unsupported_reference_roles: list[str],
) -> dict[str, object]:
    dumped_snapshot = snapshot.model_dump(mode="json")
    return {
        "included_reference_asset_ids": list(included_reference_asset_ids),
        "omitted_reference_asset_ids": list(omitted_reference_asset_ids),
        "reference_roles": _reference_roles(dumped_snapshot["items"]),
        "reference_usage": dumped_snapshot,
        "reference_warning_count": reference_warning_count,
        "rights_snapshot": _rights_snapshot(dumped_snapshot["items"]),
        "unsupported_reference_roles": list(unsupported_reference_roles),
    }


def _append_unique_assignment(
    assignments: list[ReferenceAssignment],
    seen: set[tuple[str, ReferenceRole]],
    assignment: ReferenceAssignment,
) -> None:
    key = (str(assignment.asset_id), assignment.role)
    if key in seen:
        return
    seen.add(key)
    assignments.append(assignment)


def _append_unique_value[T](values: list[T], value: T) -> None:
    if value not in values:
        values.append(value)


def _unsupported_roles_for_provider(provider: str) -> set[ReferenceRole]:
    if provider.strip().lower() in BFL_REFERENCE_UNSUPPORTED_PROVIDERS:
        return set(ReferenceRole)
    return set()


def _reference_roles(items: list[object]) -> dict[str, list[str]]:
    roles: dict[str, list[str]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("enabled") is False:
            continue
        role = str(item.get("role") or "").strip()
        asset_id = str(item.get("asset_id") or "").strip()
        if not role or not asset_id:
            continue
        roles.setdefault(role, [])
        if asset_id not in roles[role]:
            roles[role].append(asset_id)
    return roles


def _rights_snapshot(items: list[object]) -> dict[str, object]:
    snapshots: dict[str, object] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        asset_id = str(item.get("asset_id") or "").strip()
        rights = item.get("rights")
        if asset_id and isinstance(rights, dict):
            snapshots[asset_id] = dict(rights)
    return snapshots


__all__ = [
    "REFERENCE_TRACE_METADATA_KEYS",
    "ReferenceAssignment",
    "ReferenceUsagePlan",
    "ReferenceRightsSnapshot",
    "ReferenceRole",
    "ReferenceUsageItem",
    "ReferenceUsageSnapshot",
    "ReferenceWarning",
    "build_reference_trace_metadata",
    "plan_reference_usage",
    "normalize_reference_assignments",
]
