# Phase 24 Summary: Preview And Parameter Correctness

## Completed

- Verified the 3D screenshot path captures the real Three.js/WebGL canvas through `canvas.toBlob()` and does not upload a scaffold 1x1 PNG.
- Exported `captureCanvasScreenshot()` from the 3D preview panel so the live-canvas capture path is directly covered by frontend tests.
- Kept and verified the API-side screenshot guardrails for MIME, image magic bytes, decoded dimensions, and declared width/height mismatch rejection.
- Updated parameter diff construction so empty strings and empty arrays are treated as intentional user edits.
- Updated reference clearing so empty assignments persist both `reference_asset_ids: []` and `reference_usage: []`.
- Removed the reference-assignment remount behavior from the workbench parameter panel so toggling a reference no longer discards unsaved draft fields.
- Added touch-aware reference ID text behavior: checkbox selection updates the reference ID field until the user manually edits that field, then explicit manual input wins.
- Updated brief patch normalization so required-but-clearable brief fields can be submitted empty and then normalized through deterministic fallbacks instead of failing validation.

## Tests Added

- Web regression proving `captureCanvasScreenshot()` reads bytes, dimensions, and content type from the live canvas blob.
- Web regression proving explicit clears for strings, lists, reference IDs, and reference usage are sent in the PATCH body.
- API regression proving empty required brief strings are accepted and normalized through fallback brief creation.

## Files Touched

- `apps/web/src/components/workbench/preview-3d-panel.tsx`
- `apps/web/src/components/workbench/parameter-panel.tsx`
- `apps/web/src/components/workbench/workbench-app.tsx`
- `apps/web/src/app/page.test.tsx`
- `services/api/src/caragent_api/routes/generation.py`
- `services/api/tests/test_generation.py`

## Notes

Phase 24 found that the main 3D screenshot implementation and API screenshot validation were already materially correct. The implementation work therefore focused on making those paths testable and fixing the real remaining correctness gap: explicit clearing of parameters and references without draft loss.