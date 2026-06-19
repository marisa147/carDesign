from __future__ import annotations

from caragent_core.generation import (
    MVP_COUPE_TEMPLATE_ID,
    MVP_TEMPLATE_IDS,
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

    assert tuple(record.id for record in records) == MVP_TEMPLATE_IDS
    for record in records:
        assert record.asset_slots.keys() == set(REQUIRED_TEMPLATE_ASSET_SLOTS)
        for slot in REQUIRED_TEMPLATE_ASSET_SLOTS:
            assert template_asset_resource(record.id, slot).is_file()


def test_legacy_coupe_id_resolves_to_mvp_coupe_record() -> None:
    resolution = resolve_vehicle_template(vehicle_template_id=SUPPORTED_TEMPLATE_ID)

    assert resolution.template_id == MVP_COUPE_TEMPLATE_ID
    assert resolution.template_label == "Generic coupe side-view"
    assert resolution.template_readiness.catalog_eligible is True
    assert resolution.template_readiness.missing_asset_slots == []
