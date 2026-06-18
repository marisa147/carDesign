from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from typing import Any

from caragent_core.editing import EditIntent

from caragent_worker.providers.base import ImageGenerationRequest, JsonObject
from caragent_worker.providers.local import render_local_concept_preview

RECOMPOSITION_PROVIDER = "deterministic-recomposition"
RECOMPOSITION_MODEL = "preview-spec-recomposer-v1"
RECOMPOSITION_ROUTE = "deterministic_recomposition"


class DeterministicRecompositionError(ValueError):
    """Raised when an edit intent cannot be safely recomposed locally."""


@dataclass(frozen=True, slots=True)
class RecompositionResult:
    image_bytes: bytes
    content_type: str
    height: int
    width: int
    metadata: JsonObject
    preview_spec: JsonObject


def recompose_targeted_edit(
    parent_preview_spec: JsonObject,
    edit_intent: EditIntent,
    *,
    height: int,
    width: int,
) -> RecompositionResult:
    if edit_intent.route_preference != RECOMPOSITION_ROUTE:
        raise DeterministicRecompositionError("edit intent is not deterministic recomposition")
    if edit_intent.target.type != "overlay_layer":
        raise DeterministicRecompositionError("only overlay layer targets can be recomposed")

    preview_spec = copy.deepcopy(parent_preview_spec)
    overlay_layers = preview_spec.get("overlay_layers")
    if not isinstance(overlay_layers, list):
        raise DeterministicRecompositionError("parent PreviewSpec has no overlay layers")

    target_layer = _target_layer(overlay_layers, edit_intent.target.id)
    safe_zones = _safe_zone_lookup(preview_spec)
    changes = _parse_recomposition_changes(edit_intent)
    if not changes:
        raise DeterministicRecompositionError("no recomposition-safe change found")

    changed_fields = _apply_changes(
        target_layer,
        changes,
        current_region=_current_region(target_layer, safe_zones, edit_intent),
    )
    if not changed_fields:
        raise DeterministicRecompositionError("no recomposition-safe change found")

    prompt_text = f"Deterministic recomposition: {edit_intent.prompt_delta.summary}"
    request = ImageGenerationRequest(
        concept_label="targeted_recomposition",
        input_artifact_ids=[],
        model=RECOMPOSITION_MODEL,
        parameters={
            "changed_fields": changed_fields,
            "recomposition_route": RECOMPOSITION_ROUTE,
            "target": edit_intent.target.model_dump(mode="json"),
        },
        prompt_payload={
            "concept_label": "targeted_recomposition",
            "edit_intent": edit_intent.model_dump(mode="json"),
            "preview_spec": preview_spec,
        },
        prompt_text=prompt_text,
        provider=RECOMPOSITION_PROVIDER,
    )
    image_bytes = render_local_concept_preview(request, height=height, width=width)
    metadata: JsonObject = {
        "changed_fields": changed_fields,
        "content_type": "image/png",
        "external_calls": False,
        "height": height,
        "model": RECOMPOSITION_MODEL,
        "preview_spec": preview_spec,
        "provider": RECOMPOSITION_PROVIDER,
        "recomposition_route": RECOMPOSITION_ROUTE,
        "target": edit_intent.target.model_dump(mode="json"),
        "width": width,
    }
    return RecompositionResult(
        content_type="image/png",
        height=height,
        image_bytes=image_bytes,
        metadata=metadata,
        preview_spec=preview_spec,
        width=width,
    )


def _target_layer(overlay_layers: list[object], target_id: str) -> JsonObject:
    for layer in overlay_layers:
        if isinstance(layer, dict) and str(layer.get("id", "")).strip() == target_id:
            return layer
    raise DeterministicRecompositionError(f"target not found in parent PreviewSpec: {target_id}")


def _parse_recomposition_changes(edit_intent: EditIntent) -> JsonObject:
    text = " ".join(
        dict.fromkeys(
            [
                edit_intent.prompt_delta.summary,
                *edit_intent.prompt_delta.instructions,
            ],
        ),
    )
    normalized = text.lower()
    changes: JsonObject = {}

    for field in ("x", "y", "width", "height", "opacity", "scale"):
        value = _number_after(field, text)
        if value is not None:
            changes[field] = value

    visible = _bool_after("visible", text)
    if visible is not None:
        changes["visible"] = visible
    elif any(token in normalized for token in ("hide", "hidden", "隐藏")):
        changes["visible"] = False
    elif any(token in normalized for token in ("show", "visible", "显示")):
        changes["visible"] = True

    text_value = _text_after("text", text)
    if text_value is not None:
        changes["text"] = text_value

    logo_value = _text_after("logo", text) or _text_after("asset_id", text)
    if logo_value is not None:
        changes["asset_id"] = logo_value

    if any(token in normalized for token in ("move up", "upward", "上移", "向上")):
        changes["move_y_delta"] = min(float(changes.get("move_y_delta", 0)) - 0.04, 0)
    if any(token in normalized for token in ("move down", "downward", "下移", "向下")):
        changes["move_y_delta"] = max(float(changes.get("move_y_delta", 0)) + 0.04, 0)
    if any(token in normalized for token in ("move left", "leftward", "左移", "向左")):
        changes["move_x_delta"] = min(float(changes.get("move_x_delta", 0)) - 0.04, 0)
    if any(token in normalized for token in ("move right", "rightward", "右移", "向右")):
        changes["move_x_delta"] = max(float(changes.get("move_x_delta", 0)) + 0.04, 0)
    if any(token in normalized for token in ("scale up", "larger", "放大")):
        changes.setdefault("scale", 1.1)
    if any(token in normalized for token in ("scale down", "smaller", "缩小")):
        changes.setdefault("scale", 0.9)

    return changes


def _apply_changes(
    layer: JsonObject,
    changes: JsonObject,
    *,
    current_region: JsonObject,
) -> list[str]:
    changed_fields: list[str] = []
    next_region = dict(current_region)

    for field in ("x", "y", "width", "height"):
        if field in changes:
            next_region[field] = float(changes[field])
            changed_fields.append(field)

    if "move_x_delta" in changes:
        next_region["x"] = float(next_region["x"]) + float(changes["move_x_delta"])
        changed_fields.append("x")
    if "move_y_delta" in changes:
        next_region["y"] = float(next_region["y"]) + float(changes["move_y_delta"])
        changed_fields.append("y")
    if "scale" in changes:
        scale = max(0.1, min(3.0, float(changes["scale"])))
        next_region = _scaled_region(next_region, scale)
        changed_fields.extend(["width", "height"])

    if any(field in changed_fields for field in ("x", "y", "width", "height")):
        next_region = _clamp_region(next_region)
        for field in ("x", "y", "width", "height"):
            layer[field] = next_region[field]

    if "opacity" in changes:
        layer["opacity"] = _clamp_float(float(changes["opacity"]), lower=0.0, upper=1.0)
        changed_fields.append("opacity")

    if "visible" in changes:
        layer["visible"] = bool(changes["visible"])
        changed_fields.append("visible")

    if "text" in changes:
        if str(layer.get("kind", "")) != "text":
            raise DeterministicRecompositionError("text changes require a text overlay layer")
        layer["text"] = str(changes["text"])
        changed_fields.append("text")

    if "asset_id" in changes:
        if str(layer.get("kind", "")) != "logo":
            raise DeterministicRecompositionError("logo swaps require a logo overlay layer")
        layer["asset_id"] = str(changes["asset_id"])
        changed_fields.append("asset_id")

    return list(dict.fromkeys(changed_fields))


def _current_region(
    layer: JsonObject,
    safe_zones: dict[str, JsonObject],
    edit_intent: EditIntent,
) -> JsonObject:
    if all(_is_number(layer.get(field)) for field in ("x", "y", "width", "height")):
        return {field: float(layer[field]) for field in ("x", "y", "width", "height")}
    zone_id = str(layer.get("zone_id", "")).strip()
    zone = safe_zones.get(zone_id)
    if zone is not None:
        return {
            "height": _number_or(zone.get("height"), edit_intent.region.height),
            "width": _number_or(zone.get("width"), edit_intent.region.width),
            "x": _number_or(zone.get("x"), edit_intent.region.x),
            "y": _number_or(zone.get("y"), edit_intent.region.y),
        }
    return {
        "height": edit_intent.region.height,
        "width": edit_intent.region.width,
        "x": edit_intent.region.x,
        "y": edit_intent.region.y,
    }


def _safe_zone_lookup(preview_spec: JsonObject) -> dict[str, JsonObject]:
    zones: dict[str, JsonObject] = {}
    safe_zones = preview_spec.get("safe_zones")
    if not isinstance(safe_zones, list):
        return zones
    for zone in safe_zones:
        if isinstance(zone, dict):
            zone_id = str(zone.get("id", "")).strip()
            if zone_id:
                zones[zone_id] = zone
    return zones


def _scaled_region(region: JsonObject, scale: float) -> JsonObject:
    width = max(0.01, min(1.0, float(region["width"]) * scale))
    height = max(0.01, min(1.0, float(region["height"]) * scale))
    center_x = float(region["x"]) + float(region["width"]) / 2
    center_y = float(region["y"]) + float(region["height"]) / 2
    return {
        "height": height,
        "width": width,
        "x": center_x - width / 2,
        "y": center_y - height / 2,
    }


def _clamp_region(region: JsonObject) -> JsonObject:
    width = _clamp_float(float(region["width"]), lower=0.01, upper=1.0)
    height = _clamp_float(float(region["height"]), lower=0.01, upper=1.0)
    return {
        "height": height,
        "width": width,
        "x": _clamp_float(float(region["x"]), lower=0.0, upper=1.0 - width),
        "y": _clamp_float(float(region["y"]), lower=0.0, upper=1.0 - height),
    }


def _number_after(field: str, text: str) -> float | None:
    match = re.search(rf"\b{re.escape(field)}\s*[:=]\s*(-?\d+(?:\.\d+)?)", text, re.I)
    return float(match.group(1)) if match else None


def _bool_after(field: str, text: str) -> bool | None:
    match = re.search(rf"\b{re.escape(field)}\s*[:=]\s*(true|false|0|1)", text, re.I)
    if not match:
        return None
    return match.group(1).lower() in {"true", "1"}


def _text_after(field: str, text: str) -> str | None:
    match = re.search(rf"\b{re.escape(field)}\s*[:=]\s*([^;\n]+)", text, re.I)
    if not match:
        return None
    value = match.group(1).strip()
    return value or None


def _number_or(value: Any, fallback: float) -> float:
    return float(value) if _is_number(value) else fallback


def _is_number(value: object) -> bool:
    return isinstance(value, int | float)


def _clamp_float(value: float, *, lower: float, upper: float) -> float:
    return min(upper, max(lower, value))
