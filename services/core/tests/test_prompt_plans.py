from __future__ import annotations

from uuid import uuid4

from caragent_core.generation import (
    PromptProviderSettings,
    build_prompt_plan,
    create_generation_brief,
)


def test_build_prompt_plan_captures_text_payload_and_provider_trace() -> None:
    reference_id = str(uuid4())
    logo_id = str(uuid4())
    brief = create_generation_brief(
        original_request=(
            "Build a white RX-7 pain-car concept with Sakura heroine art, "
            "pink and teal accents, and MOON DRIVE side text."
        ),
        character_theme="Sakura heroine art",
        character_focus="door portrait",
        color_harmony="white base with pink and teal balance",
        coverage="full side coverage",
        overlay_logo_asset_ids=[logo_id],
        palette=["white", "pink", "teal"],
        racing_cues=["number plate", "tow arrows"],
        reference_asset_ids=[reference_id],
        style="clean racing itasha",
        supporting_graphics=["sakura petals", "music waveform"],
        text=["MOON DRIVE"],
        typography_intent="bold readable side lettering",
        vehicle_template_id="mazda-rx7",
        view="rear",
    )
    provider_settings = PromptProviderSettings(
        provider="local-deterministic",
        model="local-concept-v1",
        parameters={"quality": "draft", "size": "1536x768"},
    )

    plan = build_prompt_plan(brief, provider_settings=provider_settings)

    assert plan.provider == "local-deterministic"
    assert plan.model == "local-concept-v1"
    assert plan.parameters == {"quality": "draft", "size": "1536x768"}
    assert plan.estimated_cost is None
    assert plan.concept_label == "concept_preview"
    assert plan.input_artifact_ids == [reference_id]

    assert "2D concept preview" in plan.prompt_text
    assert "Generic side-view coupe" in plan.prompt_text
    assert "side view" in plan.prompt_text
    assert "Sakura heroine art" in plan.prompt_text
    assert "clean racing itasha" in plan.prompt_text
    assert "white, pink, teal" in plan.prompt_text
    assert "MOON DRIVE" in plan.prompt_text
    assert "full side coverage" in plan.prompt_text

    payload = plan.prompt_payload
    assert payload["original_request"] == brief.original_request
    assert payload["concept_label"] == "concept_preview"
    assert payload["provider"] == "local-deterministic"
    assert payload["model"] == "local-concept-v1"
    assert payload["parameters"] == {"quality": "draft", "size": "1536x768"}
    assert payload["input_artifact_ids"] == [reference_id]
    assert payload["vehicle_template"] == {
        "id": brief.vehicle_template_id,
        "label": brief.vehicle_template_label,
        "view": brief.view,
        "canvas_width": brief.canvas_width,
        "canvas_height": brief.canvas_height,
    }
    assert payload["brief"] == {
        "character_focus": "door portrait",
        "character_theme": "Sakura heroine art",
        "color_harmony": "white base with pink and teal balance",
        "style": "clean racing itasha",
        "palette": ["white", "pink", "teal"],
        "racing_cues": ["number plate", "tow arrows"],
        "supporting_graphics": ["sakura petals", "music waveform"],
        "text": ["MOON DRIVE"],
        "typography_intent": "bold readable side lettering",
        "coverage": "full side coverage",
    }
    preview_spec = payload["preview_spec"]
    assert preview_spec["canvas"] == {"width": 1536, "height": 768}
    assert preview_spec["template"]["id"] == brief.vehicle_template_id
    assert preview_spec["template"]["view"] == brief.view
    assert {zone["id"] for zone in preview_spec["safe_zones"]} >= {
        "door-main",
        "side-window",
    }
    assert preview_spec["overlay_layers"] == [
        {
            "id": "text-1",
            "kind": "text",
            "text": "MOON DRIVE",
            "zone_id": "door-main",
        },
        {
            "asset_id": logo_id,
            "id": "logo-1",
            "kind": "logo",
            "zone_id": "rear-quarter",
        },
    ]
    assert preview_spec["warnings"][0]["message"].startswith("Unsupported vehicle template")
    assert payload["warnings"] == brief.warnings
    assert "Unsupported vehicle template" in " ".join(payload["warnings"])
    assert "Unsupported view" in " ".join(payload["warnings"])
    assert "binary" not in str(payload).lower()


def test_prompt_plan_is_deterministic_and_json_serializable() -> None:
    brief = create_generation_brief(
        original_request="Black coupe with neon dragon girl, gold accents, and STARRY logo.",
        character_theme="neon dragon girl",
        palette=["black", "gold"],
        text=["STARRY"],
    )

    first = build_prompt_plan(brief)
    second = build_prompt_plan(brief)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.provider == "local-deterministic"
    assert first.model == "local-concept-v1"
    assert first.parameters == {"size": "1536x768", "quality": "concept"}
    assert first.model_dump(mode="json")["estimated_cost"] is None


def test_generation_brief_accepts_structured_reference_usage() -> None:
    reference_id = str(uuid4())

    brief = create_generation_brief(
        original_request="White coupe with heroine reference and palette board.",
        character_theme="heroine reference",
        reference_asset_ids=[reference_id],
        reference_usage=[
            {
                "asset_id": reference_id,
                "enabled": True,
                "role": "character",
            },
        ],
    )

    dumped = brief.model_dump(mode="json")
    assert dumped["reference_asset_ids"] == [reference_id]
    assert dumped["reference_usage"] == [
        {
            "asset_id": reference_id,
            "enabled": True,
            "role": "character",
            "schema_version": 1,
        },
    ]
    assert "binary" not in str(dumped).lower()
