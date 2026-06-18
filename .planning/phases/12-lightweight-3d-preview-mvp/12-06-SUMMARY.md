---
phase: 12-lightweight-3d-preview-mvp
plan: "06"
subsystem: preview3d-warning-posture
tags: [preview3d, warnings, accessibility, screenshot-metadata, safe-zones]
requires:
  - phase: 12-lightweight-3d-preview-mvp
    plan: "04"
    provides: PreviewSpec-driven material plan and 3D preview UI
  - phase: 12-lightweight-3d-preview-mvp
    plan: "05"
    provides: preview_3d_screenshot artifact persistence
provides:
  - required Preview3D warning id helper
  - screenshot metadata recovery for concept-only and UV-not-verified warnings
  - accessible 3D panel region label for persistent non-production posture
  - compatible and fallback UI assertions for non-production labeling
affects: [phase-12, api-metadata, web-preview, accessibility]
tech-stack:
  added: []
  patterns:
    - API derives required screenshot warning ids from core contracts instead of trusting web payload completeness
    - 3D preview panel exposes persistent non-production semantics through visible copy and accessible region naming
key-files:
  modified:
    - services/core/src/caragent_core/preview3d.py
    - services/api/src/caragent_api/routes/jobs.py
    - services/api/tests/test_jobs.py
    - apps/web/src/components/workbench/preview-3d-panel.tsx
    - apps/web/src/app/page.test.tsx
key-decisions:
  - "Required 3D screenshot warnings are owned by core contracts and restored server-side."
  - "The 3D preview panel remains explicitly labeled as concept-only/non-production in both visible UI and accessible region naming."
patterns-established:
  - "Use `required_preview_3d_warning_ids()` when packaging metadata that must survive incomplete client payloads."
  - "Keep lightweight 3D UI labels independent from viewer readiness, fallback, and screenshot capture state."
requirements-progress: ["V2-3D-03", "V2-3D-04", "V2-3D-05"]
duration: 22 min
completed: 2026-06-18
---

# Phase 12 Plan 06 Summary

**Hardened 3D preview warnings and non-production labeling**

## Performance

- **Duration:** 22 min
- **Started:** 2026-06-18T17:31:00Z
- **Completed:** 2026-06-18T17:53:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added a failing API regression test proving screenshot metadata restores required warnings when `preview_3d.warnings` is empty.
- Added `REQUIRED_PREVIEW_3D_WARNING_IDS` and `required_preview_3d_warning_ids()` in core Preview3D contracts.
- Updated screenshot artifact metadata creation to always store `non_production_preview` and `uv_not_verified` warning ids.
- Added an accessible region label to the 3D preview panel so non-production posture persists across compatible and fallback states.
- Strengthened page tests to assert the labeled 3D preview region in both compatible and incompatible shell paths.

## Task Commits

1. **Task 1: Add red warning metadata test** - `ad47071` (test)
2. **Tasks 2-3: Implement warning metadata and UI label hardening** - `7e149c5` (feat)

## Verification

- `cd services/api && uv run pytest -q tests/test_jobs.py` - passed, 13 tests.
- `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_generation.py` - passed, 39 tests with existing aiosqlite thread-close warnings.
- `cd services/api && uv run ruff check src tests/test_jobs.py tests/test_generation.py` - passed.
- `cd services/api && .\.venv\Scripts\mypy.exe src` - passed.
- `cd services/core && .\.venv\Scripts\mypy.exe src\caragent_core\preview3d.py --no-incremental --no-sqlite-cache --cache-dir .pytest_cache` - passed.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `git diff --check` - passed.

## Deviations from Plan

### Environment-limited Verification

**1. [Rule 3 - Blocking] Focused Vitest remains blocked by Windows sandbox process spawning**
- **Found during:** Task 3 verification
- **Issue:** `corepack pnpm --filter @caragent/web test` fails while loading `vitest.config.ts` with `Error: spawn EPERM` from esbuild before tests execute.
- **Fix:** Used web typecheck and lint as available in-sandbox verification. The UI assertions were added but should be rerun outside the sandbox when process spawning is available.
- **Files modified:** None for the environment issue.
- **Verification:** web typecheck and eslint passed.

---

**Total deviations:** 1 environment/tooling constraint.
**Impact on plan:** API warning metadata behavior is verified. UI type/lint verification passed, but Vitest runtime assertions remain pending outside the sandbox.

## Issues Encountered

- `uv run pytest` needed elevated execution because the sandbox cannot access `C:\Users\25858\AppData\Local\uv\cache`.
- The combined API test suite emitted existing aiosqlite thread-close warnings while still passing.

## User Setup Required

None.

## Next Phase Readiness

Ready for 12-07. The next plan can perform browser desktop/mobile performance and accessibility checks for the 3D preview workflow.

---
*Phase: 12-lightweight-3d-preview-mvp*
*Completed: 2026-06-18*
