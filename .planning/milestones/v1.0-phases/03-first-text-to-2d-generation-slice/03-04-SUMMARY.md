---
phase: 03-first-text-to-2d-generation-slice
plan: "04"
subsystem: worker
tags: [generation, ledger, jobs, artifacts, model-runs, design-versions]

requires:
  - phase: 03-01
    provides: typed generation brief payload
  - phase: 03-02
    provides: deterministic prompt plan contract
  - phase: 03-03
    provides: local and hosted image provider adapters
  - phase: 02-05
    provides: durable jobs and job events
  - phase: 02-07
    provides: artifacts, model runs, and design versions
provides:
  - worker-owned 2D concept generation task
  - local generation ledger writes for model run, artifact, design version, job costs, and events
  - failure path with sanitized job and model-run errors
  - missing-rights reference gate before provider execution
affects: [phase-03-api-generation, phase-03-smoke, phase-05-iteration-lineage]

tech-stack:
  added: []
  patterns:
    - Async worker helper with injectable provider and object storage for tests
    - Core service helpers for model-run completion and failure
    - Durable PostgreSQL ledger remains source of truth

key-files:
  created:
    - services/core/tests/test_generation_jobs.py
    - services/worker/tests/test_generation_tasks.py
  modified:
    - services/core/src/caragent_core/services/jobs.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/worker/tests/test_worker_app.py

key-decisions:
  - "The Celery task delegates to an async helper so tests can inject storage/provider without Redis or MinIO."
  - "Worker creates the model run before checking rights so failure state still has prompt trace context."
  - "A job is marked succeeded only after generated image bytes are stored, artifact metadata is created, model run is completed, and design version is created."

patterns-established:
  - "Core jobs service owns model-run status mutation instead of worker code mutating ORM rows directly."
  - "Generation task uses InMemoryObjectStorage in tests and FileObjectStorage for local task default."
  - "Provider/config errors are sanitized before durable latest_error and model-run error_message fields."

requirements-completed: [GEN-04, GEN-05, GEN-06, GEN-07]

duration: 24 min
completed: 2026-06-17
---

# Phase 3 Plan 04: Worker Generation Ledger Summary

**Worker-owned local generation pipeline writes prompt trace, generated artifact, design version, costs, and durable job events**

## Performance

- **Duration:** 24 min
- **Started:** 2026-06-17T07:08:00Z
- **Completed:** 2026-06-17T07:32:21Z
- **Tasks:** 4
- **Files modified:** 5

## Accomplishments

- Added `complete_model_run(...)` and `fail_model_run(...)` helpers in core so worker code can finalize model runs without direct ORM mutation.
- Added `generate_2d_concept_job` and `run_generate_2d_concept_job(...)` for worker-owned prompt planning, rights validation, provider execution, artifact storage, design version creation, cost updates, and job events.
- Added generation worker tests proving success ledger completeness, provider failure sanitization, and missing-rights blocking before provider calls.
- Preserved worker architecture guard and added a Celery registration assertion for the generation task.

## Task Commits

No task commits were created during this inline run because the workspace already contains broad uncommitted GSD Phase 1/2/3 changes. The completed files are listed below and verified by the commands in this summary.

## Files Created/Modified

- `services/core/src/caragent_core/services/jobs.py` - Model-run completion/failure helpers and secret-aware error sanitization.
- `services/core/tests/test_generation_jobs.py` - Core tests for model-run completion timestamps/output artifact and sanitized failure text.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Generation Celery task and async helper for local provider execution and ledger writes.
- `services/worker/tests/test_generation_tasks.py` - Worker tests for successful generation, provider failure, and missing-rights failure.
- `services/worker/tests/test_worker_app.py` - Celery task registration assertion.

## Decisions Made

- Success event order is explicit: queued, worker started, prompt planned, artifact stored, design version created, generation completed.
- Missing-rights assets fail after prompt trace/model-run creation but before provider execution, preserving audit context without leaking invalid assets.
- The task returns compact IDs and status only; detailed state remains in durable job/model/artifact/version records.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `uv --no-cache run mypy src` for core and worker needed non-sandbox execution because uv could not open `.venv/.lock` inside the sandbox.
- Commit protocol was not applied because this workspace has existing broad uncommitted GSD outputs; this avoids mixing unrelated prior changes into an atomic `03-04` commit.

## Verification

- `uv run pytest -q tests/test_generation_tasks.py` - RED failed before implementation because `run_generate_2d_concept_job` was not exported.
- `uv run pytest -q tests/test_generation_jobs.py` - RED failed before implementation because `complete_model_run` and `fail_model_run` did not exist.
- `uv run pytest -q tests/test_worker_app.py tests/test_generation_tasks.py tests/test_image_providers.py` - passed, 13 tests.
- `uv run pytest -q tests/test_jobs.py tests/test_generation_jobs.py` - passed, 5 tests.
- `uv run pytest -q` in `services/worker` - passed, 21 tests.
- `uv run pytest -q` in `services/core` - passed, 30 tests.
- `uv run ruff check .` in `services/worker` - passed.
- `uv run ruff check .` in `services/core` - passed.
- `uv --no-cache run mypy src` in `services/worker` - passed outside sandbox, no issues in 10 source files.
- `uv --no-cache run mypy src` in `services/core` - passed outside sandbox, no issues in 16 source files.

## User Setup Required

None for local deterministic generation. Hosted provider calls remain gated by explicit worker settings.

## Next Phase Readiness

Ready for `03-05`: API routes can create/reuse typed briefs, enqueue `generate_2d_concept_job`, expose status, and retry failed generation while relying on the durable worker ledger.

---
*Phase: 03-first-text-to-2d-generation-slice*
*Completed: 2026-06-17*
