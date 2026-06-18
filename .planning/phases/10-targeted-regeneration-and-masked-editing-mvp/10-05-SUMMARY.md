---
phase: 10-targeted-regeneration-and-masked-editing-mvp
plan: "05"
subsystem: targeted-edit-ledger
tags: [targeted-edit, lineage, ledger, api-evidence, recomposition, provider-mask]

requires:
  - phase: 10-targeted-regeneration-and-masked-editing-mvp
    plan: "01"
    provides: typed edit intent metadata
  - phase: 10-targeted-regeneration-and-masked-editing-mvp
    plan: "03"
    provides: deterministic recomposition execution route
  - phase: 10-targeted-regeneration-and-masked-editing-mvp
    plan: "04"
    provides: provider-mask request contract and capability gates
provides:
  - Unified targeted edit trace metadata on recomposition outputs
  - Worker tests proving parent/child lineage and immutable parent records
  - API tests proving jobs, events, versions, artifacts, and model-runs expose targeted edit evidence
affects:
  - worker-generation-pipeline
  - job-event-ledger
  - version-artifact-model-run API evidence
  - future comparison UI

tech-stack:
  added: []
  patterns:
    - targeted edit evidence uses durable JSON metadata already exposed by existing APIs
    - recomposition and provider-mask routes share `edit_route`, target, region, mask, and prompt-delta field names
    - provider-mask edits do not fall back to local full generation after provider failure

key-files:
  created:
    - .planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-05-SUMMARY.md
  modified:
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/worker/tests/test_generation_tasks.py
    - services/api/tests/test_jobs.py
    - .planning/ROADMAP.md
    - .planning/STATE.md

key-decisions:
  - "No new API response fields are needed in 10-05; existing metadata-bearing responses already expose the comparison evidence."
  - "Recomposition trace metadata now uses the same `edit_route`, mask, region, target, and prompt-delta names as provider-mask generation."
  - "Provider-mask generation is not allowed to silently fallback to local generation because that would change edit semantics."

patterns-established:
  - "Child versions carry parent id, lineage depth, route, target, region, prompt delta, mask artifact metadata, and provider/model details."
  - "Artifacts and model-runs mirror the same targeted edit evidence needed by web comparison UI."
  - "Job operations and final events include route metadata for operator diagnosis."

requirements-advanced:
  - V2-EDIT-02
  - V2-EDIT-03
  - V2-EDIT-04

duration: 8 min
completed: 2026-06-18
---

# Phase 10 Plan 05: Targeted Edit Ledger Summary

**Targeted edit executions now leave durable, API-readable lineage and route evidence**

## Performance

- **Duration:** 8 min
- **Completed:** 2026-06-18T13:02:42Z
- **Tasks:** 4
- **Files modified:** 5

## Accomplishments

- Added unified targeted edit metadata to the deterministic recomposition worker branch.
- Ensured recomposition model-run parameters, prompt payload, child version parameters, artifact metadata, job operations, and job events all expose route, mask, region, target, and prompt delta evidence.
- Strengthened provider-mask mock-path tests to assert child lineage, parent immutability, model-run metadata, job operations, and completion event route evidence.
- Added API jobs tests proving targeted edit metadata is readable through existing job, event, version, artifact, and model-run endpoints.
- Blocked provider-mask local fallback after provider failure to avoid silently changing targeted edit semantics.

## Task Commits

1. **Tasks 1-4: Persist and expose targeted edit ledger evidence** - pending current commit.

## Files Created/Modified

- `services/worker/src/caragent_worker/tasks/jobs.py` - Recomposition now writes shared targeted edit trace metadata; provider-mask route skips local fallback.
- `services/worker/tests/test_generation_tasks.py` - Adds durable evidence assertions for recomposition and provider-mask branches.
- `services/api/tests/test_jobs.py` - Adds API-readable targeted edit evidence fixture and endpoint assertions.
- `.planning/ROADMAP.md` - Marks 10-05 complete.
- `.planning/STATE.md` - Advances current plan to 10-06.

## Decisions Made

- Existing `metadata`, `parameters`, and `prompt_payload` API fields are sufficient for comparison UI evidence in this plan.
- Typed API fields can wait until a UI consumer proves generic metadata is too loose.
- Provider-mask fallback to local generation is disabled for semantic safety.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Minor] API test helper tripped a ruff getattr rule**
- **Found during:** Verification
- **Issue:** A test helper used `getattr(obj, "id")` for constant attributes.
- **Fix:** Imported the typed model classes and used direct `.id` access.
- **Verification:** API ruff and jobs tests passed.

**2. [Rule 3 - Blocking] compileall needed unsandboxed uv cache access**
- **Found during:** Verification
- **Issue:** `uv run python -m compileall src tests` hit Windows user-cache permission errors in the sandbox.
- **Fix:** Reran compileall with sandbox escalation.
- **Verification:** API and worker compileall checks passed.

---

**Total deviations:** 2 auto-fixed (1 minor, 1 blocking)
**Impact on plan:** No scope change. API surface stayed backward-compatible.

## Issues Encountered

- The existing API already exposes metadata-rich records, so no OpenAPI schema changes were needed and contract artifacts remained current.
- Provider-mask real hosted calls are still deferred; 10-05 validates the mocked/provider-capable branch only.

## Verification

- `cd services/worker && uv run pytest -q tests/test_generation_tasks.py` - passed, 27 tests.
- `cd services/api && uv run pytest -q tests/test_jobs.py` - passed, 7 tests.
- `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_generation.py` - passed, 29 tests.
- `cd services/worker && uv run pytest -q tests/test_generation_tasks.py tests/test_config.py tests/test_image_providers.py` - passed, 61 tests.
- `cd services/api && uv run ruff check .` - passed.
- `cd services/worker && uv run ruff check .` - passed.
- `cd services/worker && uv run mypy src` - passed with unsandboxed execution.
- `cd services/api && uv run python -m compileall src tests` - passed with unsandboxed execution.
- `cd services/worker && uv run python -m compileall src tests` - passed with unsandboxed execution.
- `corepack pnpm contracts:check` - passed; contract artifacts are current.
- `git diff --check` - passed.

## User Setup Required

None for default validation. `V2_TARGETED_REGENERATION_ENABLED=true` is still required for worker-side targeted edits outside tests.

## Next Phase Readiness

Ready for `10-06-PLAN.md`: failure classification, retry eligibility, and rollback-safe targeted edit UX can now rely on complete route and lineage evidence.

---
*Phase: 10-targeted-regeneration-and-masked-editing-mvp*
*Completed: 2026-06-18*
