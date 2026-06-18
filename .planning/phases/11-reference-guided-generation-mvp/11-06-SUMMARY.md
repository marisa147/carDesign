---
phase: 11-reference-guided-generation-mvp
plan: "06"
subsystem: reference-workbench-ux
tags: [references, workbench, provider-readiness, child-iterations, trace-ui]

requires:
  - phase: 11-reference-guided-generation-mvp
    plan: "02"
    provides: workbench reference role assignment and rights eligibility
  - phase: 11-reference-guided-generation-mvp
    plan: "05"
    provides: durable reference trace metadata on jobs, versions, artifacts, and exports
provides:
  - Pre-submit reference/provider readiness visibility
  - Reference warning diagnostics in progress UI
  - Compact reference trace evidence in version comparison UI
  - Child iteration payloads that reuse current reference assignments
affects:
  - workbench-reference-ux
  - progress-diagnostics
  - version-comparison
  - child-iteration-submission

tech-stack:
  added: []
  patterns:
    - child iteration request construction uses a shared payload helper
    - UI shows counts and role labels instead of raw trace JSON
    - warning diagnostics are sanitized before display

key-files:
  created: []
  modified:
    - apps/web/src/lib/api/iteration.ts
    - apps/web/src/components/workbench/workbench-app.tsx
    - apps/web/src/components/workbench/asset-panel.tsx
    - apps/web/src/components/workbench/progress-panel.tsx
    - apps/web/src/components/workbench/comparison-panel.tsx
    - apps/web/src/app/page.test.tsx

key-decisions:
  - "Reference assignments are preserved through child iteration payloads via `parameter_overrides.reference_usage`."
  - "Provider readiness can be refreshed before a generation job exists, so unsupported reference roles are visible before submission."
  - "Progress and comparison surfaces show compact role counts, included/omitted counts, warning counts, and unsupported-role labels."
  - "Raw rights snapshots and trace JSON are hidden from compact UI rows."

patterns-established:
  - "`buildIterationSubmissionPayload()` merges provider intent and reference overrides without duplicating `reference_usage`."
  - "Reference trace display filters trace metadata keys out of generic parameter diffs."
  - "The asset panel can warn when the currently selected provider does not support an enabled role."

requirements-completed:
  - V2-REF-01
  - V2-REF-02
  - V2-REF-03
  - V2-REF-04
  - V2-REF-05

duration: 24 min
completed: 2026-06-18
---

# Phase 11 Plan 06: Reference Workbench UX Summary

**Reference-guided generation is now visible and reusable in the workbench: selected roles, provider limitations, progress warnings, version trace evidence, and child iterations all carry the same structured reference usage.**

## Performance

- **Duration:** 24 min
- **Completed:** 2026-06-18T23:13:29+08:00
- **Tasks:** 4
- **Files modified:** 6

## Accomplishments

- Added red web and API tests covering unsupported BFL reference roles, progress diagnostics, compact version reference trace, and child iteration reference reuse.
- Added `buildIterationSubmissionPayload()` so child iteration requests preserve provider intent, targeted edit fields, and current `reference_usage`.
- Updated the workbench to surface selected-provider unsupported reference roles in asset rows and parameter warnings.
- Enabled provider readiness refresh before a generation job exists, allowing pre-submit hosted/reference warnings.
- Added sanitized reference diagnostics to the progress panel using job/event metadata.
- Added compact reference trace rows to version comparison and removed raw trace metadata from generic parameter diffs.

## Task Commits

1. **Task 1: Add red reference UX and reuse tests** - `84bcaa2` (test)
2. **Tasks 2-4: Complete reference UX, diagnostics, trace display, and child iteration reuse** - `fce52e7` (feat)

## Files Created/Modified

- `apps/web/src/lib/api/iteration.ts` - Adds the child iteration payload helper that merges provider intent and reference usage.
- `apps/web/src/components/workbench/workbench-app.tsx` - Uses the helper for child iterations, passes provider unsupported roles to assets, and syncs active provider after readiness refresh.
- `apps/web/src/components/workbench/asset-panel.tsx` - Shows provider-unsupported warning state for enabled reference roles.
- `apps/web/src/components/workbench/progress-panel.tsx` - Allows pre-submit readiness refresh and renders sanitized reference diagnostics.
- `apps/web/src/components/workbench/comparison-panel.tsx` - Shows compact reference trace evidence and hides trace keys from raw parameter diffs.
- `apps/web/src/app/page.test.tsx` - Covers reference warning, progress diagnostics, version trace, and iteration reuse behavior.

## Decisions Made

- Child iterations reuse the current workbench reference assignments instead of relying on parent version metadata alone.
- Provider capability warnings are shown before submission by allowing operations status refresh in the no-job state.
- Compact UI surfaces show reference counts and role labels, not full rights snapshots or raw metadata.
- BFL reference-image unsupported roles remain warnings/blocked states only; this plan does not enable hosted reference-image payloads.

## Deviations from Plan

### Auto-fixed Issues

- The first implementation assumed provider readiness could be refreshed from the no-job progress state, but that button was disabled. Plan 06 fixed this so users can see hosted/reference readiness before submitting generation.

---

**Total deviations:** 1
**Impact on plan:** No scope change; the fix strengthens the intended pre-submit warning flow.

## Issues Encountered

- Vitest still requires running `apps/web/node_modules/.bin/vitest.CMD` with sandbox escalation on this Windows setup because the sandboxed run hits `spawn EPERM`.

## Verification

- `cd apps/web && ./node_modules/.bin/vitest.CMD --run src/app/page.test.tsx src/lib/workbench/store.test.ts src/lib/api/generation.test.ts src/lib/api/iteration.test.ts` - passed with escalation, 49 tests.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `git diff --check` - passed.

## User Setup Required

None - automated coverage uses mocked provider status and local workbench state only.

## Next Phase Readiness

Ready for `11-07-PLAN.md`: Phase 11 has schema, UI assignment, prompt planning, provider handling, durable trace, and workbench reuse in place; remaining work is smoke, docs, rights-gate regression, and Browser UAT.

---
*Phase: 11-reference-guided-generation-mvp*
*Completed: 2026-06-18*
