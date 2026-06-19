# Plan 18.05 Summary: Lightweight 3D Shell Compatibility And 2D Fallback Per Template

## Result

Completed. Lightweight 3D compatibility now resolves both the legacy `generic-side-coupe` id and canonical `generic_coupe_side_v1` id, while unsupported MVP templates fall back to 2D with template-specific reasons.

## Evidence

- Frontend compatibility test covers canonical coupe shell resolution.
- Frontend compatibility test covers van fallback and selected-template fallback reason.
- Existing legacy coupe fixture remains compatible.
- 3D warnings continue to include non-production and UV-not-verified labels.

## Files

- `apps/web/src/lib/preview3d/shells.ts`
- `apps/web/src/app/page.test.tsx`

