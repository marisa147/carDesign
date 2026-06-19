# Phase 16: MVP Generic Template Pack - Context

## Scope

Phase 16 creates the internal-original reusable template pack promised by v3.0. The pack must contain generic side-view coupe, sedan, hatchback, SUV, and van templates with deterministic assets, source/license metadata, safe zones, and a one-command validation path.

## Requirements

- V3-PACK-01: selectable internal-original MVP side-view template pack with coupe, sedan, hatchback, SUV, and van.
- V3-PACK-02: each template includes base image, body/window/wheel/handle masks, panel lines, safe-zones JSON, template metadata, and thumbnail.
- V3-PACK-03: one command validates package structure, dimensions, mask bounds, safe-zone coordinates, and metadata schema.
- V3-PACK-04: deterministic thumbnails or preview fixtures exist without unauthorized vehicle imagery.
- V3-PACK-05: brief resolution preserves selected template id, label, view, source/license status, warnings, and safe zones.
- V3-PACK-06: tests cover all five MVP templates plus the legacy coupe alias.

## Boundaries

- Templates are internal generic silhouettes, not brand/model-specific vehicle reproductions.
- Phase 16 does not expose a catalog API or Workbench selector; that is Phase 17.
- Phase 16 does not make production/print-ready claims.
- Existing `generic-side-coupe` payloads must continue to resolve.

## Implementation Notes

- Store template assets inside the core package so API, worker, contracts, and tests read one shared registry.
- Generate deterministic raster assets from local geometry, not web imagery.
- Keep safe zones normalized to the template canvas for renderer-neutral PreviewSpec use.
- Use registry records as the single runtime source of selected template metadata.
