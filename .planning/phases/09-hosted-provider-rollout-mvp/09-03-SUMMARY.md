---
phase: 09-hosted-provider-rollout-mvp
plan: "03"
subsystem: api-worker-provider-routing
tags: [hosted-provider, preflight, api-contracts, worker-routing, quota]

requires:
  - phase: 09-hosted-provider-rollout-mvp
    provides: capability map and BFL adapter behavior from 09-01 and 09-02
provides:
  - Generation submission provider/model/provider_parameters intent contract
  - API preflight that blocks hosted jobs before enqueue unless all BFL gates pass
  - Worker routing from persisted job provider intent with runtime hosted preflight
affects:
  - phase-09-hosted-provider
  - provider-trace-persistence
  - hosted-failure-mapping
  - workbench-provider-selector

tech-stack:
  added: []
  patterns:
    - API accepts optional provider intent but never trusts browser cost or credentials
    - persisted job provider_intent is the worker route source when present
    - worker repeats hosted rollout, calls, credential, quota, rate, and cost gates before provider calls

key-files:
  created:
    - .planning/phases/09-hosted-provider-rollout-mvp/09-03-SUMMARY.md
  modified:
    - services/api/tests/test_generation.py
    - services/api/src/caragent_api/schemas.py
    - services/api/src/caragent_api/routes/generation.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts
    - services/worker/tests/test_generation_tasks.py
    - services/worker/src/caragent_worker/tasks/jobs.py

key-decisions:
  - "Keep provider intent as optional submission fields so omitted fields preserve V1 local deterministic behavior."
  - "Persist normalized provider intent on both job columns and `metadata.provider_intent` for worker routing and later trace APIs."
  - "Ignore browser-submitted estimated_cost; cost remains server/provider-owned."
  - "Apply the same provider intent schema to iteration submissions so follow-up generations do not need a parallel route later."

patterns-established:
  - "Generation route normalizes provider intent through local helper functions before calling `jobs.create_job()`."
  - "Worker extracts `metadata.provider_intent` and job provider/model columns before prompt planning."
  - "Unsupported persisted providers fail as provider_configuration before external provider calls."

requirements-completed:
  - V2-PROVIDER-01
  - V2-PROVIDER-02
  - V2-PROVIDER-05

duration: 9 min
completed: 2026-06-18
---

# Phase 9 Plan 03: Hosted Provider Preflight And Routing Summary

**Hosted provider submission intent with API-side BFL preflight, generated contracts, and worker-side runtime preflight before external calls**

## Performance

- **Duration:** 9 min
- **Started:** 2026-06-18T08:42:02Z
- **Completed:** 2026-06-18T08:51:01Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Added red API tests proving local default submission remains unchanged, blocked hosted intent is not enqueued, unsupported BFL models are rejected, and allowed BFL intent is persisted.
- Extended generation and iteration submission contracts with optional `provider`, `model`, and `provider_parameters` fields.
- Added API preflight against the browser-safe capability map so BFL requests require rollout flag, calls flag, credentials, quota/rate/cost guards, and allowed model.
- Regenerated OpenAPI and TypeScript contracts for the new submission fields.
- Added worker tests proving persisted provider intent overrides process defaults, runtime preflight blocks stale/unsafe hosted jobs, and unsupported persisted providers fail before provider calls.
- Updated worker prompt planning to consume persisted job provider intent while preserving local deterministic behavior when intent is absent.

## Task Commits

1. **Task 1: Add red API tests for provider/model submission intent and preflight** - `a4303af` (test)
2. **Task 2: Extend submission contracts and persist provider intent** - `486005a` (feat)
3. **Task 3: Route worker generation from persisted provider intent with authoritative preflight** - `d36b2f3` (test), `44d37f0` (feat)

## Files Created/Modified

- `services/api/tests/test_generation.py` - API submission preflight and provider intent persistence tests.
- `services/api/src/caragent_api/schemas.py` - Optional provider intent fields on generation and iteration submission requests.
- `services/api/src/caragent_api/routes/generation.py` - Provider intent normalization, BFL capability preflight, and safe job metadata persistence.
- `packages/contracts/openapi/openapi.json` and `packages/contracts/src/generated/client.ts` - Generated contract artifacts for provider intent fields.
- `services/worker/tests/test_generation_tasks.py` - Worker persisted-intent, runtime preflight, unsupported provider, and local-path tests.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Job provider intent extraction, prompt-provider settings override, and hosted runtime gate checks.

## Decisions Made

- Omitted provider fields continue to create local deterministic jobs with no provider/model columns set, preserving V1 behavior.
- Browser-supplied `estimated_cost` is ignored on generation submission. Estimated/actual costs remain server/provider controlled.
- Iteration submissions receive the same optional provider intent fields as first-generation submissions for consistency.
- Worker gate checks include V2 rollout flag, provider-call flag, BFL credential, quota, rate, and max-cost guard before any external call.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `uv run python -m caragent_api.scripts.export_openapi` needed the required `--out` argument; reran with `--out ../../packages/contracts/openapi/openapi.json`.
- `corepack pnpm contracts:check` needed escalated execution because the Node script invokes local `corepack pnpm generate`.
- Worker pytest passed with one aiosqlite event-loop-close warning during test teardown; no assertion failed.

## Verification

- Red tests failed first:
  - `cd services/api && uv run pytest -q tests/test_generation.py tests/test_operations.py` failed because BFL intent was ignored and blocked submissions returned 201.
  - `cd services/worker && uv run pytest -q tests/test_generation_tasks.py` failed because worker routing ignored persisted provider intent.
- Green verification passed:
  - `cd services/api && uv run pytest -q tests/test_generation.py tests/test_operations.py`
  - `cd services/worker && uv run pytest -q tests/test_generation_tasks.py`
  - `cd services/api && uv run ruff check .`
  - `cd services/worker && uv run ruff check .`
  - `corepack pnpm contracts:check`

## User Setup Required

None - no external service configuration required. Hosted calls still require explicit rollout/calls flags, BFL credentials, and guard limits before they can be enqueued or executed.

## Next Phase Readiness

Ready for `09-04-PLAN.md`: provider/model intent, provider parameters, and runtime route decisions now exist on jobs and model runs, so trace persistence can expose hosted route, fallback, cost, and sanitized diagnostics.

## Self-Check: PASSED

- Key files exist: PASS.
- Task acceptance criteria verified: PASS.
- Plan-level verification commands passed: PASS.
- Summary requirements match plan frontmatter: PASS.

---
*Phase: 09-hosted-provider-rollout-mvp*
*Completed: 2026-06-18*
