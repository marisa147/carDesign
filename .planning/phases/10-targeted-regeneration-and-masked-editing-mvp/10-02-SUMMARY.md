---
phase: 10-targeted-regeneration-and-masked-editing-mvp
plan: "02"
subsystem: web-workbench
tags: [targeted-edit, workbench, preview-spec, mask-preview, iteration-payload]

requires:
  - phase: 10-targeted-regeneration-and-masked-editing-mvp
    plan: "01"
    provides: typed EditIntent contract and iteration request field
provides:
  - Workbench-local targeted edit draft state
  - PreviewSpec safe-zone and overlay-layer selection controls
  - Visible selected-region mask preview
  - Version-scoped targeted edit payload builder for child iterations
affects:
  - workbench-target-selection
  - child-iteration-submit
  - phase-10-worker-recomposition
  - provider-mask-routing

tech-stack:
  added: []
  patterns:
    - targeted edit state remains synchronous UI state in the Zustand workbench store
    - selectable regions are derived from the selected version PreviewSpec
    - incomplete targeted-edit drafts fail locally before API submission

key-files:
  created:
    - .planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-02-SUMMARY.md
  modified:
    - apps/web/src/lib/workbench/store.ts
    - apps/web/src/lib/workbench/store.test.ts
    - apps/web/src/components/workbench/preview-panel.tsx
    - apps/web/src/components/workbench/workbench-app.tsx
    - apps/web/src/app/page.test.tsx

key-decisions:
  - "Use existing PreviewSpec safe zones and overlay layers as the first MVP target model."
  - "Clear selected target, prompt delta, route preference, and mask preview when the selected version changes."
  - "Build the initial mask reference from the selected generated artifact metadata instead of creating binary masks in the browser."

patterns-established:
  - "Non-targeted child iterations omit `edit_intent` entirely."
  - "Targeted child iterations include `schema_version`, target, normalized rectangle region, prompt delta, parent version id, route preference, and mask artifact metadata."
  - "Page tests reset the workbench store between cases to avoid cross-test UI state leakage."

requirements-advanced:
  - V2-EDIT-01
  - V2-EDIT-02

duration: 45 min
completed: 2026-06-18
---

# Phase 10 Plan 02: Workbench Target Selection Summary

**PreviewSpec-derived target selection, mask preview, and typed targeted-edit child iteration submissions**

## Performance

- **Duration:** 45 min
- **Completed:** 2026-06-18T12:25:39Z
- **Tasks:** 4
- **Files modified:** 5

## Accomplishments

- Extended the workbench store with targeted edit mode, selected target, prompt delta, route preference, mask preview visibility, and deterministic reset behavior.
- Made PreviewSpec safe zones and overlay layers selectable in local edit mode, with accessible labels and a visible mask-region highlight.
- Wired targeted edit metadata into the existing child iteration submit path while preserving the normal non-targeted iteration payload.
- Added page and store regression coverage for stale target clearing, mask preview toggling, safe-zone and overlay-layer selection, and request payload shape.

## Task Commits

1. **Tasks 1-4: Add workbench target selection, mask preview, and submit payload** - pending current commit.

## Files Created/Modified

- `apps/web/src/lib/workbench/store.ts` - Added targeted edit UI state and reset actions.
- `apps/web/src/lib/workbench/store.test.ts` - Covers targeted edit draft state and stale target clearing.
- `apps/web/src/components/workbench/preview-panel.tsx` - Adds edit mode, selectable PreviewSpec targets, selected target summary, and mask preview overlay.
- `apps/web/src/components/workbench/workbench-app.tsx` - Builds typed `edit_intent` payloads for targeted child iterations and blocks incomplete drafts locally.
- `apps/web/src/app/page.test.tsx` - Adds workbench-level targeted edit flow coverage and isolates store state between page tests.

## Decisions Made

- Region selection is limited to normalized rectangle regions from PreviewSpec safe zones for this plan.
- Overlay layers inherit their region from their associated safe zone; missing zones fall back to a small stable rectangle rather than throwing.
- Route preference defaults to `deterministic_recomposition`; real provider-mask routing remains later Phase 10 work.
- Browser mask preview is metadata-only in this plan; no binary mask artifact is generated client-side.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Vitest needed a package-local command and unsandboxed execution**
- **Found during:** Task 1/verification
- **Issue:** `corepack pnpm --filter @caragent/web exec vitest ...` did not resolve the package-local `vitest` binary, and the package script hit Windows `spawn EPERM` when esbuild started inside the sandbox.
- **Fix:** Used `corepack pnpm --dir apps/web exec vitest ...` with sandbox escalation for focused web tests.
- **Verification:** Target page and store tests passed, 30 tests.

**2. [Rule 3 - Blocking] Page tests leaked Zustand UI state across cases**
- **Found during:** Task 3 targeted edit RED/GREEN loop
- **Issue:** A prior preview test could leave `showSafeZones` enabled, causing the targeted edit test to toggle it off.
- **Fix:** Reset `useWorkbenchStore` in the page test `afterEach` and wrap the reset in `act`.
- **Verification:** Target page and store tests passed without act warnings.

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** No scope change. Verification command and test isolation are now documented for later web work.

## Issues Encountered

- The plan listed `parameter-panel.tsx` and `lib/api/iteration.ts` as possible touch points, but the existing iteration client already accepted the generated request type and no parameter panel changes were required.
- Overlay-layer controls initially rendered as buttons even outside edit mode; adjusted so they are focusable only when they are actionable.

## Verification

- `corepack pnpm --dir apps/web exec vitest --run src/app/page.test.tsx src/lib/workbench/store.test.ts` - passed with unsandboxed execution, 30 tests.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `git diff --check` - passed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for `10-03-PLAN.md`: worker-side deterministic recomposition can now consume typed targeted edit metadata submitted by the workbench.

---
*Phase: 10-targeted-regeneration-and-masked-editing-mvp*
*Completed: 2026-06-18*
