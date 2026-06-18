from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

PREVIEW_3D_SCHEMA_VERSION = 1


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


__all__ = [
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
    "default_preview_3d_warnings",
]
