# Phase 18 Patterns

## Template Context

Use this durable shape wherever a concise template trace is needed:

```json
{
  "vehicle_template": {
    "canvas": {"height": 768, "width": 1536},
    "id": "generic_coupe_side_v1",
    "label": "Generic coupe side-view",
    "source_type": "internal_original",
    "license_status": "approved",
    "view": "side"
  }
}
```

PreviewSpec keeps the richer `template.source` and `template.readiness` objects.

## Overlay Zone Selection

1. Prefer an exact known safe-zone id when it exists.
2. Prefer body zones for text and logo layers.
3. Prefer a second body zone for logo layers when available.
4. Fall back to the first safe zone.
5. If no safe zone exists, omit `zone_id` and let renderer fall back.

## Compatibility

- Legacy `generic-side-coupe` and canonical `generic_coupe_side_v1` both map to the lightweight coupe shell.
- Shell metadata should keep the matched template id so exported Preview3D specs explain what resolved.
- Unsupported templates must preserve the selected template id in the fallback reason.

