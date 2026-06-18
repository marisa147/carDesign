---
phase: 10-targeted-regeneration-and-masked-editing-mvp
plan: "07"
subsystem: targeted-edit-comparison-ui
tags: [targeted-edit, comparison, workbench, metadata, region-highlight]

requires:
  - phase: 10-targeted-regeneration-and-masked-editing-mvp
    plan: "05"
    provides: durable targeted edit route and lineage evidence
  - phase: 10-targeted-regeneration-and-masked-editing-mvp
    plan: "06"
    provides: retry-safe targeted edit diagnostics and route metadata
provides:
  - Targeted child comparison mode in workbench state
  - Version history affordance for comparing targeted edit children with parents
  - Metadata-backed route, target, prompt delta, provider/model/cost evidence
  - Normalized changed-region highlight without pixel-diff claims
affects:
  - workbench-preview-panel
  - workbench-comparison-panel
  - targeted-edit-history-ui
  - V2-EDIT-05

tech-stack:
  added: []
  patterns:
    - targeted comparison is driven by durable DesignVersion parameters
    - version history exposes comparison only for targeted child versions
    - changed-region UI renders normalized edit metadata and avoids pixel-perfect diff claims

key-files:
  created:
    - .planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-07-SUMMARY.md
  modified:
    - apps/web/src/lib/workbench/store.ts
    - apps/web/src/lib/workbench/store.test.ts
    - apps/web/src/components/workbench/preview-panel.tsx
    - apps/web/src/components/workbench/comparison-panel.tsx
    - apps/web/src/app/page.test.tsx
    - .planning/ROADMAP.md
    - .planning/STATE.md
    - .planning/REQUIREMENTS.md

key-decisions:
  - "Targeted comparison reads existing version parameters instead of adding a new API surface."
  - "Only child versions with targeted edit metadata expose a version-history compare button."
  - "Changed-region highlighting is explicitly metadata-backed and does not claim pixel-perfect visual diffing."

patterns-established:
  - "Comparison state stores the selected child id locally and clears when the user makes a normal version selection."
  - "Comparison metadata is parsed defensively from top-level version parameters, edit_intent, or prompt_payload.mask_edit."
  - "Provider evidence is shown only from sanitized public version parameters."

requirements-completed:
  - V2-EDIT-05

duration: 13 min
completed: 2026-06-18
---

# Phase 10 Plan 07: Targeted Edit Comparison Summary

**Workbench users can compare targeted edit children against parents with route evidence and metadata-backed region highlights**

## Performance

- **Duration:** 13 min
- **Started:** 2026-06-18T13:10:59Z
- **Completed:** 2026-06-18T13:23:42Z
- **Tasks:** 4
- **Files modified:** 8

## Accomplishments

- Added local workbench comparison state for selected targeted child versions.
- Added version-history compare controls only for targeted edit children with parent lineage and edit metadata.
- Upgraded the comparison panel to show parent/child titles, route labels, raw route id, selected target, prompt delta, changed fields, mask id, provider, model, and cost when available.
- Added a compact normalized region highlight that is explicitly labeled as metadata-backed, not a pixel diff.
- Covered deterministic recomposition, provider masked generation, and missing-parent fallback behavior in web tests.

## Task Commits

1. **Tasks 1-4: Add targeted comparison state, history affordance, and metadata-backed comparison UI** - pending current commit.

## Files Created/Modified

- `apps/web/src/lib/workbench/store.ts` - Adds targeted comparison mode and selected child id state.
- `apps/web/src/lib/workbench/store.test.ts` - Verifies comparison state and reset behavior.
- `apps/web/src/components/workbench/preview-panel.tsx` - Adds targeted-child compare affordances in version history and clears invalid comparison state.
- `apps/web/src/components/workbench/comparison-panel.tsx` - Renders targeted edit comparison details and changed-region highlight from metadata.
- `apps/web/src/app/page.test.tsx` - Covers recomposition/provider comparison UI and missing parent fallback.
- `.planning/ROADMAP.md` - Marks 10-07 complete and advances Phase 10 progress.
- `.planning/STATE.md` - Advances current position to 10-08.
- `.planning/REQUIREMENTS.md` - Marks V2-EDIT-05 complete.

## Decisions Made

- Comparison remains metadata-first: no new endpoint or image diff pipeline was added.
- Version history keeps the normal version selection path intact; targeted comparison is a separate icon button.
- Provider/model/cost display is limited to public version parameter fields already exposed through the existing jobs/version APIs.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Vitest command needed web workspace execution**
- **Found during:** Task 1 red test verification
- **Issue:** `corepack pnpm --filter @caragent/web exec vitest ...` and sandboxed `--dir` execution did not resolve the local Vitest binary on Windows.
- **Fix:** Ran focused Vitest with `corepack pnpm --dir apps/web exec vitest ...` under sandbox escalation.
- **Verification:** Focused web and store tests passed, 34 tests.

**2. [Rule 3 - Blocking] TypeScript needed explicit Record narrowing**
- **Found during:** Verification
- **Issue:** TypeScript would not treat a generic `object` as `Record<string, unknown>` in comparison metadata parsing.
- **Fix:** Added an explicit cast inside the defensive `asRecord` helper.
- **Verification:** Web typecheck passed.

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** No scope expansion. The UI still avoids pixel-diff claims and uses existing metadata only.

## Issues Encountered

- None beyond the auto-fixed verification/tooling issues above.

## Verification

- `corepack pnpm --dir apps/web exec vitest --run src/lib/workbench/store.test.ts src/app/page.test.tsx` - passed with unsandboxed execution, 34 tests.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `corepack pnpm contracts:check` - passed; contract artifacts are current.
- `git diff --check` - passed.

## User Setup Required

None.

## Next Phase Readiness

Ready for `10-08-PLAN.md`: Phase 10 has comparison UI coverage and can move into smoke, docs, regression validation, and Browser UAT.

---
*Phase: 10-targeted-regeneration-and-masked-editing-mvp*
*Completed: 2026-06-18*
