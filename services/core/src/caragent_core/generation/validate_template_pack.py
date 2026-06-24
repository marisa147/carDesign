from __future__ import annotations

import json
import struct
import zlib
from dataclasses import dataclass
from typing import Any

from caragent_core.generation.templates import (
    ALL_TEMPLATE_IDS,
    GR86_BRZ_TEMPLATE_ID,
    MVP_TEMPLATE_IDS,
    REQUIRED_TEMPLATE_ASSET_SLOTS,
    TemplateAssetSlot,
    VehicleTemplateRecord,
    evaluate_template_readiness,
    list_vehicle_templates,
    template_asset_resource,
    template_pack_root,
)

CANVAS_SIZE = (1536, 768)
THUMBNAIL_SIZE = (384, 192)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
FULL_SIZE_PNG_SLOTS: tuple[TemplateAssetSlot, ...] = (
    "base",
    "body_mask",
    "window_mask",
    "wheel_mask",
    "handle_mask",
    "panel_lines",
)
MASK_SLOTS: tuple[TemplateAssetSlot, ...] = (
    "body_mask",
    "window_mask",
    "wheel_mask",
    "handle_mask",
    "panel_lines",
)


@dataclass(frozen=True)
class PngImage:
    width: int
    height: int
    bit_depth: int
    color_type: int
    pixels: bytes


def main() -> int:
    errors = validate_template_pack()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(
        f"Validated {len(ALL_TEMPLATE_IDS)} vehicle templates, "
        "including maintained deep templates."
    )
    return 0


def validate_template_pack() -> list[str]:
    errors: list[str] = []
    records = list_vehicle_templates()
    record_ids = tuple(record.id for record in records)
    if record_ids != ALL_TEMPLATE_IDS:
        errors.append(f"template ids {record_ids!r} do not match expected {ALL_TEMPLATE_IDS!r}")

    for record in records:
        errors.extend(_validate_record(record))
    return errors


def _validate_record(record: VehicleTemplateRecord) -> list[str]:
    errors: list[str] = []
    errors.extend(_validate_metadata(record))

    readiness = evaluate_template_readiness(record)
    if not readiness.catalog_eligible:
        errors.append(f"{record.id}: template is not catalog eligible: {readiness.model_dump()!r}")
    if readiness.missing_asset_slots:
        errors.append(f"{record.id}: missing asset slots {readiness.missing_asset_slots!r}")
    if readiness.blocking_reasons:
        errors.append(f"{record.id}: blocking reasons {readiness.blocking_reasons!r}")

    for slot in REQUIRED_TEMPLATE_ASSET_SLOTS:
        resource = template_asset_resource(record.id, slot)
        if not resource.is_file():
            errors.append(f"{record.id}: slot {slot} is missing resource {resource.name}")

    for slot in FULL_SIZE_PNG_SLOTS:
        errors.extend(_validate_png_slot(record, slot, CANVAS_SIZE))
    errors.extend(_validate_png_slot(record, "thumbnail", THUMBNAIL_SIZE))
    errors.extend(_validate_safe_zones(record))
    if record.id == GR86_BRZ_TEMPLATE_ID:
        errors.extend(_validate_deep_vehicle_template(record))
    return errors


def _validate_metadata(record: VehicleTemplateRecord) -> list[str]:
    errors: list[str] = []
    metadata = _read_metadata(record)
    if metadata.get("id") != record.id:
        errors.append(f"{record.id}: template.json id does not match record id")
    if record.id in MVP_TEMPLATE_IDS and (metadata.get("view") != "side" or record.view != "side"):
        errors.append(f"{record.id}: only side-view templates are valid in the MVP pack")
    if metadata.get("canvas_width") != CANVAS_SIZE[0]:
        errors.append(f"{record.id}: canvas_width must be {CANVAS_SIZE[0]}")
    if metadata.get("canvas_height") != CANVAS_SIZE[1]:
        errors.append(f"{record.id}: canvas_height must be {CANVAS_SIZE[1]}")
    if metadata.get("thumbnail_width") != THUMBNAIL_SIZE[0]:
        errors.append(f"{record.id}: thumbnail_width must be {THUMBNAIL_SIZE[0]}")
    if metadata.get("thumbnail_height") != THUMBNAIL_SIZE[1]:
        errors.append(f"{record.id}: thumbnail_height must be {THUMBNAIL_SIZE[1]}")
    if record.source.source_type != "internal_original":
        errors.append(f"{record.id}: source_type must be internal_original")
    if record.source.license_status != "approved":
        errors.append(f"{record.id}: license_status must be approved")
    if not record.source.distribution_allowed:
        errors.append(f"{record.id}: distribution_allowed must be true")
    return errors


def _validate_png_slot(
    record: VehicleTemplateRecord,
    slot: TemplateAssetSlot,
    expected_size: tuple[int, int],
) -> list[str]:
    errors: list[str] = []
    try:
        image = _decode_png(template_asset_resource(record.id, slot).read_bytes())
    except ValueError as exc:
        return [f"{record.id}: slot {slot} is not a valid template PNG: {exc}"]

    if (image.width, image.height) != expected_size:
        errors.append(
            f"{record.id}: slot {slot} size {(image.width, image.height)!r} "
            f"does not match {expected_size!r}",
        )
    if image.bit_depth != 8 or image.color_type != 6:
        errors.append(f"{record.id}: slot {slot} must be 8-bit RGBA PNG")
    if slot in MASK_SLOTS and _alpha_bounds(image) is None:
        errors.append(f"{record.id}: slot {slot} has no non-transparent mask pixels")
    return errors


def _validate_safe_zones(record: VehicleTemplateRecord) -> list[str]:
    errors: list[str] = []
    required_zone_ids = {
        "door-main",
        "front-wheel-arch",
        "rear-quarter",
        "rear-wheel-arch",
        "side-window",
    }
    zone_ids = {str(zone.get("id", "")) for zone in record.safe_zones}
    missing_zone_ids = sorted(required_zone_ids - zone_ids)
    if missing_zone_ids:
        errors.append(f"{record.id}: missing safe zones {missing_zone_ids!r}")

    for zone in record.safe_zones:
        zone_id = str(zone.get("id", "<missing-id>"))
        x = _number(zone.get("x"))
        y = _number(zone.get("y"))
        width = _number(zone.get("width"))
        height = _number(zone.get("height"))
        if x is None or y is None or width is None or height is None:
            errors.append(f"{record.id}: safe zone {zone_id} has non-numeric bounds")
            continue
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            errors.append(f"{record.id}: safe zone {zone_id} has invalid positive bounds")
        if x + width > 1 or y + height > 1:
            errors.append(f"{record.id}: safe zone {zone_id} exceeds normalized canvas")
        if not zone.get("label") or not zone.get("kind"):
            errors.append(f"{record.id}: safe zone {zone_id} requires label and kind")
    return errors


def _validate_deep_vehicle_template(record: VehicleTemplateRecord) -> list[str]:
    errors: list[str] = []
    required_views = {"side", "front", "rear", "top"}
    supported_views = set(record.supported_views)
    if supported_views != required_views:
        errors.append(
            f"{record.id}: supported_views {sorted(supported_views)!r} must be "
            f"{sorted(required_views)!r}",
        )

    for view in sorted(required_views):
        view_assets = record.view_assets.get(view, {})
        base_asset = view_assets.get("base")
        if not base_asset:
            errors.append(f"{record.id}: view {view} requires a base asset")
            continue
        try:
            image = _decode_png(template_pack_root().joinpath(record.id, base_asset).read_bytes())
        except (FileNotFoundError, ValueError) as exc:
            errors.append(f"{record.id}: view {view} base asset is invalid: {exc}")
            continue
        if (image.width, image.height) != CANVAS_SIZE:
            errors.append(
                f"{record.id}: view {view} size {(image.width, image.height)!r} "
                f"does not match {CANVAS_SIZE!r}"
            )

    if not record.sections:
        errors.append(f"{record.id}: sections are required")
    else:
        section_ids = {str(section.get("id", "")) for section in record.sections}
        for required_section in {
            "door-left",
            "front-fender",
            "hood",
            "rear-quarter",
            "roof",
            "trunk",
        }:
            if required_section not in section_ids:
                errors.append(f"{record.id}: missing section {required_section}")
        for section in record.sections:
            errors.extend(_validate_bounded_item(record.id, "section", section))
            if not section.get("views"):
                errors.append(
                    f"{record.id}: section "
                    f"{section.get('id', '<missing-id>')} requires views"
                )
            if not section.get("real_size_mm"):
                errors.append(
                    f"{record.id}: section "
                    f"{section.get('id', '<missing-id>')} requires real_size_mm"
                )

    if not record.forbidden_zones:
        errors.append(f"{record.id}: forbidden_zones are required")
    else:
        for zone in record.forbidden_zones:
            errors.extend(_validate_bounded_item(record.id, "forbidden zone", zone))
            if not zone.get("views"):
                errors.append(
                    f"{record.id}: forbidden zone "
                    f"{zone.get('id', '<missing-id>')} requires views"
                )

    dimensions = record.dimensions or {}
    for field in ("unit", "overall_length", "overall_width", "overall_height", "wheelbase"):
        if field not in dimensions:
            errors.append(f"{record.id}: dimensions.{field} is required")
    if dimensions.get("unit") != "mm":
        errors.append(f"{record.id}: dimensions.unit must be mm")

    scale = record.scale or {}
    if scale.get("unit") != "mm_per_canvas_px":
        errors.append(f"{record.id}: scale.unit must be mm_per_canvas_px")
    for field in ("side_x", "side_y"):
        if _number(scale.get(field)) is None:
            errors.append(f"{record.id}: scale.{field} must be numeric")

    export_config = record.export_config or {}
    if set(export_config.get("formats", [])) != {"svg", "pdf", "png"}:
        errors.append(f"{record.id}: export_config.formats must be svg/pdf/png")
    for field in ("bleed_mm", "safe_margin_mm"):
        if _number(export_config.get(field)) is None:
            errors.append(f"{record.id}: export_config.{field} must be numeric")
    if not export_config.get("layer_prefix"):
        errors.append(f"{record.id}: export_config.layer_prefix is required")

    authorization = record.authorization or {}
    for field in ("source", "scope", "reviewer", "version"):
        if not authorization.get(field):
            errors.append(f"{record.id}: authorization.{field} is required")
    if "commercial_use" not in authorization:
        errors.append(f"{record.id}: authorization.commercial_use is required")
    return errors


def _validate_bounded_item(record_id: str, label: str, item: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    item_id = str(item.get("id", "<missing-id>"))
    bounds = item.get("bounds")
    if not isinstance(bounds, dict):
        return [f"{record_id}: {label} {item_id} requires bounds"]
    x = _number(bounds.get("x"))
    y = _number(bounds.get("y"))
    width = _number(bounds.get("width"))
    height = _number(bounds.get("height"))
    if x is None or y is None or width is None or height is None:
        errors.append(f"{record_id}: {label} {item_id} has non-numeric bounds")
    elif x < 0 or y < 0 or width <= 0 or height <= 0 or x + width > 1 or y + height > 1:
        errors.append(f"{record_id}: {label} {item_id} bounds exceed normalized canvas")
    if not item.get("label"):
        errors.append(f"{record_id}: {label} {item_id} requires label")
    return errors


def _read_metadata(record: VehicleTemplateRecord) -> dict[str, Any]:
    value = json.loads(template_asset_resource(record.id, "metadata").read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{record.id}: template metadata must be a JSON object")
    return value


def _decode_png(data: bytes) -> PngImage:
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("missing PNG signature")

    offset = len(PNG_SIGNATURE)
    width = 0
    height = 0
    bit_depth = 0
    color_type = 0
    idat_parts: list[bytes] = []

    while offset < len(data):
        if offset + 8 > len(data):
            raise ValueError("truncated chunk header")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_type = data[offset + 4 : offset + 8]
        chunk_start = offset + 8
        chunk_end = chunk_start + length
        crc_end = chunk_end + 4
        if crc_end > len(data):
            raise ValueError(f"truncated {chunk_type.decode('ascii', errors='replace')} chunk")
        payload = data[chunk_start:chunk_end]
        offset = crc_end

        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, _, _, _ = struct.unpack(">IIBBBBB", payload)
        elif chunk_type == b"IDAT":
            idat_parts.append(payload)
        elif chunk_type == b"IEND":
            break

    if width <= 0 or height <= 0:
        raise ValueError("missing IHDR")
    if bit_depth != 8 or color_type != 6:
        raise ValueError("only 8-bit RGBA PNG is supported")

    stride = width * 4
    raw = zlib.decompress(b"".join(idat_parts))
    expected_length = height * (stride + 1)
    if len(raw) != expected_length:
        raise ValueError("unexpected decompressed pixel length")

    pixels = bytearray(width * height * 4)
    for row in range(height):
        raw_start = row * (stride + 1)
        filter_type = raw[raw_start]
        if filter_type != 0:
            raise ValueError("template PNG must use filter type 0")
        row_start = row * stride
        pixels[row_start : row_start + stride] = raw[raw_start + 1 : raw_start + 1 + stride]

    return PngImage(
        bit_depth=bit_depth,
        color_type=color_type,
        height=height,
        pixels=bytes(pixels),
        width=width,
    )


def _alpha_bounds(image: PngImage) -> tuple[int, int, int, int] | None:
    left = image.width
    top = image.height
    right = -1
    bottom = -1
    for y in range(image.height):
        for x in range(image.width):
            alpha = image.pixels[((y * image.width + x) * 4) + 3]
            if alpha == 0:
                continue
            left = min(left, x)
            top = min(top, y)
            right = max(right, x)
            bottom = max(bottom, y)
    if right < left or bottom < top:
        return None
    return (left, top, right, bottom)


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)


if __name__ == "__main__":
    raise SystemExit(main())
