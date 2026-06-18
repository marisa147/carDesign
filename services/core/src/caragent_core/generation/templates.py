from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SUPPORTED_TEMPLATE_ID = "generic-side-coupe"
SUPPORTED_TEMPLATE_LABEL = "Generic side-view coupe"
SUPPORTED_VIEW = "side"
SUPPORTED_CANVAS_WIDTH = 1536
SUPPORTED_CANVAS_HEIGHT = 768

SafeZone = dict[str, Any]

SUPPORTED_SAFE_ZONES: tuple[SafeZone, ...] = (
    {
        "height": 0.24,
        "id": "door-main",
        "kind": "body",
        "label": "Door / main side panel",
        "width": 0.34,
        "x": 0.32,
        "y": 0.47,
    },
    {
        "height": 0.16,
        "id": "side-window",
        "kind": "window",
        "label": "Side window",
        "width": 0.34,
        "x": 0.24,
        "y": 0.29,
    },
    {
        "height": 0.2,
        "id": "front-wheel-arch",
        "kind": "risky",
        "label": "Front wheel arch",
        "width": 0.16,
        "x": 0.16,
        "y": 0.58,
    },
    {
        "height": 0.2,
        "id": "rear-wheel-arch",
        "kind": "risky",
        "label": "Rear wheel arch",
        "width": 0.16,
        "x": 0.68,
        "y": 0.58,
    },
    {
        "height": 0.2,
        "id": "rear-quarter",
        "kind": "body",
        "label": "Rear quarter panel",
        "width": 0.18,
        "x": 0.64,
        "y": 0.43,
    },
)


@dataclass(frozen=True)
class TemplateResolution:
    template_id: str
    template_label: str
    view: str
    canvas_width: int
    canvas_height: int
    warnings: list[str]
    safe_zones: list[SafeZone]


def resolve_vehicle_template(
    *,
    vehicle_template_id: str | None = None,
    view: str | None = None,
) -> TemplateResolution:
    requested_template = (vehicle_template_id or SUPPORTED_TEMPLATE_ID).strip()
    requested_view = (view or SUPPORTED_VIEW).strip().lower()
    warnings: list[str] = []

    if requested_template != SUPPORTED_TEMPLATE_ID:
        warnings.append(
            "Unsupported vehicle template "
            f"'{requested_template}' normalized to '{SUPPORTED_TEMPLATE_ID}'.",
        )

    if requested_view != SUPPORTED_VIEW:
        warnings.append(
            f"Unsupported view '{requested_view}' normalized to '{SUPPORTED_VIEW}'.",
        )

    return TemplateResolution(
        canvas_height=SUPPORTED_CANVAS_HEIGHT,
        canvas_width=SUPPORTED_CANVAS_WIDTH,
        safe_zones=supported_safe_zones(),
        template_id=SUPPORTED_TEMPLATE_ID,
        template_label=SUPPORTED_TEMPLATE_LABEL,
        view=SUPPORTED_VIEW,
        warnings=warnings,
    )


def supported_safe_zones() -> list[SafeZone]:
    return [dict(zone) for zone in SUPPORTED_SAFE_ZONES]
