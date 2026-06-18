---
phase: 07-operations-and-provider-strategy
plan: "06"
subsystem: hosted-quota-rate-preflight
tags: [worker, api, quota, rate-limit, provider, operations]

requires:
  - phase: "07-05"
    provides: explicit provider routing and attempt lifecycle
provides:
  - hosted quota/rate/cost settings
  - operations API guard summary fields
  - hosted provider preflight guard
  - durable model-run usage counting
  - refreshed OpenAPI and TypeScript contracts
affects:
  - phase-07-07-workbench-operations-ui

tech-stack:
  patterns:
    - local deterministic provider is quota-exempt
    - hosted guard counts durable non-local `ModelRun` rows
    - current model run is excluded from quota/rate counts
    - guard failures are classified as provider configuration failures

key-files:
  modified:
    - .env.example
    - docs/development.md
    - services/api/.env.example
    - services/api/src/caragent_api/config.py
    - services/api/src/caragent_api/routes/operations.py
    - services/api/src/caragent_api/schemas.py
    - services/api/tests/test_operations.py
    - services/api/tests/test_openapi_export.py
    - services/worker/.env.example
    - services/worker/src/caragent_worker/config.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/worker/tests/test_config.py
    - services/worker/tests/test_generation_tasks.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts

key-decisions:
  - "Hosted calls require daily, per-minute, and per-job cost guard settings before execution."
  - "Missing or exceeded hosted guards fail before provider execution and do not call the provider adapter."
  - "Local deterministic generation bypasses hosted quota/rate controls and remains zero-cost."
  - "v1 guard usage is derived from existing durable `ModelRun` rows; no billing/quota table is added."
  - "Operations API exposes guard values and blocked reason without secrets or account identifiers."

patterns-established:
  - "Quota/rate preflight runs after rights checks but before provider selection/generation."
  - "Operations provider summary distinguishes provider configured state from quota guard enabled state."
  - "Env examples document all hosted provider guard variables with blank local defaults."

requirements-completed:
  - OPS-06 partial
  - OPS-03 partial

duration: 35 min
completed: 2026-06-18
---

# Phase 7 Plan 06: Hosted Quota And Rate Preflight Summary

**Hosted provider calls are now blocked before execution unless quota, rate, and per-job cost guards are explicitly configured and not exceeded.**

## Accomplishments

- Added worker/API settings for `AI_HOSTED_DAILY_CALL_LIMIT`, `AI_HOSTED_RATE_LIMIT_PER_MINUTE`, and `AI_MAX_ESTIMATED_COST_PER_JOB`.
- Extended `/operations/provider-status` provider summary with hosted guard values, guard-enabled boolean, and blocked reason.
- Added worker preflight before hosted provider execution.
- Counted prior hosted attempts from durable `ModelRun` rows, excluding the current attempt row.
- Blocked hosted calls with missing guard settings, exceeded daily limit, and exceeded per-minute rate limit before provider adapter execution.
- Preserved local deterministic generation as quota-exempt and zero-cost.
- Updated env examples and development docs for hosted guard configuration.
- Refreshed OpenAPI and generated TypeScript contracts for new operations fields.

## Verification

- RED: `uv run pytest -q tests/test_config.py -k "quota or rate"` in `services/worker` failed before quota/rate settings existed.
- RED: `uv run pytest -q tests/test_operations.py -k quota` in `services/api` failed before operations summary fields existed.
- RED: `uv run pytest -q tests/test_generation_tasks.py -k "quota or rate or hosted"` in `services/worker` failed because hosted calls still executed without guard checks.
- GREEN: focused worker config, API operations quota, and worker hosted quota/rate checks passed after implementation.
- `uv run pytest -q tests/test_config.py tests/test_image_providers.py tests/test_generation_tasks.py` in `services/worker` passed, 37 tests.
- `uv run ruff check .` in `services/worker` passed after import sorting.
- `uv run mypy src` in `services/worker` passed with escalation for the Windows `uv` cache permission issue.
- `uv run pytest -q tests/test_operations.py tests/test_openapi_export.py` in `services/api` passed, 10 tests.
- `uv run ruff check .` in `services/api` passed.
- `uv run mypy src` in `services/api` passed with escalation for the Windows `uv` cache permission issue.
- `corepack pnpm exec node scripts/check-env-examples.mjs` passed.
- `uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json` refreshed OpenAPI.
- `corepack pnpm --filter @caragent/contracts generate` refreshed generated TypeScript client.
- `corepack pnpm contracts:check` passed with escalation.
- `corepack pnpm --filter @caragent/web typecheck` passed.

## Deviations from Plan

- No dedicated quota/billing table was added. Existing `ModelRun` rows are sufficient for v1 guard preflight and keep Phase 7 migration-free.
- Unknown estimated cost is allowed when max-cost guard is configured; the current BFL/local adapter paths do not yet emit real price estimates. Exceeded known estimates are still blocked.
- API settings mirror worker guard fields for operations visibility, but provider execution remains worker-owned.

## Next Plan Readiness

Ready for `07-07`: workbench operations UI, docs, smoke, and UAT closure.
