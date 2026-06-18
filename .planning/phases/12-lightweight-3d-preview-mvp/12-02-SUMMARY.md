---
phase: 12-lightweight-3d-preview-mvp
plan: "02"
subsystem: preview3d-compatibility
tags: [preview3d, shell-registry, compatibility, web-helpers, fallback]
requires:
  - phase: 12-lightweight-3d-preview-mvp
    plan: "01"
    provides: typed Preview3DSpec contracts and generated TypeScript exposure
provides:
  - generic-side-coupe-lightweight-v1 shell registry
  - core PreviewSpec-to-Preview3DSpec resolver with explicit incompatible fallback
  - web-side pure compatibility helpers for selected version/artifact data
affects: [phase-12, web-preview, preview3d-contracts]
tech-stack:
  added: []
  patterns:
    - small allowlist registry for template/view compatibility
    - pure frontend helper layer before rendering Three.js
key-files:
  created:
    - apps/web/src/lib/preview3d/shells.ts
    - apps/web/src/lib/preview3d/spec.ts
  modified:
    - services/core/src/caragent_core/preview3d.py
    - services/core/tests/test_generation_jobs.py
    - apps/web/src/app/page.test.tsx
key-decisions:
  - "Use `generic-side-coupe-lightweight-v1` as the first inspectable lightweight shell fixture linked to `generic-side-coupe` and `side` view."
  - "Unsupported template/view pairs produce an explicit incompatible Preview3DSpec instead of throwing."
  - "Frontend computes compatibility through pure helpers before adding any Three.js render surface."
patterns-established:
  - "Preview3D shell compatibility is a small allowlist keyed by template id and view."
  - "Projection overlays preserve PreviewSpec records and add `side-decal-plane` as the default material slot."
requirements-progress: ["V2-3D-01", "V2-3D-05"]
duration: 16 min
completed: 2026-06-18
---

# Phase 12 Plan 02 Summary

**Registered the first lightweight 3D shell and deterministic compatibility resolver**

## Performance

- **Duration:** 16 min
- **Started:** 2026-06-18T16:02:00Z
- **Completed:** 2026-06-18T16:18:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added red tests for resolving `generic-side-coupe-lightweight-v1` from current PreviewSpec fixture data and for returning an explicit fallback for unknown templates.
- Added core shell registry, default camera preset, material-slot projection, and `build_preview_3d_spec`.
- Added web `preview3d` helpers that derive compatibility from selected version/artifact data or existing generated `preview_3d` contract data.
- Kept unsupported templates on the 2D fallback path with a stable Chinese fallback message for UI tests.

## Task Commits

1. **Task 1: Add red compatibility tests** - `3345343` (test)
2. **Task 2: Implement core shell registry** - `4d04081` (feat)
3. **Task 3: Add web spec and shell helpers** - `377145e` (feat)
4. **Lint follow-up** - `7bc78d7` (fix)

## Verification

- `cd services/core && uv run pytest -q tests/test_generation_jobs.py` - passed, 6 tests.
- `cd services/core && uv run ruff check src tests/test_generation_jobs.py` - passed.
- `cd services/core && .\.venv\Scripts\mypy.exe src\caragent_core\preview3d.py --no-incremental --no-sqlite-cache --cache-dir .pytest_cache` - passed.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `git diff --check` - passed.

## Deviations from Plan

### Environment-limited Verification

**1. [Rule 3 - Blocking] Focused Vitest is blocked by Windows sandbox process spawning**
- **Found during:** Task 1 and final verification
- **Issue:** `./node_modules/.bin/vitest.CMD --run src/app/page.test.tsx` fails while loading `vitest.config.ts` with `Error: spawn EPERM` from esbuild. A later escalation attempt was rejected by the environment because the Codex usage limit had been reached.
- **Fix:** Used web typecheck as the available in-sandbox frontend verification. The initial red typecheck proved the missing helper module, and the final typecheck passed after implementation.
- **Files modified:** None for the environment issue.
- **Verification:** Core tests/ruff/mypy passed; web typecheck passed.

---

**Total deviations:** 1 environment-limited test runner.
**Impact on plan:** Core compatibility behavior is tested directly, and frontend helper contracts typecheck. Focused page Vitest still needs a non-sandbox run when process spawning is available.

## Issues Encountered

- None in product logic. The only blocker was the sandbox's Vitest/esbuild `spawn EPERM` behavior.

## User Setup Required

None.

## Next Phase Readiness

Ready for 12-03. The next plan can render a client-only 3D preview scaffold using the shell/spec helpers and tested 2D fallback state.

---
*Phase: 12-lightweight-3d-preview-mvp*
*Completed: 2026-06-18*
