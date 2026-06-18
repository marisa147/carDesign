---
phase: 05-iteration-feedback-and-concept-export
plan: "01"
subsystem: backend-feedback-export
tags: [fastapi, core, feedback, export, manifest]

requires:
  - phase: "05-CONTEXT"
    provides: Phase 5 scope and export safety boundary
provides:
  - feedback create API
  - concept export create API
  - workspace/version ownership validation
  - concept-preview manifest defaults
affects: [phase-05-02-child-iteration, phase-05-03-contract-refresh]

tech-stack:
  patterns:
    - FastAPI request schemas live in `services/api/src/caragent_api/schemas.py`
    - job/export/feedback durable behavior lives in `caragent_core.services.jobs`
    - route errors reuse existing 404/422 helpers

key-files:
  modified:
    - services/core/src/caragent_core/services/jobs.py
    - services/core/tests/test_jobs.py
    - services/api/src/caragent_api/schemas.py
    - services/api/src/caragent_api/routes/jobs.py
    - services/api/tests/test_jobs.py

key-decisions:
  - "Feedback/export creation validates that the version belongs to the workspace."
  - "Concept exports are limited to `png`, `jpg`, and `jpeg`."
  - "Export manifests include a server-generated `Concept preview only, not print-ready.` disclaimer."
  - "Artifact ids are validated against the selected workspace and version when supplied."

patterns-established:
  - "Phase 5 creation APIs use workspace/version-scoped routes."
  - "Server-generated export manifest fields override caller-supplied safety-critical fields."

requirements-completed:
  - ITER-04
  - ITER-05
  - ITER-06

duration: 20 min
completed: 2026-06-17
---

# Phase 5 Plan 01: Backend Feedback And Concept Export Summary

**Backend feedback and concept-export creation are now API-backed and safety-scoped.**

## Accomplishments

- Added failing core tests for version/workspace ownership and unsupported export formats, then implemented validation.
- Added failing API tests for feedback creation, concept export creation, invalid rating, wrong workspace, and unsupported export format.
- Added `FeedbackCreateRequest` and `ExportCreateRequest`.
- Added `POST /workspaces/{workspace_id}/versions/{version_id}/feedback`.
- Added `POST /workspaces/{workspace_id}/versions/{version_id}/exports`.
- Added server-generated concept export manifest fields, including selected version, workspace, source artifact, parameters, concept label, format, and a not-print-ready disclaimer.

## Deviations from Plan

- None.

## Verification

- RED: `uv run pytest -q tests/test_jobs.py` in `services/core` failed for missing workspace/version validation and unsupported format rejection.
- RED: `uv run pytest -q tests/test_jobs.py` in `services/api` failed because POST feedback/export routes were missing.
- GREEN: `uv run pytest -q tests/test_jobs.py` in `services/core` passed, 5 tests.
- GREEN: `uv run pytest -q tests/test_jobs.py` in `services/api` passed, 5 tests.
- `uv run ruff check .` in `services/core` passed.
- `uv run ruff check .` in `services/api` passed.

## Next Plan Readiness

Ready for `05-02`: child iteration submission and worker lineage support.
