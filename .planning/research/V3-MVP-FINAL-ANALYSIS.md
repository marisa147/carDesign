# V3 MVP_FINAL Analysis

**Created:** 2026-06-19
**Source:** `C:/Users/25858/Downloads/MVP_FINAL.md`
**Purpose:** Translate the final MVP delivery note into the next active milestone after archived v2.0.

## Source Signals

`MVP_FINAL.md` treats MVP1 + MVP2 as complete and explicitly keeps the product in concept-design territory: not print-ready wrap production, not verified UV, not template marketplace, not ordering/payment, and not installer collaboration.

The strongest unclosed capability signal is the template foundation described in the final MVP note:

- Source strategy and license metadata for templates.
- A reusable MVP side-view template pack.
- Template metadata, masks, safe zones, thumbnails, warnings, and catalog UI/API.
- Explicit source restrictions: `internal_original`, `licensed_template`, and `user_provided_with_rights` are allowed under conditions; `web_crawled_image` and third-party reference-only material cannot become reusable template assets.
- V3 candidates include production handoff, true 3D, advanced generation, template library expansion, and business/collaboration layers, with a warning not to do all of them at once.

## Current Codebase Gap Scan

The current v2.0 codebase already has:

- Durable jobs/artifacts/versions/export lineage.
- Itasha safe zones and PreviewSpec persistence.
- Targeted edits and reference-guided generation metadata.
- Enhanced concept handoff ZIPs with concept-only disclaimers.
- Lightweight 3D preview for `generic-side-coupe`.

The current template implementation is still narrow:

- `services/core/src/caragent_core/generation/templates.py` exposes one supported template id: `generic-side-coupe`.
- No five-template MVP pack exists for `generic_coupe_side_v1`, `generic_sedan_side_v1`, `generic_hatchback_side_v1`, `generic_suv_side_v1`, and `generic_van_side_v1`.
- No first-class template source/license registry was found in code search.
- No template catalog API/UI surface was found beyond existing brief/template fields and preview labels.

## Selected v3.0 Direction

v3.0 should be **Template Library And Production Readiness**:

1. Build the governance layer for template source, licensing, readiness, and prohibited-source blocking.
2. Add an internal-original MVP generic side-view template pack.
3. Expose a template catalog and Workbench selection flow.
4. Integrate selected templates through generation, preview, targeted edit, reference trace, lightweight 3D fallback, and enhanced handoff.
5. Add a concept-only production readiness preflight that explains why a design is not print-ready yet.

This is the safest next milestone because production handoff, true 3D, real licensed templates, marketplace, ordering, and installer collaboration all depend on trustworthy template provenance and validation first.

## Explicit Non-Goals For v3.0

- No print-ready PSD/AI/PDF export.
- No verified wrap-shop scale, bleed, DPI, color profile, installer notes, or UV guarantees.
- No real licensed vehicle-specific template marketplace.
- No automated legal-grade copyright verification.
- No ordering, quote, payment, gallery, or installer network.
- No claim that hosted providers are production-ready.

## Phase Shape

- Phase 15: Template Source Governance And Compatibility
- Phase 16: MVP Generic Template Pack
- Phase 17: Template Catalog API And Workbench Selection
- Phase 18: Template-Aware Generation, Preview, And Editing
- Phase 19: Concept Handoff And Production Readiness Preflight
- Phase 20: V3 Hardening, Docs, Smoke, And UAT
