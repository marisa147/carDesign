---
phase: 11-reference-guided-generation-mvp
plan: "03"
subsystem: reference-prompt-planning
tags: [references, prompt-planning, provider-capabilities, warnings, contracts]

requires:
  - phase: 11-reference-guided-generation-mvp
    plan: "01"
    provides: shared reference contracts and provider capability metadata
  - phase: 11-reference-guided-generation-mvp
    plan: "02"
    provides: structured workbench `reference_usage` payloads
provides:
  - Reference planner normalization for structured and legacy reference inputs
  - Prompt payload fields for requested usage, included ids, omitted ids, unsupported roles, and warnings
  - Role-aware prompt text for selected references
  - API job metadata for unsupported provider reference roles
affects:
  - prompt-planning
  - generation-submission
  - hosted-provider-warning-surface
  - reference-trace-foundation

tech-stack:
  added: []
  patterns:
    - reference usage normalization lives in core and is reused by prompt planning and API submission
    - provider-specific unsupported roles become deterministic warning metadata rather than silent drops
    - legacy raw reference ids are converted to `inspiration` assignments

key-files:
  created: []
  modified:
    - services/core/src/caragent_core/references.py
    - services/core/src/caragent_core/generation/prompts.py
    - services/api/src/caragent_api/routes/generation.py
    - services/core/tests/test_prompt_plans.py
    - services/api/tests/test_generation.py

key-decisions:
  - "Reference planner deduplicates by `(asset_id, role)` while preserving stable order."
  - "BFL currently omits all reference roles because current adapter support for reference-image input is unverified."
  - "Disabled references are represented as omitted references with warning metadata."
  - "API generation submission records reference warning metadata only when warnings exist."

patterns-established:
  - "`plan_reference_usage()` is the shared source for prompt payload and API warning metadata."
  - "`PromptPlan.input_artifact_ids` now derives from included reference ids, not raw legacy ids."
  - "`prompt_payload.reference_usage.schema_version` remains `1`."

requirements-completed:
  - V2-REF-03
  - V2-REF-04
  - V2-REF-05

duration: 15 min
completed: 2026-06-18
---

# Phase 11 Plan 03: Reference Prompt Planner Summary

**Role-aware reference normalization, prompt payload trace, and unsupported-role warning metadata**

## Performance

- **Duration:** 15 min
- **Completed:** 2026-06-18T22:28:39+08:00
- **Tasks:** 4
- **Files modified:** 5

## Accomplishments

- Added core reference planning helpers that normalize structured `reference_usage` plus legacy `reference_asset_ids`.
- Updated prompt planning so role-aware references appear in prompt text, `prompt_payload.reference_usage`, included ids, omitted ids, unsupported roles, and warning counts.
- Added BFL unsupported-reference handling so unsupported roles are omitted and represented as warning metadata.
- Added API submission metadata so generation jobs expose unsupported reference roles before worker/provider execution.

## Task Commits

1. **Task 1: Add red tests for role-aware prompt planning** - `97efe42` (test)
2. **Tasks 2-4: Normalize reference usage, update prompt plans, and surface API warnings** - `c1f30e4` (feat)

## Files Created/Modified

- `services/core/src/caragent_core/references.py` - Added normalization and provider-aware reference planning helpers.
- `services/core/src/caragent_core/generation/prompts.py` - Adds reference usage fields and role text to prompt plans.
- `services/api/src/caragent_api/routes/generation.py` - Adds provider-specific reference warning metadata to generation job creation.
- `services/core/tests/test_prompt_plans.py` - Covers structured usage, legacy default role, deterministic output, and BFL unsupported warnings.
- `services/api/tests/test_generation.py` - Covers hosted generation reference warning metadata.

## Decisions Made

- Legacy raw reference ids map to the `inspiration` role for deterministic backward compatibility.
- Local deterministic generation treats references as prompt-guidance trace and includes enabled ids.
- BFL omits all role-based references for now because current reference-image support is not verified in this adapter path.

## Deviations from Plan

### Auto-fixed Issues

None.

---

**Total deviations:** 0
**Impact on plan:** No scope change.

## Issues Encountered

- API focused tests emitted existing aiosqlite event-loop-close warnings in one targeted edit validation area. The focused suite still passed after implementation.
- `corepack pnpm contracts:check` required sandbox escalation, as in earlier contract runs, to avoid fallback behavior.

## Verification

- `cd services/core && uv run pytest -q tests/test_prompt_plans.py tests/test_generation_jobs.py` - passed, 8 tests.
- `cd services/api && uv run pytest -q tests/test_generation.py` - passed, 26 tests.
- `cd services/core && uv run ruff check .` - passed.
- `cd services/api && uv run ruff check .` - passed.
- `corepack pnpm contracts:check` - passed with unsandboxed execution.
- `git diff --check` - passed.

## User Setup Required

None - no hosted provider call is made by these tests.

## Next Phase Readiness

Ready for `11-04-PLAN.md`: worker/provider handling can now consume deterministic reference plans and persist omitted/unsupported decisions.

---
*Phase: 11-reference-guided-generation-mvp*
*Completed: 2026-06-18*
