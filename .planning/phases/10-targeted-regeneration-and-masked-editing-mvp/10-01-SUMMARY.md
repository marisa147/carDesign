---
phase: 10-targeted-regeneration-and-masked-editing-mvp
plan: "01"
subsystem: api-contracts
tags: [targeted-edit, mask, pydantic, openapi, contracts]

requires:
  - phase: 09-hosted-provider-rollout-mvp
    provides: provider intent fields, capability map, and default-off hosted guardrails
provides:
  - Typed `EditIntent`, `EditRegion`, `MaskAssetRef`, and `PromptDelta` schemas
  - `ArtifactKind.MASK` ledger classification
  - Version-scoped iteration request contract carrying targeted edit metadata
  - Generated OpenAPI and TypeScript client fields for targeted edits
affects:
  - phase-10-targeted-editing
  - workbench-target-selection
  - worker-recomposition
  - provider-mask-routing

tech-stack:
  added: []
  patterns:
    - shared core Pydantic schemas are imported by API request contracts
    - targeted edit parent lineage is route-derived before job metadata persistence
    - contract checks may need unsandboxed execution on Windows to avoid fallback client generation

key-files:
  created:
    - services/core/src/caragent_core/editing.py
    - .planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-01-SUMMARY.md
  modified:
    - services/core/src/caragent_core/enums.py
    - services/api/src/caragent_api/schemas.py
    - services/api/src/caragent_api/routes/generation.py
    - services/api/tests/test_generation.py
    - services/core/tests/test_models.py
    - services/core/tests/test_generation_jobs.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts

key-decisions:
  - "Use shared core Pydantic edit schemas so API, worker, and generated contracts share one targeted-edit shape."
  - "Persist request-time targeted edit metadata under `job.metadata_json.edit_intent`, with `parent_version_id` overwritten from the version-scoped route."
  - "Represent masks as durable artifacts with kind `mask`; binary mask bytes stay out of job metadata."

patterns-established:
  - "`EditIntent.model_dump(mode=\"json\")` produces browser/worker-safe metadata with string UUIDs."
  - "FastAPI request validation rejects invalid normalized regions, unsupported route preferences, and incomplete prompt deltas before enqueueing."
  - "Local deterministic provider intent remains compatible with targeted iteration submissions."

requirements-completed:
  - V2-EDIT-02

duration: 17 min
completed: 2026-06-18
---

# Phase 10 Plan 01: Targeted Edit Schema Foundation Summary

**Typed targeted-edit intent schemas with mask artifact metadata, route-derived parent lineage, and generated API contracts**

## Performance

- **Duration:** 17 min
- **Started:** 2026-06-18T09:40:39Z
- **Completed:** 2026-06-18T09:57:54Z
- **Tasks:** 4
- **Files modified:** 8

## Accomplishments

- Added shared core schemas for targeted edit intent, selected target, normalized rectangle region, prompt delta, and mask artifact references.
- Extended version-scoped iteration submission so valid targeted edit metadata is validated and persisted on queued generation jobs.
- Added `ArtifactKind.MASK` and ledger tests proving mask artifacts can store metadata without embedding binary mask payloads.
- Regenerated OpenAPI and TypeScript contracts so the web app can type targeted edit payloads.

## Task Commits

1. **Task 1: Add red tests for targeted edit request and ledger metadata** - `a068c07` (test)
2. **Tasks 2-3: Add shared edit schema helpers and extend iteration API contract** - `e531b85` (feat)
3. **Task 4: Regenerate/check OpenAPI and TypeScript contracts** - `6629b7e` (feat)

**Plan metadata:** pending in current docs commit.

## Files Created/Modified

- `services/core/src/caragent_core/editing.py` - Shared Phase 10 edit intent Pydantic schemas.
- `services/core/src/caragent_core/enums.py` - Added `ArtifactKind.MASK`.
- `services/api/src/caragent_api/schemas.py` - Added optional `edit_intent` to iteration submission request.
- `services/api/src/caragent_api/routes/generation.py` - Persists route-derived targeted edit metadata on iteration jobs.
- `services/api/tests/test_generation.py` - API coverage for targeted edit metadata persistence and validation.
- `services/core/tests/test_models.py` - Core schema and mask kind coverage.
- `services/core/tests/test_generation_jobs.py` - Mask artifact ledger coverage.
- `packages/contracts/openapi/openapi.json` and `packages/contracts/src/generated/client.ts` - Generated contract updates.

## Decisions Made

- Parent version id in `edit_intent` is accepted for round-trip schema compatibility but overwritten from the route before persistence.
- Region geometry starts with normalized rectangles only; polygon/freeform masks remain later Phase 10 work.
- Provider mask execution is not enabled here; this plan only creates the typed request and metadata foundation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Contract check needed unsandboxed execution**
- **Found during:** Task 4 (Regenerate/check OpenAPI and TypeScript contracts)
- **Issue:** `corepack pnpm contracts:check` can fall back to a minimal deterministic client inside the sandbox because it cannot spawn the real orval generation path.
- **Fix:** Regenerated the real orval client, then reran `corepack pnpm contracts:check` with sandbox escalation.
- **Files modified:** `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/client.ts`
- **Verification:** `corepack pnpm contracts:check` reported "Contract artifacts are current."
- **Committed in:** `6629b7e`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope change. The generated contract artifacts are current and the Windows sandbox behavior is documented for future runs.

## Issues Encountered

- Initial API RED test had a helper defined after `pytest.mark.parametrize`, causing collection failure. Fixed before accepting RED so failures reflected missing targeted-edit behavior.
- One test expectation guessed the local provider model name incorrectly; corrected to the existing `local-concept-v1` constant behavior.
- API ruff found one line-length issue in the new test; fixed and reran focused checks.

## Verification

- `cd services/api && uv run pytest -q tests/test_generation.py tests/test_jobs.py` - passed, 26 tests.
- `cd services/core && uv run pytest -q tests/test_models.py tests/test_generation_jobs.py` - passed, 10 tests.
- `cd services/core && uv run ruff check .` - passed.
- `cd services/api && uv run ruff check .` - passed.
- `corepack pnpm contracts:check` - passed with unsandboxed execution so real orval generation ran.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for `10-02-PLAN.md`: the web workbench can now consume generated targeted-edit request types and submit `edit_intent` metadata through the existing child iteration path.

---
*Phase: 10-targeted-regeneration-and-masked-editing-mvp*
*Completed: 2026-06-18*
