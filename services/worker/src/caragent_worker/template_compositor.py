from __future__ import annotations

from hashlib import sha256
from io import BytesIO
from typing import Literal

from caragent_core.generation import (
    DEFAULT_TEMPLATE_ID,
    TemplateCompositionRequest,
    TemplateCompositionResult,
    template_asset_resource,
)
from caragent_core.generation.compositor import JsonObject
from caragent_core.generation.templates import TemplateAssetSlot
from PIL import Image, ImageChops, ImageDraw

TEMPLATE_IMAGE_SLOTS: list[TemplateAssetSlot] = [
    "base",
    "body_mask",
    "window_mask",
    "wheel_mask",
    "handle_mask",
    "panel_lines",
]
PROTECTED_MASK_SLOTS: list[TemplateAssetSlot] = ["window_mask", "wheel_mask", "handle_mask"]
OverlayKind = Literal["text", "logo"]


class PillowTemplateCompositor:
    def compose(self, request: TemplateCompositionRequest) -> TemplateCompositionResult:
        template_id = _template_id_from_payload(request.prompt_payload)
        base = _load_rgba(template_id, "base")
        body_mask = _load_alpha(template_id, "body_mask")
        panel_lines = _load_rgba(template_id, "panel_lines")
        protected_mask = _protected_mask(template_id, base.size)
        decoration_mask = ImageChops.subtract(body_mask, protected_mask)

        image = base.copy()
        image = _apply_body_tint(
            image,
            decoration_mask,
            _palette_colors(request.prompt_payload, fallback_seed=_prompt_seed(request)),
        )
        image = _apply_preview_overlays(image, decoration_mask, request.prompt_payload)
        image = Image.alpha_composite(image, panel_lines)

        if image.size != (request.width, request.height):
            image = image.resize((request.width, request.height), Image.Resampling.LANCZOS)

        output = BytesIO()
        image.save(output, format="PNG")
        return TemplateCompositionResult(
            content_type="image/png",
            height=request.height,
            image_bytes=output.getvalue(),
            metadata={
                "asset_slots": list(TEMPLATE_IMAGE_SLOTS),
                "decorative_mask_pixels": _nonzero_alpha_count(decoration_mask),
                "protected_mask_slots": list(PROTECTED_MASK_SLOTS),
                "template_id": template_id,
            },
            width=request.width,
        )


def _apply_body_tint(
    image: Image.Image,
    decoration_mask: Image.Image,
    colors: list[tuple[int, int, int]],
) -> Image.Image:
    tinted = Image.new("RGBA", image.size, (*colors[0], 62))
    clipped = Image.new("RGBA", image.size, (0, 0, 0, 0))
    clipped.paste(tinted, (0, 0), decoration_mask)
    return Image.alpha_composite(image, clipped)


def _apply_preview_overlays(
    image: Image.Image,
    decoration_mask: Image.Image,
    prompt_payload: JsonObject,
) -> Image.Image:
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    preview_spec = _preview_spec_from_payload(prompt_payload)
    safe_zones = _safe_zone_lookup(preview_spec)
    colors = _palette_colors(prompt_payload, fallback_seed=repr(prompt_payload))

    _draw_palette_stripes(draw, image.size[0], image.size[1], safe_zones, colors)
    for layer in _json_list(preview_spec.get("overlay_layers")):
        if not isinstance(layer, dict) or layer.get("visible") is False:
            continue
        kind = str(layer.get("kind", ""))
        if kind == "text":
            _draw_overlay_layer(draw, image.size[0], image.size[1], layer, safe_zones, "text")
        elif kind == "logo":
            _draw_overlay_layer(draw, image.size[0], image.size[1], layer, safe_zones, "logo")

    clipped = Image.new("RGBA", image.size, (0, 0, 0, 0))
    clipped.paste(overlay, (0, 0), decoration_mask)
    return Image.alpha_composite(image, clipped)


def _draw_palette_stripes(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    safe_zones: dict[str, JsonObject],
    colors: list[tuple[int, int, int]],
) -> None:
    zone = safe_zones.get("door-main") or {"height": 0.24, "width": 0.34, "x": 0.32, "y": 0.47}
    box = _zone_box(zone, width, height)
    stripe_height = max(6, (box[3] - box[1]) // max(2, len(colors)))
    for index, color in enumerate(colors[:5]):
        y0 = box[1] + index * stripe_height
        draw.rectangle((box[0], y0, box[2], y0 + stripe_height), fill=(*color, 120))


def _draw_overlay_layer(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    layer: JsonObject,
    safe_zones: dict[str, JsonObject],
    kind: OverlayKind,
) -> None:
    box = _zone_box(_layer_zone(layer, safe_zones), width, height)
    opacity = _normalized_float(layer.get("opacity"), fallback=1.0)
    alpha = max(32, min(230, int(opacity * 210)))
    if kind == "text":
        text = str(layer.get("text", "")).strip()
        if not text:
            return
        draw.rounded_rectangle(box, radius=max(4, height // 80), fill=(32, 38, 42, alpha))
        draw.text(
            (box[0] + max(6, width // 96), box[1] + max(4, height // 72)),
            text[:32],
            fill=(250, 250, 246, 255),
        )
        return

    draw.rounded_rectangle(
        box,
        radius=max(4, height // 80),
        fill=(250, 250, 246, alpha),
        outline=(28, 32, 36, 220),
        width=max(1, width // 260),
    )
    draw.text(
        (box[0] + max(5, width // 100), box[1] + max(4, height // 80)),
        "LOGO",
        fill=(28, 32, 36, 255),
    )


def _template_id_from_payload(prompt_payload: JsonObject) -> str:
    template = prompt_payload.get("vehicle_template")
    if not isinstance(template, dict):
        preview_spec = _preview_spec_from_payload(prompt_payload)
        preview_template = preview_spec.get("template")
        template = preview_template if isinstance(preview_template, dict) else {}
    template_id = _text(template.get("id"))
    return template_id or DEFAULT_TEMPLATE_ID


def _preview_spec_from_payload(prompt_payload: JsonObject) -> JsonObject:
    preview_spec = prompt_payload.get("preview_spec")
    return dict(preview_spec) if isinstance(preview_spec, dict) else {}


def _safe_zone_lookup(preview_spec: JsonObject) -> dict[str, JsonObject]:
    zones: dict[str, JsonObject] = {}
    for zone in _json_list(preview_spec.get("safe_zones")):
        if isinstance(zone, dict):
            zone_id = str(zone.get("id", "")).strip()
            if zone_id:
                zones[zone_id] = dict(zone)
    return zones


def _layer_zone(layer: JsonObject, safe_zones: dict[str, JsonObject]) -> JsonObject:
    if all(_is_number(layer.get(field)) for field in ("x", "y", "width", "height")):
        return {
            "height": float(layer["height"]),
            "width": float(layer["width"]),
            "x": float(layer["x"]),
            "y": float(layer["y"]),
        }
    zone = safe_zones.get(str(layer.get("zone_id", "")))
    if zone is not None:
        return zone
    return {"height": 0.18, "width": 0.3, "x": 0.35, "y": 0.5}


def _zone_box(zone: JsonObject, width: int, height: int) -> tuple[int, int, int, int]:
    x = _normalized_float(zone.get("x"), fallback=0.35)
    y = _normalized_float(zone.get("y"), fallback=0.5)
    zone_width = _normalized_float(zone.get("width"), fallback=0.3)
    zone_height = _normalized_float(zone.get("height"), fallback=0.18)
    return (
        int(width * x),
        int(height * y),
        int(width * (x + zone_width)),
        int(height * (y + zone_height)),
    )


def _palette_colors(
    prompt_payload: JsonObject,
    *,
    fallback_seed: str,
) -> list[tuple[int, int, int]]:
    brief = prompt_payload.get("brief")
    palette = brief.get("palette") if isinstance(brief, dict) else None
    tokens = (
        [str(value) for value in palette if str(value).strip()]
        if isinstance(palette, list)
        else []
    )
    if not tokens:
        tokens = [fallback_seed[index : index + 8] for index in range(0, 24, 8)]
    return [_color_from_token(token) for token in tokens]


def _color_from_token(token: str) -> tuple[int, int, int]:
    digest = sha256(token.lower().encode("utf-8")).digest()
    return 80 + digest[0] % 150, 80 + digest[1] % 150, 80 + digest[2] % 150


def _prompt_seed(request: TemplateCompositionRequest) -> str:
    return sha256((request.prompt_text + repr(request.prompt_payload)).encode("utf-8")).hexdigest()


def _load_rgba(template_id: str, slot: TemplateAssetSlot) -> Image.Image:
    return Image.open(
        BytesIO(template_asset_resource(template_id, slot).read_bytes()),
    ).convert("RGBA")


def _load_alpha(template_id: str, slot: TemplateAssetSlot) -> Image.Image:
    return _load_rgba(template_id, slot).getchannel("A")


def _protected_mask(template_id: str, size: tuple[int, int]) -> Image.Image:
    protected = Image.new("L", size, 0)
    for slot in PROTECTED_MASK_SLOTS:
        protected = ImageChops.lighter(protected, _load_alpha(template_id, slot))
    return protected


def _nonzero_alpha_count(mask: Image.Image) -> int:
    histogram = mask.histogram()
    return sum(histogram[1:])


def _normalized_float(value: object, *, fallback: float) -> float:
    if isinstance(value, int | float):
        return min(1.0, max(0.0, float(value)))
    return fallback


def _is_number(value: object) -> bool:
    return isinstance(value, int | float)


def _json_list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _text(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None