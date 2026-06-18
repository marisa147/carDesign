---
phase: 03-first-text-to-2d-generation-slice
plan: "03"
subsystem: worker
tags: [generation, providers, local-deterministic, bfl, httpx, pillow]

requires:
  - phase: 03-02
    provides: deterministic PromptPlan contract with prompt text and structured payload
provides:
  - normalized image provider request/result/error contracts
  - deterministic local PNG provider for no-key development and smoke tests
  - mocked BFL-style hosted adapter with submit, poll, result download, timeout, and error handling
  - worker provider runtime settings and dependencies
affects: [phase-03-worker-generation, phase-03-smoke, phase-07-provider-ops]

tech-stack:
  added:
    - httpx
    - Pillow
  patterns:
    - Worker-scoped provider adapters
    - Hosted provider calls gated by WorkerSettings
    - Sanitized provider errors

key-files:
  created:
    - services/worker/src/caragent_worker/providers/__init__.py
    - services/worker/src/caragent_worker/providers/base.py
    - services/worker/src/caragent_worker/providers/local.py
    - services/worker/src/caragent_worker/providers/bfl.py
    - services/worker/tests/test_image_providers.py
  modified:
    - services/worker/pyproject.toml
    - services/worker/uv.lock
    - services/worker/src/caragent_worker/config.py
    - services/worker/tests/test_worker_app.py

key-decisions:
  - "Local deterministic generation returns real PNG bytes and zero-cost metadata without external calls."
  - "BFL-style hosted execution is available only behind AI_PROVIDER_CALLS_ENABLED and API-key settings."
  - "Provider errors are normalized and sanitized before reaching later job events."
  - "Requirement checkboxes remain pending until worker/API ledger storage completes later in Phase 3."

patterns-established:
  - "ImageGenerationRequest.from_prompt_plan bridges core PromptPlan to worker adapters."
  - "select_image_provider returns local deterministic output unless hosted calls are explicitly enabled."
  - "Worker source guard now blocks direct external SDK imports while allowing project-owned adapter modules."

requirements-completed: [GEN-04, GEN-05, GEN-06, GEN-07]

duration: 14 min
completed: 2026-06-17
---

# Phase 3 Plan 03: Provider Adapter Boundary Summary

**Worker-scoped image provider adapters with deterministic local PNG output and mocked BFL-style hosted flow**

## Performance

- **Duration:** 14 min
- **Started:** 2026-06-17T07:08:00Z
- **Completed:** 2026-06-17T07:22:27Z
- **Tasks:** 4
- **Files modified:** 9

## Accomplishments

- Added worker provider contracts for image generation requests, results, errors, timeout errors, configuration errors, sanitized error handling, and PNG dimension extraction.
- Implemented `LocalDeterministicImageProvider` using Pillow to generate deterministic concept-preview PNG bytes with prompt digest, dimensions, reference ids, and zero-cost metadata.
- Implemented `BflImageProvider` using `httpx` with mocked submit/poll/result-download coverage, bounded polling, missing-key errors, Authorization headers, signed URL byte download, and error redaction.
- Added provider runtime settings for model name, hosted timeout/polling, local image size, and BFL endpoint paths while keeping provider calls disabled by default.

## Task Commits

No task commits were created during this inline run because the workspace already contains broad uncommitted GSD Phase 1/2/3 changes. The completed files are listed below and verified by the commands in this summary.

## Files Created/Modified

- `services/worker/src/caragent_worker/providers/base.py` - Normalized provider contracts and common error helpers.
- `services/worker/src/caragent_worker/providers/local.py` - Deterministic local Pillow PNG provider.
- `services/worker/src/caragent_worker/providers/bfl.py` - Mockable BFL-style async provider adapter.
- `services/worker/src/caragent_worker/providers/__init__.py` - Public exports and provider selector.
- `services/worker/src/caragent_worker/config.py` - Provider model, timeout, poll, local image, and BFL endpoint settings.
- `services/worker/pyproject.toml` and `services/worker/uv.lock` - Worker-scoped `httpx` and `Pillow` dependencies.
- `services/worker/tests/test_image_providers.py` - Adapter tests for local PNG, hosted gating, mocked BFL flow, timeout, missing key, and sanitized errors.
- `services/worker/tests/test_worker_app.py` - Source guard narrowed to forbid direct external provider SDK imports, not project-owned adapter modules.

## Decisions Made

- Kept `AI_PROVIDER_CALLS_ENABLED=false` as the default hosted-provider gate.
- Kept selector fallback local and deterministic when hosted provider calls are disabled.
- Stored only reference asset ids in provider request metadata, not binary reference payloads.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Narrowed obsolete worker source guard**
- **Found during:** Task 4 verification
- **Issue:** Existing test rejected any source occurrence of `bfl`, which was correct before provider adapters existed but blocked the planned project-owned BFL-style adapter.
- **Fix:** Updated the guard to block direct external SDK imports from `fal`/`bfl`, while allowing `caragent_worker.providers.bfl`.
- **Files modified:** `services/worker/tests/test_worker_app.py`
- **Verification:** `uv run pytest -q` and `uv run ruff check .` passed.
- **Committed in:** Not committed in this inline run.

---

**Total deviations:** 1 auto-fixed (missing critical test-boundary update).
**Impact on plan:** The change preserves the original safety intent while allowing the planned provider adapter boundary.

## Issues Encountered

- `uv add httpx pillow` needed non-sandbox execution because uv could not initialize its Windows cache inside the sandbox.
- `uv --no-cache run mypy src` needed non-sandbox execution because uv could not open `services/worker/.venv/.lock` inside the sandbox.
- Commit protocol was not applied because this workspace has existing broad uncommitted GSD outputs; this avoids mixing unrelated prior changes into an atomic `03-03` commit.

## Verification

- `uv run pytest -q tests/test_image_providers.py` - RED failed before implementation because `caragent_worker.providers` did not exist.
- `uv run python -c "from caragent_worker.config import get_settings; print(get_settings().ai_provider_calls_enabled)"` - printed `False`.
- `uv run pytest -q tests/test_image_providers.py` - passed, 6 tests.
- `uv run pytest -q` - passed, 17 tests.
- `uv run ruff check .` - passed.
- `uv --no-cache run mypy src` - passed outside sandbox, no issues in 10 source files.

## User Setup Required

None for local deterministic mode. Hosted BFL-style execution remains disabled unless `AI_PROVIDER_CALLS_ENABLED=true` and `AI_PROVIDER_BFL_API_KEY` are explicitly configured.

## Next Phase Readiness

Ready for `03-04`: the worker generation pipeline can now consume `PromptPlan`, select a provider, generate image bytes locally, and persist model-run/artifact/version ledger records.

---
*Phase: 03-first-text-to-2d-generation-slice*
*Completed: 2026-06-17*
