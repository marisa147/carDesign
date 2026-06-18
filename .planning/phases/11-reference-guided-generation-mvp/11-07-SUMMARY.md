---
phase: 11-reference-guided-generation-mvp
plan: "07"
subsystem: phase-11-closure
tags: [verification, docs, uat, requirements, milestone-close]

requires:
  - phase: 11-reference-guided-generation-mvp
    plan: "01-06"
    provides: reference contracts, planner, provider handling, durable trace, and workbench UX
provides:
  - Phase 11 verification report
  - Human UAT checklist
  - Milestone notes
  - Updated README and developer runbook
  - Closed V2-REF requirements and roadmap/state progress
affects:
  - project-docs
  - planning-state
  - phase-evidence

tech-stack:
  added: []
  patterns:
    - hosted reference smoke is manual-only and separated from default validation
    - full aggregate validation must run with host access when sandbox blocks Python/Corepack
    - closure state advances only after verification evidence exists

key-files:
  created:
    - .planning/phases/11-reference-guided-generation-mvp/11-VERIFICATION.md
    - .planning/phases/11-reference-guided-generation-mvp/11-HUMAN-UAT.md
    - .planning/phases/11-reference-guided-generation-mvp/11-MILESTONE-NOTES.md
  modified:
    - README.md
    - docs/development.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md
    - .planning/phases/11-reference-guided-generation-mvp/11-VALIDATION.md
    - services/core/src/caragent_core/generation/briefs.py
    - services/api/tests/test_config.py
    - services/worker/src/caragent_worker/tasks/jobs.py

key-decisions:
  - "Phase 11 default validation remains local/provider-off/free."
  - "Hosted reference-image smoke is documented as manual-only and skipped without credentials, cost approval, and verified provider support."
  - "Local deterministic provider supports prompt-only reference guidance, not reference-image inputs."
  - "Project state advances to Phase 12 planning only after focused, smoke, contracts, and aggregate validation passed."

patterns-established:
  - "Phase verification reports distinguish automated evidence from manual UAT checklists."
  - "Provider capability tests assert prompt-only local references separately from reference-image inputs."
  - "Reference role strings from metadata are normalized before typed snapshot persistence."

requirements-completed:
  - V2-REF-01
  - V2-REF-02
  - V2-REF-03
  - V2-REF-04
  - V2-REF-05

duration: 33 min
completed: 2026-06-18
---

# Phase 11 Plan 07: Smoke, Docs, And UAT Summary

**Phase 11 is closed. Reference-guided generation is verified, documented, and mapped to V2-REF-01 through V2-REF-05, with project state ready for Phase 12 planning.**

## Performance

- **Duration:** 33 min
- **Completed:** 2026-06-18T23:28:37+08:00
- **Tasks:** 4
- **Files created:** 3
- **Files modified:** 9

## Accomplishments

- Ran Phase 11 focused core/API/worker/web regression commands.
- Ran `corepack pnpm contracts:check`, `corepack pnpm smoke:worker -- --dry-run`, and full `corepack pnpm validate`.
- Fixed validation blockers discovered by aggregate validation: mixed reference assignment typing, stale API provider capability expectations, and worker role enum conversion.
- Created Phase 11 verification report, Human UAT checklist, and milestone notes.
- Updated README and developer runbook with reference roles, rights/source gates, provider warnings, trace keys, default provider-off validation, and optional hosted reference smoke prerequisites.
- Marked V2-REF requirements complete and advanced roadmap/state to Phase 12 planning readiness.

## Task Commits

1. **Validation fixes discovered during closure** - `2284e10` (fix)
2. **Docs/planning closure for Phase 11** - this docs closure commit

## Files Created/Modified

- `.planning/phases/11-reference-guided-generation-mvp/11-VERIFICATION.md` - Records focused, smoke, contracts, aggregate, and requirement-mapping evidence.
- `.planning/phases/11-reference-guided-generation-mvp/11-HUMAN-UAT.md` - Documents provider-off browser UAT and optional hosted reference smoke.
- `.planning/phases/11-reference-guided-generation-mvp/11-MILESTONE-NOTES.md` - Summarizes Phase 11 shipped scope, requirement closure, and Phase 12 handoff.
- `README.md` - Adds Phase 11 overview, manual hosted reference boundary, and focused commands.
- `docs/development.md` - Adds Phase 11 runbook, UAT, requirement coverage, source coverage, security, and troubleshooting notes.
- `.planning/REQUIREMENTS.md` - Marks V2-REF-01..05 complete with evidence.
- `.planning/ROADMAP.md` - Marks Phase 11 plan 07 complete and Phase 11 complete.
- `.planning/STATE.md` - Advances project state to Phase 12 planning readiness.
- `.planning/phases/11-reference-guided-generation-mvp/11-VALIDATION.md` - Marks Phase 11 validation checks green and sign-off passed.
- `services/core/src/caragent_core/generation/briefs.py` - Normalizes reference usage input before typed payload construction.
- `services/api/tests/test_config.py` - Updates capability assertions for local prompt-only references and unsupported BFL reference images.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Converts metadata role strings into `ReferenceRole` before snapshot persistence.

## Decisions Made

- Browser UAT is recorded as a checklist because live services/browser were not started by the agent run.
- Hosted reference smoke remains skipped and is not claimed as evidence.
- Aggregate validation warnings from `aiosqlite` event-loop thread teardown are recorded as non-blocking because tests pass and the warning is not requirement-specific.

## Deviations from Plan

### Auto-fixed Issues

- `corepack pnpm contracts:check` needed sandbox escalation; sandbox fallback can generate a minimal `/health` client and cause false stale artifacts.
- `corepack pnpm validate` needed sandbox escalation because host Python/uv/Corepack checks fail under restricted sandbox access.
- Aggregate validation surfaced three type/test mismatches that focused tests had not caught; all were fixed and revalidated.

---

**Total deviations:** 3
**Impact on plan:** No scope reduction; closure evidence is stronger because aggregate validation now passes.

## Issues Encountered

- API full pytest still emits existing `aiosqlite` event-loop teardown warnings in targeted iteration tests. They are recorded as non-blocking warnings in verification evidence.

## Verification

- `cd services/core && uv run pytest -q tests/test_models.py tests/test_prompt_plans.py tests/test_generation_jobs.py` - passed, 16 tests.
- `cd services/api && uv run pytest -q tests/test_generation.py tests/test_jobs.py tests/test_operations.py` - passed, 43 tests.
- `cd services/worker && uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py tests/test_config.py` - passed, 69 tests.
- `cd apps/web && ./node_modules/.bin/vitest.CMD --run src/app/page.test.tsx src/lib/workbench/store.test.ts src/lib/api/generation.test.ts src/lib/api/assets.test.ts src/lib/api/iteration.test.ts` - passed with escalation, 53 tests.
- `corepack pnpm contracts:check` - passed with escalation.
- `corepack pnpm smoke:worker -- --dry-run` - passed.
- `corepack pnpm validate` - passed with escalation.

## User Setup Required

None for default validation. Live browser UAT and hosted reference smoke remain optional/manual host-run steps.

## Next Phase Readiness

Ready for Phase 12 planning: `Lightweight 3D Preview MVP`.

---
*Phase: 11-reference-guided-generation-mvp*
*Completed: 2026-06-18*
