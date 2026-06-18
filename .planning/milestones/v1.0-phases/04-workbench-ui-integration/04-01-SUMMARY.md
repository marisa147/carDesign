---
phase: 04-workbench-ui-integration
plan: "01"
subsystem: web-data-foundation
tags: [nextjs, react-query, zustand, contracts, assets]

requires:
  - phase: 03
    provides: durable workspace, generation, artifact, version, and asset API surfaces
provides:
  - browser-safe asset API wrapper module
  - durable design brief listing wrapper for workspace resume
  - stable workbench query key helpers
  - Zustand-backed local UI state boundary
  - workbench QueryClient provider
affects: [phase-04-workbench-ui]

tech-stack:
  patterns:
    - generated contract URL helpers wrapped behind small web API clients
    - TanStack Query provider for API-backed server state
    - Zustand store for local preview/selection state only

key-files:
  created:
    - apps/web/src/lib/api/assets.ts
    - apps/web/src/lib/api/assets.test.ts
    - apps/web/src/lib/workbench/query-keys.ts
    - apps/web/src/lib/workbench/store.ts
    - apps/web/src/lib/workbench/store.test.ts
    - apps/web/src/components/workbench/query-provider.tsx
  modified:
    - apps/web/package.json
    - pnpm-lock.yaml
    - apps/web/src/lib/api/workspaces.ts
    - apps/web/src/lib/api/workspaces.test.ts

key-decisions:
  - "Zustand was added through pnpm using the repo-local `.pnpm-store` to honor the project-local UI state convention."
  - "Asset uploads use multipart `FormData` and intentionally do not set a JSON content type."
  - "The local workbench store contains only selected tab/view/version and preview transform state, not durable messages, jobs, assets, or briefs."

patterns-established:
  - "Workbench query keys are centralized under `apps/web/src/lib/workbench/query-keys.ts`."
  - "Web API wrappers continue to accept injectable `apiBaseUrl`, `fetch`, and `signal` options for deterministic tests."

requirements-completed: []

duration: 18 min
completed: 2026-06-17
---

# Phase 4 Plan 01: Web Data Foundation Summary

**The workbench now has typed asset/brief wrappers, a Query provider, and an isolated Zustand UI-state boundary.**

## Accomplishments

- Added `apps/web/src/lib/api/assets.ts` for upload/list/get/update-rights routes using generated contract URL helpers.
- Extended `apps/web/src/lib/api/workspaces.ts` with `listWorkspaceDesignBriefs` so Phase 4 can resume editable brief parameters from canonical API state.
- Added workbench query key helpers for workspace, messages, briefs, assets, jobs, and generation state.
- Added `apps/web/src/lib/workbench/store.ts` with Zustand-managed local UI state for selected version/view/tab and preview zoom/pan.
- Added `WorkbenchQueryProvider` with a stable client-side `QueryClient`.
- Added focused tests for asset wrappers, brief listing, query keys, and UI-state boundaries.

## Deviations from Plan

- None. Zustand installation succeeded after rerunning pnpm with the existing repo-local `.pnpm-store`.

## Issues Encountered

- Sandbox Vitest failed with `spawn EPERM`; the same focused test command passed outside the sandbox.
- The first pnpm add attempt failed because pnpm tried to use `D:\.pnpm-store\v11` while the repo was linked to `D:\python\carAgent\.pnpm-store\v11`. Rerunning with `--store-dir .pnpm-store` fixed it.

## Verification

- RED: `corepack pnpm --filter @caragent/web test -- assets.test.ts workspaces.test.ts store.test.ts` failed after tests were added because `@/lib/api/assets`, `@/lib/workbench/query-keys`, and `listWorkspaceDesignBriefs` were missing.
- GREEN: `corepack pnpm --filter @caragent/web test -- assets.test.ts workspaces.test.ts store.test.ts` passed, 6 files / 27 tests.
- `corepack pnpm --filter @caragent/web lint` passed.
- `corepack pnpm --filter @caragent/web typecheck` passed.

## Next Plan Readiness

Ready for `04-02`: the data/state foundation is in place, so the proof-first page can be replaced with the Phase 4 workbench shell and future-feature gates.
