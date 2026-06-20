# Phase 20 Desktop And Mobile Browser UAT

**Status:** Passed  
**Date:** 2026-06-20  
**Requirement:** V3-REL-03

## Setup

- Seeded a local SQLite fixture with `.planning/phases/20-v3-hardening-docs-smoke-and-uat/evidence/phase20_seed_uat.py`.
- Started FastAPI against the fixture on `127.0.0.1:8150`.
- Started Next.js against the fixture API on `127.0.0.1:3150`.
- Ran Headless Chrome through CDP with `.planning/phases/20-v3-hardening-docs-smoke-and-uat/evidence/phase20_browser_uat.mjs`.
- Stopped the local API and web services after capture; ports `8150` and `3150` had no listening processes after cleanup.

## Captures

| View | Screenshot | Overflow | Key Signals |
|------|------------|----------|-------------|
| Desktop 2D/preflight | `evidence/phase20-v3-desktop-2d-preflight.png` | No | Template catalog, selected van PreviewSpec, targeted edit, enhanced handoff files, production preflight, concept-only status. |
| Desktop 3D fallback | `evidence/phase20-v3-desktop-3d-fallback.png` | No | Selected van template, explicit 3D fallback, enhanced handoff files, production preflight, non-production label. |
| Mobile 2D/preflight | `evidence/phase20-v3-mobile-2d-preflight.png` | No | Template catalog, selected van PreviewSpec, targeted edit, enhanced handoff files, production preflight, concept-only status. |
| Mobile 3D fallback | `evidence/phase20-v3-mobile-3d-fallback.png` | No | Selected van template, explicit 3D fallback, enhanced handoff files, production preflight, non-production label. |

## Evidence

- `evidence/phase20-browser-metrics.json`
- `evidence/phase20-uat-seed.json`
- `evidence/phase20-api-8150b.err.log`
- `evidence/phase20-web-3150b.out.log`

## Notes

- A stale Next dev server was occupying `apps/web` on port `3140`; it was stopped so the UAT could use a controlled fixture-backed service on `3150`.
- The seeded UAT version used `generic_van_side_v1`, which intentionally has no lightweight 3D shell. This proves the selected-template 2D fallback path and keeps the non-production boundary visible.
- All captures reported `horizontalOverflow: false`.

## Result

Browser UAT passed for desktop and mobile. V3 catalog selection, selected-template evidence, targeted edit controls, 3D fallback, enhanced handoff evidence, production preflight, and concept-only labels were visible and stable.

