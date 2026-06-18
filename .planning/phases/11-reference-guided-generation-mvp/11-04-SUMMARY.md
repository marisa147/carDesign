---
phase: 11-reference-guided-generation-mvp
plan: "04"
subsystem: worker-provider-reference-handling
tags: [references, worker, providers, rights-gates, hosted-guards]

requires:
  - phase: 11-reference-guided-generation-mvp
    plan: "01"
    provides: reference contracts and provider capability map
  - phase: 11-reference-guided-generation-mvp
    plan: "03"
    provides: prompt planner reference usage and unsupported-role warning metadata
provides:
  - Normalized worker provider requests carrying `reference_usage`
  - Local deterministic provider metadata for prompt-only reference usage
  - Worker reference capability preflight before provider execution
  - BFL guard proving unverified reference-image fields are not sent
affects:
  - worker-generation
  - provider-boundary
  - reference-rights-preflight
  - hosted-provider-safety

tech-stack:
  added: []
  patterns:
    - provider requests carry reference snapshots separately from binary payloads
    - local deterministic records reference metadata while keeping `external_calls: False`
    - hosted providers fail closed when reference-image capability is unverified

key-files:
  created: []
  modified:
    - services/worker/src/caragent_worker/providers/base.py
    - services/worker/src/caragent_worker/providers/local.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/worker/tests/test_generation_tasks.py
    - services/worker/tests/test_image_providers.py
    - services/worker/tests/test_config.py

key-decisions:
  - "ImageGenerationRequest now carries `reference_usage` from the prompt plan."
  - "Local deterministic generation treats references as prompt/context trace only and remains external-call-free."
  - "BFL reference-image input remains blocked because current adapter support is not verified."
  - "Worker failure metadata includes reference warning and unsupported-role fields for blocked hosted references."

patterns-established:
  - "`_reference_usage_metadata()` is the worker-side helper for model-run, artifact, version, event, and job metadata."
  - "`_enforce_reference_capability_preflight()` is the fail-closed boundary before provider execution."
  - "BFL `_submit_payload()` continues to omit `reference_usage`, input asset ids, and prompt payload internals."

requirements-completed:
  - V2-REF-02
  - V2-REF-03
  - V2-REF-04
  - V2-REF-05

duration: 13 min
completed: 2026-06-18
---

# Phase 11 Plan 04: Worker/Provider Reference Handling Summary

**Reference usage now crosses the worker/provider boundary safely, with hosted-reference calls fail-closed unless capability support is verified.**

## Performance

- **Duration:** 13 min
- **Completed:** 2026-06-18T22:39:51+08:00
- **Tasks:** 4
- **Files modified:** 6

## Accomplishments

- Added red worker/provider tests for structured reference usage, missing rights, BFL unsupported reference roles, local deterministic metadata, and BFL payload omission.
- Extended `ImageGenerationRequest` so worker/provider code can carry `reference_usage` without embedding binary data or local paths.
- Updated local deterministic provider metadata to include reference usage, warning count, and warnings while preserving `external_calls: False`.
- Added worker reference capability preflight so BFL reference roles fail before provider execution and persist warning metadata.
- Verified BFL adapter payloads do not send `reference_usage`, input asset ids, or prompt payload internals.

## Task Commits

1. **Task 1: Add red worker/provider tests for reference preflight** - `8418da4` (test)
2. **Tasks 2-4: Extend request metadata and guard provider reference handling** - `15361d6` (feat)

## Files Created/Modified

- `services/worker/src/caragent_worker/providers/base.py` - Adds normalized `reference_usage` to provider requests.
- `services/worker/src/caragent_worker/providers/local.py` - Persists prompt-only reference metadata in deterministic local results.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Adds reference metadata propagation and capability preflight.
- `services/worker/tests/test_generation_tasks.py` - Covers worker request propagation, rights gates, and BFL fail-closed behavior.
- `services/worker/tests/test_image_providers.py` - Covers local metadata and BFL payload omission.
- `services/worker/tests/test_config.py` - Confirms the reference guidance flag does not enable hosted reference-image inputs.

## Decisions Made

- Worker repeats reference rights checks for included reference ids before provider execution.
- Hosted reference image inputs remain disabled even when `V2_REFERENCE_GUIDANCE_ENABLED=true` unless provider capability metadata explicitly verifies support.
- BFL unsupported reference usage is a provider-configuration failure at `reference_capability_preflight`, not a silent warning-only hosted call.

## Deviations from Plan

### Auto-fixed Issues

- Fixed a first-pass implementation error where a synchronous preflight helper was accidentally awaited.

---

**Total deviations:** 1
**Impact on plan:** No scope change; focused worker tests caught the issue before commit.

## Issues Encountered

- Git safe.directory checks require using `git -c safe.directory=D:/python/carAgent ...` in this desktop environment.

## Verification

- `cd services/worker && uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py tests/test_config.py` - passed.
- `cd services/worker && uv run ruff check .` - passed.
- `git diff --check` - passed.

## User Setup Required

None - hosted reference-image calls remain blocked by default and no real provider call is made by automated tests.

## Next Phase Readiness

Ready for `11-05-PLAN.md`: worker/provider requests now carry safe reference metadata, so trace persistence can snapshot exact references, roles, warnings, and rights evidence across durable records and exports.

---
*Phase: 11-reference-guided-generation-mvp*
*Completed: 2026-06-18*
