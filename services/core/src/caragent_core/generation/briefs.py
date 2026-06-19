from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, Field, field_validator

from caragent_core.generation.templates import (
    SafeZone,
    TemplateReadinessReport,
    TemplateSourceMetadata,
    resolve_vehicle_template,
)
from caragent_core.references import ReferenceAssignment


class GenerationBriefPayload(BaseModel):
    original_request: str = Field(min_length=1)
    vehicle_template_id: str = Field(min_length=1)
    vehicle_template_label: str = Field(min_length=1)
    view: str = Field(min_length=1)
    character_theme: str = Field(min_length=1)
    character_focus: str = ""
    style: str = Field(min_length=1)
    palette: list[str] = Field(default_factory=list)
    text: list[str] = Field(default_factory=list)
    supporting_graphics: list[str] = Field(default_factory=list)
    racing_cues: list[str] = Field(default_factory=list)
    typography_intent: str = ""
    color_harmony: str = ""
    coverage: str = Field(min_length=1)
    reference_asset_ids: list[str] = Field(default_factory=list)
    reference_usage: list[ReferenceAssignment] = Field(default_factory=list)
    overlay_logo_asset_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    safe_zones: list[SafeZone] = Field(default_factory=list)
    canvas_width: int
    canvas_height: int
    template_source: TemplateSourceMetadata
    template_readiness: TemplateReadinessReport

    @field_validator(
        "character_focus",
        "color_harmony",
        "original_request",
        "vehicle_template_id",
        "vehicle_template_label",
        "view",
        "character_theme",
        "style",
        "typography_intent",
        "coverage",
        mode="before",
    )
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator(
        "overlay_logo_asset_ids",
        "palette",
        "racing_cues",
        "reference_asset_ids",
        "supporting_graphics",
        "text",
        "warnings",
        mode="before",
    )
    @classmethod
    def strip_list_items(cls, value: object) -> object:
        if value is None:
            return []
        if isinstance(value, list):
            return [item.strip() for item in value if isinstance(item, str) and item.strip()]
        return value

    @field_validator("reference_usage", mode="before")
    @classmethod
    def normalize_reference_usage(cls, value: object) -> object:
        if value is None:
            return []
        return value


def create_generation_brief(
    *,
    original_request: str,
    vehicle_template_id: str | None = None,
    view: str | None = None,
    character_theme: str | None = None,
    character_focus: str | None = None,
    style: str | None = None,
    palette: list[str] | None = None,
    text: list[str] | None = None,
    supporting_graphics: list[str] | None = None,
    racing_cues: list[str] | None = None,
    typography_intent: str | None = None,
    color_harmony: str | None = None,
    coverage: str | None = None,
    reference_asset_ids: list[str] | None = None,
    reference_usage: Sequence[ReferenceAssignment | Mapping[str, Any]] | None = None,
    overlay_logo_asset_ids: list[str] | None = None,
) -> GenerationBriefPayload:
    normalized_request = original_request.strip()
    resolution = resolve_vehicle_template(
        vehicle_template_id=vehicle_template_id,
        view=view,
    )
    warnings = [*resolution.warnings, *_quality_warnings(text or [])]

    return GenerationBriefPayload(
        canvas_height=resolution.canvas_height,
        canvas_width=resolution.canvas_width,
        character_focus=character_focus or "",
        character_theme=(character_theme or normalized_request),
        color_harmony=color_harmony or "",
        coverage=(coverage or "balanced side coverage"),
        original_request=normalized_request,
        overlay_logo_asset_ids=overlay_logo_asset_ids or [],
        palette=palette or [],
        racing_cues=racing_cues or [],
        reference_asset_ids=reference_asset_ids or [],
        reference_usage=_normalize_reference_usage_input(reference_usage),
        safe_zones=resolution.safe_zones,
        style=(style or "itasha concept"),
        supporting_graphics=supporting_graphics or [],
        template_readiness=resolution.template_readiness,
        template_source=resolution.template_source,
        text=text or [],
        typography_intent=typography_intent or "",
        vehicle_template_id=resolution.template_id,
        vehicle_template_label=resolution.template_label,
        view=resolution.view,
        warnings=warnings,
    )


def refresh_generation_brief_warnings(brief: GenerationBriefPayload) -> GenerationBriefPayload:
    template_warnings = [
        warning for warning in brief.warnings if not warning.startswith("Text may be hard to read")
    ]
    return brief.model_copy(
        update={"warnings": [*template_warnings, *_quality_warnings(brief.text)]},
    )


def _normalize_reference_usage_input(
    reference_usage: Sequence[ReferenceAssignment | Mapping[str, Any]] | None,
) -> list[ReferenceAssignment]:
    if not reference_usage:
        return []

    return [
        item if isinstance(item, ReferenceAssignment) else ReferenceAssignment.model_validate(item)
        for item in reference_usage
    ]


def _quality_warnings(text: list[str]) -> list[str]:
    if any(len(value.strip()) > 28 for value in text):
        return ["Text may be hard to read; shorten or enlarge the lettering."]
    return []
