---
phase: 03-first-text-to-2d-generation-slice
plan: "02"
subsystem: core
tags: [generation, prompts, pydantic, traceability]

requires:
  - phase: 03-01
    provides: typed generation brief payload and normalized template/view metadata
provides:
  - deterministic prompt-planning data contract
  - auditable prompt text and structured prompt payload builder
  - provider/model/parameter/input-artifact trace fields for later model-run storage
affects: [phase-03-worker-generation, phase-03-api-generation, contracts]

tech-stack:
  added: []
  patterns:
    - Pydantic models for generation prompt traces
    - Pure deterministic core builder with no provider calls

key-files:
  created:
    - services/core/src/caragent_core/generation/prompts.py
    - services/core/tests/test_prompt_plans.py
  modified:
    - services/core/src/caragent_core/generation/__init__.py

key-decisions:
  - "Prompt planning stays deterministic and local-provider-first."
  - "Prompt payload carries reference asset ids only; no binary data is embedded."
  - "GEN-04 is represented at the trace-contract layer here; durable model-run storage is completed by later Phase 3 worker/API plans."

patterns-established:
  - "PromptProviderSettings keeps provider/model/parameters configurable instead of hard-coding them into job services."
  - "PromptPlan stores both exact prompt text and structured payload for auditability."

requirements-completed: [GEN-04]

duration: 8 min
completed: 2026-06-17
---

# Phase 3 Plan 02: Deterministic Prompt Planning Summary

**Deterministic prompt-plan contract from normalized generation briefs with provider/model/parameter trace fields**

## Performance

- **Duration:** 8 min
- **Started:** 2026-06-17T06:57:00Z
- **Completed:** 2026-06-17T07:05:45Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments

- Added `PromptProviderSettings` and `PromptPlan` Pydantic models for provider, model, parameters, prompt text, prompt payload, input artifact ids, estimated cost, and concept label.
- Added `build_prompt_plan(...)`, a deterministic pure function that converts `GenerationBriefPayload` into exact prompt text and a JSON-safe structured trace payload.
- Covered prompt text, payload, unsupported-template warnings, reference asset ids, deterministic output, and JSON serialization with focused tests.

## Task Commits

No task commits were created during this inline run because the workspace already contains broad uncommitted GSD Phase 1/2/3 changes. The completed files are listed below and verified by the commands in this summary.

## Files Created/Modified

- `services/core/src/caragent_core/generation/prompts.py` - Prompt provider settings, prompt plan model, and deterministic prompt builder.
- `services/core/src/caragent_core/generation/__init__.py` - Exports prompt-planning models and builder through the generation package.
- `services/core/tests/test_prompt_plans.py` - TDD tests for prompt trace contract, determinism, warnings, and serialization.

## Decisions Made

- Default provider/model are `local-deterministic` and `local-concept-v1`, matching Phase 3 no-key validation.
- Default provider parameters are `{"size": "1536x768", "quality": "concept"}` so the plan stays aligned with the single supported canvas.
- Prompt text explicitly says the output is a concept preview and not an installer-ready production wrap.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- `uv --no-cache run mypy src` could not acquire `.venv/.lock` inside the sandbox and produced a mypy internal error. Re-running the same command outside the sandbox passed.
- Commit protocol was not applied because this workspace has existing broad uncommitted GSD outputs; this avoids mixing unrelated prior changes into an atomic `03-02` commit.

## Verification

- `uv run pytest -q tests/test_prompt_plans.py` - RED failed before implementation because `PromptProviderSettings` was not exported.
- `uv run pytest -q tests/test_prompt_plans.py tests/test_generation_briefs.py` - passed, 7 tests.
- `uv run ruff check .` - passed.
- `uv run pytest -q` - passed, 28 tests.
- `uv --no-cache run mypy src` - passed outside sandbox, no issues in 16 source files.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for `03-03`: provider adapter boundary, local deterministic image provider, and hosted-adapter scaffold can consume `PromptPlan` without changing brief parsing.

---
*Phase: 03-first-text-to-2d-generation-slice*
*Completed: 2026-06-17*
