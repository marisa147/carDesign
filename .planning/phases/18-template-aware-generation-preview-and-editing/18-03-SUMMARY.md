# Plan 18.03 Summary: Targeted Edit Region And Mask Selection From Selected Template

## Result

Completed. Targeted edit selection uses the current version's PreviewSpec regions and clears stale targets when switching to an incompatible or legacy version.

## Evidence

- Workbench test submits a van safe-zone edit intent with the van region coordinates.
- Workbench test clears an overlay-layer target after switching to a version with no matching PreviewSpec.
- Worker recomposition test preserves selected van template trace through child model run, artifact, version, job operations, and event metadata.

## Files

- `apps/web/src/components/workbench/preview-panel.tsx`
- `apps/web/src/app/page.test.tsx`
- `services/worker/tests/test_generation_tasks.py`
- `services/worker/src/caragent_worker/tasks/jobs.py`

