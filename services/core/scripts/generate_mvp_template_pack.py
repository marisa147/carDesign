from __future__ import annotations

import binascii
import json
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

CANVAS_SIZE = (1536, 768)
THUMBNAIL_SIZE = (384, 192)
PACK_ROOT = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "caragent_core"
    / "generation"
    / "template_pack"
    / "mvp_generic_side_v1"
)

Color = tuple[int, int, int, int]
Point = tuple[float, float]
Rect = tuple[float, float, float, float]
Ellipse = tuple[float, float, float, float]
RenderMode = Literal[
    "base",
    "body_mask",
    "window_mask",
    "wheel_mask",
    "handle_mask",
    "panel_lines",
]

ASSET_SLOTS = {
    "base": "base.png",
    "body_mask": "body_mask.png",
    "handle_mask": "handle_mask.png",
    "metadata": "template.json",
    "panel_lines": "panel_lines.png",
    "safe_zones": "safe_zones.json",
    "thumbnail": "thumbnail.png",
    "wheel_mask": "wheel_mask.png",
    "window_mask": "window_mask.png",
}


@dataclass(frozen=True)
class TemplateSpec:
    id: str
    label: str
    body: tuple[Point, ...]
    windows: tuple[tuple[Point, ...], ...]
    wheels: tuple[Ellipse, ...]
    handles: tuple[Rect, ...]
    panel_lines: tuple[tuple[Point, ...], ...]
    safe_zones: tuple[dict[str, object], ...]
    body_color: Color
    aliases: tuple[str, ...] = ()


TEMPLATES: tuple[TemplateSpec, ...] = (
    TemplateSpec(
        aliases=("generic-side-coupe",),
        body=(
            (0.11, 0.64),
            (0.16, 0.50),
            (0.27, 0.43),
            (0.37, 0.31),
            (0.55, 0.31),
            (0.68, 0.47),
            (0.86, 0.52),
            (0.91, 0.63),
            (0.83, 0.70),
            (0.17, 0.70),
        ),
        body_color=(217, 226, 234, 255),
        handles=((0.49, 0.49, 0.035, 0.012),),
        id="generic_coupe_side_v1",
        label="Generic coupe side-view",
        panel_lines=(
            ((0.31, 0.43), (0.30, 0.68)),
            ((0.58, 0.46), (0.61, 0.68)),
            ((0.18, 0.57), (0.84, 0.57)),
        ),
        safe_zones=(
            {
                "height": 0.24,
                "id": "door-main",
                "kind": "body",
                "label": "Door / main side panel",
                "width": 0.32,
                "x": 0.33,
                "y": 0.45,
            },
            {
                "height": 0.16,
                "id": "side-window",
                "kind": "window",
                "label": "Side window",
                "width": 0.31,
                "x": 0.31,
                "y": 0.30,
            },
            {
                "height": 0.18,
                "id": "front-wheel-arch",
                "kind": "risky",
                "label": "Front wheel arch",
                "width": 0.14,
                "x": 0.16,
                "y": 0.56,
            },
            {
                "height": 0.18,
                "id": "rear-wheel-arch",
                "kind": "risky",
                "label": "Rear wheel arch",
                "width": 0.14,
                "x": 0.70,
                "y": 0.56,
            },
            {
                "height": 0.20,
                "id": "rear-quarter",
                "kind": "body",
                "label": "Rear quarter panel",
                "width": 0.18,
                "x": 0.64,
                "y": 0.44,
            },
        ),
        wheels=((0.24, 0.69, 0.07, 0.095), (0.76, 0.69, 0.07, 0.095)),
        windows=(
            ((0.33, 0.33), (0.45, 0.33), (0.45, 0.45), (0.27, 0.45)),
            ((0.47, 0.33), (0.55, 0.34), (0.64, 0.46), (0.47, 0.45)),
        ),
    ),
    TemplateSpec(
        body=(
            (0.09, 0.65),
            (0.15, 0.52),
            (0.28, 0.46),
            (0.36, 0.34),
            (0.58, 0.34),
            (0.70, 0.47),
            (0.87, 0.52),
            (0.92, 0.64),
            (0.84, 0.71),
            (0.16, 0.71),
        ),
        body_color=(224, 229, 220, 255),
        handles=((0.42, 0.50, 0.03, 0.012), (0.57, 0.50, 0.03, 0.012)),
        id="generic_sedan_side_v1",
        label="Generic sedan side-view",
        panel_lines=(
            ((0.31, 0.46), (0.30, 0.69)),
            ((0.50, 0.40), (0.50, 0.69)),
            ((0.67, 0.48), (0.68, 0.69)),
            ((0.17, 0.58), (0.85, 0.58)),
        ),
        safe_zones=(
            {
                "height": 0.23,
                "id": "door-main",
                "kind": "body",
                "label": "Front and rear doors",
                "width": 0.36,
                "x": 0.33,
                "y": 0.46,
            },
            {
                "height": 0.15,
                "id": "side-window",
                "kind": "window",
                "label": "Cabin window band",
                "width": 0.36,
                "x": 0.31,
                "y": 0.34,
            },
            {
                "height": 0.18,
                "id": "front-wheel-arch",
                "kind": "risky",
                "label": "Front wheel arch",
                "width": 0.14,
                "x": 0.15,
                "y": 0.57,
            },
            {
                "height": 0.18,
                "id": "rear-wheel-arch",
                "kind": "risky",
                "label": "Rear wheel arch",
                "width": 0.14,
                "x": 0.72,
                "y": 0.57,
            },
            {
                "height": 0.20,
                "id": "rear-quarter",
                "kind": "body",
                "label": "Rear quarter panel",
                "width": 0.16,
                "x": 0.68,
                "y": 0.46,
            },
        ),
        wheels=((0.23, 0.70, 0.07, 0.095), (0.78, 0.70, 0.07, 0.095)),
        windows=(
            ((0.34, 0.36), (0.46, 0.36), (0.46, 0.47), (0.29, 0.47)),
            ((0.48, 0.36), (0.58, 0.37), (0.66, 0.48), (0.48, 0.47)),
        ),
    ),
    TemplateSpec(
        body=(
            (0.10, 0.66),
            (0.16, 0.52),
            (0.31, 0.45),
            (0.39, 0.34),
            (0.56, 0.34),
            (0.69, 0.46),
            (0.82, 0.50),
            (0.88, 0.63),
            (0.80, 0.71),
            (0.17, 0.71),
        ),
        body_color=(229, 220, 235, 255),
        handles=((0.43, 0.50, 0.03, 0.012), (0.58, 0.50, 0.03, 0.012)),
        id="generic_hatchback_side_v1",
        label="Generic hatchback side-view",
        panel_lines=(
            ((0.32, 0.45), (0.31, 0.69)),
            ((0.52, 0.39), (0.53, 0.69)),
            ((0.69, 0.47), (0.78, 0.68)),
            ((0.18, 0.58), (0.80, 0.58)),
        ),
        safe_zones=(
            {
                "height": 0.23,
                "id": "door-main",
                "kind": "body",
                "label": "Door / compact side panel",
                "width": 0.33,
                "x": 0.34,
                "y": 0.46,
            },
            {
                "height": 0.15,
                "id": "side-window",
                "kind": "window",
                "label": "Cabin window band",
                "width": 0.34,
                "x": 0.31,
                "y": 0.34,
            },
            {
                "height": 0.18,
                "id": "front-wheel-arch",
                "kind": "risky",
                "label": "Front wheel arch",
                "width": 0.14,
                "x": 0.16,
                "y": 0.57,
            },
            {
                "height": 0.18,
                "id": "rear-wheel-arch",
                "kind": "risky",
                "label": "Rear wheel arch",
                "width": 0.14,
                "x": 0.67,
                "y": 0.57,
            },
            {
                "height": 0.20,
                "id": "rear-quarter",
                "kind": "body",
                "label": "Rear hatch quarter panel",
                "width": 0.14,
                "x": 0.64,
                "y": 0.45,
            },
        ),
        wheels=((0.24, 0.70, 0.07, 0.095), (0.73, 0.70, 0.07, 0.095)),
        windows=(
            ((0.35, 0.36), (0.46, 0.36), (0.46, 0.47), (0.30, 0.47)),
            ((0.48, 0.36), (0.58, 0.37), (0.66, 0.48), (0.48, 0.47)),
        ),
    ),
    TemplateSpec(
        body=(
            (0.08, 0.66),
            (0.13, 0.45),
            (0.25, 0.37),
            (0.35, 0.27),
            (0.70, 0.27),
            (0.86, 0.42),
            (0.92, 0.62),
            (0.84, 0.72),
            (0.16, 0.72),
        ),
        body_color=(219, 232, 232, 255),
        handles=((0.43, 0.48, 0.03, 0.012), (0.61, 0.48, 0.03, 0.012)),
        id="generic_suv_side_v1",
        label="Generic SUV side-view",
        panel_lines=(
            ((0.31, 0.39), (0.30, 0.70)),
            ((0.52, 0.32), (0.52, 0.70)),
            ((0.72, 0.38), (0.73, 0.70)),
            ((0.16, 0.57), (0.86, 0.57)),
        ),
        safe_zones=(
            {
                "height": 0.27,
                "id": "door-main",
                "kind": "body",
                "label": "Tall door side panel",
                "width": 0.40,
                "x": 0.31,
                "y": 0.43,
            },
            {
                "height": 0.17,
                "id": "side-window",
                "kind": "window",
                "label": "Tall cabin window band",
                "width": 0.43,
                "x": 0.28,
                "y": 0.28,
            },
            {
                "height": 0.19,
                "id": "front-wheel-arch",
                "kind": "risky",
                "label": "Front wheel arch",
                "width": 0.14,
                "x": 0.15,
                "y": 0.58,
            },
            {
                "height": 0.19,
                "id": "rear-wheel-arch",
                "kind": "risky",
                "label": "Rear wheel arch",
                "width": 0.14,
                "x": 0.73,
                "y": 0.58,
            },
            {
                "height": 0.23,
                "id": "rear-quarter",
                "kind": "body",
                "label": "Rear quarter panel",
                "width": 0.16,
                "x": 0.69,
                "y": 0.44,
            },
        ),
        wheels=((0.23, 0.70, 0.075, 0.105), (0.79, 0.70, 0.075, 0.105)),
        windows=(
            ((0.31, 0.30), (0.47, 0.30), (0.47, 0.45), (0.24, 0.45)),
            ((0.49, 0.30), (0.67, 0.31), (0.76, 0.45), (0.49, 0.45)),
        ),
    ),
    TemplateSpec(
        body=(
            (0.08, 0.67),
            (0.11, 0.39),
            (0.19, 0.28),
            (0.78, 0.28),
            (0.88, 0.39),
            (0.92, 0.66),
            (0.84, 0.73),
            (0.16, 0.73),
        ),
        body_color=(235, 228, 214, 255),
        handles=((0.39, 0.48, 0.03, 0.012), (0.59, 0.48, 0.03, 0.012)),
        id="generic_van_side_v1",
        label="Generic van side-view",
        panel_lines=(
            ((0.28, 0.31), (0.28, 0.71)),
            ((0.51, 0.29), (0.51, 0.71)),
            ((0.75, 0.31), (0.76, 0.71)),
            ((0.15, 0.56), (0.86, 0.56)),
        ),
        safe_zones=(
            {
                "height": 0.29,
                "id": "door-main",
                "kind": "body",
                "label": "Large van side panel",
                "width": 0.43,
                "x": 0.30,
                "y": 0.42,
            },
            {
                "height": 0.17,
                "id": "side-window",
                "kind": "window",
                "label": "Van window band",
                "width": 0.47,
                "x": 0.25,
                "y": 0.30,
            },
            {
                "height": 0.18,
                "id": "front-wheel-arch",
                "kind": "risky",
                "label": "Front wheel arch",
                "width": 0.14,
                "x": 0.16,
                "y": 0.59,
            },
            {
                "height": 0.18,
                "id": "rear-wheel-arch",
                "kind": "risky",
                "label": "Rear wheel arch",
                "width": 0.14,
                "x": 0.72,
                "y": 0.59,
            },
            {
                "height": 0.24,
                "id": "rear-quarter",
                "kind": "body",
                "label": "Rear cargo quarter panel",
                "width": 0.18,
                "x": 0.67,
                "y": 0.44,
            },
        ),
        wheels=((0.23, 0.71, 0.07, 0.095), (0.78, 0.71, 0.07, 0.095)),
        windows=(
            ((0.25, 0.31), (0.43, 0.31), (0.43, 0.46), (0.20, 0.46)),
            ((0.46, 0.31), (0.69, 0.31), (0.74, 0.46), (0.46, 0.46)),
        ),
    ),
)


def main() -> None:
    PACK_ROOT.mkdir(parents=True, exist_ok=True)
    for spec in TEMPLATES:
        output_dir = PACK_ROOT / spec.id
        output_dir.mkdir(parents=True, exist_ok=True)
        _write_template_files(spec, output_dir)


def _write_template_files(spec: TemplateSpec, output_dir: Path) -> None:
    _write_json(output_dir / "template.json", _template_metadata(spec))
    _write_json(output_dir / "safe_zones.json", list(spec.safe_zones))

    for mode in (
        "base",
        "body_mask",
        "window_mask",
        "wheel_mask",
        "handle_mask",
        "panel_lines",
    ):
        pixels = _render_template(spec, CANVAS_SIZE, mode)
        _write_png(output_dir / ASSET_SLOTS[mode], CANVAS_SIZE, pixels)

    thumbnail = _render_template(spec, THUMBNAIL_SIZE, "base")
    _write_png(output_dir / "thumbnail.png", THUMBNAIL_SIZE, thumbnail)


def _template_metadata(spec: TemplateSpec) -> dict[str, object]:
    return {
        "aliases": list(spec.aliases),
        "asset_slots": ASSET_SLOTS,
        "canvas_height": CANVAS_SIZE[1],
        "canvas_width": CANVAS_SIZE[0],
        "id": spec.id,
        "label": spec.label,
        "source": {
            "allowed_usage_scope": "mvp_concept_preview",
            "audit_timestamp": "2026-06-19T14:40:00Z",
            "distribution_allowed": True,
            "license_evidence": "internal-mvp-generic-template-pack-v1",
            "license_status": "approved",
            "rights_notes": (
                "Internal generic side-view silhouette generated from geometric primitives "
                "for concept preview templates."
            ),
            "source_type": "internal_original",
        },
        "thumbnail_height": THUMBNAIL_SIZE[1],
        "thumbnail_width": THUMBNAIL_SIZE[0],
        "view": "side",
    }


def _render_template(spec: TemplateSpec, size: tuple[int, int], mode: RenderMode) -> bytearray:
    width, height = size
    pixels = bytearray(width * height * 4)

    if mode == "base":
        _fill_ellipse(pixels, size, (0.50, 0.73, 0.43, 0.035), (0, 0, 0, 38))
        _fill_polygon(pixels, size, spec.body, spec.body_color)
        for window in spec.windows:
            _fill_polygon(pixels, size, window, (151, 176, 190, 230))
        for wheel in spec.wheels:
            _fill_ellipse(pixels, size, wheel, (34, 38, 42, 255))
            _fill_ellipse(
                pixels,
                size,
                (wheel[0], wheel[1], wheel[2] * 0.44, wheel[3] * 0.44),
                (133, 142, 150, 255),
            )
        for handle in spec.handles:
            _fill_rect(pixels, size, handle, (64, 72, 80, 255))
        _draw_panel_lines(pixels, size, spec)
        return pixels

    if mode == "body_mask":
        _fill_polygon(pixels, size, spec.body, (255, 255, 255, 255))
    elif mode == "window_mask":
        for window in spec.windows:
            _fill_polygon(pixels, size, window, (255, 255, 255, 255))
    elif mode == "wheel_mask":
        for wheel in spec.wheels:
            _fill_ellipse(pixels, size, wheel, (255, 255, 255, 255))
    elif mode == "handle_mask":
        for handle in spec.handles:
            _fill_rect(pixels, size, handle, (255, 255, 255, 255))
    elif mode == "panel_lines":
        _draw_panel_lines(pixels, size, spec)
    return pixels


def _draw_panel_lines(pixels: bytearray, size: tuple[int, int], spec: TemplateSpec) -> None:
    _draw_polyline(pixels, size, (*spec.body, spec.body[0]), (54, 62, 70, 255), 3)
    for line in spec.panel_lines:
        _draw_polyline(pixels, size, line, (54, 62, 70, 230), 2)
    for window in spec.windows:
        _draw_polyline(pixels, size, (*window, window[0]), (54, 62, 70, 220), 2)


def _fill_polygon(
    pixels: bytearray,
    size: tuple[int, int],
    points: tuple[Point, ...],
    color: Color,
) -> None:
    width, height = size
    vertices = [(_to_px(x, width), _to_px(y, height)) for x, y in points]
    min_y = max(min(y for _, y in vertices), 0)
    max_y = min(max(y for _, y in vertices), height - 1)

    for y in range(min_y, max_y + 1):
        intersections: list[float] = []
        for index, (x1, y1) in enumerate(vertices):
            x2, y2 = vertices[(index + 1) % len(vertices)]
            if y1 == y2:
                continue
            edge_min_y = min(y1, y2)
            edge_max_y = max(y1, y2)
            if edge_min_y <= y < edge_max_y:
                intersections.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        intersections.sort()
        for start, end in zip(intersections[0::2], intersections[1::2], strict=False):
            _fill_span(pixels, size, y, int(round(start)), int(round(end)), color)


def _fill_ellipse(
    pixels: bytearray,
    size: tuple[int, int],
    ellipse: Ellipse,
    color: Color,
) -> None:
    width, height = size
    cx = _to_px(ellipse[0], width)
    cy = _to_px(ellipse[1], height)
    rx = max(1, int(round(ellipse[2] * (width - 1))))
    ry = max(1, int(round(ellipse[3] * (height - 1))))
    for y in range(max(0, cy - ry), min(height, cy + ry + 1)):
        yy = ((y - cy) / ry) ** 2
        for x in range(max(0, cx - rx), min(width, cx + rx + 1)):
            if ((x - cx) / rx) ** 2 + yy <= 1:
                _set_pixel(pixels, size, x, y, color)


def _fill_rect(
    pixels: bytearray,
    size: tuple[int, int],
    rect: Rect,
    color: Color,
) -> None:
    width, height = size
    x = _to_px(rect[0], width)
    y = _to_px(rect[1], height)
    rect_width = max(1, int(round(rect[2] * (width - 1))))
    rect_height = max(1, int(round(rect[3] * (height - 1))))
    for row in range(max(0, y), min(height, y + rect_height)):
        _fill_span(pixels, size, row, x, x + rect_width, color)


def _draw_polyline(
    pixels: bytearray,
    size: tuple[int, int],
    points: tuple[Point, ...],
    color: Color,
    width: int,
) -> None:
    for start, end in zip(points, points[1:], strict=False):
        _draw_line(pixels, size, start, end, color, width)


def _draw_line(
    pixels: bytearray,
    size: tuple[int, int],
    start: Point,
    end: Point,
    color: Color,
    width: int,
) -> None:
    canvas_width, canvas_height = size
    x1 = _to_px(start[0], canvas_width)
    y1 = _to_px(start[1], canvas_height)
    x2 = _to_px(end[0], canvas_width)
    y2 = _to_px(end[1], canvas_height)
    dx = abs(x2 - x1)
    sx = 1 if x1 < x2 else -1
    dy = -abs(y2 - y1)
    sy = 1 if y1 < y2 else -1
    error = dx + dy
    x = x1
    y = y1

    while True:
        _stamp(pixels, size, x, y, width, color)
        if x == x2 and y == y2:
            break
        e2 = 2 * error
        if e2 >= dy:
            error += dy
            x += sx
        if e2 <= dx:
            error += dx
            y += sy


def _stamp(
    pixels: bytearray,
    size: tuple[int, int],
    x: int,
    y: int,
    width: int,
    color: Color,
) -> None:
    radius = max(0, width // 2)
    for row in range(y - radius, y + radius + 1):
        for column in range(x - radius, x + radius + 1):
            _set_pixel(pixels, size, column, row, color)


def _fill_span(
    pixels: bytearray,
    size: tuple[int, int],
    y: int,
    start_x: int,
    end_x: int,
    color: Color,
) -> None:
    width, _ = size
    for x in range(max(0, start_x), min(width, end_x + 1)):
        _set_pixel(pixels, size, x, y, color)


def _set_pixel(
    pixels: bytearray,
    size: tuple[int, int],
    x: int,
    y: int,
    color: Color,
) -> None:
    width, height = size
    if x < 0 or y < 0 or x >= width or y >= height:
        return
    index = (y * width + x) * 4
    pixels[index : index + 4] = bytes(color)


def _to_px(value: float, size: int) -> int:
    return int(round(value * (size - 1)))


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_png(path: Path, size: tuple[int, int], pixels: bytearray) -> None:
    path.write_bytes(_encode_png(size, pixels))


def _encode_png(size: tuple[int, int], pixels: bytearray) -> bytes:
    width, height = size
    stride = width * 4
    raw = bytearray()
    for row in range(height):
        raw.append(0)
        start = row * stride
        raw.extend(pixels[start : start + stride])
    return b"".join(
        (
            b"\x89PNG\r\n\x1a\n",
            _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)),
            _png_chunk(b"IDAT", zlib.compress(bytes(raw), level=9)),
            _png_chunk(b"IEND", b""),
        ),
    )


def _png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    checksum = binascii.crc32(chunk_type)
    checksum = binascii.crc32(payload, checksum) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", checksum)


if __name__ == "__main__":
    main()
