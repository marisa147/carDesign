from __future__ import annotations

from uuid import uuid4

import pytest

from caragent_core.generation import (
    MVP_COUPE_TEMPLATE_ID,
    SUPPORTED_TEMPLATE_ID,
    SUPPORTED_VIEW,
    GenerationBriefPayload,
    TemplateRegistry,
    TemplateSourceMetadata,
    VehicleTemplateRecord,
    audit_vehicle_templates,
    create_generation_brief,
    register_vehicle_template,
    resolve_vehicle_template,
    template_source_policy_table,
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
    assert brief.template_source.source_type == "internal_original"
    assert brief.template_source.license_status == "approved"
    assert brief.template_readiness.reusable_asset_allowed is True
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
    assert resolution.template_source.source_type == "internal_original"
    assert resolution.template_readiness.reusable_asset_allowed is True
    for zone in resolution.safe_zones:
        assert 0 <= zone["x"] <= 1
        assert 0 <= zone["y"] <= 1
        assert 0 < zone["width"] <= 1
        assert 0 < zone["height"] <= 1


def test_template_source_policy_table_documents_allowed_and_blocked_sources() -> None:
    policies = {item["source_type"]: item for item in template_source_policy_table()}

    assert policies["internal_original"]["allowed_for_template_library"] is True
    assert policies["licensed_template"]["requires_license_evidence"] is True
    assert policies["user_provided_with_rights"]["allowed_for_reusable_assets"] is True
    assert policies["third_party_reference_only"]["allowed_for_reusable_assets"] is False
    assert policies["web_crawled_image"]["allowed_for_template_library"] is False


def test_register_vehicle_template_blocks_disallowed_reusable_sources() -> None:
    registry = TemplateRegistry()
    record = _template_record(
        source=TemplateSourceMetadata(
            allowed_usage_scope="reference_only",
            audit_timestamp="2026-06-19T00:00:00Z",
            distribution_allowed=False,
            license_evidence="reference-only-source",
            license_status="reference_only",
            rights_notes="Third-party image may only be used as inspiration.",
            source_type="third_party_reference_only",
        ),
    )

    with pytest.raises(ValueError, match="cannot be registered as reusable template assets"):
        register_vehicle_template(record, registry=registry)

    assert audit_vehicle_templates(registry) == []


def test_register_vehicle_template_requires_license_evidence_for_licensed_sources() -> None:
    registry = TemplateRegistry()
    record = _template_record(
        source=TemplateSourceMetadata(
            allowed_usage_scope="licensed_catalog",
            audit_timestamp="2026-06-19T00:00:00Z",
            distribution_allowed=True,
            license_status="approved",
            rights_notes="Licensed but missing evidence.",
            source_type="licensed_template",
        ),
    )

    with pytest.raises(ValueError, match="requires license evidence"):
        register_vehicle_template(record, registry=registry)


def test_legacy_template_alias_resolves_without_breaking_existing_id() -> None:
    resolution = resolve_vehicle_template(vehicle_template_id=MVP_COUPE_TEMPLATE_ID)

    assert resolution.template_id == SUPPORTED_TEMPLATE_ID
    assert resolution.template_label == "Generic side-view coupe"
    assert resolution.view == SUPPORTED_VIEW
    assert resolution.warnings == []


def test_template_registry_replace_clears_previous_aliases() -> None:
    registry = TemplateRegistry()
    first = _template_record(source=_internal_source(), aliases=("old-alias",))
    replacement = _template_record(source=_internal_source(), aliases=("new-alias",))

    register_vehicle_template(first, registry=registry)
    register_vehicle_template(replacement, registry=registry, replace=True)

    assert registry.resolve("old-alias") is None
    assert registry.resolve("new-alias") == replacement


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
    assert dumped["template_source"]["source_type"] == "internal_original"
    assert dumped["template_readiness"]["reusable_asset_allowed"] is True
    assert dumped["safe_zones"][0]["id"]
    assert dumped["overlay_logo_asset_ids"] == []


def _internal_source() -> TemplateSourceMetadata:
    return TemplateSourceMetadata(
        allowed_usage_scope="mvp_concept_preview",
        audit_timestamp="2026-06-19T00:00:00Z",
        distribution_allowed=True,
        license_evidence="internal-test-template",
        license_status="approved",
        rights_notes="Internal test template.",
        source_type="internal_original",
    )


def _template_record(
    *,
    source: TemplateSourceMetadata,
    aliases: tuple[str, ...] = (),
) -> VehicleTemplateRecord:
    return VehicleTemplateRecord(
        aliases=aliases,
        asset_slots={
            "base": "base.png",
            "body_mask": "body_mask.png",
            "handle_mask": "handle_mask.png",
            "metadata": "template.json",
            "panel_lines": "panel_lines.png",
            "safe_zones": "safe_zones.json",
            "thumbnail": "thumbnail.png",
            "wheel_mask": "wheel_mask.png",
            "window_mask": "window_mask.png",
        },
        canvas_height=768,
        canvas_width=1536,
        id="test_template_side_v1",
        label="Test template",
        safe_zones=[{"height": 0.2, "id": "door-main", "width": 0.3, "x": 0.3, "y": 0.4}],
        source=source,
        view="side",
    )
