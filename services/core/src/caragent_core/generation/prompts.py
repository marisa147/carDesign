from __future__ import annotations

from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator

from caragent_core.generation.briefs import GenerationBriefPayload

DEFAULT_PROVIDER = "local-deterministic"
DEFAULT_MODEL = "local-concept-v1"
CONCEPT_LABEL = "concept_preview"

JsonObject = dict[str, Any]


def _default_parameters() -> JsonObject:
    return {"size": "1536x768", "quality": "concept"}


class PromptProviderSettings(BaseModel):
    provider: str = Field(default=DEFAULT_PROVIDER, min_length=1)
    model: str = Field(default=DEFAULT_MODEL, min_length=1)
    parameters: JsonObject = Field(default_factory=_default_parameters)
    estimated_cost: Decimal | None = None

    @field_validator("provider", "model", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class PromptPlan(BaseModel):
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    parameters: JsonObject = Field(default_factory=dict)
    prompt_text: str = Field(min_length=1)
    prompt_payload: JsonObject = Field(default_factory=dict)
    input_artifact_ids: list[str] = Field(default_factory=list)
    estimated_cost: Decimal | None = None
    concept_label: str = Field(default=CONCEPT_LABEL, min_length=1)


def build_prompt_plan(
    brief: GenerationBriefPayload,
    *,
    provider_settings: PromptProviderSettings | None = None,
) -> PromptPlan:
    settings = provider_settings or PromptProviderSettings()
    parameters = dict(settings.parameters)
    input_artifact_ids = list(brief.reference_asset_ids)
    prompt_text = _build_prompt_text(brief)

    prompt_payload: JsonObject = {
        "brief": {
            "character_focus": brief.character_focus,
            "character_theme": brief.character_theme,
            "color_harmony": brief.color_harmony,
            "coverage": brief.coverage,
            "palette": list(brief.palette),
            "racing_cues": list(brief.racing_cues),
            "style": brief.style,
            "supporting_graphics": list(brief.supporting_graphics),
            "text": list(brief.text),
            "typography_intent": brief.typography_intent,
        },
        "concept_label": CONCEPT_LABEL,
        "input_artifact_ids": input_artifact_ids,
        "model": settings.model,
        "original_request": brief.original_request,
        "parameters": parameters,
        "provider": settings.provider,
        "vehicle_template": {
            "canvas_height": brief.canvas_height,
            "canvas_width": brief.canvas_width,
            "id": brief.vehicle_template_id,
            "label": brief.vehicle_template_label,
            "view": brief.view,
        },
        "preview_spec": _build_preview_spec(brief),
        "warnings": list(brief.warnings),
    }

    return PromptPlan(
        concept_label=CONCEPT_LABEL,
        estimated_cost=settings.estimated_cost,
        input_artifact_ids=input_artifact_ids,
        model=settings.model,
        parameters=parameters,
        prompt_payload=prompt_payload,
        prompt_text=prompt_text,
        provider=settings.provider,
    )


def _build_prompt_text(brief: GenerationBriefPayload) -> str:
    character_focus = brief.character_focus or "designer-selected character placement"
    color_harmony = brief.color_harmony or "balanced with selected palette"
    palette = _join_values(brief.palette, fallback="designer-selected palette")
    racing_cues = _join_values(brief.racing_cues, fallback="no fixed racing cues")
    supporting_graphics = _join_values(
        brief.supporting_graphics,
        fallback="no fixed supporting graphics",
    )
    text = _join_values(brief.text, fallback="no fixed text requested")
    typography = brief.typography_intent or "designer-selected typography"
    references = _join_values(
        brief.reference_asset_ids,
        fallback="no reference assets supplied",
    )
    warnings = _join_values(brief.warnings, fallback="no template warnings")

    return "\n".join(
        [
            "Create a 2D concept preview for a pain-car livery.",
            (
                "Vehicle template: "
                f"{brief.vehicle_template_label} ({brief.vehicle_template_id}), "
                f"{brief.view} view, canvas {brief.canvas_width}x{brief.canvas_height}."
            ),
            f"Character/theme: {brief.character_theme}.",
            f"Character focus: {character_focus}.",
            f"Style: {brief.style}.",
            f"Supporting graphics: {supporting_graphics}.",
            f"Racing/JDM cues: {racing_cues}.",
            f"Palette: {palette}.",
            f"Color harmony: {color_harmony}.",
            f"Text intent: {text}.",
            f"Typography intent: {typography}.",
            f"Coverage: {brief.coverage}.",
            f"Reference asset ids: {references}.",
            f"Template/view notes: {warnings}.",
            "Output is a concept preview only, not an installer-ready production wrap.",
        ],
    )


def _join_values(values: list[str], *, fallback: str) -> str:
    return ", ".join(values) if values else fallback


def _build_preview_spec(brief: GenerationBriefPayload) -> JsonObject:
    return {
        "canvas": {"height": brief.canvas_height, "width": brief.canvas_width},
        "overlay_layers": _build_overlay_layers(brief),
        "safe_zones": [dict(zone) for zone in brief.safe_zones],
        "sources": {
            "overlay_logo_asset_ids": list(brief.overlay_logo_asset_ids),
            "reference_asset_ids": list(brief.reference_asset_ids),
        },
        "template": {
            "id": brief.vehicle_template_id,
            "label": brief.vehicle_template_label,
            "view": brief.view,
        },
        "warnings": [
            {"id": f"warning-{index}", "message": warning}
            for index, warning in enumerate(brief.warnings, start=1)
        ],
    }


def _build_overlay_layers(brief: GenerationBriefPayload) -> list[JsonObject]:
    layers: list[JsonObject] = []
    for index, text in enumerate(brief.text, start=1):
        layers.append(
            {
                "id": f"text-{index}",
                "kind": "text",
                "text": text,
                "zone_id": "door-main",
            },
        )
    for index, asset_id in enumerate(brief.overlay_logo_asset_ids, start=1):
        layers.append(
            {
                "asset_id": asset_id,
                "id": f"logo-{index}",
                "kind": "logo",
                "zone_id": "rear-quarter",
            },
        )
    return layers
