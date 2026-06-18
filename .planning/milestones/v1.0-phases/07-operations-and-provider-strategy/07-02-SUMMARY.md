---
phase: 07-operations-and-provider-strategy
plan: "02"
subsystem: provider-worker-health-operations-api
tags: [api, worker, operations, health, queue, contracts]

requires:
  - phase: "07-CONTEXT"
    provides: Phase 7 provider/worker health requirements
  - phase: "07-01"
    provides: shared operations metadata contract
provides:
  - enriched worker health payload
  - API provider/queue/worker operations status endpoint
  - best-effort Celery queue inspection
  - recent classified failure summaries
  - refreshed generated OpenAPI and TypeScript contracts
affects:
  - phase-07-03-failure-classification
  - phase-07-04-cancellation
  - phase-07-07-workbench-operations-ui

tech-stack:
  patterns:
    - operations endpoints report configured/unavailable truthfully instead of failing health requests
    - queue inspection is best-effort and non-canonical
    - provider secret values are represented only as booleans

key-files:
  modified:
    - services/worker/src/caragent_worker/config.py
    - services/worker/src/caragent_worker/tasks/health.py
    - services/worker/tests/test_worker_app.py
    - services/worker/tests/test_config.py
    - services/api/src/caragent_api/queue.py
    - services/api/src/caragent_api/routes/operations.py
    - services/api/src/caragent_api/main.py
    - services/api/src/caragent_api/schemas.py
    - services/api/tests/test_operations.py
    - services/api/tests/test_openapi_export.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts

key-decisions:
  - "Worker health now reports version, task name, queue, provider summary, hosted provider configured boolean, and recommended local pool."
  - "Operations API uses `app.state.settings` so tests and runtime report the actual configured API settings."
  - "Celery inspect failures degrade to queue/worker `unavailable` with sanitized generic detail."
  - "Recent failures are read from durable `GenerationJob` rows and operations metadata, not Celery result state."

patterns-established:
  - "Queue inspection returns a typed dataclass from the queue boundary; API schemas use `from_attributes=True` to accept it."
  - "Operations API schemas are contract-generated before frontend use."

requirements-completed:
  - OPS-01 partial
  - OPS-04 partial

duration: 30 min
completed: 2026-06-18
---

# Phase 7 Plan 02: Provider/Worker Health And Operations API Summary

**Operators can now inspect provider configuration, worker/queue availability, and recent failures through a typed API surface.**

## Accomplishments

- Added failing worker tests for enriched health payload and provider secret presence reporting.
- Added `WorkerSettings.hosted_provider_configured`.
- Updated `worker_health` to report worker version, generation task name, queue, provider default/model, calls-enabled flag, hosted-provider configured boolean, and Windows-safe `recommended_pool="solo"`.
- Added `QueueInspection` and `inspect_generation_queue()` to the API queue boundary.
- Added `GET /operations/provider-status` with provider, queue, worker, and recent failure summaries.
- Added tests for disabled local provider mode, hosted BFL configured mode without secret leakage, queue probe failure degradation, dataclass queue inspection, and recent classified failures.
- Refreshed OpenAPI and generated TypeScript contracts for the new route and schemas.

## Verification

- RED: `uv run pytest -q tests/test_worker_app.py tests/test_config.py -k "worker_health or hosted_provider"` in `services/worker` failed as expected because the health payload/settings summary were absent.
- GREEN: same worker focused command passed, 3 tests.
- `uv run pytest -q tests/test_worker_app.py tests/test_config.py` in `services/worker` passed, 12 tests.
- `uv run ruff check .` in `services/worker` passed.
- `uv run mypy src` in `services/worker` passed after rerunning with escalation for the Windows `uv` cache permission issue.
- RED: `uv run pytest -q tests/test_operations.py tests/test_health.py tests/test_openapi_export.py -k "operations or provider_status"` in `services/api` failed as expected because the operations route was missing.
- GREEN: same API focused command passed after route/schema implementation.
- Added a second RED/GREEN check for real `QueueInspection` dataclass validation; it failed before `from_attributes=True` and passed after the schema fix.
- `uv run pytest -q tests/test_operations.py tests/test_health.py tests/test_openapi_export.py` in `services/api` passed, 12 tests.
- `uv run ruff check .` in `services/api` passed.
- `uv run mypy src` in `services/api` passed after rerunning with escalation for the Windows `uv` cache permission issue.
- `corepack pnpm contracts:check` passed outside the sandbox.
- `corepack pnpm --filter @caragent/web typecheck` passed.

## Deviations from Plan

- Added an extra dataclass-path regression test after noticing the fake queue client only returned dictionaries. This caught and fixed a real Pydantic validation gap before live queue use.
- Contract artifacts were refreshed in this plan because a new API route/schema was introduced.

## Next Plan Readiness

Ready for `07-03`: failure classification and structured worker events.
