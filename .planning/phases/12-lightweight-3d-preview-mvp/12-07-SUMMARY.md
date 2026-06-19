---
phase: 12-lightweight-3d-preview-mvp
plan: "07"
subsystem: preview3d-browser-uat
tags: [preview3d, webgl, accessibility, responsive, browser-uat]
requires:
  - phase: 12-lightweight-3d-preview-mvp
    plan: "03"
    provides: 2D/3D preview mode switch and client-only viewer scaffold
  - phase: 12-lightweight-3d-preview-mvp
    plan: "04"
    provides: PreviewSpec safe-zone and overlay material mapping
  - phase: 12-lightweight-3d-preview-mvp
    plan: "06"
    provides: persistent 3D preview warning and non-production labels
provides:
  - accessible 3D preview region and camera/screenshot controls
  - reduced-motion-aware 3D render loop behavior
  - mobile-framed WebGL canvas sizing and camera distance
  - desktop and mobile browser evidence for nonblank lightweight 3D preview
affects: [phase-12, web-preview, accessibility, browser-uat]
tech-stack:
  added: []
  patterns:
    - WebGL renderer canvas dimensions must be constrained by both drawing-buffer size and CSS width/height.
    - Browser visual evidence can use headless Chrome CDP screenshot crops when direct WebGL readback is unavailable.
key-files:
  created:
    - .planning/phases/12-lightweight-3d-preview-mvp/evidence/12-07-desktop-3d.png
    - .planning/phases/12-lightweight-3d-preview-mvp/evidence/12-07-mobile-3d.png
    - .planning/phases/12-lightweight-3d-preview-mvp/12-07-SUMMARY.md
  modified:
    - apps/web/src/app/page.test.tsx
    - apps/web/src/components/workbench/preview-3d-panel.tsx
    - apps/web/src/components/workbench/preview-3d-viewer.tsx
    - .planning/phases/12-lightweight-3d-preview-mvp/12-HUMAN-UAT.md
key-decisions:
  - "The lightweight 3D browser UAT is accepted from real desktop/mobile Chrome screenshots plus screenshot-crop pixel statistics."
  - "The 3D viewer keeps the canvas CSS-constrained and pulls the camera back on narrow aspect ratios to avoid mobile clipping."
patterns-established:
  - "Treat in-app Browser DOM verification and external CDP screenshot evidence as complementary when one surface cannot capture WebGL pixels."
  - "Keep 3D preview control labels and concept-only warning text visible across compatible, fallback, desktop, and mobile states."
requirements-progress: ["V2-3D-02", "V2-3D-03", "V2-3D-05"]
requirements-completed: ["V2-3D-02", "V2-3D-03", "V2-3D-05"]
duration: 2 sessions
completed: 2026-06-19
---

# Phase 12 Plan 07 Summary

**Browser-verified lightweight 3D preview with accessible controls and mobile-safe WebGL framing**

## Performance

- **Duration:** 2 sessions
- **Started:** 2026-06-18T17:55:00Z
- **Completed:** 2026-06-19T06:55:00Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Added focused page assertions for the 3D preview region, accessible camera/screenshot controls, persistent non-production labels, UV warning text, fallback copy, and 2D fallback availability.
- Hardened the 3D panel/viewer with accessible region/control names, reduced-motion-aware render loop behavior, cleanup-safe rendering, and wrapped mobile controls.
- Fixed mobile WebGL framing by constraining the renderer canvas CSS size and backing the camera away on narrow aspect ratios.
- Captured desktop and mobile Chrome evidence showing a nonblank lightweight 3D shell, visible warning posture, readable source metadata, and no control overlap.
- Recorded screenshot-crop pixel statistics proving the visible 3D surface is nonblank in both browser viewports.

## Task Commits

1. **Tasks 1-2: Accessibility and responsive hardening** - `d6564b1` (feat)
2. **Task 3: Initial browser UAT attempt record** - `3615ece` (docs)
3. **Task 3: Mobile canvas framing and browser evidence** - `5da5569` (fix)

## Verification

- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `git diff --check` - passed.
- Desktop Chrome 1440x900 screenshot: `.planning/phases/12-lightweight-3d-preview-mvp/evidence/12-07-desktop-3d.png` - passed.
- Mobile Chrome 390x844 screenshot: `.planning/phases/12-lightweight-3d-preview-mvp/evidence/12-07-mobile-3d.png` - passed.
- Desktop crop `(430, 257, 974, 563)` - 290 unique colors, 32,627 non-background pixels - passed.
- Mobile crop `(100, 284, 679, 795)` - 339 unique colors, 52,130 non-background pixels - passed.

## Files Created/Modified

- `apps/web/src/app/page.test.tsx` - Adds 3D preview accessibility/fallback assertions.
- `apps/web/src/components/workbench/preview-3d-panel.tsx` - Exposes accessible 3D region/control labels and wrapped control layout.
- `apps/web/src/components/workbench/preview-3d-viewer.tsx` - Adds reduced-motion behavior, CSS-constrained canvas sizing, and aspect-aware camera distance.
- `.planning/phases/12-lightweight-3d-preview-mvp/12-HUMAN-UAT.md` - Records browser visual evidence and remaining Vitest limitation.
- `.planning/phases/12-lightweight-3d-preview-mvp/evidence/12-07-desktop-3d.png` - Desktop browser UAT screenshot.
- `.planning/phases/12-lightweight-3d-preview-mvp/evidence/12-07-mobile-3d.png` - Mobile browser UAT screenshot.

## Decisions Made

- Use screenshot crop statistics as the durable nonblank proof because direct WebGL `readPixels` returned zeroed samples in this browser environment while screenshots clearly captured the scene.
- Keep the renderer canvas explicitly CSS-sized even though `renderer.setSize(width, height, false)` controls the drawing buffer; without CSS sizing, narrow mobile viewports can clip the scene.
- Preserve the concept-only and UV-not-verified labels as visible text and accessible names in all browser-checked states.

## Deviations from Plan

### Environment-limited Verification

**1. [Rule 3 - Blocking] Focused Vitest remains blocked by Windows sandbox process spawning**
- **Found during:** Task 1 and final verification.
- **Issue:** `corepack pnpm --filter @caragent/web test` reaches the package script but fails while loading `vitest.config.ts` with esbuild `Error: spawn EPERM`.
- **Fix:** Used web typecheck, eslint, DOM inspection, browser screenshots, and screenshot-crop pixel statistics for this plan's required evidence.
- **Files modified:** None for the environment issue.
- **Verification:** Typecheck, lint, browser screenshots, and crop statistics passed.

---

**Total deviations:** 1 environment/tooling constraint.
**Impact on plan:** The browser UAT success criteria are satisfied; Vitest runtime assertions should be rerun outside the sandbox when process spawning is available.

## Issues Encountered

- The in-app Browser could inspect the 3D DOM/accessibility state but screenshot capture and direct canvas readback timed out or returned unusable data in this run.
- The initial mobile screenshot revealed real scene clipping; the fix was to CSS-constrain the WebGL canvas and use aspect-aware camera distance.
- Direct WebGL `readPixels` produced zeroed samples in headless capture, so screenshot-crop statistics were used for nonblank proof.

## User Setup Required

None.

## Next Phase Readiness

Ready for 12-08. The remaining Phase 12 work can aggregate smoke/docs/fixture tests/UAT evidence and close the lightweight 3D preview MVP.

---
*Phase: 12-lightweight-3d-preview-mvp*
*Completed: 2026-06-19*
