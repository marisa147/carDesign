from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
from io import BytesIO
from typing import Any

from PIL import Image, ImageDraw

from caragent_worker.providers.base import (
    ImageGenerationRequest,
    ImageGenerationResult,
    JsonObject,
)

LOCAL_PROVIDER = "local-deterministic"
LOCAL_MODEL = "local-concept-v1"


class LocalDeterministicImageProvider:
    def __init__(
        self,
        *,
        width: int = 1536,
        height: int = 768,
        provider: str = LOCAL_PROVIDER,
        model: str = LOCAL_MODEL,
    ) -> None:
        self._width = width
        self._height = height
        self._provider = provider
        self._model = model

    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        image_bytes = _render_concept_preview(request, width=self._width, height=self._height)
        preview_spec = _preview_spec_from_payload(request.prompt_payload)
        reference_warnings = _json_list(request.prompt_payload.get("reference_warnings"))
        metadata: JsonObject = {
            "concept_label": request.concept_label,
            "external_calls": False,
            "height": self._height,
            "input_artifact_ids": list(request.input_artifact_ids),
            "overlay_layer_count": len(_json_list(preview_spec.get("overlay_layers"))),
            "preview_spec": preview_spec,
            "prompt_digest": sha256(request.prompt_text.encode("utf-8")).hexdigest(),
            "reference_warning_count": _integer_from_payload(
                request.prompt_payload.get("reference_warning_count"),
                fallback=len(reference_warnings),
            ),
            "reference_warnings": reference_warnings,
            "safe_zone_count": len(_json_list(preview_spec.get("safe_zones"))),
            "warning_count": len(_json_list(preview_spec.get("warnings"))),
            "width": self._width,
        }
        if request.reference_usage is not None:
            metadata["reference_usage"] = dict(request.reference_usage)

        return ImageGenerationResult(
            actual_cost=Decimal("0.0000"),
            content_type="image/png",
            estimated_cost=Decimal("0.0000"),
            height=self._height,
            image_bytes=image_bytes,
            metadata=metadata,
            model=self._model,
            provider=self._provider,
            width=self._width,
        )


def render_local_concept_preview(
    request: ImageGenerationRequest,
    *,
    width: int,
    height: int,
) -> bytes:
    return _render_concept_preview(request, width=width, height=height)


def _render_concept_preview(
    request: ImageGenerationRequest,
    *,
    width: int,
    height: int,
) -> bytes:
    image = Image.new("RGB", (width, height), (248, 248, 244))
    draw = ImageDraw.Draw(image)

    prompt_hash = sha256(
        (request.prompt_text + repr(request.prompt_payload)).encode("utf-8"),
    ).hexdigest()
    accent_colors = _palette_colors(request.prompt_payload, fallback_seed=prompt_hash)

    draw.rectangle((0, 0, width, height), fill=(248, 248, 244))
    draw.rectangle((0, int(height * 0.72), width, height), fill=(222, 225, 221))
    draw.rounded_rectangle(
        (
            int(width * 0.09),
            int(height * 0.36),
            int(width * 0.91),
            int(height * 0.72),
        ),
        radius=max(12, int(height * 0.08)),
        fill=(244, 244, 239),
        outline=(32, 38, 42),
        width=max(2, width // 180),
    )
    draw.rectangle(
        (
            int(width * 0.22),
            int(height * 0.28),
            int(width * 0.64),
            int(height * 0.44),
        ),
        fill=(225, 231, 232),
        outline=(32, 38, 42),
        width=max(2, width // 220),
    )

    stripe_top = int(height * 0.49)
    stripe_height = max(12, int(height * 0.05))
    for index, color in enumerate(accent_colors[:5]):
        x0 = int(width * 0.14) + index * int(width * 0.145)
        x1 = x0 + int(width * 0.12)
        draw.rectangle((x0, stripe_top, x1, stripe_top + stripe_height), fill=color)

    wheel_radius = max(18, int(height * 0.09))
    for center_x in (int(width * 0.24), int(width * 0.76)):
        draw.ellipse(
            (
                center_x - wheel_radius,
                int(height * 0.67) - wheel_radius,
                center_x + wheel_radius,
                int(height * 0.67) + wheel_radius,
            ),
            fill=(26, 30, 34),
        )
        inner_radius = max(8, wheel_radius // 2)
        draw.ellipse(
            (
                center_x - inner_radius,
                int(height * 0.67) - inner_radius,
                center_x + inner_radius,
                int(height * 0.67) + inner_radius,
            ),
            fill=(180, 188, 190),
        )

    preview_spec = _preview_spec_from_payload(request.prompt_payload)
    _draw_preview_overlays(draw, width, height, preview_spec)

    labels = _labels_from_payload(request.prompt_payload)
    for index, label in enumerate(labels):
        draw.text((24, 24 + index * 18), label, fill=(28, 32, 34))

    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


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


def _preview_spec_from_payload(prompt_payload: JsonObject) -> JsonObject:
    preview_spec = prompt_payload.get("preview_spec")
    return dict(preview_spec) if isinstance(preview_spec, dict) else {}


def _draw_preview_overlays(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    preview_spec: JsonObject,
) -> None:
    safe_zones = _safe_zone_lookup(preview_spec)
    for layer in _json_list(preview_spec.get("overlay_layers")):
        if not isinstance(layer, dict):
            continue
        if layer.get("visible") is False:
            continue

        zone = _layer_zone(layer, safe_zones)
        box = _zone_box(zone, width, height)
        kind = str(layer.get("kind", ""))
        opacity = _normalized_float(layer.get("opacity"), fallback=1.0)

        if kind == "text":
            text = str(layer.get("text", "")).strip()
            if text:
                draw.rounded_rectangle(
                    box,
                    radius=max(4, height // 80),
                    fill=_blend_color((35, 42, 48), (248, 248, 244), opacity),
                    outline=(248, 248, 244),
                    width=max(1, width // 260),
                )
                draw.text(
                    (box[0] + max(6, width // 80), box[1] + max(4, height // 60)),
                    text[:32],
                    fill=(248, 248, 244),
                )
        elif kind == "logo":
            draw.rounded_rectangle(
                box,
                radius=max(4, height // 80),
                fill=_blend_color((248, 248, 244), (244, 244, 239), opacity),
                outline=(32, 38, 42),
                width=max(1, width // 260),
            )
            draw.text(
                (box[0] + max(5, width // 90), box[1] + max(4, height // 70)),
                "LOGO",
                fill=(32, 38, 42),
            )


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


def _safe_zone_lookup(preview_spec: JsonObject) -> dict[str, JsonObject]:
    zones: dict[str, JsonObject] = {}
    for zone in _json_list(preview_spec.get("safe_zones")):
        if isinstance(zone, dict):
            zone_id = str(zone.get("id", "")).strip()
            if zone_id:
                zones[zone_id] = dict(zone)
    return zones


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


def _normalized_float(value: object, *, fallback: float) -> float:
    if isinstance(value, int | float):
        return min(1.0, max(0.0, float(value)))
    return fallback


def _is_number(value: object) -> bool:
    return isinstance(value, int | float)


def _blend_color(
    foreground: tuple[int, int, int],
    background: tuple[int, int, int],
    opacity: float,
) -> tuple[int, int, int]:
    return (
        int(background[0] + (foreground[0] - background[0]) * opacity),
        int(background[1] + (foreground[1] - background[1]) * opacity),
        int(background[2] + (foreground[2] - background[2]) * opacity),
    )


def _json_list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _integer_from_payload(value: object, *, fallback: int) -> int:
    if isinstance(value, int):
        return value
    return fallback


def _labels_from_payload(prompt_payload: JsonObject) -> list[str]:
    brief = prompt_payload.get("brief")
    vehicle_template = prompt_payload.get("vehicle_template")
    if not isinstance(brief, dict):
        brief = {}
    if not isinstance(vehicle_template, dict):
        vehicle_template = {}

    values: list[tuple[str, Any]] = [
        ("Concept", prompt_payload.get("concept_label", "concept_preview")),
        ("Template", vehicle_template.get("label", "generic side-view vehicle")),
        ("Theme", brief.get("character_theme", "unspecified theme")),
        ("Style", brief.get("style", "itasha concept")),
        ("Text", ", ".join(str(item) for item in brief.get("text", [])) or "none"),
    ]
    return [f"{label}: {str(value)[:72]}" for label, value in values]
