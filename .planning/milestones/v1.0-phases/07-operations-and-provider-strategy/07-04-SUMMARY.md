---
phase: 07-operations-and-provider-strategy
plan: "04"
subsystem: job-cancellation
tags: [api, worker, queue, cancellation, operations]

requires:
  - phase: "07-01"
    provides: core operations metadata and cancellation failure category
  - phase: "07-02"
    provides: API queue boundary and operations visibility surface
provides:
  - durable queued/running job cancellation
  - generation queue task-id persistence
  - best-effort Celery revoke handoff
  - worker cancellation guards before expensive side effects
  - generated OpenAPI and TypeScript cancel contracts
affects:
  - phase-07-05-retry-fallback
  - phase-07-06-quota-rate-limit
  - phase-07-07-workbench-operations-ui

tech-stack:
  patterns:
    - durable job status is authoritative; Celery revoke is best-effort
    - generation enqueue metadata is persisted under `job.metadata.queue`
    - worker checks durable canceled state before provider/storage/success writes

key-files:
  modified:
    - services/core/src/caragent_core/services/jobs.py
    - services/core/tests/test_jobs.py
    - services/api/src/caragent_api/queue.py
    - services/api/src/caragent_api/routes/generation.py
    - services/api/src/caragent_api/routes/jobs.py
    - services/api/src/caragent_api/schemas.py
    - services/api/tests/test_generation.py
    - services/api/tests/test_queue.py
    - services/api/tests/test_openapi_export.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/worker/tests/test_generation_tasks.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts

key-decisions:
  - "Cancellation is allowed only from queued or running jobs; terminal jobs reject with validation."
  - "API cancellation writes the durable canceled state first, then attempts queue revoke without undoing the state if revoke fails."
  - "Known Celery task id, task name, and queue name are stored on generation jobs immediately after enqueue."
  - "Worker cancellation guards return `canceled` and avoid provider/storage/version side effects when canceled state is observed before those stages."
  - "Provider calls already in flight remain best-effort; worker prevents final success overwrite after observing cancellation."

patterns-established:
  - "Queue boundary returns typed dataclasses for enqueue, inspect, and revoke operations."
  - "Cancellation tests assert job status, latest_error, operations metadata, queue revoke response, and worker side-effect absence together."

requirements-completed:
  - OPS-05 partial
  - OPS-04 partial

duration: 45 min
completed: 2026-06-18
---

# Phase 7 Plan 04: Job Cancellation Summary

**Users can now cancel eligible generation jobs through the API, and workers respect the durable canceled state before expensive or final side effects.**

## Accomplishments

- Added `jobs.cancel_job()` in core with queued/running-only validation and structured `canceled` operations metadata.
- Added generation queue metadata persistence for submit, retry, and child-iteration jobs.
- Added `QueueRevokeResult` and `revoke_generation_task()` to the API queue boundary.
- Added `POST /jobs/{job_id}/cancel` returning both the canceled job and queue revoke summary.
- Added cancellation request/response schemas and refreshed OpenAPI plus generated TypeScript contracts.
- Added worker guards for canceled jobs at worker start, after prompt planning, after rights checks, after provider return, and before final success transition.
- Added tests proving canceled jobs do not call the provider before execution, do not create artifacts/versions after cancellation is observed, and do not overwrite canceled state with success.

## Verification

- RED: `uv run pytest -q tests/test_jobs.py -k "cancel_job"` in `services/core` failed before `cancel_job()` existed.
- GREEN: `uv run pytest -q tests/test_jobs.py -k "cancel_job"` in `services/core` passed, 2 tests.
- `uv run pytest -q tests/test_jobs.py` in `services/core` passed, 10 tests.
- `uv run ruff check .` in `services/core` passed.
- `uv run mypy src` in `services/core` passed with escalation for the Windows `uv` cache permission issue.
- `uv run pytest -q tests/test_generation.py tests/test_jobs.py tests/test_queue.py tests/test_openapi_export.py` in `services/api` passed, 22 tests.
- `uv run ruff check .` in `services/api` passed after import sorting.
- `uv run mypy src` in `services/api` passed with escalation for the Windows `uv` cache permission issue.
- RED: `uv run pytest -q tests/test_generation_tasks.py -k cancel` in `services/worker` failed because the worker still called the provider and lacked cancel guards.
- GREEN: same worker cancel command passed, 3 tests.
- `uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py` in `services/worker` passed, 18 tests.
- `uv run ruff check .` in `services/worker` passed.
- `uv run mypy src` in `services/worker` passed with escalation for the Windows `uv` cache permission issue.
- `uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json` refreshed OpenAPI.
- `corepack pnpm --filter @caragent/contracts generate` refreshed generated TypeScript client.
- `corepack pnpm contracts:check` passed with escalation.
- `corepack pnpm --filter @caragent/web typecheck` passed.

## Deviations from Plan

- Queue revoke failure is reported in the API response rather than appended as a separate job event. The durable canceled event already records who canceled and why; the revoke result belongs to the request handoff.
- Worker tests use controlled same-session cancellation hooks for mid-pipeline stages to avoid unrelated SQLite/event-sequence transaction races.
- Running provider requests are not forcibly terminated. The worker treats those as best-effort and prevents later storage/version/success writes after canceled state is observed.

## Next Plan Readiness

Ready for `07-05`: provider routing, bounded retries, and visible fallback.
