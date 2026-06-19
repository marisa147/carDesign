# Phase 18: Template-Aware Generation, Preview, And Editing - Context

## Scope

Phase 18 makes the selected MVP template part of the real generation and review pipeline. A template selected in the Workbench must carry through deterministic generation, PromptPlan, PreviewSpec, provider/model trace, generated artifacts, design versions, targeted edit metadata, reference trace, lightweight 3D compatibility, and archived compatibility tests.

## Requirements

- V3-INTEGRATION-01: User can generate a concept on any MVP template through the local deterministic provider path.
- V3-INTEGRATION-02: Safe-zone overlays, risk warnings, text/logo layers, and PreviewSpec coordinates align with the selected template in 2D preview.
- V3-INTEGRATION-03: Targeted edits use selected template safe zones and masks for region selection, mask preview, and recomposition metadata.
- V3-INTEGRATION-04: Reference-guided generation records template context alongside reference roles and rights snapshots.
- V3-INTEGRATION-05: Lightweight 3D preview links supported template shells when present and falls back with template-specific non-production labels when absent.
- V3-INTEGRATION-06: Contracts and generated TypeScript types expose template catalog, selection, and readiness fields without breaking archived v1/v2 payloads.

## Boundaries

- Phase 18 does not add print-ready export, verified UV mapping, measured scale, bleed, DPI, color profile, or installer notes.
- Phase 18 does not add real vehicle-specific template assets or hosted provider rollout claims.
- Phase 18 does not change the catalog source policy from Phase 15 or template pack asset inventory from Phase 16.
- Unsupported 3D templates must fall back to 2D with explicit concept-only wording instead of implying production fit.

## Implementation Notes

- Treat `GenerationBriefPayload.vehicle_template_id` and its resolved safe zones as the authoritative template context for prompt planning.
- Keep deterministic local generation valid for every `MVP_TEMPLATE_IDS` record.
- Build overlay layers from available safe zones instead of hard-coding zones that may not exist on every template.
- Persist `vehicle_template` metadata beside reference usage and provider/model metadata on model runs, generated artifacts, versions, job operations, and final events.
- Resolve legacy `generic-side-coupe` and canonical `generic_coupe_side_v1` consistently for lightweight 3D shell compatibility.
- Keep frontend target selection tied to the selected version's PreviewSpec, not just the currently selected catalog item.

