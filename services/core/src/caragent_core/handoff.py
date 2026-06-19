from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
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
FORBIDDEN_HANDOFF_MARKERS = (
    "api_key",
    "secret",
    "image_base64",
    "image_bytes",
    "binary",
)
_LOCAL_PATH_PATTERN = re.compile(r"[A-Za-z]:\\[^\s,)\]}]+")

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


class HandoffSafeZoneReport(HandoffBaseModel):
    safe_zones: list[JsonObject] = Field(default_factory=list)
    schema_version: int = Field(default=HANDOFF_PACKAGE_SCHEMA_VERSION, ge=1, le=1)
    template: JsonObject = Field(default_factory=dict)


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


def build_handoff_warning_report(
    *,
    preview_spec: Mapping[str, object] | None = None,
    preview_3d: Mapping[str, object] | None = None,
    preview_3d_screenshot: Mapping[str, object] | None = None,
) -> HandoffWarningReport:
    items: list[JsonObject] = []
    optional_missing: list[JsonObject] = []

    _append_warning_items(items, _mapping_list(preview_spec, "warnings"), source="preview_spec")
    _append_warning_items(items, _mapping_list(preview_3d, "warnings"), source="preview_3d")

    screenshot_warning_ids = _mapping_list(preview_3d_screenshot, "warning_ids")
    if screenshot_warning_ids:
        for warning_id in screenshot_warning_ids:
            _append_warning_item(
                items,
                {
                    "id": str(warning_id),
                    "message": f"Preview 3D screenshot carries warning id {warning_id}.",
                    "severity": "warning",
                    "source": "preview_3d_screenshot",
                },
            )
    else:
        optional_missing.append(
            {
                "id": "preview_3d_screenshot",
                "message": "No preview 3D screenshot warning metadata was available.",
                "severity": "info",
            },
        )

    return HandoffWarningReport(items=items, optional_missing=optional_missing)


def build_handoff_safe_zone_report(
    preview_spec: Mapping[str, object] | None,
) -> HandoffSafeZoneReport:
    template: JsonObject = {}
    safe_zones: list[JsonObject] = []
    if preview_spec is not None:
        template = _json_object(preview_spec.get("template"))
        safe_zones = [_json_object(item) for item in _mapping_list(preview_spec, "safe_zones")]
    return HandoffSafeZoneReport(template=template, safe_zones=safe_zones)


def build_handoff_reference_manifest(
    parameters: Mapping[str, object],
) -> HandoffReferenceManifest:
    rights_snapshot = {
        str(asset_id): _json_object(snapshot)
        for asset_id, snapshot in _mapping_value(parameters.get("rights_snapshot")).items()
    }
    reference_roles: dict[str, list[str]] = {
        str(role): [str(asset_id) for asset_id in _sequence_value(asset_ids)]
        for role, asset_ids in _mapping_value(parameters.get("reference_roles")).items()
    }
    return HandoffReferenceManifest(
        included_reference_asset_ids=[
            str(asset_id)
            for asset_id in _sequence_value(parameters.get("included_reference_asset_ids"))
        ],
        omitted_reference_asset_ids=[
            str(asset_id)
            for asset_id in _sequence_value(parameters.get("omitted_reference_asset_ids"))
        ],
        reference_roles=reference_roles,
        reference_warning_count=_int_value(parameters.get("reference_warning_count")),
        rights_snapshot=rights_snapshot,
        unsupported_reference_roles=[
            str(role)
            for role in _sequence_value(parameters.get("unsupported_reference_roles"))
        ],
    )


def render_handoff_notes_markdown(
    *,
    references: HandoffReferenceManifest | Mapping[str, object] | None = None,
    review_notes: Sequence[str] = (),
    safe_zones: Sequence[Mapping[str, object]] = (),
    template: Mapping[str, object] | None = None,
    warnings: HandoffWarningReport | Mapping[str, object] | None = None,
) -> str:
    safe_zone_report = HandoffSafeZoneReport(
        safe_zones=[_json_object(item) for item in safe_zones],
        template=_json_object(template),
    )
    reference_manifest = _reference_manifest(references)
    warning_report = _warning_report(warnings)

    lines = [
        "# Concept Handoff Notes",
        "",
        HANDOFF_CONCEPT_ONLY_DISCLAIMER,
        "",
        "## Template",
    ]
    lines.extend(_markdown_key_values(safe_zone_report.template, fallback="- Not specified."))
    lines.extend(["", "## Safe Zones"])
    lines.extend(_markdown_records(safe_zone_report.safe_zones, empty="- No safe zones recorded."))
    lines.extend(["", "## References"])
    lines.append(
        "- Included: "
        + (
            ", ".join(reference_manifest.included_reference_asset_ids)
            if reference_manifest.included_reference_asset_ids
            else "none"
        ),
    )
    lines.append(
        "- Omitted: "
        + (
            ", ".join(reference_manifest.omitted_reference_asset_ids)
            if reference_manifest.omitted_reference_asset_ids
            else "none"
        ),
    )
    lines.append(f"- Warning count: {reference_manifest.reference_warning_count}")
    lines.extend(["", "## Warning Summary"])
    lines.append(f"- Warning items: {len(warning_report.items)}")
    lines.append(f"- Optional missing: {len(warning_report.optional_missing)}")
    lines.extend(["", "## Review Notes"])
    if review_notes:
        lines.extend(f"- {_sanitize_text(note)}" for note in review_notes)
    else:
        lines.append("- None.")
    return _join_markdown(lines)


def render_handoff_warnings_markdown(
    warnings: HandoffWarningReport | Mapping[str, object],
) -> str:
    warning_report = _warning_report(warnings)
    lines = ["# Warning Report", "", HANDOFF_CONCEPT_ONLY_DISCLAIMER, "", "## Items"]
    lines.extend(_markdown_records(warning_report.items, empty="- No warning items recorded."))
    lines.extend(["", "## Blocked"])
    lines.extend(_markdown_records(warning_report.blocked, empty="- None."))
    lines.extend(["", "## Optional Missing"])
    lines.extend(_markdown_records(warning_report.optional_missing, empty="- None."))
    return _join_markdown(lines)


def render_handoff_prompt_trace_markdown(
    *,
    model_runs: Sequence[object] = (),
    prompt_trace: HandoffPromptTrace | Mapping[str, object] | None = None,
    provider_trace: HandoffProviderTrace | Mapping[str, object] | None = None,
) -> str:
    lines = ["# Prompt Trace", "", HANDOFF_CONCEPT_ONLY_DISCLAIMER]
    if prompt_trace is not None:
        trace = _prompt_trace(prompt_trace)
        lines.extend(["", "## Summary"])
        if trace.summary:
            lines.append(f"- {_sanitize_text(trace.summary)}")
        lines.append(
            "- Model runs: "
            + (", ".join(trace.model_run_ids) if trace.model_run_ids else "none"),
        )
    if provider_trace is not None:
        trace = _provider_trace(provider_trace)
        lines.extend(["", "## Provider"])
        lines.extend(
            _markdown_key_values(
                trace.model_dump(mode="json", exclude_none=True),
                fallback="- Not specified.",
            ),
        )
    if model_runs:
        lines.extend(["", "## Model Runs"])
        for model_run in model_runs:
            lines.extend(_markdown_model_run(model_run))
    return _join_markdown(lines)


def render_handoff_references_json(
    references: HandoffReferenceManifest | Mapping[str, object],
) -> str:
    manifest = _reference_manifest(references)
    return json.dumps(manifest.model_dump(mode="json"), indent=2, sort_keys=True)


def _append_warning_items(
    items: list[JsonObject],
    warnings: Sequence[object],
    *,
    source: str,
) -> None:
    for warning in warnings:
        if isinstance(warning, Mapping):
            item = _json_object(warning)
            item.setdefault("source", source)
            _append_warning_item(items, item)
        else:
            text = _sanitize_text(str(warning))
            _append_warning_item(
                items,
                {
                    "id": text,
                    "message": text,
                    "severity": "warning",
                    "source": source,
                },
            )


def _append_warning_item(items: list[JsonObject], item: Mapping[str, object]) -> None:
    warning_id = str(item.get("id") or item.get("message") or "").strip()
    if not warning_id:
        return
    for existing in items:
        if existing.get("id") == warning_id:
            return
    sanitized = _json_object(item)
    sanitized.setdefault("id", warning_id)
    sanitized.setdefault("severity", "warning")
    items.append(sanitized)


def _mapping_list(
    mapping: Mapping[str, object] | None,
    key: str,
) -> list[object]:
    if mapping is None:
        return []
    return list(_sequence_value(mapping.get(key)))


def _sequence_value(value: object) -> Sequence[object]:
    if isinstance(value, str) or value is None:
        return []
    if isinstance(value, Sequence):
        return value
    return []


def _mapping_value(value: object) -> Mapping[str, object]:
    if isinstance(value, Mapping):
        return value
    return {}


def _json_object(value: object) -> JsonObject:
    if not isinstance(value, Mapping):
        return {}
    return {
        str(key): sanitized
        for key, item in value.items()
        if not _is_forbidden_text(str(key))
        for sanitized in [_json_safe_value(item)]
    }


def _json_safe_value(value: object) -> object:
    if isinstance(value, Mapping):
        return _json_object(value)
    if isinstance(value, Sequence) and not isinstance(value, str):
        return [_json_safe_value(item) for item in value]
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, str):
        return _sanitize_text(value)
    return value


def _sanitize_text(value: str) -> str:
    sanitized = _LOCAL_PATH_PATTERN.sub("[local-path]", value)
    if _is_forbidden_text(sanitized):
        return "[redacted]"
    return sanitized.replace("\r", " ").replace("\n", " ").strip()


def _is_forbidden_text(value: str) -> bool:
    lower = value.lower()
    return any(marker in lower for marker in FORBIDDEN_HANDOFF_MARKERS) or ":\\" in lower


def _int_value(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return max(value, 0)
    return 0


def _warning_report(
    warnings: HandoffWarningReport | Mapping[str, object] | None,
) -> HandoffWarningReport:
    if isinstance(warnings, HandoffWarningReport):
        return warnings
    if isinstance(warnings, Mapping):
        return HandoffWarningReport.model_validate(_json_object(warnings))
    return HandoffWarningReport()


def _reference_manifest(
    references: HandoffReferenceManifest | Mapping[str, object] | None,
) -> HandoffReferenceManifest:
    if isinstance(references, HandoffReferenceManifest):
        return references
    if isinstance(references, Mapping):
        return HandoffReferenceManifest.model_validate(_json_object(references))
    return HandoffReferenceManifest()


def _prompt_trace(
    prompt_trace: HandoffPromptTrace | Mapping[str, object],
) -> HandoffPromptTrace:
    if isinstance(prompt_trace, HandoffPromptTrace):
        return prompt_trace
    return HandoffPromptTrace.model_validate(_json_object(prompt_trace))


def _provider_trace(
    provider_trace: HandoffProviderTrace | Mapping[str, object],
) -> HandoffProviderTrace:
    if isinstance(provider_trace, HandoffProviderTrace):
        return provider_trace
    return HandoffProviderTrace.model_validate(_json_object(provider_trace))


def _markdown_model_run(model_run: object) -> list[str]:
    record = {
        "id": str(getattr(model_run, "id", "")),
        "provider": getattr(model_run, "provider", None),
        "model": getattr(model_run, "model", None),
        "status": getattr(model_run, "status", None),
        "estimated_cost": getattr(model_run, "estimated_cost", None),
        "actual_cost": getattr(model_run, "actual_cost", None),
        "input_artifact_ids": getattr(model_run, "input_artifact_ids", None),
        "output_artifact_id": str(getattr(model_run, "output_artifact_id", "") or ""),
        "prompt_text": getattr(model_run, "prompt_text", None),
    }
    lines = [f"- Model run: {_sanitize_text(record['id'])}"]
    for key, value in record.items():
        if key == "id" or value in (None, "", []):
            continue
        lines.append(f"  - {key}: {_format_markdown_value(value)}")
    return lines


def _markdown_key_values(
    record: Mapping[str, object],
    *,
    fallback: str,
) -> list[str]:
    lines = [
        f"- {key}: {_format_markdown_value(value)}"
        for key, value in record.items()
        if not _is_forbidden_text(str(key))
    ]
    return lines or [fallback]


def _markdown_records(records: Sequence[Mapping[str, object]], *, empty: str) -> list[str]:
    if not records:
        return [empty]
    lines: list[str] = []
    for record in records:
        item = _json_object(record)
        label = item.get("id") or item.get("label") or item.get("message") or "item"
        lines.append(f"- {_format_markdown_value(label)}")
        for key, value in item.items():
            if key == "id":
                continue
            lines.append(f"  - {key}: {_format_markdown_value(value)}")
    return lines


def _format_markdown_value(value: object) -> str:
    safe = _json_safe_value(value)
    if isinstance(safe, list):
        return ", ".join(_format_markdown_value(item) for item in safe) or "none"
    if isinstance(safe, Mapping):
        return json.dumps(safe, sort_keys=True)
    return _sanitize_text(str(safe))


def _join_markdown(lines: Sequence[str]) -> str:
    return "\n".join(lines).strip() + "\n"


__all__ = [
    "ENHANCED_HANDOFF_PACKAGE_FORMAT",
    "ENHANCED_HANDOFF_PACKAGE_TYPE",
    "HANDOFF_CONCEPT_ONLY_DISCLAIMER",
    "HANDOFF_PACKAGE_SCHEMA_VERSION",
    "HandoffSafeZoneReport",
    "HandoffPackageArtifact",
    "HandoffPackageFile",
    "HandoffPackageManifest",
    "HandoffPromptTrace",
    "HandoffProviderTrace",
    "HandoffReferenceManifest",
    "HandoffSourceArtifact",
    "HandoffWarningReport",
    "build_handoff_reference_manifest",
    "build_handoff_safe_zone_report",
    "build_handoff_warning_report",
    "render_handoff_notes_markdown",
    "render_handoff_prompt_trace_markdown",
    "render_handoff_references_json",
    "render_handoff_warnings_markdown",
]
