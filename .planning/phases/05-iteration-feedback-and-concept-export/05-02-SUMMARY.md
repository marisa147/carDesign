---
phase: 05-iteration-feedback-and-concept-export
plan: "02"
subsystem: iteration-lineage
tags: [fastapi, worker, lineage, generation, versioning]

requires:
  - phase: "05-01"
    provides: workspace/version-scoped backend creation API patterns
provides:
  - child iteration submission API
  - parent version ownership validation
  - durable iteration job metadata
  - worker-created child design versions
  - model-run and version iteration parameters
affects: [phase-05-03-contract-refresh, phase-05-04-lineage-ui]

tech-stack:
  patterns:
    - FastAPI generation routes enqueue Celery work through `QueueClient`
    - iteration job metadata is stored on `GenerationJob.metadata_json`
    - worker lineage is applied by passing `parent_version_id` to `create_design_version`

key-files:
  modified:
    - services/core/src/caragent_core/services/jobs.py
    - services/api/src/caragent_api/schemas.py
    - services/api/src/caragent_api/routes/generation.py
    - services/api/tests/test_generation.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/worker/tests/test_generation_tasks.py

key-decisions:
  - "Iteration submission uses `POST /workspaces/{workspace_id}/versions/{version_id}/iterations`."
  - "The API validates that the selected parent version belongs to the target workspace before creating a job."
  - "Iteration metadata stores `parent_version_id`, `change_request`, `parameter_overrides`, `iteration`, and `source`."
  - "The worker keeps normal generation as root versions and creates child versions only when job metadata contains a parent version id."

patterns-established:
  - "Generation job metadata is the durable handoff contract between API iteration requests and worker lineage creation."
  - "Worker model-run parameters and design-version parameters both carry iteration context for traceability."

requirements-completed:
  - ITER-01
  - ITER-02
  - ITER-03

duration: 25 min
completed: 2026-06-17
---

# Phase 5 Plan 02: Child Iteration Lineage Summary

Child iteration submission and worker lineage preservation are implemented.

## Accomplishments

- Added TDD coverage for submitting an iteration from a selected parent version.
- Added TDD coverage for rejecting missing or wrong-workspace parent versions.
- Added TDD coverage proving the worker creates a child `DesignVersion` with `parent_version_id` and incremented `lineage_depth`.
- Added `GenerationIterationSubmissionRequest`.
- Added `POST /workspaces/{workspace_id}/versions/{version_id}/iterations`.
- Added a public `jobs.get_workspace_version` helper and tightened parent-version workspace validation in `create_design_version`.
- Updated the generation worker to read iteration metadata and include it in both model-run parameters and child version parameters.

## Deviations from Plan

- None.

## Verification

- RED: `uv run pytest -q tests/test_generation.py` in `services/api` failed with 404 for the missing iteration route.
- RED: `uv run pytest -q tests/test_generation_tasks.py` in `services/worker` failed because the generated child version had no `parent_version_id`.
- GREEN: `uv run pytest -q tests/test_generation.py` in `services/api` passed, 7 tests.
- GREEN: `uv run pytest -q tests/test_generation_tasks.py` in `services/worker` passed, 4 tests.
- `uv run ruff check .` passed in `services/api`, `services/core`, and `services/worker`.
- `uv run mypy src` passed in `services/api`, `services/core`, and `services/worker`.
- `uv run pytest -q tests` passed in `services/core`, 32 tests.
- `uv run pytest -q tests` passed in `services/api`, 32 tests.
- `uv run pytest -q tests` passed in `services/worker`, 22 tests.

## Next Plan Readiness

Ready for `05-03`: refresh OpenAPI/contracts and add frontend wrappers/query keys for iteration, feedback, and export APIs.
