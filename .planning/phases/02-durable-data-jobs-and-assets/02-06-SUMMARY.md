---
phase: 02-durable-data-jobs-and-assets
plan: "06"
subsystem: "typed contracts and frontend API wrappers"
tags: ["openapi", "orval", "contracts", "frontend", "wrappers"]
requires:
  - ".planning/phases/02-durable-data-jobs-and-assets/02-06-PLAN.md"
  - ".planning/phases/02-durable-data-jobs-and-assets/02-03-SUMMARY.md"
  - ".planning/phases/02-durable-data-jobs-and-assets/02-04-SUMMARY.md"
  - ".planning/phases/02-durable-data-jobs-and-assets/02-05-SUMMARY.md"
provides:
  - "OpenAPI test coverage for Phase 2 product routes and schemas"
  - "Refreshed OpenAPI artifact and generated TypeScript client"
  - "Typed workspace and job frontend API wrappers"
  - "Wrapper tests for generated route helpers, JSON bodies, fetch injection, and error handling"
key-files:
  created:
    - "apps/web/src/lib/api/workspaces.ts"
    - "apps/web/src/lib/api/workspaces.test.ts"
    - "apps/web/src/lib/api/jobs.ts"
    - "apps/web/src/lib/api/jobs.test.ts"
  modified:
    - "services/api/tests/test_openapi_export.py"
    - "packages/contracts/openapi/openapi.json"
    - "packages/contracts/src/generated/client.ts"
    - "scripts/check-contracts.mjs"
key-decisions:
  - "Frontend wrappers import generated URL helpers and generated request/response types instead of duplicating API interfaces."
  - "Wrappers keep binary/object-storage concerns out of the browser-facing Phase 2 proof surface."
  - "`scripts/check-contracts.mjs` falls back to `corepack pnpm` when `pnpm` is not directly on PATH under NVM-managed Node."
requirements-completed: ["DATA-01", "DATA-02", "DATA-03", "DATA-04", "DATA-05", "DATA-06", "DATA-07"]
duration: "in-session"
completed: 2026-06-17
---

# Phase 2 Plan 06: Contracts And Frontend Wrappers Summary

Plan 02-06 refreshed the typed API contract surface for all Phase 2 product routes and added small generated-contract-based frontend wrappers for workspace and job persistence flows.

## Tasks Completed

| Task | Result | Evidence |
|------|--------|----------|
| OpenAPI product route coverage | Complete | `test_openapi_export_includes_phase_2_product_routes_and_schemas` asserts workspaces, messages, briefs, assets, rights, jobs, events, versions, artifacts, feedback, exports, and cost/idempotency fields. |
| Contract generation/check | Complete | FastAPI OpenAPI was exported, Orval regenerated `packages/contracts/src/generated/client.ts`, and contract drift check passed. |
| Frontend workspace wrappers | Complete | Added create/resume workspace and list/create message wrappers using generated URL helpers and generated types. |
| Frontend job wrappers | Complete | Added create/list/read job and list event wrappers using generated URL helpers and generated types. |
| Wrapper tests | Complete | Tests failed RED before modules existed, then passed after implementation. |

## Verification

| Command | Result |
|---------|--------|
| `cd services/api && uv run pytest -q tests/test_openapi_export.py` | Passed, `3 passed`. |
| `cd services/api && uv run ruff check .` | Passed. |
| `corepack pnpm --filter @caragent/contracts generate` | Passed; Orval generated the client. |
| `corepack pnpm --filter @caragent/contracts check` | Passed; contract artifacts current. |
| `corepack pnpm --filter @caragent/contracts typecheck` | Passed. |
| `corepack pnpm --filter @caragent/web typecheck` | Passed. |
| `corepack pnpm --filter @caragent/web test` | Passed, `13 passed`. |
| `corepack pnpm --filter @caragent/web lint` | Passed. |

## Deviations from Plan

**[Rule 1 - Toolchain] Use Corepack when pnpm is not on PATH**
- Found during: contract check.
- Issue: Under NVM Node 22.15.0, `pnpm` was still not directly available on PATH. `corepack pnpm` worked after Corepack initialized pnpm.
- Fix: Updated `scripts/check-contracts.mjs` to retry contract generation through `corepack pnpm` when direct `pnpm` is unavailable or sandbox-blocked.
- Verification: `corepack pnpm --filter @caragent/contracts check` passed.

**[Rule 1 - Generated Type Shape] Request body helper accepts generated interfaces**
- Found during: web typecheck.
- Issue: Wrapper internals used `Record<string, unknown>`, which rejected generated request interfaces without index signatures.
- Fix: Loosened the internal JSON body parameter to `unknown` while preserving generated request types at wrapper boundaries.
- Verification: Web typecheck and wrapper tests passed.

## Self-Check: PASSED

All Phase 2 product routes are represented in deterministic OpenAPI, generated TypeScript contracts are current, and frontend code consumes generated contract helpers/types for the Phase 2 persistence proof surface. No wrapper exposes object-storage credentials or handwritten API response interfaces.

## Next

Ready for `02-07-PLAN.md`: worker no-provider durable job simulation and boundary tests.
