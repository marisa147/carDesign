---
phase: 12-lightweight-3d-preview-mvp
plan: "03"
subsystem: web-3d-preview
tags: [preview3d, threejs, workbench, camera-controls, fallback]
requires:
  - phase: 12-lightweight-3d-preview-mvp
    plan: "02"
    provides: shell compatibility helper layer
provides:
  - workbench 2D/3D preview mode switch
  - client-only Three.js viewer scaffold with deterministic no-WebGL fallback
  - preview 3D camera state and resettable controls
affects: [phase-12, web-preview, workbench-store]
tech-stack:
  added:
    - three
    - "@types/three"
  patterns:
    - dynamic browser-only Three.js import inside viewer effect
    - jsdom/no-WebGL fallback branch for deterministic tests
key-files:
  created:
    - apps/web/src/components/workbench/preview-3d-panel.tsx
    - apps/web/src/components/workbench/preview-3d-viewer.tsx
  modified:
    - apps/web/package.json
    - pnpm-lock.yaml
    - apps/web/src/lib/workbench/store.ts
    - apps/web/src/lib/workbench/store.test.ts
    - apps/web/src/components/workbench/preview-panel.tsx
    - apps/web/src/components/workbench/future-gates.tsx
    - apps/web/src/app/page.test.tsx
key-decisions:
  - "Load Three.js dynamically inside the 3D viewer surface, not through server-rendered workbench paths."
  - "Keep 3D camera state local in the workbench store and separate from 2D preview zoom/pan state."
  - "Remove the obsolete disabled `3D 预览后续开放` gate once the preview mode is available."
patterns-established:
  - "3D mode always shows `概念 3D 预览` and `非生产贴膜参考`."
  - "No compatible shell or no WebGL yields a visible fallback instead of a blank canvas."
requirements-progress: ["V2-3D-02", "V2-3D-03", "V2-3D-05"]
duration: 24 min
completed: 2026-06-18
---

# Phase 12 Plan 03 Summary

**Added the frontend 3D preview surface, camera controls, and fallback scaffold**

## Performance

- **Duration:** 24 min
- **Started:** 2026-06-18T16:19:00Z
- **Completed:** 2026-06-18T16:43:00Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Added failing page/store tests for opening 3D preview, preserving selected version state, camera controls, and unsupported-template fallback.
- Added `three` and `@types/three` to the web app.
- Added `previewMode` and resettable `preview3DCamera` state to the workbench store.
- Added a 2D/3D mode switch in the preview panel while keeping version history and 2D controls intact.
- Added `Preview3DPanel` with persistent concept-only labels, rotate/zoom/reset/capture controls, compatible shell evidence, and fallback copy.
- Added `Preview3DViewer` with browser-only dynamic Three.js setup and a deterministic no-WebGL/jsdom fallback preview.
- Removed the stale disabled `3D 预览后续开放` future gate.

## Task Commits

1. **Task 1: Add red web tests for opening 3D preview and fallback** - `00de52a` (test)
2. **Task 2/3: Add Three.js viewer scaffold, mode switch, and camera controls** - `4e8a2c7` (feat)

## Verification

- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `git diff --check` - passed.

## Deviations from Plan

### Environment-limited Verification

**1. [Rule 3 - Blocking] Focused Vitest remains blocked by Windows sandbox process spawning**
- **Found during:** Task 1 and final verification
- **Issue:** `./node_modules/.bin/vitest.CMD --run src/app/page.test.tsx src/lib/workbench/store.test.ts` fails while loading `vitest.config.ts` with `Error: spawn EPERM` from esbuild before tests execute.
- **Fix:** Used typecheck and lint as available in-sandbox verification. The red typecheck captured missing store APIs before implementation, and final typecheck/lint passed after implementation.
- **Files modified:** None for the environment issue.
- **Verification:** web typecheck and eslint passed.

---

**Total deviations:** 1 environment-limited test runner.
**Impact on plan:** UI and store contracts typecheck and lint cleanly. Focused Vitest should be rerun outside the sandbox when process spawning is available.

## Issues Encountered

- Three.js requires `@types/three` for the current strict TypeScript setup.
- React lint disallows synchronous state updates inside effects, so viewer fallback status is scheduled asynchronously.

## User Setup Required

None.

## Next Phase Readiness

Ready for 12-04. The next plan can map PreviewSpec overlays and safe zones onto the lightweight shell material slots.

---
*Phase: 12-lightweight-3d-preview-mvp*
*Completed: 2026-06-18*
