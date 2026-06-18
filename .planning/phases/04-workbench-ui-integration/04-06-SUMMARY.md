---
phase: 04-workbench-ui-integration
plan: "06"
subsystem: web-workbench-progress-preview
tags: [nextjs, react, jobs, preview, history, zustand]

requires:
  - plan: "04-03"
    provides: workspace and brief resume state
  - plan: "04-04"
    provides: parameter panel context preservation
  - plan: "04-05"
    provides: asset/reference state in the workbench
provides:
  - generation progress panel
  - retry action for failed jobs
  - durable job/event/artifact/version loading
  - 2D preview panel
  - local zoom/view/version switching controls
affects: [phase-04-final-verification]

tech-stack:
  patterns:
    - `WorkbenchApp` loads latest job state through list-jobs plus generation-state routes
    - `ProgressPanel` renders job/events and retry action
    - `PreviewPanel` renders artifact/version metadata and local controls
    - Zustand remains local-only for selected version, view, zoom, and pan

key-files:
  created:
    - apps/web/src/components/workbench/progress-panel.tsx
    - apps/web/src/components/workbench/preview-panel.tsx
  modified:
    - apps/web/src/components/workbench/workbench-app.tsx
    - apps/web/src/lib/workbench/store.ts
    - apps/web/src/lib/workbench/store.test.ts
    - apps/web/src/app/page.test.tsx

key-decisions:
  - "Progress is driven by durable job/events state, not local placeholder state."
  - "Retry uses `retryGenerationJob` with deterministic `retry-{job_id}` idempotency keys."
  - "Preview displays 2D concept metadata and object keys; true image delivery URL handling remains outside Phase 4."
  - "Version selection, view switching, and zoom/reset are local UI state and do not mutate server data."

patterns-established:
  - "Latest job selection sorts by updated_at before loading generation state."
  - "Preview zoom changes in 0.25 steps and is clamped in the Zustand store."

requirements-completed:
  - UI-04
  - UI-05
  - UI-06
  - UI-07

duration: 45 min
completed: 2026-06-17
---

# Phase 4 Plan 06: Progress, Preview, And History Summary

**The workbench now renders durable generation progress and a usable 2D preview/history surface.**

## Accomplishments

- Added `ProgressPanel` with queued/running/succeeded/failed labels, latest event copy, event list, refresh, and retry for failed jobs.
- Wired workspace resume to list jobs and load the latest job's job/events/artifacts/versions state.
- Added deterministic retry behavior using `retryGenerationJob`.
- Added `PreviewPanel` with stable empty/loaded states, artifact metadata, zoom controls, reset, view switching, and version buttons.
- Added store actions for zoom in/out with clamping.
- Added tests covering progress statuses, retry request payload, preview version switching, local zoom/view controls, and preservation of chat/parameter context.

## Deviations from Plan

- The preview renders artifact metadata/object keys rather than a real object-storage image URL. Phase 4 verifies the renderer contract and state switching; signed image delivery remains a later integration detail.

## Issues Encountered

- Generated `JobEventResponse.progress` is typed as `string | null`, so progress fixtures use string values.
- Local `Button` supports `default` and `sm` sizes only; preview icon buttons use `sm`.
- Failure text can appear as both latest event and latest error, so tests assert presence without assuming a single occurrence.

## Verification

- RED: `corepack pnpm --filter @caragent/web test -- page.test.tsx store.test.ts` failed for missing zoom actions, job state loading, progress, and preview UI.
- GREEN: `corepack pnpm --filter @caragent/web test -- page.test.tsx store.test.ts` passed, 6 files / 31 tests.
- `corepack pnpm --filter @caragent/web typecheck` passed.
- `corepack pnpm --filter @caragent/web lint` passed.

## Next Plan Readiness

Ready for `04-07`: Phase 4 functionality is implemented and needs final docs, verification evidence, and Browser UAT checks.
