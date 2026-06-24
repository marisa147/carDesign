from __future__ import annotations

from uuid import uuid4

import pytest

from caragent_core.generation import (
    DEFAULT_TEMPLATE_ID,
    MVP_COUPE_TEMPLATE_ID,
    MVP_TEMPLATE_IDS,
    SUPPORTED_TEMPLATE_ID,
    SUPPORTED_VIEW,
    BriefDraft,
    BriefParserInput,
    DeterministicBriefParser,
    GenerationBriefPayload,
    StructuredBriefParser,
    TemplateRegistry,
    TemplateSourceMetadata,
    VehicleTemplateRecord,
    audit_vehicle_templates,
    create_generation_brief,
    create_generation_brief_from_draft,
    list_vehicle_templates,
    register_vehicle_template,
    resolve_vehicle_template,
    select_brief_parser,
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
    assert brief.vehicle_template_id == DEFAULT_TEMPLATE_ID
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
    assert brief.vehicle_template_id == DEFAULT_TEMPLATE_ID
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



def test_create_generation_brief_normalizes_string_list_fields_from_parser() -> None:
    draft = BriefDraft(
        character_theme="Hatsune Miku racing theme",
        original_request="白色双门跑车，初音未来主题，车门写 MIKU RACING。",
        palette="白色车身，青绿色线条",
        racing_cues="赛车线条",
        supporting_graphics="青绿色速度线、音符装饰",
        text="MIKU RACING",
    )

    brief = create_generation_brief_from_draft(draft)

    assert brief.palette == ["白色车身", "青绿色线条"]
    assert brief.racing_cues == ["赛车线条"]
    assert brief.supporting_graphics == ["青绿色速度线", "音符装饰"]
    assert brief.text == ["MIKU RACING"]
def test_empty_original_request_is_rejected() -> None:
    with pytest.raises(ValueError, match="original_request"):
        create_generation_brief(original_request="   ")


def test_resolve_vehicle_template_reports_unsupported_inputs() -> None:
    resolution = resolve_vehicle_template(
        vehicle_template_id="rx7-widebody",
        view="rear",
    )

    assert resolution.template_id == DEFAULT_TEMPLATE_ID
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


def test_mvp_template_registry_contains_all_catalog_ready_templates() -> None:
    records = list_vehicle_templates()
    audits = audit_vehicle_templates()

    assert tuple(record.id for record in records) == MVP_TEMPLATE_IDS
    assert {audit.id for audit in audits} == set(MVP_TEMPLATE_IDS)
    assert all(audit.source_type == "internal_original" for audit in audits)
    assert all(audit.license_status == "approved" for audit in audits)
    assert all(audit.catalog_eligible for audit in audits)
    assert all(audit.reusable_asset_allowed for audit in audits)
    assert all(audit.missing_asset_slots == [] for audit in audits)
    assert all(audit.blocking_reasons == [] for audit in audits)


@pytest.mark.parametrize("template_id", MVP_TEMPLATE_IDS)
def test_create_generation_brief_preserves_selected_mvp_template(template_id: str) -> None:
    brief = create_generation_brief(
        original_request=f"Create a design for {template_id}.",
        vehicle_template_id=template_id,
    )

    assert brief.vehicle_template_id == template_id
    assert brief.vehicle_template_label.startswith("Generic ")
    assert brief.view == SUPPORTED_VIEW
    assert brief.template_source.source_type == "internal_original"
    assert brief.template_source.license_status == "approved"
    assert brief.template_readiness.catalog_eligible is True
    assert brief.template_readiness.missing_asset_slots == []
    assert brief.warnings == []
    assert {zone["id"] for zone in brief.safe_zones} >= {
        "door-main",
        "front-wheel-arch",
        "rear-quarter",
        "rear-wheel-arch",
        "side-window",
    }


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
    resolution = resolve_vehicle_template(vehicle_template_id=SUPPORTED_TEMPLATE_ID)

    assert resolution.template_id == MVP_COUPE_TEMPLATE_ID
    assert resolution.template_label == "Generic coupe side-view"
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
    assert dumped["vehicle_template_id"] == DEFAULT_TEMPLATE_ID
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


def test_deterministic_brief_parser_returns_strict_draft_and_payload() -> None:
    parser_input = BriefParserInput(
        character_theme="Sakura heroine",
        coverage="full side coverage",
        original_request="White coupe with Sakura heroine and MOON DRIVE text.",
        palette=["white", "pink"],
        style="clean racing itasha",
        text=["MOON DRIVE"],
        vehicle_template_id=MVP_COUPE_TEMPLATE_ID,
    )

    draft = DeterministicBriefParser().parse(parser_input)
    payload = create_generation_brief_from_draft(draft)

    assert isinstance(draft, BriefDraft)
    assert draft.original_request == parser_input.original_request
    assert draft.character_theme == "Sakura heroine"
    assert draft.palette == ["white", "pink"]
    assert payload.vehicle_template_id == MVP_COUPE_TEMPLATE_ID
    assert payload.character_theme == "Sakura heroine"
    assert payload.text == ["MOON DRIVE"]


def test_select_brief_parser_keeps_llm_parser_behind_feature_flag() -> None:
    class RecordingParser:
        calls = 0

        def parse(self, parser_input: BriefParserInput) -> BriefDraft:
            self.calls += 1
            return BriefDraft(original_request=parser_input.original_request, style="llm style")

    llm_parser = RecordingParser()
    parser = select_brief_parser(llm_enabled=False, llm_parser=llm_parser)

    draft = parser.parse(BriefParserInput(original_request="Black hatchback with neon decals."))

    assert isinstance(parser, DeterministicBriefParser)
    assert llm_parser.calls == 0
    assert draft.style is None


def test_structured_brief_parser_rejects_extra_llm_fields() -> None:
    parser = StructuredBriefParser(
        lambda parser_input: {
            "extra_database_write": "nope",
            "original_request": parser_input.original_request,
            "style": "structured style",
        },
    )

    with pytest.raises(ValueError, match="extra_database_write"):
        parser.parse(BriefParserInput(original_request="Silver sedan with star graphics."))
