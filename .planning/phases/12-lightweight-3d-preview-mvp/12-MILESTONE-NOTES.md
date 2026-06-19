---
phase: 12-lightweight-3d-preview-mvp
artifact: milestone-notes
status: complete
created: 2026-06-19
requirements: [V2-3D-01, V2-3D-02, V2-3D-03, V2-3D-04, V2-3D-05]
---

# Phase 12 Milestone Notes - Lightweight 3D Preview MVP

## Outcome

Phase 12 adds a concept-only lightweight 3D preview path for generated versions. Users can open `3D 预览`, inspect a simple shell, rotate/zoom/reset the camera, save a version-linked screenshot artifact, and fall back cleanly to 2D preview when no shell is compatible.

## What Shipped

- Typed `Preview3DSpec`, camera preset, compatibility, material plan, warning, and screenshot artifact contracts.
- `preview_3d_screenshot` artifact kind and version-scoped screenshot persistence.
- One registered shell fixture, `generic-side-coupe-lightweight-v1`, for the `generic-side-coupe` side PreviewSpec path.
- Client-only Three.js viewer with mobile-safe canvas sizing and aspect-aware camera distance.
- PreviewSpec safe-zone and overlay material mapping with visible chips and source artifact evidence.
- Persistent `非生产贴膜参考`, concept-only, and UV-not-verified warning posture in UI and metadata.
- Desktop/mobile browser evidence and screenshot-crop nonblank statistics.
- README and development runbook updates for feature flag, screenshot behavior, fallback behavior, and limitations.

## Verification Summary

- `corepack pnpm validate` passed in an elevated host run.
- `corepack pnpm smoke:worker -- --dry-run` passed.
- Focused core/API/web checks passed.
- Browser UAT passed at desktop and mobile widths with screenshots in `evidence/`.
- Final web tests passed 9 files / 71 tests. The JSDOM canvas warning is expected and covered by browser UAT.

## Boundaries

The lightweight 3D preview is not production UV proof, print-ready output, physical wrap validation, or a broad vehicle-shell library. It is a concept inspection tool for review workflows. Verified vehicle-specific UV mapping, full production handoff, and print-shop package validation remain deferred.

## Next

Phase 13 should use the Phase 12 screenshot artifact and warning metadata when building the enhanced concept handoff package, while preserving concept-only disclaimers.

---
*Completed: 2026-06-19*
