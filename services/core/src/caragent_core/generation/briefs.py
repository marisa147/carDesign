from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator

from caragent_core.generation.templates import (
    SafeZone,
    TemplateReadinessReport,
    TemplateSourceMetadata,
    resolve_vehicle_template,
)
from caragent_core.references import ReferenceAssignment

_TEXT_LIST_SPLIT_PATTERN = re.compile(r"[\n,;，；、]+")


def _split_text_list(value: str) -> list[str]:
    return [
        item.strip()
        for item in _TEXT_LIST_SPLIT_PATTERN.split(value)
        if item.strip()
    ]


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
        if isinstance(value, str):
            return _split_text_list(value)
        if isinstance(value, list):
            return [item.strip() for item in value if isinstance(item, str) and item.strip()]
        return value

    @field_validator("reference_usage", mode="before")
    @classmethod
    def normalize_reference_usage(cls, value: object) -> object:
        if value is None:
            return []
        return value


class BriefDraft(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    original_request: str = Field(min_length=1)
    vehicle_template_id: str | None = None
    view: str | None = None
    character_theme: str | None = None
    character_focus: str | None = None
    style: str | None = None
    palette: list[str] | None = None
    text: list[str] | None = None
    supporting_graphics: list[str] | None = None
    racing_cues: list[str] | None = None
    typography_intent: str | None = None
    color_harmony: str | None = None
    coverage: str | None = None
    reference_asset_ids: list[str] | None = None
    reference_usage: list[ReferenceAssignment] | None = None
    overlay_logo_asset_ids: list[str] | None = None

    @field_validator("original_request", mode="before")
    @classmethod
    def strip_original_request(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator(
        "character_focus",
        "character_theme",
        "color_harmony",
        "coverage",
        "style",
        "typography_intent",
        "vehicle_template_id",
        "view",
        mode="before",
    )
    @classmethod
    def strip_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return value

    @field_validator(
        "overlay_logo_asset_ids",
        "palette",
        "racing_cues",
        "reference_asset_ids",
        "supporting_graphics",
        "text",
        mode="before",
    )
    @classmethod
    def strip_optional_list_items(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            return _split_text_list(value) or None
        if isinstance(value, list):
            return [item.strip() for item in value if isinstance(item, str) and item.strip()]
        return value

    @field_validator("reference_usage", mode="before")
    @classmethod
    def normalize_draft_reference_usage(cls, value: object) -> object:
        if value is None:
            return None
        return value


class BriefParserInput(BriefDraft):
    """Strict input boundary for deterministic or structured brief parsing."""


class BriefParser(Protocol):
    def parse(self, parser_input: BriefParserInput) -> BriefDraft:
        """Return a strict draft only; persistence stays outside the parser."""


class DeterministicBriefParser:
    def parse(self, parser_input: BriefParserInput) -> BriefDraft:
        return BriefDraft.model_validate(parser_input.model_dump(mode="python"))


StructuredBriefSource = Callable[[BriefParserInput], BriefDraft | Mapping[str, Any]]


class StructuredBriefParser:
    def __init__(self, source: StructuredBriefSource) -> None:
        self._source = source

    def parse(self, parser_input: BriefParserInput) -> BriefDraft:
        raw_draft = self._source(parser_input)
        if isinstance(raw_draft, BriefDraft):
            return raw_draft
        return BriefDraft.model_validate(raw_draft)


def select_brief_parser(
    *,
    llm_enabled: bool = False,
    llm_parser: BriefParser | None = None,
) -> BriefParser:
    if llm_enabled and llm_parser is not None:
        return llm_parser
    return DeterministicBriefParser()


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
    draft = BriefDraft(
        character_focus=character_focus,
        character_theme=character_theme,
        color_harmony=color_harmony,
        coverage=coverage,
        original_request=original_request,
        overlay_logo_asset_ids=overlay_logo_asset_ids,
        palette=palette,
        racing_cues=racing_cues,
        reference_asset_ids=reference_asset_ids,
        reference_usage=_normalize_reference_usage_input(reference_usage),
        style=style,
        supporting_graphics=supporting_graphics,
        text=text,
        typography_intent=typography_intent,
        vehicle_template_id=vehicle_template_id,
        view=view,
    )
    return create_generation_brief_from_draft(draft)


def create_generation_brief_from_draft(draft: BriefDraft) -> GenerationBriefPayload:
    normalized_request = draft.original_request.strip()
    resolution = resolve_vehicle_template(
        vehicle_template_id=draft.vehicle_template_id,
        view=draft.view,
    )
    warnings = [*resolution.warnings, *_quality_warnings(draft.text or [])]

    return GenerationBriefPayload(
        canvas_height=resolution.canvas_height,
        canvas_width=resolution.canvas_width,
        character_focus=draft.character_focus or "",
        character_theme=(draft.character_theme or normalized_request),
        color_harmony=draft.color_harmony or "",
        coverage=(draft.coverage or "balanced side coverage"),
        original_request=normalized_request,
        overlay_logo_asset_ids=draft.overlay_logo_asset_ids or [],
        palette=draft.palette or [],
        racing_cues=draft.racing_cues or [],
        reference_asset_ids=draft.reference_asset_ids or [],
        reference_usage=draft.reference_usage or [],
        safe_zones=resolution.safe_zones,
        style=(draft.style or "itasha concept"),
        supporting_graphics=draft.supporting_graphics or [],
        template_readiness=resolution.template_readiness,
        template_source=resolution.template_source,
        text=draft.text or [],
        typography_intent=draft.typography_intent or "",
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


