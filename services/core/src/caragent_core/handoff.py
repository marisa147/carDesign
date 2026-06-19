from __future__ import annotations

import json
import re
import zipfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from io import BytesIO
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from caragent_core.storage import ObjectStorage

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


class HandoffPackageBuildError(ValueError):
    pass


@dataclass(frozen=True)
class HandoffPackageZipResult:
    byte_size: int
    checksum_sha256: str
    content: bytes
    content_type: str
    files: list[HandoffPackageFile]
    manifest: HandoffPackageManifest


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


def validate_handoff_rights_source(parameters: Mapping[str, object]) -> None:
    included_reference_asset_ids = [
        str(asset_id).strip()
        for asset_id in _sequence_value(parameters.get("included_reference_asset_ids"))
        if str(asset_id).strip()
    ]
    if not included_reference_asset_ids:
        return

    rights_snapshot = _mapping_value(parameters.get("rights_snapshot"))
    blocked_asset_ids: list[str] = []
    for asset_id in included_reference_asset_ids:
        snapshot = _mapping_value(rights_snapshot.get(asset_id))
        rights_status = str(snapshot.get("rights_status") or "").strip().lower()
        source_label = str(snapshot.get("source_label") or "").strip()
        source_url = str(snapshot.get("source_url") or "").strip()
        if rights_status != "confirmed" or not (source_label or source_url):
            blocked_asset_ids.append(asset_id)

    if blocked_asset_ids:
        raise HandoffPackageBuildError(
            "Missing required rights/source metadata for included references: "
            + ", ".join(blocked_asset_ids),
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


async def build_handoff_package_zip(
    *,
    package_object_key: str,
    source_artifact: object,
    storage: ObjectStorage,
    version: object,
    model_runs: Sequence[object] = (),
    review_notes: Sequence[str] = (),
    screenshot_artifacts: Sequence[object] = (),
) -> HandoffPackageZipResult:
    parameters = _mapping_value(getattr(version, "parameters", None))
    validate_handoff_rights_source(parameters)
    preview_spec = _mapping_value(parameters.get("preview_spec"))
    preview_3d = _mapping_value(parameters.get("preview_3d"))
    warning_report = build_handoff_warning_report(
        preview_3d=preview_3d,
        preview_3d_screenshot={"warning_ids": _screenshot_warning_ids(screenshot_artifacts)}
        if screenshot_artifacts
        else None,
        preview_spec=preview_spec,
    )
    references = build_handoff_reference_manifest(parameters)

    source_object_key = _artifact_object_key(source_artifact)
    source_object = await _read_required_object(
        storage,
        source_object_key,
        "source concept image",
    )
    concept_path = (
        f"images/concept{_artifact_extension(source_artifact, source_object.content_type)}"
    )

    binary_members: list[tuple[str, bytes, str]] = [
        (concept_path, source_object.content, "concept_image"),
    ]
    for screenshot in screenshot_artifacts:
        screenshot_object_key = _artifact_object_key(screenshot)
        screenshot_path = (
            f"screenshots/{_artifact_id(screenshot)}"
            f"{_artifact_extension(screenshot, 'image/png')}"
        )
        try:
            screenshot_object = await storage.get_object(screenshot_object_key)
        except FileNotFoundError:
            _append_warning_item(
                warning_report.items,
                {
                    "artifact_id": _artifact_id(screenshot),
                    "id": "preview_3d_screenshot_missing_object",
                    "message": (
                        "Preview 3D screenshot metadata exists, but the optional "
                        "screenshot bytes could not be read from object storage."
                    ),
                    "severity": "warning",
                    "source": "package_builder",
                },
            )
            continue
        binary_members.append((screenshot_path, screenshot_object.content, "screenshot"))

    files = [
        HandoffPackageFile(kind="manifest", path="manifest.json"),
        HandoffPackageFile(kind="notes", path="handoff-notes.md"),
        HandoffPackageFile(kind="warnings", path="warnings.md"),
        HandoffPackageFile(kind="prompt_trace", path="prompt-trace.md"),
        HandoffPackageFile(kind="references", path="references.json"),
        HandoffPackageFile(kind="concept_image", path=concept_path),
        *[
            HandoffPackageFile(kind=kind, path=path, required=False)
            for path, _content, kind in binary_members
            if kind == "screenshot"
        ],
    ]
    safe_zone_report = build_handoff_safe_zone_report(preview_spec)
    prompt_trace = HandoffPromptTrace(
        model_run_ids=[_model_run_id(model_run) for model_run in model_runs],
        summary=_prompt_summary(model_runs),
    )
    provider_trace = _provider_trace_from_model_runs(model_runs)
    manifest = HandoffPackageManifest(
        brief_id=getattr(version, "brief_id", None),
        files=files,
        format=ENHANCED_HANDOFF_PACKAGE_FORMAT,
        package_artifact=HandoffPackageArtifact(
            content_type="application/zip",
            object_key=package_object_key,
        ),
        package_type=ENHANCED_HANDOFF_PACKAGE_TYPE,
        parent_version_id=getattr(version, "parent_version_id", None),
        preview_3d=_json_object(preview_3d),
        preview_spec=_json_object(preview_spec),
        prompt_trace=prompt_trace,
        provider_trace=provider_trace,
        references=references,
        review_notes=[_sanitize_text(note) for note in review_notes],
        source_artifact=HandoffSourceArtifact(
            byte_size=len(source_object.content),
            checksum_sha256=getattr(source_artifact, "checksum_sha256", None),
            content_type=(
                getattr(source_artifact, "content_type", None)
                or source_object.content_type
            ),
            height=getattr(source_artifact, "height", None),
            id=UUID(_artifact_id(source_artifact)),
            object_key=source_object_key,
            width=getattr(source_artifact, "width", None),
        ),
        template=safe_zone_report.template,
        version_id=version.id,
        warnings=warning_report,
        workspace_id=version.workspace_id,
    )

    text_members = {
        "manifest.json": json.dumps(
            manifest.model_dump(mode="json"),
            indent=2,
            sort_keys=True,
        ),
        "handoff-notes.md": render_handoff_notes_markdown(
            references=references,
            review_notes=review_notes,
            safe_zones=safe_zone_report.safe_zones,
            template=safe_zone_report.template,
            warnings=warning_report,
        ),
        "warnings.md": render_handoff_warnings_markdown(warning_report),
        "prompt-trace.md": render_handoff_prompt_trace_markdown(
            model_runs=model_runs,
            prompt_trace=prompt_trace,
            provider_trace=provider_trace,
        ),
        "references.json": render_handoff_references_json(references),
    }

    content = _write_zip_members(text_members=text_members, binary_members=binary_members)
    checksum = sha256(content).hexdigest()
    return HandoffPackageZipResult(
        byte_size=len(content),
        checksum_sha256=checksum,
        content=content,
        content_type="application/zip",
        files=files,
        manifest=manifest,
    )


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


async def _read_required_object(
    storage: ObjectStorage,
    key: str,
    label: str,
) -> object:
    try:
        return await storage.get_object(key)
    except FileNotFoundError as error:
        raise HandoffPackageBuildError(f"Missing required {label}: {key}") from error


def _artifact_id(artifact: object) -> str:
    value = getattr(artifact, "id", None)
    if value is None:
        raise HandoffPackageBuildError("Artifact id is required")
    return str(value)


def _artifact_object_key(artifact: object) -> str:
    value = getattr(artifact, "object_key", None)
    if not isinstance(value, str) or not value.strip():
        raise HandoffPackageBuildError("Artifact object_key is required")
    return value.strip()


def _artifact_extension(artifact: object, stored_content_type: str | None) -> str:
    content_type = (
        str(getattr(artifact, "content_type", "") or stored_content_type or "")
        .strip()
        .lower()
    )
    content_type_extensions = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    if content_type in content_type_extensions:
        return content_type_extensions[content_type]

    object_key = _artifact_object_key(artifact).lower()
    for extension in (".png", ".jpg", ".jpeg", ".webp"):
        if object_key.endswith(extension):
            return ".jpg" if extension == ".jpeg" else extension
    return ".png"


def _screenshot_warning_ids(screenshot_artifacts: Sequence[object]) -> list[str]:
    warning_ids: list[str] = []
    for screenshot in screenshot_artifacts:
        metadata = _mapping_value(getattr(screenshot, "metadata_json", None))
        screenshot_metadata = _mapping_value(metadata.get("preview_3d_screenshot"))
        for warning_id in _sequence_value(screenshot_metadata.get("warning_ids")):
            warning_text = str(warning_id)
            if warning_text not in warning_ids:
                warning_ids.append(warning_text)
    return warning_ids


def _model_run_id(model_run: object) -> str:
    value = getattr(model_run, "id", None)
    return str(value) if value is not None else "unknown"


def _prompt_summary(model_runs: Sequence[object]) -> str | None:
    for model_run in model_runs:
        prompt_text = getattr(model_run, "prompt_text", None)
        if isinstance(prompt_text, str) and prompt_text.strip():
            return _sanitize_text(prompt_text[:240])
    return None


def _provider_trace_from_model_runs(
    model_runs: Sequence[object],
) -> HandoffProviderTrace:
    if not model_runs:
        return HandoffProviderTrace()
    model_run = model_runs[-1]
    return HandoffProviderTrace(
        actual_cost=getattr(model_run, "actual_cost", None),
        estimated_cost=getattr(model_run, "estimated_cost", None),
        model=getattr(model_run, "model", None),
        provider=getattr(model_run, "provider", None),
        status=getattr(model_run, "status", None),
    )


def _write_zip_members(
    *,
    text_members: Mapping[str, str],
    binary_members: Sequence[tuple[str, bytes, str]],
) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in [
            "manifest.json",
            "handoff-notes.md",
            "warnings.md",
            "prompt-trace.md",
            "references.json",
        ]:
            archive.writestr(path, text_members[path].encode("utf-8"))
        for path, content, _kind in binary_members:
            archive.writestr(path, content)
    return buffer.getvalue()


__all__ = [
    "ENHANCED_HANDOFF_PACKAGE_FORMAT",
    "ENHANCED_HANDOFF_PACKAGE_TYPE",
    "HANDOFF_CONCEPT_ONLY_DISCLAIMER",
    "HANDOFF_PACKAGE_SCHEMA_VERSION",
    "HandoffPackageBuildError",
    "HandoffPackageZipResult",
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
    "build_handoff_package_zip",
    "build_handoff_warning_report",
    "render_handoff_notes_markdown",
    "render_handoff_prompt_trace_markdown",
    "render_handoff_references_json",
    "render_handoff_warnings_markdown",
    "validate_handoff_rights_source",
]
