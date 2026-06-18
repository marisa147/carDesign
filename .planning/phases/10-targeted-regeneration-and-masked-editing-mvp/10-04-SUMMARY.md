---
phase: 10-targeted-regeneration-and-masked-editing-mvp
plan: "04"
subsystem: provider-capabilities
tags: [targeted-edit, provider-mask, capability-map, hosted-guards, worker-preflight]

requires:
  - phase: 10-targeted-regeneration-and-masked-editing-mvp
    plan: "01"
    provides: typed EditIntent metadata
  - phase: 09-hosted-provider-rollout-mvp
    plan: "01"
    provides: browser-safe provider capability map
  - phase: 09-hosted-provider-rollout-mvp
    plan: "03"
    provides: hosted provider preflight guardrails
provides:
  - Provider capability fields for supported edit routes and mask input requirements
  - Normalized provider request surface for mask/edit metadata
  - API and worker preflight for provider_masked_generation
  - Explicit BFL deferral for unverified real hosted mask payloads
affects:
  - operations-provider-status
  - generation-iteration-api
  - worker-generation-pipeline
  - BFL-provider-adapter

tech-stack:
  added: []
  patterns:
    - provider-mask routes must pass hosted preflight and mask capability preflight
    - provider adapters receive normalized MaskEditRequest metadata, not raw API payloads
    - unverified hosted mask payloads are blocked before provider submission

key-files:
  created:
    - .planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-04-SUMMARY.md
  modified:
    - .planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-RESEARCH.md
    - services/core/src/caragent_core/provider_capabilities.py
    - services/api/src/caragent_api/routes/generation.py
    - services/worker/src/caragent_worker/providers/base.py
    - services/worker/src/caragent_worker/providers/bfl.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/api/tests/test_config.py
    - services/api/tests/test_generation.py
    - services/api/tests/test_operations.py
    - services/worker/tests/test_config.py
    - services/worker/tests/test_generation_tasks.py
    - services/worker/tests/test_image_providers.py

key-decisions:
  - "Real BFL provider_masked_generation remains deferred because the current FLUX.2 adapter route has no verified explicit mask field."
  - "BFL full generation can remain enabled while mask-aware generation is reported as unsupported in browser-safe capability data."
  - "The worker repeats provider-mask capability checks after hosted preflight so persisted jobs cannot bypass API validation."

patterns-established:
  - "Operations status exposes `supported_edit_routes`, `unsupported_edit_routes`, and `mask_input` without secrets."
  - "ImageGenerationRequest can carry optional `MaskEditRequest` metadata for provider adapters."
  - "BFL adapter fails fast when mask edit metadata is present, before submitting any unverified payload."
  - "Worker model-run, artifact, version, and prompt payload metadata record `edit_route`, mask artifact metadata, target, region, and prompt delta."

requirements-advanced:
  - V2-EDIT-02
  - V2-EDIT-04

duration: 16 min
completed: 2026-06-18
---

# Phase 10 Plan 04: Provider Mask Capability Summary

**Provider-mask targeted edits now have a typed request contract and explicit capability gates**

## Performance

- **Duration:** 16 min
- **Completed:** 2026-06-18T12:54:26Z
- **Tasks:** 4
- **Files modified:** 13

## Accomplishments

- Re-checked official BFL docs and recorded the implementation boundary in `10-RESEARCH.md`.
- Extended the shared provider capability map with mask-aware generation support, supported/unsupported edit routes, mask input metadata, and user-safe caveats.
- Added `MaskEditRequest` to the normalized worker provider request contract.
- Blocked BFL mask edit requests inside the adapter before any hosted submission.
- Added API validation for unsupported `provider_masked_generation` iteration requests.
- Added worker-side provider-mask preflight for parent version, mask artifact, hosted guards, and provider capability.
- Added regression coverage for operations status, config capability maps, request metadata, BFL fail-fast behavior, API blocking, worker blocking, and mock-provider pass-through.

## Task Commits

1. **Tasks 1-4: Add provider-mask request contract and capability gates** - pending current commit.

## Files Created/Modified

- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-RESEARCH.md` - Documents official BFL FLUX.2/FLUX.1 Fill mask findings and deferral.
- `services/core/src/caragent_core/provider_capabilities.py` - Adds mask/edit-route capability fields.
- `services/api/src/caragent_api/routes/generation.py` - Rejects unsupported provider-mask targeted iterations before enqueue.
- `services/worker/src/caragent_worker/providers/base.py` - Adds normalized `MaskEditRequest`.
- `services/worker/src/caragent_worker/providers/bfl.py` - Fails fast for unverified mask edit metadata.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Adds authoritative worker provider-mask preflight and trace metadata.
- API and worker tests - Cover capability exposure, unsupported route blocking, and allowed mock-provider metadata flow.

## Decisions Made

- Current BFL FLUX.2 adapter keeps real mask calls disabled; explicit mask support is only documented for a separate FLUX.1 Fill route that is not implemented here.
- Provider-mask preflight is separate from hosted preflight, preserving clear errors for credentials/quota first and unsupported mask route second.
- Mock-provider tests prove the normalized mask contract can pass through once capability checks are intentionally enabled.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] mypy needed unsandboxed uv cache access**
- **Found during:** Verification
- **Issue:** `uv run mypy src` hit Windows user-cache permission errors in the sandbox.
- **Fix:** Reran mypy with sandbox escalation.
- **Verification:** API, worker, and core mypy checks passed.

**2. [Rule 3 - Minor] Root compileall scanned ignored dependency/cache directories**
- **Found during:** Verification
- **Issue:** `uv run python -m compileall .` passed but produced noisy output while scanning `.cache` and `node_modules`.
- **Fix:** No code fix required; worktree remained clean except intended files.
- **Verification:** `git status --short` showed only 10-04 source/planning changes.

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 minor)
**Impact on plan:** No scope change. Real hosted mask calls remain intentionally deferred.

## Issues Encountered

- The current operations capability schema is intentionally browser-safe `dict` data, so OpenAPI/TypeScript contract artifacts did not need regeneration.
- API can block obvious provider-mask failures, but worker remains authoritative for persisted jobs and mask artifact validation.

## Verification

- `cd services/api && uv run pytest -q tests/test_generation.py tests/test_operations.py tests/test_config.py` - passed, 39 tests.
- `cd services/worker && uv run pytest -q tests/test_config.py tests/test_image_providers.py tests/test_generation_tasks.py` - passed, 61 tests.
- `cd services/api && uv run ruff check .` - passed.
- `cd services/worker && uv run ruff check .` - passed.
- `cd services/core && uv run ruff check .` - passed.
- `cd services/api && uv run mypy src` - passed with unsandboxed execution.
- `cd services/worker && uv run mypy src` - passed with unsandboxed execution.
- `cd services/core && uv run mypy src` - passed with unsandboxed execution.
- `uv run python -m compileall .` - passed.
- `corepack pnpm contracts:check` - passed; contract artifacts are current.
- `git diff --check` - passed.

## User Setup Required

None for default validation. Real provider-mask hosted calls remain disabled until a mask-specific provider route is explicitly implemented and verified.

## Next Phase Readiness

Ready for `10-05-PLAN.md`: the worker can now build on the provider-mask request contract and capability gates when adding broader targeted-edit pipeline ledger behavior.

---
*Phase: 10-targeted-regeneration-and-masked-editing-mvp*
*Completed: 2026-06-18*
