# Phase 31 Context: Section-First Design Workspace

## Goal

Make vehicle sections the main customization surface. Users should choose wrap scope by sections, see each section's related views and flat panel dimensions, and have local edit scope tied to section geometry instead of free-floating overlays.

## Requirements

- SECT-01: User can choose wrap scope by vehicle sections such as doors, rear quarter, front fender, hood, roof, trunk, bumpers, and side skirt.
- SECT-02: User can select a section and see its related side/front/rear/top position plus flat/unfolded construction panel where available.
- SECT-03: Preview overlays and local edits are constrained to selected template sections instead of floating over a generic car silhouette.

## Current System

- Phase 28 added GR86/BRZ sections in template detail metadata.
- `ParameterPanel` receives catalog items only, not template detail records.
- Workbench targeted editing already has `selectedEditTarget` and normalized rectangle regions.
- PreviewPanel can render and submit targeted edit regions once a target is selected.

## Scope

In scope:
- Fetch selected template detail in `WorkbenchApp`.
- Pass template sections into `ParameterPanel`.
- Add section-first selector and flat panel summary.
- Sync selected section into targeted edit target state with section bounds.
- Keep generation payload unchanged for now; section persistence through generation/export is Phase 32/33.

Out of scope:
- True unfolded SVG panel rendering.
- Persisted per-section design plans.
- Section-clipped provider generation.
