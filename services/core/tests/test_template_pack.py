from __future__ import annotations

from caragent_core.generation import (
    ALL_TEMPLATE_IDS,
    GR86_BRZ_TEMPLATE_ID,
    MVP_COUPE_TEMPLATE_ID,
    REQUIRED_TEMPLATE_ASSET_SLOTS,
    SUPPORTED_TEMPLATE_ID,
    list_vehicle_templates,
    resolve_vehicle_template,
    template_asset_resource,
)
from caragent_core.generation.validate_template_pack import validate_template_pack


def test_mvp_template_pack_validator_passes() -> None:
    assert validate_template_pack() == []


def test_mvp_template_pack_assets_are_packaged_for_every_template() -> None:
    records = list_vehicle_templates()

    assert tuple(record.id for record in records) == ALL_TEMPLATE_IDS
    for record in records:
        assert record.asset_slots.keys() == set(REQUIRED_TEMPLATE_ASSET_SLOTS)
        for slot in REQUIRED_TEMPLATE_ASSET_SLOTS:
            assert template_asset_resource(record.id, slot).is_file()


def test_gr86_brz_template_exposes_construction_metadata() -> None:
    record = next(
        record for record in list_vehicle_templates() if record.id == GR86_BRZ_TEMPLATE_ID
    )

    assert record.supported_views == ("side", "front", "rear", "top")
    assert set(record.view_assets) == {"side", "front", "rear", "top"}
    assert record.dimensions == {
        "unit": "mm",
        "overall_length": 4265,
        "overall_width": 1775,
        "overall_height": 1310,
        "wheelbase": 2575,
    }
    assert record.scale and record.scale["unit"] == "mm_per_canvas_px"
    assert record.export_config and set(record.export_config["formats"]) == {"svg", "pdf", "png"}
    assert record.authorization and record.authorization["source"] == "internal_generated"
    assert {section["id"] for section in record.sections} >= {
        "door-left",
        "front-bumper",
        "front-fender",
        "hood",
        "rear-bumper",
        "rear-quarter",
        "roof",
        "side-skirt",
        "trunk",
    }
    assert {zone["id"] for zone in record.forbidden_zones} >= {
        "side-window",
        "front-windshield",
        "rear-window",
    }


def test_legacy_coupe_id_resolves_to_mvp_coupe_record() -> None:
    resolution = resolve_vehicle_template(vehicle_template_id=SUPPORTED_TEMPLATE_ID)

    assert resolution.template_id == MVP_COUPE_TEMPLATE_ID
    assert resolution.template_label == "Generic coupe side-view"
    assert resolution.template_readiness.catalog_eligible is True
    assert resolution.template_readiness.missing_asset_slots == []
