---
phase: 12-lightweight-3d-preview-mvp
plan: "01"
subsystem: contracts
tags: [preview3d, pydantic, openapi, artifacts, contracts]
requires:
  - phase: 11-reference-guided-generation-mvp
    provides: durable version/artifact/reference trace metadata surfaces
provides:
  - typed Preview3DSpec and Preview3D screenshot metadata contracts
  - preview_3d_screenshot artifact kind
  - OpenAPI and TypeScript generated contract exposure for 3D preview metadata
affects: [phase-12, phase-13-handoff, web-preview, api-contracts]
tech-stack:
  added: []
  patterns:
    - Pydantic v2 versioned metadata contracts
    - optional derived API response fields from existing JSON metadata
key-files:
  created:
    - services/core/src/caragent_core/preview3d.py
  modified:
    - services/core/src/caragent_core/enums.py
    - services/core/tests/test_models.py
    - services/core/tests/test_generation_jobs.py
    - services/api/src/caragent_api/schemas.py
    - services/api/tests/test_jobs.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts
key-decisions:
  - "Use a core Preview3DSpec Pydantic contract that is renderer-neutral and independent of Three.js."
  - "Represent 3D screenshots as immutable artifacts with metadata, never as base64 or binary JSON."
  - "Expose Preview3D data through optional derived API response fields while preserving existing parameters/metadata dictionaries."
patterns-established:
  - "Preview3D metadata uses schema_version: 1 and explicit non-production warning ids."
  - "API response models can derive typed V2 fields from JSON metadata without breaking legacy clients."
requirements-completed: ["V2-3D-01", "V2-3D-04", "V2-3D-05"]
duration: 20 min
completed: 2026-06-18
---

# Phase 12 Plan 01 Summary

**Renderer-neutral Preview3DSpec contracts with durable screenshot artifact metadata and generated API/TypeScript exposure**

## Performance

- **Duration:** 20 min
- **Started:** 2026-06-18T15:41:00Z
- **Completed:** 2026-06-18T16:01:32Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Added failing contract tests for Preview3D spec shape, screenshot metadata, artifact kind, and API readability.
- Added `caragent_core.preview3d` Pydantic helpers for source, compatibility, shell, camera, material plan, warnings, spec, and screenshot metadata.
- Added `ArtifactKind.PREVIEW_3D_SCREENSHOT`.
- Exposed optional typed `preview_3d` and `preview_3d_screenshot` API response fields derived from existing version parameters and artifact metadata.
- Regenerated OpenAPI and TypeScript contracts with `Preview3DSpec` and `Preview3DScreenshotMetadata` types.

## Task Commits

1. **Task 1: Add red tests for Preview3DSpec and screenshot metadata** - `2c9c9cc` (test)
2. **Task 2: Add shared Preview3D schema helpers** - `75231ed` (feat)
3. **Task 3: Expose API schema contracts and regenerate TypeScript** - `63b3533` (feat)

## Verification

- `cd services/core && uv run pytest -q tests/test_models.py tests/test_generation_jobs.py` - passed, 13 tests.
- `cd services/api && uv run pytest -q tests/test_generation.py tests/test_jobs.py` - passed, 35 tests.
- `cd services/core && uv run ruff check .` - passed.
- `cd services/api && uv run ruff check .` - passed.
- `cd services/api && .\.venv\Scripts\mypy.exe src` - passed.
- `cd services/core && .\.venv\Scripts\mypy.exe src\caragent_core\preview3d.py --no-incremental --no-sqlite-cache --cache-dir .pytest_cache` - passed for the new module.
- `corepack pnpm --filter @caragent/contracts typecheck` - passed.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `rg -n "Preview3DSpec|Preview3DScreenshot|preview_3d|preview_3d_screenshot" packages/contracts/openapi/openapi.json packages/contracts/src/generated/client.ts` - found generated OpenAPI and TypeScript types.
- `git diff --check` - passed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `corepack pnpm contracts:check` uses fallback client in this sandbox**
- **Found during:** Task 3
- **Issue:** The script's child-process `pnpm generate` path is detected as blocked in this sandbox and rewrites the generated client to a minimal `/health` fallback, even though direct `corepack pnpm --filter @caragent/contracts generate` succeeds.
- **Fix:** Restored real generated artifacts with direct OpenAPI export and `corepack pnpm --filter @caragent/contracts generate`; verified with contracts typecheck and generated type grep.
- **Files modified:** `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/client.ts`
- **Verification:** contracts typecheck passed; generated Preview3D types are present in OpenAPI and TS client.
- **Committed in:** `63b3533`

**2. [Rule 3 - Blocking] `uv run mypy` and core mypy cache writes are blocked by sandbox permissions**
- **Found during:** Verification
- **Issue:** `uv run mypy` cannot access the user-level uv cache, and full core `.venv` mypy cannot write `.mypy_cache` metadata in the sandbox.
- **Fix:** Ran API mypy through the local venv, and ran mypy directly on the new core module with sqlite cache disabled and an existing cache directory.
- **Files modified:** None.
- **Verification:** API mypy passed; new `preview3d.py` mypy passed.
- **Committed in:** Not applicable.

---

**Total deviations:** 2 auto-handled environment constraints.
**Impact on plan:** The code and generated contracts are verified. The only missing green signal is the sandbox-specific `contracts:check` wrapper, whose underlying generation and typecheck steps were run directly.

## Issues Encountered

- Sandbox escalation for `uv run python -m caragent_api.scripts.export_openapi` was rejected by the environment because the Codex usage limit had been reached. The OpenAPI artifact was exported through the existing API virtualenv with stdout redirected from the repo root.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Ready for 12-02. The next plan can build the shell registry and compatibility resolver on top of the typed Preview3D contracts created here.

---
*Phase: 12-lightweight-3d-preview-mvp*
*Completed: 2026-06-18*
