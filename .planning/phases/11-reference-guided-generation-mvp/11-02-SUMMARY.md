---
phase: 11-reference-guided-generation-mvp
plan: "02"
subsystem: workbench-reference-ui
tags: [references, workbench, assets, rights, provider-warnings, vitest]

requires:
  - phase: 11-reference-guided-generation-mvp
    plan: "01"
    provides: typed reference role and reference usage contracts
provides:
  - Asset-row role controls for character, style, vehicle, logo, palette, and inspiration references
  - Rights-based reference generation eligibility in the asset library
  - Workbench structured `reference_usage` state with legacy `reference_asset_ids` compatibility
  - Parameter-panel reference summary, rights warning, and provider reference support display
affects:
  - workbench-asset-library
  - workbench-parameter-save
  - provider-capability-display
  - reference-guided-generation-payloads

tech-stack:
  added: []
  patterns:
    - workbench state stores structured reference assignments and derives legacy ids for compatibility
    - asset rows keep local rights form state while role/include state is owned by WorkbenchApp
    - provider reference capability metadata is normalized once in the operations API helper

key-files:
  created: []
  modified:
    - apps/web/src/components/workbench/asset-panel.tsx
    - apps/web/src/components/workbench/parameter-panel.tsx
    - apps/web/src/components/workbench/workbench-app.tsx
    - apps/web/src/lib/api/assets.ts
    - apps/web/src/lib/api/generation.ts
    - apps/web/src/lib/api/operations.ts
    - apps/web/src/app/page.test.tsx
    - apps/web/src/lib/api/assets.test.ts
    - apps/web/src/lib/api/generation.test.ts

key-decisions:
  - "Legacy `reference_asset_ids` are derived from enabled structured assignments and still sent with brief updates."
  - "Legacy briefs with only raw reference ids resume as enabled `inspiration` assignments."
  - "Missing-rights assets may have a role selected for organization, but cannot be enabled for generation."
  - "Provider reference support is displayed as accepted, prompt-only, or unsupported based on capability metadata."

patterns-established:
  - "`buildReferenceUsagePayload` returns both `reference_usage` and enabled legacy `reference_asset_ids`."
  - "`getReferenceEligibility` centralizes rights-based generation eligibility labels."
  - "`AssetPanel` role controls have accessible labels containing each asset filename."

requirements-completed:
  - V2-REF-01
  - V2-REF-02
  - V2-REF-04

duration: 16 min
completed: 2026-06-18
---

# Phase 11 Plan 02: Reference Role Workbench UI Summary

**Asset role assignment, rights eligibility, structured payload save, and provider reference summary**

## Performance

- **Duration:** 16 min
- **Completed:** 2026-06-18T22:22:10+08:00
- **Tasks:** 4
- **Files modified:** 9

## Accomplishments

- Added role controls in the asset list using the six Phase 11 labels: `角色`, `风格`, `车辆`, `Logo`, `配色`, `仅灵感`.
- Added rights-based eligibility badges and disabled generation include controls for assets without confirmed rights.
- Replaced flat selected-reference state as the primary workbench state with structured assignments shaped as `{assetId, role, enabled}`.
- Added parameter-panel reference summary with selected role counts, prompt-only provider note, unsupported-role warning, and rights warning.
- Added helper-level and page-level Vitest coverage for eligibility classification, structured payload creation, and UI save behavior.

## Task Commits

1. **Task 1: Add red workbench tests for role assignment and eligibility** - `b311ffa` (test)
2. **Tasks 2-4: Add structured state, asset controls, and parameter/provider warnings** - `e8cf4b8` (feat)

## Files Created/Modified

- `apps/web/src/lib/api/assets.ts` - Added reference eligibility helper and labels.
- `apps/web/src/lib/api/generation.ts` - Added role options, default legacy role, structured assignment draft type, and payload builder.
- `apps/web/src/lib/api/operations.ts` - Normalizes provider `reference_input` metadata for workbench display.
- `apps/web/src/components/workbench/workbench-app.tsx` - Owns structured reference assignments and derives legacy ids.
- `apps/web/src/components/workbench/asset-panel.tsx` - Adds role select, eligibility badges, and rights-gated include toggle.
- `apps/web/src/components/workbench/parameter-panel.tsx` - Adds reference summary, warning display, and structured save payload.
- `apps/web/src/app/page.test.tsx` - Covers role assignment, missing-rights blocking, and structured save payload.
- `apps/web/src/lib/api/assets.test.ts` and `apps/web/src/lib/api/generation.test.ts` - Cover helper behavior.

## Decisions Made

- The default role for legacy raw ID references is `inspiration`, because it is the least presumptive guidance mode.
- Missing-rights assets stay visible and role-assignable for organization, but `enabled` cannot be toggled until rights are confirmed.
- Reference role/provider warnings are shown in the existing parameter panel instead of creating a new workflow surface.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Vitest needed unsandboxed execution**
- **Found during:** Task 1 RED verification and GREEN verification
- **Issue:** Sandbox blocked Vite/esbuild child process startup with `spawn EPERM`.
- **Fix:** Reran the focused Vitest command with sandbox escalation.
- **Verification:** `corepack pnpm --dir apps/web exec vitest --run src/app/page.test.tsx src/lib/api/generation.test.ts src/lib/api/assets.test.ts` passed.

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope change. The focused frontend test suite was verified with the real Vitest runtime.

## Issues Encountered

- `corepack pnpm --filter @caragent/web exec vitest ...` did not resolve the Vitest binary in this Windows shell. `corepack pnpm --dir apps/web exec vitest ...` worked after escalation.
- Existing legacy reference save test needed its expected patch body updated to include structured `reference_usage` alongside legacy ids.

## Verification

- `corepack pnpm --dir apps/web exec vitest --run src/app/page.test.tsx src/lib/api/generation.test.ts src/lib/api/assets.test.ts` - passed, 38 tests.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `git diff --check` - passed.

## User Setup Required

None - no API server or provider credentials required for the tested workbench behavior.

## Next Phase Readiness

Ready for `11-03-PLAN.md`: prompt planning can now consume structured `reference_usage` submitted from the workbench and convert provider capability gaps into warnings.

---
*Phase: 11-reference-guided-generation-mvp*
*Completed: 2026-06-18*
