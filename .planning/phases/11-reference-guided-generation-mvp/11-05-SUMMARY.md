---
phase: 11-reference-guided-generation-mvp
plan: "05"
subsystem: reference-trace-persistence
tags: [references, traceability, exports, metadata, rights-snapshot]

requires:
  - phase: 11-reference-guided-generation-mvp
    plan: "03"
    provides: reference plan fields and provider warnings
  - phase: 11-reference-guided-generation-mvp
    plan: "04"
    provides: worker/provider reference usage request metadata and preflight
provides:
  - Shared reference trace metadata helper
  - Rights/source snapshots on durable generation records
  - Export manifest source data for future handoff packaging
  - Web export submission carrying selected-version reference trace
affects:
  - worker-generation
  - model-run-trace
  - artifact-version-metadata
  - concept-export-manifest
  - workbench-export

tech-stack:
  added: []
  patterns:
    - reference trace keys are centralized in core references
    - durable records use snapshot `reference_usage.items` with embedded rights/source snapshots
    - export manifests lift selected-version reference trace to top-level manifest fields

key-files:
  created: []
  modified:
    - services/core/src/caragent_core/references.py
    - services/core/src/caragent_core/services/jobs.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - apps/web/src/components/workbench/workbench-app.tsx
    - services/worker/tests/test_generation_tasks.py
    - services/api/tests/test_jobs.py
    - apps/web/src/app/page.test.tsx

key-decisions:
  - "Durable `reference_usage` uses `ReferenceUsageSnapshot.items` rather than the provider-request `requested` shape."
  - "Rights/source metadata is copied from asset rows at worker execution time and stored as `rights_snapshot`."
  - "Concept export manifests include top-level reference trace fields from the selected version parameters."
  - "No binary bytes, local paths, provider keys, or secret-like fields are added to reference trace metadata."

patterns-established:
  - "`build_reference_trace_metadata()` emits the canonical trace shape."
  - "`REFERENCE_TRACE_METADATA_KEYS` is reused by export manifest construction."
  - "Workbench export submission mirrors the same trace keys from `selectedVersion.parameters`."

requirements-completed:
  - V2-REF-05

duration: 17 min
completed: 2026-06-18
---

# Phase 11 Plan 05: Reference Trace Persistence Summary

**Reference usage evidence now persists consistently across model runs, artifacts, versions, job metadata/events, and concept export manifest source data.**

## Performance

- **Duration:** 17 min
- **Completed:** 2026-06-18T22:51:40+08:00
- **Tasks:** 4
- **Files modified:** 7

## Accomplishments

- Added red tests proving reference trace must appear on model-run parameters, model-run prompt payload, artifact metadata, version parameters, job completion metadata, and events.
- Added a core `build_reference_trace_metadata()` helper plus shared `REFERENCE_TRACE_METADATA_KEYS`.
- Updated worker generation to snapshot confirmed asset rights/source data at execution time and merge the same trace into durable generation records.
- Updated concept export manifest construction so version-level reference trace is available as top-level source data.
- Updated the workbench export submission to include selected-version reference trace in the submitted manifest.

## Task Commits

1. **Task 1: Add red durable reference trace tests** - `e4b3889` (test)
2. **Tasks 2-4: Persist trace and include export manifest source data** - `1e45184` (feat)

## Files Created/Modified

- `services/core/src/caragent_core/references.py` - Adds canonical reference trace metadata helper and trace key list.
- `services/core/src/caragent_core/services/jobs.py` - Lifts reference trace fields into export manifests.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Builds rights snapshots and persists trace across generation surfaces.
- `apps/web/src/components/workbench/workbench-app.tsx` - Includes selected-version reference trace in concept export requests.
- `services/worker/tests/test_generation_tasks.py` - Covers durable trace equality and no-secret/no-binary metadata.
- `services/api/tests/test_jobs.py` - Covers export manifest source trace.
- `apps/web/src/app/page.test.tsx` - Covers workbench export manifest body.

## Decisions Made

- Provider request metadata remains lightweight, but durable records use the snapshot shape with rights evidence.
- Export manifests do not wait for Phase 13 ZIP work; they now carry source trace data for that later package builder.
- Reference trace persistence is provider-agnostic and does not enable any hosted reference-image input.

## Deviations from Plan

### Auto-fixed Issues

- Updated a Plan 04 assertion that expected model-run prompt payload to keep the request-time `requested` shape; Plan 05 intentionally upgrades durable prompt payload trace to the snapshot shape.

---

**Total deviations:** 1
**Impact on plan:** No scope change; the distinction between provider request shape and durable trace shape is now explicit.

## Issues Encountered

- `corepack pnpm ... exec vitest` did not find `vitest` on this Windows setup. Running `apps/web/node_modules/.bin/vitest.CMD` worked, but required sandbox escalation because esbuild hit `spawn EPERM`.

## Verification

- `cd services/worker && uv run pytest -q tests/test_generation_tasks.py` - passed, 32 tests.
- `cd services/api && uv run pytest -q tests/test_jobs.py` - passed, 8 tests.
- `cd apps/web && ./node_modules/.bin/vitest.CMD --run src/app/page.test.tsx src/lib/api/iteration.test.ts` - passed with escalation, 32 tests.
- `cd services/core && uv run ruff check .` - passed.
- `cd services/api && uv run ruff check .` - passed.
- `cd services/worker && uv run ruff check .` - passed.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `git diff --check` - passed.

## User Setup Required

None - this work uses local deterministic generation and metadata/export tests only.

## Next Phase Readiness

Ready for `11-06-PLAN.md`: durable trace is now available for UX surfaces that show reference reuse, warnings, and iteration behavior.

---
*Phase: 11-reference-guided-generation-mvp*
*Completed: 2026-06-18*
