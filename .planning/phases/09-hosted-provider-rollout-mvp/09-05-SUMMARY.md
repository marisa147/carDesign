---
phase: 09-hosted-provider-rollout-mvp
plan: "05"
subsystem: hosted-failure-classification
tags: [provider-failures, moderation, rate-limit, credits, diagnostics, contracts]

requires:
  - phase: 09-hosted-provider-rollout-mvp
    provides: provider_status diagnostics from 09-04 and BFL status mapping from 09-02
provides:
  - BFL HTTP provider_status mapping for validation, credits, and rate-limit failures
  - Worker provider_failure_kind metadata for moderation, validation, credits, rate limits, timeout, and provider errors
  - API-visible provider_failure_kind in operations recent failures
affects:
  - phase-09-hosted-provider
  - workbench-provider-selector
  - operations-diagnostics

tech-stack:
  added: []
  patterns:
    - preserve existing failure_category values while adding provider_failure_kind for hosted subcategories
    - map provider_status deterministically before API exposure
    - keep provider diagnostics redacted and structured

key-files:
  created:
    - .planning/phases/09-hosted-provider-rollout-mvp/09-05-SUMMARY.md
  modified:
    - services/worker/tests/test_image_providers.py
    - services/worker/tests/test_generation_tasks.py
    - services/worker/src/caragent_worker/providers/bfl.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/api/tests/test_operations.py
    - services/api/src/caragent_api/schemas.py
    - services/api/src/caragent_api/routes/operations.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts

key-decisions:
  - "Do not expand the top-level FailureCategory enum for this plan; keep compatibility and add `provider_failure_kind` metadata instead."
  - "Map BFL 400/422 to `provider_validation`, 402 to `insufficient_credits`, and 429 to `rate_limited`."
  - "Expose provider_failure_kind through operations status so UI/operator surfaces can distinguish moderation, rate, credit, validation, timeout, and generic provider failures."

patterns-established:
  - "Worker failure metadata includes provider_status, provider_status_code when available, and provider_failure_kind."
  - "Operations recent failures expose category plus provider subcategory fields without raw provider payloads."
  - "BFL adapter normalizes HTTP-level provider failures before worker classification."

requirements-completed:
  - V2-PROVIDER-02
  - V2-PROVIDER-04

duration: 6 min
completed: 2026-06-18
---

# Phase 9 Plan 05: Hosted Failure Classification Summary

**Hosted provider failures now preserve compatible categories while exposing structured moderation, validation, credits, rate-limit, timeout, and provider-error diagnostics**

## Performance

- **Duration:** 6 min
- **Started:** 2026-06-18T08:58:42Z
- **Completed:** 2026-06-18T09:04:22Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Added red tests for BFL HTTP status normalization, worker provider_status to provider_failure_kind mapping, and operations API exposure.
- Updated the BFL adapter so HTTP 400/422 become `provider_validation`, 402 becomes `insufficient_credits`, and 429 remains `rate_limited`.
- Added worker metadata mapping from provider_status/classes to provider_failure_kind while keeping existing failure_category behavior.
- Exposed provider_failure_kind in operations recent failures and regenerated OpenAPI/TypeScript contracts.
- Verified diagnostics remain secret-free in provider, worker, and API tests.

## Task Commits

1. **Task 1: Add red tests for hosted failure classification** - `8e3c407` (test)
2. **Task 2: Implement provider failure categories or structured subcategories** - `97c9fc1` (feat)
3. **Task 3: Expose safe failure diagnostics to API and operations** - `05b68c8` (feat)

## Files Created/Modified

- `services/worker/tests/test_image_providers.py` - BFL HTTP status mapping tests.
- `services/worker/tests/test_generation_tasks.py` - Worker provider_status/provider_failure_kind metadata tests.
- `services/worker/src/caragent_worker/providers/bfl.py` - BFL HTTP status normalization.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Provider failure metadata and provider_failure_kind mapping.
- `services/api/tests/test_operations.py` - Operations provider_failure_kind response test.
- `services/api/src/caragent_api/schemas.py` - Recent failure provider_failure_kind field.
- `services/api/src/caragent_api/routes/operations.py` - Recent failure provider_failure_kind mapping.
- `packages/contracts/openapi/openapi.json` and `packages/contracts/src/generated/client.ts` - Generated contract artifacts.

## Decisions Made

- Keep `failure_category` stable for existing clients and use `provider_failure_kind` for hosted-specific subcategories.
- Treat provider validation as a structured provider subcategory rather than a generic unknown error.
- Keep all provider diagnostics derived from sanitized/normalized metadata only.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `corepack pnpm contracts:check` required escalated execution because its Node script invokes local `corepack pnpm generate`.

## Verification

- Red tests failed first:
  - `cd services/worker && uv run pytest -q tests/test_image_providers.py tests/test_generation_tasks.py` failed on BFL 400 mapping and missing worker provider_status/provider_failure_kind metadata.
  - `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_operations.py` failed on missing operations provider_failure_kind.
- Green verification passed:
  - `cd services/worker && uv run pytest -q tests/test_image_providers.py tests/test_generation_tasks.py`
  - `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_operations.py`
  - `cd services/worker && uv run ruff check .`
  - `cd services/api && uv run ruff check .`
  - `corepack pnpm contracts:check`

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for `09-06-PLAN.md`: API and operations responses now expose enough provider capability, guard, route, cost, and failure diagnostics for the workbench provider selector and hosted-call warning UI.

## Self-Check: PASSED

- Key files exist: PASS.
- Task acceptance criteria verified: PASS.
- Plan-level verification commands passed: PASS.
- Summary requirements match plan frontmatter: PASS.

---
*Phase: 09-hosted-provider-rollout-mvp*
*Completed: 2026-06-18*
