# Phase 24 Context: Preview And Parameter Correctness

## Goal

Fix two high-trust workflow lies: 3D screenshot upload must contain real rendered canvas bytes, and parameter updates must be able to intentionally clear strings, lists, and reference assignments.

## Requirements

- PREV-01: 3D preview screenshot capture uploads real WebGL canvas bytes instead of a hardcoded 1x1 PNG.
- PREV-02: API rejects 3D screenshot uploads when MIME, magic bytes, or actual image dimensions do not match the request.
- PREV-03: User can clear optional brief strings, lists, and reference assignments from the parameter panel.

## Likely Files

- `apps/web/src/components/workbench/preview-3d-panel.tsx`
- `apps/web/src/components/workbench/preview-3d-viewer.tsx`
- `apps/web/src/components/workbench/parameter-panel.tsx`
- `apps/web/src/app/page.test.tsx`
- `services/api/src/caragent_api/routes/jobs.py`
- `services/api/tests/test_jobs.py`

## Non-Goals

- Do not introduce verified production UV or print-ready 3D claims.
- Do not redesign the parameter panel.
- Do not add a new 3D engine or server-side renderer.
