---
phase: 10-targeted-regeneration-and-masked-editing-mvp
plan: "03"
subsystem: worker-recomposition
tags: [targeted-edit, deterministic-recomposition, worker, preview-spec, lineage]

requires:
  - phase: 10-targeted-regeneration-and-masked-editing-mvp
    plan: "01"
    provides: typed EditIntent metadata on iteration jobs
  - phase: 10-targeted-regeneration-and-masked-editing-mvp
    plan: "02"
    provides: workbench-submitted deterministic edit intents
provides:
  - Deterministic recomposition helper for overlay-layer changes
  - Worker route that bypasses hosted provider calls for safe targeted edits
  - Child artifact/version/model-run trace metadata for recomposition-only edits
  - Local renderer support for layer geometry, opacity, and visibility fields
affects:
  - worker-generation-pipeline
  - preview-spec-rendering
  - child-version-lineage
  - hosted-provider-guardrails

tech-stack:
  added: []
  patterns:
    - recomposition-safe edits are validated against the parent version PreviewSpec
    - deterministic recomposition is treated as a local/non-hosted provider route
    - parent versions and artifacts remain immutable; recomposition always writes child records

key-files:
  created:
    - services/worker/src/caragent_worker/recomposition.py
    - .planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-03-SUMMARY.md
  modified:
    - services/worker/src/caragent_worker/providers/local.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/worker/tests/test_generation_tasks.py
    - services/worker/tests/test_image_providers.py

key-decisions:
  - "Only overlay-layer targets are recomposition-safe in this plan; safe-zone/freeform content regeneration remains provider-mask work."
  - "Recomposition accepts explicit layer fields and a small set of directional/natural-language hints, then writes changed fields into PreviewSpec metadata."
  - "The recomposition route uses provider `deterministic-recomposition` and model `preview-spec-recomposer-v1`, counted as local/non-hosted for quota purposes."

patterns-established:
  - "A targeted edit job with `route_preference=deterministic_recomposition` short-circuits before hosted preflight and provider selection."
  - "Child version/artifact/model-run metadata includes `recomposition_route`, target, parent version/artifact ids, and changed fields."
  - "Invalid recomposition targets fail without creating partial child versions or artifacts."

requirements-advanced:
  - V2-EDIT-02
  - V2-EDIT-03

duration: 14 min
completed: 2026-06-18
---

# Phase 10 Plan 03: Deterministic Recomposition Summary

**Safe overlay-layer targeted edits now complete through a local recomposition route without hosted provider calls**

## Performance

- **Duration:** 14 min
- **Completed:** 2026-06-18T12:39:09Z
- **Tasks:** 4
- **Files modified:** 5

## Accomplishments

- Added `caragent_worker.recomposition` to validate and apply safe overlay-layer edits against the parent PreviewSpec.
- Supported move, scale, opacity, visibility, text edit, and logo swap metadata changes, with deterministic PNG rendering through the local preview renderer.
- Routed deterministic targeted edit jobs in the worker before hosted preflight/provider execution, preserving zero-cost local execution.
- Persisted child version, child artifact, model-run, job operation, and event metadata proving route, target, parent lineage, and changed fields.
- Added regression coverage for helper behavior, provider bypass, parent immutability, child lineage, and invalid target rollback.

## Task Commits

1. **Tasks 1-4: Add deterministic recomposition helper and worker route** - pending current commit.

## Files Created/Modified

- `services/worker/src/caragent_worker/recomposition.py` - New deterministic recomposition helper and metadata result type.
- `services/worker/src/caragent_worker/providers/local.py` - Renderer now honors layer-level geometry, visibility, and opacity.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Worker detects deterministic edit intents and writes recomposition-only outputs.
- `services/worker/tests/test_image_providers.py` - Helper tests for move, scale, opacity, visibility, text edit, logo swap, and unknown target rejection.
- `services/worker/tests/test_generation_tasks.py` - Worker tests for provider bypass, child lineage, trace metadata, and invalid target rollback.

## Decisions Made

- Recomposition does not read parent image bytes because current `ObjectStorage` only exposes `put_object`; it regenerates the deterministic concept preview from updated PreviewSpec metadata.
- Provider-mask and unsafe visual-content regeneration are deferred to `10-04-PLAN.md`.
- Targeted regeneration is gated by `V2_TARGETED_REGENERATION_ENABLED`; tests enable it explicitly for recomposition jobs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Compile/mypy needed unsandboxed uv execution**
- **Found during:** Verification
- **Issue:** `uv run mypy src` and initial compileall attempts hit Windows user-cache permission errors in the sandbox.
- **Fix:** Reran verification with sandbox escalation.
- **Verification:** `uv run mypy src` and `uv run python -m compileall src tests` passed.

**2. [Rule 3 - Blocking] Prompt delta parser duplicated summary and instruction text**
- **Found during:** Helper test run
- **Issue:** Test edit intents use the same string for summary and instructions, causing `text=...` and `logo=...` parsing to capture duplicate content.
- **Fix:** Deduplicated prompt-delta fragments before parsing recomposition changes.
- **Verification:** Helper and worker tests passed, 45 tests.

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** No scope change. Recomposition remains conservative and provider-mask work is still deferred to 10-04.

## Issues Encountered

- A broad compileall command scanned `.venv` and produced long output; the final verification uses `src tests` only.
- Generic validation categories are still coarse because existing `FailureCategory` has no dedicated targeted-edit validation value; richer user-facing edit failure mapping is planned for 10-06.

## Verification

- `cd services/worker && uv run pytest -q tests/test_image_providers.py tests/test_generation_tasks.py` - passed, 45 tests.
- `cd services/worker && uv run ruff check .` - passed.
- `cd services/worker && uv run mypy src` - passed with unsandboxed execution.
- `cd services/worker && uv run python -m compileall src tests` - passed with unsandboxed execution.
- `git diff --check` - passed.

## User Setup Required

Set `V2_TARGETED_REGENERATION_ENABLED=true` before expecting worker-side deterministic targeted edits to execute outside tests.

## Next Phase Readiness

Ready for `10-04-PLAN.md`: provider-mask request contracts and capability checks can now use deterministic recomposition as the local fallback path.

---
*Phase: 10-targeted-regeneration-and-masked-editing-mvp*
*Completed: 2026-06-18*
