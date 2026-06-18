---
phase: 03-first-text-to-2d-generation-slice
plan: "05"
subsystem: api
tags: [fastapi, generation, queue, celery, openapi]

requires:
  - phase: 03-01
    provides: typed generation brief schema
  - phase: 03-02
    provides: prompt trace contract
  - phase: 03-04
    provides: worker generation task and durable ledger writes
  - phase: 02-06
    provides: API job/status/event contract patterns
provides:
  - structured generation brief API routes
  - generation job submission route
  - failed-job retry route
  - queue boundary that enqueues worker task by name without importing worker modules
  - OpenAPI source coverage for Phase 3 generation routes
affects: [phase-03-contracts-web, phase-03-smoke, phase-04-workbench-ui]

tech-stack:
  added:
    - celery
  patterns:
    - API queue protocol with fake queue injection in tests
    - Async generation route returns pollable durable job state
    - Retry creates a new durable job preserving failed attempt state

key-files:
  created:
    - services/api/src/caragent_api/queue.py
    - services/api/src/caragent_api/routes/generation.py
    - services/api/tests/test_generation.py
  modified:
    - services/api/pyproject.toml
    - services/api/uv.lock
    - services/api/src/caragent_api/dependencies.py
    - services/api/src/caragent_api/main.py
    - services/api/src/caragent_api/schemas.py
    - services/api/tests/test_openapi_export.py

key-decisions:
  - "API enqueues `caragent_worker.generate_2d_concept_job` by string task name and never imports worker modules."
  - "Duplicate generation submissions reuse the existing idempotent job and do not enqueue duplicate work."
  - "Retry is limited to failed jobs and creates a new durable job tied to the original brief."

patterns-established:
  - "FastAPI routes depend on `QueueClient` from app state, allowing tests to inject a fake queue."
  - "Generation brief API returns typed `GenerationBriefPayload` instead of arbitrary JSON only."
  - "OpenAPI tests list Phase 3 generation routes as contract-source requirements."

requirements-completed: [GEN-01, GEN-02, GEN-03, GEN-05, GEN-07]

duration: 16 min
completed: 2026-06-17
---

# Phase 3 Plan 05: Generation API Routes Summary

**FastAPI generation routes create structured briefs, enqueue async generation jobs, and retry failed attempts without provider work in request handlers**

## Performance

- **Duration:** 16 min
- **Started:** 2026-06-17T07:22:30Z
- **Completed:** 2026-06-17T07:38:50Z
- **Tasks:** 4
- **Files modified:** 9

## Accomplishments

- Added structured generation brief create/update routes with typed `GenerationBriefPayload` responses.
- Added generation job submission route using operation `generate_2d_concept`, durable idempotency, and fake-queue injectable async enqueueing.
- Added failed-job retry route that preserves the failed job and creates a new queued attempt tied to the same brief.
- Added OpenAPI coverage for Phase 3 generation routes and schemas.

## Task Commits

No task commits were created during this inline run because the workspace already contains broad uncommitted GSD Phase 1/2/3 changes. The completed files are listed below and verified by the commands in this summary.

## Files Created/Modified

- `services/api/src/caragent_api/queue.py` - Queue protocol and Celery task-name client.
- `services/api/src/caragent_api/routes/generation.py` - Generation brief, submit, and retry routes.
- `services/api/src/caragent_api/dependencies.py` - Queue dependency accessor.
- `services/api/src/caragent_api/main.py` - Queue client registration and generation router inclusion.
- `services/api/src/caragent_api/schemas.py` - Generation brief/job/retry/queue schemas.
- `services/api/pyproject.toml` and `services/api/uv.lock` - API-scoped Celery client dependency and mypy override.
- `services/api/tests/test_generation.py` - API generation behavior, queue, retry, validation, and boundary tests.
- `services/api/tests/test_openapi_export.py` - Phase 3 route/schema OpenAPI assertions.

## Decisions Made

- The API queue boundary returns only task metadata, never provider secrets or database URLs in responses.
- Duplicate idempotency submissions do not re-enqueue the worker task.
- The route boundary allows the worker task name as a string but forbids importing `caragent_worker`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Celery lacks typed stubs, so API mypy config now mirrors worker mypy behavior with an `ignore_missing_imports` override for `celery`.
- `uv add celery==5.6.3` and API mypy required non-sandbox execution due uv cache/lock permissions.
- Commit protocol was not applied because this workspace has existing broad uncommitted GSD outputs; this avoids mixing unrelated prior changes into an atomic `03-05` commit.

## Verification

- `uv run pytest -q tests/test_generation.py` - RED failed before implementation because generation routes returned 404.
- `uv run pytest -q tests/test_generation.py` - passed, 5 tests.
- `uv run pytest -q tests/test_openapi_export.py tests/test_generation.py` - passed, 8 tests.
- `uv run pytest -q` in `services/api` - passed, 28 tests.
- `uv run ruff check .` in `services/api` - passed.
- `uv --no-cache run mypy src` in `services/api` - passed outside sandbox, no issues in 13 source files.

## User Setup Required

None for tests. Running the real API queue requires Redis/Celery configuration; local tests inject a fake queue and do not contact Redis.

## Next Phase Readiness

Ready for `03-06`: OpenAPI can be exported, generated TypeScript contracts can be refreshed, and the web proof can call the new generation routes.

---
*Phase: 03-first-text-to-2d-generation-slice*
*Completed: 2026-06-17*
