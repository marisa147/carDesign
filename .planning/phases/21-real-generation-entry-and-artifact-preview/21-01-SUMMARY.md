---
phase: 21-real-generation-entry-and-artifact-preview
plan: 1
subsystem: ui
tags: [react, workbench, generation-jobs, polling]
requires:
  - phase: 18
    provides: template-aware workbench generation state and PreviewSpec surfaces
provides:
  - Explicit workbench generation action
  - In-flight generation job polling
affects: [workbench, generation, progress]
tech-stack:
  added: []
  patterns: [WorkbenchApp orchestrates generation submission, ParameterPanel owns visible actions]
key-files:
  created: []
  modified:
    - apps/web/src/components/workbench/workbench-app.tsx
    - apps/web/src/components/workbench/parameter-panel.tsx
    - apps/web/src/app/page.test.tsx
key-decisions:
  - "Keep generation submission in WorkbenchApp and pass a small onGenerate callback into ParameterPanel."
  - "Poll durable API state every 1500 ms only while the active job is queued or running."
patterns-established:
  - "Generation actions save dirty brief state before submitting jobs."
requirements-completed:
  - GENC-01
  - GENC-02
duration: completed-before-gsd-sync
completed: 2026-06-22
---

# Phase 21 Plan 01: Workbench Generation Entry And Active Polling Summary

**Explicit workbench `生成概念` action that submits durable generation jobs and polls active job state.**

## Performance

- **Duration:** completed before GSD execution sync
- **Started:** 2026-06-22T00:00:00+08:00
- **Completed:** 2026-06-22T12:00:00+08:00
- **Tasks:** 4
- **Files modified:** 3

## Accomplishments

- Added a visible `生成概念` action to the parameter panel.
- Saved dirty brief updates before generation submission.
- Submitted jobs through `buildGenerationSubmissionPayload()` and `submitGenerationJob()`.
- Added 1500 ms polling for queued/running jobs and stopped polling for terminal states.
- Added/updated web tests for the explicit generation action.

## Task Commits

This execution was synchronized after implementation work had already been applied in the working tree. No per-task GSD commits were created during this fallback run.

## Files Created/Modified

- `apps/web/src/components/workbench/workbench-app.tsx` - submits generation jobs, seeds state, refreshes active job state, and polls in-flight jobs.
- `apps/web/src/components/workbench/parameter-panel.tsx` - exposes `生成概念`, save-before-generate behavior, disabled states, and inline submission error state.
- `apps/web/src/app/page.test.tsx` - covers explicit generation submission from the workbench.

## Decisions Made

- Keep provider-aware payload building in the existing generation API helper.
- Use `requested_by: "web-workbench"` for workbench generation submissions.
- Use a 1500 ms polling interval, inside the required 1-2 second window.

## Deviations from Plan

The implementation existed before this GSD execution pass, so the executor verified and documented the plan instead of making fresh code edits.

## Issues Encountered

Initial Vitest execution failed in the sandbox with `spawn EPERM` from esbuild. Re-running with elevated permissions passed.

## User Setup Required

None.

## Next Phase Readiness

Plan 21.02 can rely on a real frontend consumer for `ArtifactResponse.content_url`.

---
*Phase: 21-real-generation-entry-and-artifact-preview*
*Completed: 2026-06-22*
