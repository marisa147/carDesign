---
phase: 07-operations-and-provider-strategy
plan: "01"
subsystem: operations-metadata-contract
tags: [core, api, contracts, operations, failures]

requires:
  - phase: "07-CONTEXT"
    provides: Phase 7 operations/provider strategy decisions
  - phase: "07-RESEARCH"
    provides: current job/provider/worker code facts and plan breakdown
provides:
  - core failure category taxonomy
  - structured job status transition metadata
  - safe job/event metadata API responses
  - refreshed generated OpenAPI and TypeScript contracts
affects:
  - phase-07-02-provider-worker-health
  - phase-07-03-failure-classification
  - phase-07-04-cancellation

tech-stack:
  patterns:
    - existing PostgreSQL JSON metadata columns carry v1 operations fields
    - Pydantic response schemas map SQLAlchemy `metadata_json` to public `metadata`
    - contract drift is checked through `corepack pnpm contracts:check`

key-files:
  modified:
    - services/core/src/caragent_core/enums.py
    - services/core/src/caragent_core/services/jobs.py
    - services/core/tests/test_jobs.py
    - services/api/src/caragent_api/schemas.py
    - services/api/tests/test_jobs.py
    - services/api/tests/test_openapi_export.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts

key-decisions:
  - "Added `FailureCategory` as a core enum rather than duplicating category strings in API/worker/web."
  - "Kept Phase 7 operational data in existing `metadata_json` columns; no database migration was needed."
  - "Sanitized metadata string values with the same secret-redaction path used for `latest_error`."
  - "Public API field is `metadata`, sourced from internal `metadata_json`."

patterns-established:
  - "Status transitions can attach structured event metadata and persist terminal operational metadata on the job."
  - "API schemas should use explicit Pydantic validation aliases when exposing model `metadata_json` fields."

requirements-completed:
  - OPS-01 partial
  - OPS-02 partial
  - OPS-04 partial

duration: 25 min
completed: 2026-06-18
---

# Phase 7 Plan 01: Operations Metadata Contract Summary

**Core/API now share a typed operational metadata contract for Phase 7.**

## Accomplishments

- Added red tests for the Phase 7 failure category taxonomy and job/event operational metadata persistence.
- Added `FailureCategory` with provider, provider configuration, validation/rights, storage, queue/worker, canceled, timeout, and unknown categories.
- Extended `transition_job_status()` with safe `metadata` and `secrets` support.
- Persisted terminal operational metadata under `GenerationJob.metadata_json["operations"]` while preserving existing metadata keys.
- Added `metadata` to `GenerationJobResponse` and `JobEventResponse`, mapped from SQLAlchemy `metadata_json`.
- Refreshed OpenAPI and generated TypeScript contracts after the API schema change.

## Verification

- RED: `uv run pytest -q tests/test_jobs.py -k "operations_taxonomy or operational_failure_metadata or canceled_operational_metadata"` in `services/core` failed as expected.
- GREEN: same core focused command passed, 3 tests.
- `uv run pytest -q tests/test_jobs.py` in `services/core` passed, 8 tests.
- `uv run ruff check .` in `services/core` passed.
- `uv run mypy src` in `services/core` passed after rerunning with escalation because the first sandboxed run hit a Windows `uv` cache permission error.
- RED: `uv run pytest -q tests/test_jobs.py tests/test_openapi_export.py -k "operational_metadata or metadata"` in `services/api` failed as expected because response metadata was absent.
- GREEN: `uv run pytest -q tests/test_jobs.py tests/test_openapi_export.py -k "operational_metadata or openapi_export_includes_phase_2_product_routes_and_schemas"` in `services/api` passed.
- `uv run pytest -q tests/test_jobs.py tests/test_openapi_export.py` in `services/api` passed, 9 tests.
- `uv run ruff check .` in `services/api` passed.
- `uv run mypy src` in `services/api` passed after rerunning with escalation for the same Windows `uv` cache permission issue.
- `corepack pnpm contracts:check` passed after running outside the sandbox; the sandboxed check falls back and rewrites `client.ts` incorrectly in this environment.
- `corepack pnpm --filter @caragent/web typecheck` passed.

## Deviations from Plan

- Contract artifacts were refreshed in Plan 07-01 instead of waiting for 07-07, because the API response schema changed and leaving generated contracts stale would break the validation baseline.
- No database migration was introduced.

## Next Plan Readiness

Ready for `07-02`: provider/worker health and operations API.
