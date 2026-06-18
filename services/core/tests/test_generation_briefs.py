from __future__ import annotations

from uuid import uuid4

import pytest

from caragent_core.generation import (
    SUPPORTED_TEMPLATE_ID,
    SUPPORTED_VIEW,
    GenerationBriefPayload,
    create_generation_brief,
    resolve_vehicle_template,
)


def test_create_generation_brief_preserves_request_and_normalizes_template() -> None:
    reference_id = str(uuid4())

    brief = create_generation_brief(
        original_request=(
            "Create a Sakura GT86 pain-car concept with Hatsune Miku, "
            "pink and cyan palette, and NEBULA door text."
        ),
        character_theme="Hatsune Miku",
        coverage="full side coverage",
        palette=["pink", "cyan"],
        reference_asset_ids=[reference_id],
        style="racing JDM",
        text=["NEBULA"],
        vehicle_template_id="toyota-gt86",
        view="three-quarter",
    )

    assert isinstance(brief, GenerationBriefPayload)
    assert brief.original_request.startswith("Create a Sakura GT86")
    assert brief.vehicle_template_id == SUPPORTED_TEMPLATE_ID
    assert brief.view == SUPPORTED_VIEW
    assert brief.character_theme == "Hatsune Miku"
    assert brief.style == "racing JDM"
    assert brief.palette == ["pink", "cyan"]
    assert brief.text == ["NEBULA"]
    assert brief.coverage == "full side coverage"
    assert brief.reference_asset_ids == [reference_id]
    assert "Unsupported vehicle template" in " ".join(brief.warnings)
    assert "Unsupported view" in " ".join(brief.warnings)


def test_create_generation_brief_defaults_missing_optional_fields() -> None:
    brief = create_generation_brief(
        original_request="Black coupe with a dragon heroine, neon violet accents, side wrap.",
    )

    assert brief.original_request == (
        "Black coupe with a dragon heroine, neon violet accents, side wrap."
    )
    assert brief.vehicle_template_id == SUPPORTED_TEMPLATE_ID
    assert brief.view == SUPPORTED_VIEW
    assert brief.character_theme == (
        "Black coupe with a dragon heroine, neon violet accents, side wrap."
    )
    assert brief.style == "itasha concept"
    assert brief.palette == []
    assert brief.text == []
    assert brief.coverage == "balanced side coverage"
    assert brief.reference_asset_ids == []
    assert brief.character_focus == ""
    assert brief.supporting_graphics == []
    assert brief.racing_cues == []
    assert brief.typography_intent == ""
    assert brief.color_harmony == ""
    assert brief.overlay_logo_asset_ids == []
    assert len(brief.safe_zones) >= 4
    assert brief.warnings == []


def test_empty_original_request_is_rejected() -> None:
    with pytest.raises(ValueError, match="original_request"):
        create_generation_brief(original_request="   ")


def test_resolve_vehicle_template_reports_unsupported_inputs() -> None:
    resolution = resolve_vehicle_template(
        vehicle_template_id="rx7-widebody",
        view="rear",
    )

    assert resolution.template_id == SUPPORTED_TEMPLATE_ID
    assert resolution.view == SUPPORTED_VIEW
    assert resolution.canvas_width == 1536
    assert resolution.canvas_height == 768
    assert len(resolution.warnings) == 2
    assert resolution.warnings[0].startswith("Unsupported vehicle template")
    assert resolution.warnings[1].startswith("Unsupported view")
    assert {zone["id"] for zone in resolution.safe_zones} >= {
        "door-main",
        "side-window",
        "front-wheel-arch",
        "rear-wheel-arch",
    }
    for zone in resolution.safe_zones:
        assert 0 <= zone["x"] <= 1
        assert 0 <= zone["y"] <= 1
        assert 0 < zone["width"] <= 1
        assert 0 < zone["height"] <= 1


def test_create_generation_brief_preserves_itasha_controls_and_quality_warnings() -> None:
    logo_id = str(uuid4())

    brief = create_generation_brief(
        original_request="White coupe with heroine portrait and a very long side slogan.",
        character_focus="driver door heroine face",
        color_harmony="white, sakura pink, cyan accents",
        overlay_logo_asset_ids=[logo_id],
        racing_cues=["kanjo number plate", "tow arrows"],
        supporting_graphics=["cherry blossom burst", "pixel stars"],
        text=["THIS IS A VERY LONG SIDE SLOGAN FOR THE DOOR PANEL"],
        typography_intent="bold readable kana-inspired Latin lettering",
    )

    assert brief.character_focus == "driver door heroine face"
    assert brief.supporting_graphics == ["cherry blossom burst", "pixel stars"]
    assert brief.racing_cues == ["kanjo number plate", "tow arrows"]
    assert brief.typography_intent == "bold readable kana-inspired Latin lettering"
    assert brief.color_harmony == "white, sakura pink, cyan accents"
    assert brief.overlay_logo_asset_ids == [logo_id]
    assert any("Text may be hard to read" in warning for warning in brief.warnings)
    assert all(len(warning) <= 140 for warning in brief.warnings)


def test_generation_brief_round_trips_as_json_safe_payload() -> None:
    brief = create_generation_brief(
        original_request="White hatchback with magical girl theme.",
        text=["STAR DRIVE"],
    )

    dumped = brief.model_dump(mode="json")

    assert dumped["original_request"] == "White hatchback with magical girl theme."
    assert dumped["text"] == ["STAR DRIVE"]
    assert dumped["vehicle_template_id"] == SUPPORTED_TEMPLATE_ID
    assert dumped["safe_zones"][0]["id"]
    assert dumped["overlay_logo_asset_ids"] == []
