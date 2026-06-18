---
phase: 06-itasha-and-template-intelligence
plan: "04"
subsystem: workbench-ui-preview-spec
tags: [nextjs, react, workbench, preview-spec, ui]

requires:
  - plan: "06-02"
    provides: worker PreviewSpec persistence in version/artifact metadata
  - plan: "06-03"
    provides: generated Phase 6 TypeScript contract fields
provides:
  - Phase 6 itasha controls in parameter panel
  - local overlay and safe-zone preview toggles
  - PreviewSpec summary and safe-zone display
  - export manifest PreviewSpec summary
affects: [phase-06-05-verification-uat]

tech-stack:
  patterns:
    - frontend request shapes come from `@caragent/contracts`
    - durable server state stays outside Zustand
    - PreviewSpec overlay toggles remain local UI state

key-files:
  modified:
    - apps/web/src/app/page.test.tsx
    - apps/web/src/components/workbench/parameter-panel.tsx
    - apps/web/src/components/workbench/preview-panel.tsx
    - apps/web/src/components/workbench/export-panel.tsx
    - apps/web/src/lib/workbench/store.ts
    - apps/web/src/lib/workbench/store.test.ts

key-decisions:
  - "Phase 6 controls live inside the existing parameter panel instead of a separate editor."
  - "Overlay and safe-zone visibility are local UI toggles and do not mutate selected version data."
  - "PreviewSpec summaries are shown in preview and export surfaces while preserving concept-preview wording."

patterns-established:
  - "Parameter saves build changed-field payloads using generated `GenerationBriefUpdateRequest` keys."
  - "PreviewSpec parsing is defensive against unknown JSON metadata shapes."
  - "Safe-zone overlays are bounded inside the existing preview region."

requirements-completed:
  - QUAL-01
  - QUAL-02
  - QUAL-03
  - QUAL-04
  - QUAL-05

duration: 35 min
completed: 2026-06-18
---

# Phase 6 Plan 04: Workbench PreviewSpec UI Summary

**The workbench now exposes Phase 6 itasha controls, PreviewSpec summaries, overlay toggles, and safe-zone inspection.**

## Accomplishments

- Added failing web tests for Phase 6 parameter controls, changed-field saves, PreviewSpec display, overlay/safe-zone toggles, export manifest summaries, and local store reset behavior.
- Extended the parameter panel with `痛车设计控制`, including character focus, supporting graphics, racing/JDM cues, typography intent, color harmony, and overlay logo asset ids.
- Kept parameter saves scoped to the existing brief PATCH route and verified they do not submit generation jobs.
- Added local Zustand state for `showOverlayLayers` and `showSafeZones`.
- Added preview-panel rendering for PreviewSpec summary counts, deterministic text/logo layers, safe-zone overlays, and template reference legend.
- Added export-panel PreviewSpec summary rendering from selected version parameters and saved export manifests.

## Verification

- RED: focused web tests failed as expected because Phase 6 controls, toggles, and PreviewSpec summaries were absent.
- GREEN: `corepack pnpm --filter @caragent/web test -- apps/web/src/app/page.test.tsx apps/web/src/lib/workbench/store.test.ts` passed after escalation, 7 files and 40 tests.
- `corepack pnpm --filter @caragent/web lint` passed.
- `corepack pnpm --filter @caragent/web typecheck` passed.

## Deviations from Plan

- No code-scope deviation.
- Vitest needed escalation because Vite/esbuild process spawning is blocked by the Windows sandbox.

## Next Plan Readiness

Ready for `06-05`: Phase 6 docs, verification, Browser UAT, and requirement closure.
