---
phase: 14
artifact: ui-spec
status: ready
created: 2026-06-19
---

# Phase 14 - UI Design Contract

Phase 14 does not introduce a new product surface. Browser UAT must use the existing workbench as the first screen and verify that the V2 controls already shipped remain readable, reachable, and honest at desktop and mobile widths.

## Required Browser Evidence

- Hosted provider controls must show local/default availability and blocked/guarded hosted state without exposing secrets.
- Targeted edit controls must show selected safe zones/layers, mask preview intent, route evidence, and parent/child comparison without obscuring the preview.
- Reference controls must show role assignment, rights/source state, unsupported-provider warnings, and generated-version trace evidence.
- Lightweight 3D preview must show non-production labeling, controls, source/shell evidence, and fallback behavior.
- Enhanced handoff export must show ZIP package preview, warning rows, successful history, and blocked rights/source state.

## Layout Acceptance

- No horizontal page scroll at desktop or mobile widths.
- Dense panels may wrap, but controls must remain reachable.
- Text must not overlap controls, warnings, screenshots, package rows, or history rows.
- Concept-only, non-production, and not-print-ready labels must remain visible near the related feature.

## Out Of Scope

- No landing page, marketing hero, redesign, visual theme change, or new workbench layout.
- No new production handoff, marketplace, payment, auth, billing, or installer UI.

---
*UI contract ready: 2026-06-19*
