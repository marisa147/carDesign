---
phase: 04-workbench-ui-integration
plan: "02"
subsystem: web-workbench-shell
tags: [nextjs, react, layout, ui-gates]

requires:
  - plan: "04-01"
    provides: workbench query provider and local UI state boundary
provides:
  - Phase 4 workbench first-screen layout
  - thin page entrypoint
  - explicit deferred future-feature gates
  - neutral workbench background color tuning
affects: [phase-04-chat, phase-04-parameters, phase-04-preview]

tech-stack:
  patterns:
    - `page.tsx` renders provider plus `WorkbenchApp`
    - workbench layout is split into shell/app/future-gates components
    - future features are disabled buttons with explicit labels

key-files:
  created:
    - apps/web/src/components/workbench/workbench-app.tsx
    - apps/web/src/components/workbench/workbench-shell.tsx
    - apps/web/src/components/workbench/future-gates.tsx
  modified:
    - apps/web/src/app/page.tsx
    - apps/web/src/app/page.test.tsx
    - apps/web/src/app/globals.css

key-decisions:
  - "The homepage is now the workbench shell rather than the Phase 1-3 proof surface."
  - "The shell exposes chat, 2D preview, parameters, assets, progress, and history regions before detailed behavior lands in later Phase 4 plans."
  - "3D preview, production export, and marketplace controls are visible but disabled/deferred."

patterns-established:
  - "Workbench panels are top-level layout zones, not nested page-section cards."
  - "Lucide icons with names that collide with DOM element names are imported with aliases, e.g. `ImageIcon`, to avoid jsx-a11y false positives."

requirements-completed: []

duration: 15 min
completed: 2026-06-17
---

# Phase 4 Plan 02: Workbench Shell Summary

**The app now opens directly into a Phase 4 workbench layout with explicit future-feature gates.**

## Accomplishments

- Replaced the large proof-page `page.tsx` with a thin entrypoint that renders `WorkbenchQueryProvider` and `WorkbenchApp`.
- Added `WorkbenchShell` with left chat, central 2D preview/progress/history, and right parameter/assets/future-gate zones.
- Added `FutureGates` with disabled controls for `3D 预览后续开放`, `生产导出后续开放`, and `市场功能后续开放`.
- Added initial placeholder panels for chat, preview, parameters, assets, progress, and history so subsequent plans can replace content without changing the layout contract.
- Adjusted global background/muted colors toward the neutral Phase 4 UI-SPEC palette.
- Replaced old page tests with Phase 4 shell expectations.

## Deviations from Plan

- None. This plan intentionally leaves real chat, parameter edit, asset upload, and preview selection behavior to later Phase 4 plans.

## Issues Encountered

- `lucide-react`'s `Image` component name triggered jsx-a11y `alt-text` warning because lint treated it like an HTML image element. Renamed the import to `ImageIcon`.

## Verification

- RED: `corepack pnpm --filter @caragent/web test -- page.test.tsx` failed because the current page still rendered the Phase 1-3 proof shell.
- GREEN: `corepack pnpm --filter @caragent/web test -- page.test.tsx` passed, 6 files / 20 tests.
- `corepack pnpm --filter @caragent/web lint` passed.
- `corepack pnpm --filter @caragent/web typecheck` passed.

## Next Plan Readiness

Ready for `04-03`: the layout now has a chat region and prompt composer that can be connected to durable workspace messages and generation brief creation.
