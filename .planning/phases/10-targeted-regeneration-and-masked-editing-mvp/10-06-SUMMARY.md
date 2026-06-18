---
phase: 10-targeted-regeneration-and-masked-editing-mvp
plan: "06"
subsystem: targeted-edit-failure-retry
tags: [targeted-edit, failure-classification, retry, workbench, diagnostics]

requires:
  - phase: 10-targeted-regeneration-and-masked-editing-mvp
    plan: "05"
    provides: durable targeted edit route and lineage evidence
provides:
  - Targeted edit failure categories
  - Retry eligibility and retry route metadata
  - API retry preservation for edit intent, parent version, provider intent, and mask artifact
  - Workbench failure diagnostics and non-retryable targeted edit states
affects:
  - worker-failure-classification
  - generation-retry-api
  - workbench-progress-panel
  - operator diagnostics

tech-stack:
  added: []
  patterns:
    - targeted edit retry metadata is persisted in job operations and final events
    - retry copies durable metadata from the failed job instead of trusting browser-supplied intent
    - UI hides retry controls when backend metadata marks a targeted edit non-retryable

key-files:
  created:
    - .planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-06-SUMMARY.md
  modified:
    - services/core/src/caragent_core/enums.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/api/src/caragent_api/routes/generation.py
    - services/api/tests/test_generation.py
    - services/worker/tests/test_generation_tasks.py
    - apps/web/src/components/workbench/progress-panel.tsx
    - apps/web/src/app/page.test.tsx
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "Targeted edit failures use dedicated `targeted_edit_invalid`, `targeted_edit_unsupported`, and `targeted_edit_conflict` categories."
  - "Targeted retries are server-side copies of the original failed job metadata; browser retry requests only supply idempotency/requester."
  - "Non-retryable targeted edits suppress retry controls in the workbench."

patterns-established:
  - "Provider/timeout/storage failures on targeted edits are retryable; invalid targets, invalid masks, disabled features, and unsupported provider-mask capabilities are not."
  - "Retry metadata includes `retry_eligible`, `retry_route`, `edit_intent`, `blocked_reason`, route, target, mask, and prompt delta."
  - "API retry revalidates parent version and mask artifact before enqueueing a targeted edit retry."

requirements-advanced:
  - V2-EDIT-04
  - V2-EDIT-05

duration: 8 min
completed: 2026-06-18
---

# Phase 10 Plan 06: Failure And Retry Summary

**Targeted edit failures are now categorized, retry-safe, and visible in the workbench**

## Performance

- **Duration:** 8 min
- **Completed:** 2026-06-18T13:10:59Z
- **Tasks:** 4
- **Files modified:** 9

## Accomplishments

- Added targeted edit failure categories to the shared enum.
- Classified invalid recomposition targets, unsupported provider-mask routes, provider failures, timeouts, storage failures, and configuration blocks into actionable categories.
- Persisted retry eligibility, retry route, edit intent, target, mask, prompt delta, and blocked reason in targeted edit failure metadata.
- Updated generation retry so targeted edit retries copy original durable metadata and revalidate parent version plus mask artifact.
- Prevented targeted retries from turning into full regenerations by accident.
- Updated the workbench progress panel to show route, target, blocked reason, and non-retryable state while keeping diagnostics sanitized.

## Task Commits

1. **Tasks 1-4: Add targeted edit failure categories, retry preservation, and workbench diagnostics** - pending current commit.

## Files Created/Modified

- `services/core/src/caragent_core/enums.py` - Adds targeted edit failure categories.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Adds targeted failure classification and retry metadata.
- `services/api/src/caragent_api/routes/generation.py` - Preserves targeted edit intent/provider metadata on retry and revalidates prerequisites.
- `services/api/tests/test_generation.py` - Covers targeted retry preservation and non-retryable failure rejection.
- `services/worker/tests/test_generation_tasks.py` - Covers invalid target, unsupported provider-mask, and retryable provider failure metadata.
- `apps/web/src/components/workbench/progress-panel.tsx` - Shows targeted failure details and hides retry for non-retryable jobs.
- `apps/web/src/app/page.test.tsx` - Covers non-retryable targeted edit failure UI.

## Decisions Made

- Retry eligibility is conservative: provider, timeout, and storage failures are retryable; invalid selection/mask and unsupported capability are not.
- Workbench retry still uses the existing retry endpoint; server-side retry metadata prevents spoofing or accidental full regeneration.
- No OpenAPI contract change was needed because retry/failure details live in existing metadata fields.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Minor] API import sorting failed ruff**
- **Found during:** Verification
- **Issue:** Adding retry prerequisite validation introduced an unsorted import block.
- **Fix:** Collapsed model imports into one sorted import line.
- **Verification:** API ruff passed.

**2. [Rule 3 - Blocking] Web tests required unsandboxed vitest execution**
- **Found during:** Verification
- **Issue:** Windows sandbox can block esbuild/Vitest process spawning.
- **Fix:** Ran focused web tests with sandbox escalation.
- **Verification:** Page and iteration tests passed, 29 tests.

**3. [Rule 3 - Blocking] mypy/compileall needed unsandboxed uv cache access**
- **Found during:** Verification
- **Issue:** `uv` cache access under the Windows user directory failed in sandbox.
- **Fix:** Reran mypy and compileall with sandbox escalation.
- **Verification:** API, worker, and core checks passed.

---

**Total deviations:** 3 auto-fixed (1 minor, 2 blocking)
**Impact on plan:** No scope change. Contracts remained current.

## Issues Encountered

- Targeted edit retry depends on the original mask artifact still existing in the same workspace; if it is gone, retry is rejected.
- Provider-mask real hosted execution is still deferred, so provider-mask retry was verified through the mocked provider-capable path.

## Verification

- `cd services/worker && uv run pytest -q tests/test_generation_tasks.py` - passed, 28 tests.
- `cd services/api && uv run pytest -q tests/test_generation.py` - passed, 24 tests.
- `cd services/api && uv run pytest -q tests/test_jobs.py` - passed, 7 tests.
- `corepack pnpm --dir apps/web exec vitest --run src/app/page.test.tsx src/lib/api/iteration.test.ts` - passed with unsandboxed execution, 29 tests.
- `cd services/api && uv run ruff check .` - passed.
- `cd services/worker && uv run ruff check .` - passed.
- `cd services/core && uv run ruff check .` - passed.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `cd services/api && uv run mypy src` - passed with unsandboxed execution.
- `cd services/worker && uv run mypy src` - passed with unsandboxed execution.
- `cd services/core && uv run mypy src` - passed with unsandboxed execution.
- `cd services/api && uv run python -m compileall src tests` - passed with unsandboxed execution.
- `cd services/worker && uv run python -m compileall src tests` - passed with unsandboxed execution.
- `cd services/core && uv run python -m compileall src tests` - passed with unsandboxed execution.
- `corepack pnpm contracts:check` - passed; contract artifacts are current.
- `git diff --check` - passed.

## User Setup Required

None for local validation. Targeted edit execution still requires `V2_TARGETED_REGENERATION_ENABLED=true` outside tests.

## Next Phase Readiness

Ready for `10-07-PLAN.md`: comparison UI can now rely on durable route, target, blocked-reason, and retry metadata.

---
*Phase: 10-targeted-regeneration-and-masked-editing-mvp*
*Completed: 2026-06-18*
