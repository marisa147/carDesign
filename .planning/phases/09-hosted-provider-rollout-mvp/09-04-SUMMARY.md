---
phase: 09-hosted-provider-rollout-mvp
plan: "04"
subsystem: provider-trace-diagnostics
tags: [model-runs, provider-trace, cost, fallback, diagnostics, contracts]

requires:
  - phase: 09-hosted-provider-rollout-mvp
    provides: BFL adapter and persisted provider intent from 09-02 and 09-03
provides:
  - Provider/model/cost trace metadata on hosted artifacts and versions
  - Durable fallback-to-local evidence in job operations, artifacts, versions, model runs, and events
  - API-visible artifact metadata and recent failure provider_status diagnostics
affects:
  - phase-09-hosted-provider
  - hosted-failure-mapping
  - workbench-provider-selector
  - operations-diagnostics

tech-stack:
  added: []
  patterns:
    - model_runs remain the canonical provider call trace
    - artifact/version/job metadata carry normalized provider route and cost summaries
    - API schemas expose normalized trace fields without raw provider payloads

key-files:
  created:
    - .planning/phases/09-hosted-provider-rollout-mvp/09-04-SUMMARY.md
  modified:
    - services/worker/tests/test_generation_tasks.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/api/tests/test_jobs.py
    - services/api/tests/test_operations.py
    - services/api/src/caragent_api/schemas.py
    - services/api/src/caragent_api/routes/operations.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts

key-decisions:
  - "Keep `model_runs` as the detailed provider-call ledger and use artifact/version/job metadata for fast UI/operator summaries."
  - "Represent costs in metadata as four-decimal strings while preserving database numeric columns for accounting."
  - "Add `fallback_to_provider` and a `Fallback provider started.` event so hosted fallback cannot be mistaken for ordinary local generation."
  - "Expose artifact metadata and recent failure provider_status through API contracts, but keep raw provider payloads and signed URLs out."

patterns-established:
  - "Worker builds provider trace metadata from the normalized request/result pair after provider execution."
  - "Fallback execution records from-provider, to-provider, reason, attempt count, and start event."
  - "Operations recent failures can surface provider_status alongside category, stage, provider, model, and sanitized message."

requirements-completed:
  - V2-PROVIDER-03
  - V2-PROVIDER-04

duration: 8 min
completed: 2026-06-18
---

# Phase 9 Plan 04: Provider Trace And Diagnostics Summary

**Provider call trace persistence with hosted cost metadata, visible fallback evidence, artifact metadata API exposure, and provider_status diagnostics**

## Performance

- **Duration:** 8 min
- **Started:** 2026-06-18T08:51:01Z
- **Completed:** 2026-06-18T08:58:42Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Added red tests for hosted provider actual cost, provider/model trace metadata, fallback visibility, artifact metadata API exposure, and operations provider_status diagnostics.
- Persisted normalized provider/model/estimated_cost/actual_cost/provider_parameters metadata on generated artifacts and design versions.
- Added `fallback_to_provider` and a durable "Fallback provider started." event so fallback execution is reviewable.
- Exposed artifact metadata through the jobs API and `provider_status` through operations recent failures.
- Regenerated OpenAPI and TypeScript contracts for the new diagnostics fields.

## Task Commits

1. **Task 1: Add red tests for provider trace and cost semantics** - `da8e05f` (test)
2. **Task 2: Persist hosted route and fallback metadata consistently** - `d629233` (feat)
3. **Task 3: Surface trace and sanitized diagnostics through API** - `e26a82f` (feat)

## Files Created/Modified

- `services/worker/tests/test_generation_tasks.py` - Provider trace, actual-cost, fallback-to-provider, and fallback event tests.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Provider trace metadata helper and fallback-start event persistence.
- `services/api/tests/test_jobs.py` - Artifact metadata API exposure test.
- `services/api/tests/test_operations.py` - Recent failure provider_status diagnostics test.
- `services/api/src/caragent_api/schemas.py` - Artifact metadata and recent failure provider_status response fields.
- `services/api/src/caragent_api/routes/operations.py` - Maps operations metadata provider_status into recent failure responses.
- `packages/contracts/openapi/openapi.json` and `packages/contracts/src/generated/client.ts` - Generated contract artifacts.

## Decisions Made

- Artifact/version metadata stores normalized provider trace summaries; model_runs remain the canonical full provider attempt record.
- Cost metadata uses strings like `0.0300` to stay JSON-safe and avoid conflating null hosted cost with free local cost.
- Failure payloads still expose only sanitized fields; raw provider bodies and signed result URLs remain excluded.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `corepack pnpm contracts:check` required escalated execution because its Node script invokes local `corepack pnpm generate`.

## Verification

- Red tests failed first:
  - `cd services/worker && uv run pytest -q tests/test_generation_tasks.py` failed on missing `fallback_to_provider` and artifact provider trace metadata.
  - `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_operations.py` failed on missing artifact `metadata` and recent failure `provider_status`.
- Green verification passed:
  - `cd services/worker && uv run pytest -q tests/test_generation_tasks.py`
  - `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_operations.py`
  - `cd services/worker && uv run ruff check .`
  - `cd services/api && uv run ruff check .`
  - `corepack pnpm contracts:check`

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for `09-05-PLAN.md`: provider_status is now surfaced safely, and the next plan can map moderation, validation, rate, credit, timeout, and provider failures into more specific user/operator categories.

## Self-Check: PASSED

- Key files exist: PASS.
- Task acceptance criteria verified: PASS.
- Plan-level verification commands passed: PASS.
- Summary requirements match plan frontmatter: PASS.

---
*Phase: 09-hosted-provider-rollout-mvp*
*Completed: 2026-06-18*
