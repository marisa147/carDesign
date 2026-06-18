---
phase: 09-hosted-provider-rollout-mvp
plan: "07"
subsystem: phase-09-closure
tags: [verification, uat, docs, runbook, provider-off, provider-on]

requires:
  - phase: 09-hosted-provider-rollout-mvp
    provides: completed Phase 9 implementation and workbench selector from 09-01..09-06
provides:
  - Phase 9 provider-off verification evidence
  - Phase 9 hosted provider runbook and UAT artifact
  - Phase 9 milestone notes and Phase 10 readiness state
affects:
  - phase-09-hosted-provider
  - phase-10-targeted-editing
  - project-docs

tech-stack:
  added: []
  patterns:
    - record provider-off automated validation separately from manual provider-on hosted smoke
    - never claim live hosted success when credentials/cost approval are absent
    - update planning ledgers only after evidence artifacts exist

key-files:
  created:
    - .planning/phases/09-hosted-provider-rollout-mvp/09-VERIFICATION.md
    - .planning/phases/09-hosted-provider-rollout-mvp/09-HUMAN-UAT.md
    - .planning/phases/09-hosted-provider-rollout-mvp/09-MILESTONE-NOTES.md
    - .planning/phases/09-hosted-provider-rollout-mvp/09-07-SUMMARY.md
  modified:
    - README.md
    - docs/development.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "Provider-off validation is the default completion path and must remain free of external provider calls."
  - "Provider-on BFL smoke is manual-only, credential-gated, cost-guarded, and reversible."
  - "Skipped provider-on smoke is recorded as a prerequisite skip, not as live hosted success."

patterns-established:
  - "09-VERIFICATION.md records exact commands, results, warnings, and provider-off evidence."
  - "09-HUMAN-UAT.md separates provider-off local evidence from optional provider-on BFL evidence."
  - "09-MILESTONE-NOTES.md captures residual risks for downstream V2 phases."

requirements-completed:
  - V2-PROVIDER-01
  - V2-PROVIDER-02
  - V2-PROVIDER-03
  - V2-PROVIDER-04
  - V2-PROVIDER-05

duration: 11 min
completed: 2026-06-18
---

# Phase 9 Plan 07: Smoke, Docs, And UAT Summary

**Phase 9 is closed with provider-off validation evidence, hosted-provider runbooks, and honest manual provider-on skip notes.**

## Performance

- **Duration:** 11 min
- **Started:** 2026-06-18T09:24:14Z
- **Completed:** 2026-06-18T09:35:11Z
- **Tasks:** 4
- **Files modified:** 9

## Accomplishments

- Updated README and development docs with Phase 9 hosted rollout guardrails, provider-off commands, manual provider-on BFL smoke prerequisites, cost/quota guidance, and disable-after-smoke instructions.
- Ran provider-off focused API, worker, web, contract, smoke dry-run, docs token check, and aggregate validation commands.
- Created `09-VERIFICATION.md` with exact commands, results, provider-off evidence, and the non-blocking aiosqlite warning.
- Created `09-HUMAN-UAT.md` with provider-off evidence/checklist and a truthful provider-on BFL skip due missing credential/cost approval.
- Created `09-MILESTONE-NOTES.md` with delivered scope, requirement coverage, residual risks, and Phase 10 readiness.
- Marked Phase 9 complete and advanced project state to Phase 10 readiness.

## Task Commits

1. **Tasks 1-3: Hosted rollout docs plus verification/UAT evidence** - `6f144c4` (docs)
2. **Task 4: Planning ledger and Phase 9 closure artifacts** - included in this metadata commit.

## Verification

- `cd services/api && uv run pytest -q tests/test_config.py tests/test_operations.py tests/test_generation.py tests/test_jobs.py` - PASS, 39 tests.
- `cd services/worker && uv run pytest -q tests/test_config.py tests/test_image_providers.py tests/test_generation_tasks.py` - PASS, 49 tests.
- `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/api/generation.test.ts src/lib/api/operations.test.ts` - PASS, 31 tests.
- `corepack pnpm contracts:check` - PASS.
- `corepack pnpm smoke:worker -- --dry-run` - PASS, no queue/provider call.
- `corepack pnpm validate` - PASS.
- `Select-String -Path README.md,docs/development.md -Pattern "Phase 9","hosted provider","provider-off","provider-on","BFL","quota","cost"` - PASS.

## Issues Encountered

- `corepack pnpm validate` emitted an aiosqlite thread-close warning in API tests but exited 0; this is recorded in `09-VERIFICATION.md`.
- Live BFL provider-on smoke was skipped because no real BFL credential or cost-spend approval was provided.

## User Setup Required

Only for optional live hosted smoke: configure ignored API/worker env files with real BFL credentials, low quota/rate/cost guards, and disable hosted flags after one job.

## Next Phase Readiness

Ready for `10-01-PLAN.md`: Phase 10 can use provider intent, safe diagnostics, local deterministic fallback, and workbench generation controls as the base for targeted editing.

## Self-Check: PASSED

- Key files exist: PASS.
- Task acceptance criteria verified: PASS.
- Plan-level verification commands passed: PASS.
- Provider-on skip is explicit and does not overclaim hosted success: PASS.

---
*Phase: 09-hosted-provider-rollout-mvp*
*Completed: 2026-06-18*
