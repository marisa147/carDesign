from __future__ import annotations

from collections.abc import Mapping
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from caragent_core.generation.templates import SUPPORTED_TEMPLATE_ID, SUPPORTED_VIEW

PREVIEW_3D_SCHEMA_VERSION = 1
GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL_ID = "generic-side-coupe-lightweight-v1"
DEFAULT_PREVIEW_3D_CAMERA_PRESET_ID = "front-left-default"
SIDE_DECAL_MATERIAL_SLOT = "side-decal-plane"


class Preview3DVector3(BaseModel):
    model_config = ConfigDict(extra="forbid")

    x: float
    y: float
    z: float


class Preview3DWarning(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    severity: Literal["info", "warning"] = "warning"


class Preview3DSource(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: UUID
    artifact_object_key: str = Field(min_length=1)
    preview_spec_template_id: str = Field(min_length=1)
    preview_spec_view: str = Field(min_length=1)
    version_id: UUID
    workspace_id: UUID


class Preview3DCompatibility(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["compatible", "incompatible"]
    shell_id: str | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def validate_status_detail(self) -> Preview3DCompatibility:
        if self.status == "compatible" and not self.shell_id:
            raise ValueError("compatible Preview3D specs require shell_id")
        if self.status == "incompatible" and not self.reason:
            raise ValueError("incompatible Preview3D specs require reason")
        return self


class Preview3DShell(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimensions: dict[str, float]
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    material_slots: list[str] = Field(min_length=1)
    template_id: str = Field(min_length=1)


class Preview3DCameraPreset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preset_id: str = Field(min_length=1)
    position: Preview3DVector3
    target: Preview3DVector3
    zoom: float = Field(default=1.0, gt=0)


class Preview3DMaterialPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decal_strategy: Literal["preview_spec_projection"]
    overlay_layers: list[dict[str, object]] = Field(default_factory=list)
    safe_zone_overlays: list[dict[str, object]] = Field(default_factory=list)
    source_artifact_id: UUID
    source_kind: Literal["preview_spec", "artifact_object_key"]


class Preview3DSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    camera: Preview3DCameraPreset
    compatibility: Preview3DCompatibility
    materials: Preview3DMaterialPlan
    mode: Literal["lightweight_shell"]
    schema_version: int = Field(default=PREVIEW_3D_SCHEMA_VERSION, ge=1, le=1)
    shell: Preview3DShell | None = None
    source: Preview3DSource
    warnings: list[Preview3DWarning] = Field(default_factory=lambda: default_preview_3d_warnings())

    @model_validator(mode="after")
    def validate_shell_matches_compatibility(self) -> Preview3DSpec:
        if self.compatibility.status == "compatible":
            if self.shell is None:
                raise ValueError("compatible Preview3D specs require shell details")
            if self.shell.id != self.compatibility.shell_id:
                raise ValueError("shell id must match compatibility shell_id")
        return self


class Preview3DScreenshotMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    camera: Preview3DCameraPreset
    preview_3d: Preview3DSpec
    schema_version: int = Field(default=PREVIEW_3D_SCHEMA_VERSION, ge=1, le=1)
    shell_id: str = Field(min_length=1)
    source_artifact_id: UUID
    warning_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_source_and_shell(self) -> Preview3DScreenshotMetadata:
        if self.shell_id != self.preview_3d.compatibility.shell_id:
            raise ValueError("screenshot shell_id must match Preview3D compatibility shell_id")
        if self.source_artifact_id != self.preview_3d.source.artifact_id:
            raise ValueError("screenshot source_artifact_id must match Preview3D source artifact")
        return self


class Preview3DScreenshotArtifactMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preview_3d_screenshot: Preview3DScreenshotMetadata


GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL = Preview3DShell(
    dimensions={"height": 1.4, "length": 4.4, "width": 1.8},
    id=GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL_ID,
    label="Generic side coupe lightweight shell",
    material_slots=["body", SIDE_DECAL_MATERIAL_SLOT, "glass", "wheel"],
    template_id=SUPPORTED_TEMPLATE_ID,
)

_SHELL_REGISTRY: dict[tuple[str, str], Preview3DShell] = {
    (SUPPORTED_TEMPLATE_ID, SUPPORTED_VIEW): GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL,
}


def default_preview_3d_warnings() -> list[Preview3DWarning]:
    return [
        Preview3DWarning(
            id="non_production_preview",
            message="Lightweight 3D preview is concept-only and not production wrap proof.",
            severity="warning",
        ),
        Preview3DWarning(
            id="uv_not_verified",
            message="Vehicle-specific UV mapping has not been verified.",
            severity="warning",
        ),
        Preview3DWarning(
            id="single_shell_fixture",
            message="Preview uses one lightweight shell fixture for MVP validation.",
            severity="info",
        ),
    ]


def registered_preview_3d_shells() -> list[Preview3DShell]:
    return [shell.model_copy(deep=True) for shell in _SHELL_REGISTRY.values()]


def resolve_preview_3d_shell(preview_spec: Mapping[str, object]) -> Preview3DShell | None:
    template_id, view = _preview_spec_identity(preview_spec)
    shell = _SHELL_REGISTRY.get((template_id, view))
    if shell is None:
        return None
    return shell.model_copy(deep=True)


def build_preview_3d_spec(
    *,
    artifact_id: UUID | str,
    artifact_object_key: str,
    preview_spec: Mapping[str, object],
    version_id: UUID | str,
    workspace_id: UUID | str,
) -> Preview3DSpec:
    template_id, view = _preview_spec_identity(preview_spec)
    shell = resolve_preview_3d_shell(preview_spec)
    compatibility: dict[str, object]
    if shell is None:
        compatibility = {
            "reason": _preview_3d_fallback_reason(template_id=template_id, view=view),
            "status": "incompatible",
        }
    else:
        compatibility = {
            "shell_id": shell.id,
            "status": "compatible",
        }

    return Preview3DSpec.model_validate(
        {
            "camera": _default_camera_preset_payload(),
            "compatibility": compatibility,
            "materials": {
                "decal_strategy": "preview_spec_projection",
                "overlay_layers": _projection_records(preview_spec.get("overlay_layers")),
                "safe_zone_overlays": _projection_records(preview_spec.get("safe_zones")),
                "source_artifact_id": artifact_id,
                "source_kind": "preview_spec",
            },
            "mode": "lightweight_shell",
            "shell": shell.model_dump(mode="json") if shell is not None else None,
            "source": {
                "artifact_id": artifact_id,
                "artifact_object_key": artifact_object_key,
                "preview_spec_template_id": template_id,
                "preview_spec_view": view,
                "version_id": version_id,
                "workspace_id": workspace_id,
            },
            "warnings": [
                warning.model_dump(mode="json") for warning in default_preview_3d_warnings()
            ],
        },
    )


def _preview_spec_identity(preview_spec: Mapping[str, object]) -> tuple[str, str]:
    template = preview_spec.get("template")
    if not isinstance(template, Mapping):
        return "unknown-template", "unknown-view"
    template_id = _string_value(template.get("id"), fallback="unknown-template")
    view = _string_value(template.get("view"), fallback="unknown-view").lower()
    return template_id, view


def _preview_3d_fallback_reason(*, template_id: str, view: str) -> str:
    return (
        "No lightweight 3D shell is registered for template "
        f"'{template_id}' with view '{view}'. Continue with the 2D PreviewSpec fallback."
    )


def _default_camera_preset_payload() -> dict[str, object]:
    return {
        "preset_id": DEFAULT_PREVIEW_3D_CAMERA_PRESET_ID,
        "position": {"x": 2.8, "y": 1.4, "z": 4.2},
        "target": {"x": 0.0, "y": 0.4, "z": 0.0},
        "zoom": 1.0,
    }


def _projection_records(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []

    records: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, Mapping):
            continue
        record = {str(key): record_value for key, record_value in item.items()}
        record.setdefault("slot", SIDE_DECAL_MATERIAL_SLOT)
        records.append(record)
    return records


def _string_value(value: object, *, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


__all__ = [
    "DEFAULT_PREVIEW_3D_CAMERA_PRESET_ID",
    "GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL",
    "GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL_ID",
    "PREVIEW_3D_SCHEMA_VERSION",
    "Preview3DCameraPreset",
    "Preview3DCompatibility",
    "Preview3DMaterialPlan",
    "Preview3DScreenshotArtifactMetadata",
    "Preview3DScreenshotMetadata",
    "Preview3DShell",
    "Preview3DSource",
    "Preview3DSpec",
    "Preview3DVector3",
    "Preview3DWarning",
    "SIDE_DECAL_MATERIAL_SLOT",
    "build_preview_3d_spec",
    "default_preview_3d_warnings",
    "registered_preview_3d_shells",
    "resolve_preview_3d_shell",
]
