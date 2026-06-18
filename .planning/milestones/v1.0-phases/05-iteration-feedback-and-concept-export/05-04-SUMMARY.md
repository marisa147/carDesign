---
phase: 05-iteration-feedback-and-concept-export
plan: "04"
subsystem: workbench-iteration-ui
tags: [nextjs, workbench, lineage, comparison, iteration, browser-uat]

requires:
  - phase: "05-03"
    provides: frontend wrappers and query keys for iteration APIs
provides:
  - workbench lineage display
  - metadata/parameter comparison panel
  - child iteration request form
  - child iteration submit flow
  - desktop/mobile browser sanity evidence
affects: [phase-05-05-feedback-ui, phase-05-06-export-ui]

tech-stack:
  patterns:
    - selected design version remains Zustand UI state
    - server state stays in API wrappers/query cache
    - child iteration submission uses `submitChildIteration`
    - comparison is metadata/parameter based and does not claim pixel diffing

key-files:
  modified:
    - apps/web/src/app/page.test.tsx
    - apps/web/src/components/workbench/comparison-panel.tsx
    - apps/web/src/components/workbench/iteration-panel.tsx
    - apps/web/src/components/workbench/workbench-app.tsx

key-decisions:
  - "Lineage and child iteration controls live in the existing `历史方案` workbench area."
  - "Comparison copy explicitly says it only compares metadata and parameters."
  - "Submitting a child iteration calls `/workspaces/{workspace_id}/versions/{version_id}/iterations` and does not call parent or selected version overwrite routes."
  - "After submit, the workbench refreshes job/generation state while preserving the selected version and existing chat/parameter context."

patterns-established:
  - "Workbench version-context panels can read selected version from Zustand while receiving canonical version lists from server state."
  - "Phase 5 UI tests assert no accidental overwrite route is called when version selection changes."

requirements-completed:
  - ITER-01
  - ITER-02
  - ITER-03

duration: 35 min
completed: 2026-06-17
---

# Phase 5 Plan 04: Workbench Iteration UI Summary

The workbench now shows version lineage, metadata/parameter comparison, and a child iteration form connected to the Phase 5 iteration API.

## Accomplishments

- Added TDD coverage for selecting a child version, seeing parent/child lineage, viewing parameter differences, and submitting a child iteration.
- Added `ComparisonPanel` for lineage depth, parent/current version labels, and parameter differences.
- Added `IterationPanel` for change-request input and child-iteration submission.
- Wired `WorkbenchApp` to submit child iterations through `submitChildIteration`, cache the result, refresh generation state, and show a submission notice.
- Preserved existing chat, parameter, asset, preview, progress, and retry behavior.

## Deviations from Plan

- `preview-panel.tsx` did not need changes; selected-version behavior already lived there and the lineage UI was cleaner in the history panel.

## Verification

- RED: `corepack pnpm --filter @caragent/web test -- page.test.tsx` failed because lineage/comparison UI was missing.
- GREEN: `corepack pnpm --filter @caragent/web test -- page.test.tsx` passed, 7 files and 36 tests.
- `corepack pnpm --filter @caragent/web test` passed, 7 files and 36 tests.
- `corepack pnpm --filter @caragent/web typecheck` passed.
- `corepack pnpm --filter @caragent/web lint` passed.
- `corepack pnpm --filter @caragent/web build` passed.
- Browser desktop check at `http://127.0.0.1:3000/` confirmed history/iteration controls render with no horizontal overflow.
- Browser mobile check at 390x844 confirmed history/iteration controls render in a single-column layout with no horizontal overflow.
- Browser console error check returned no errors.

## Next Plan Readiness

Ready for `05-05`: feedback, rating, approval, rejection, and comment UI can use the Phase 5 feedback wrappers and selected-version context.
