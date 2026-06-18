---
phase: 12-lightweight-3d-preview-mvp
plan: "05"
subsystem: preview3d-screenshot-persistence
tags: [preview3d, screenshots, artifacts, api, contracts, web-capture]
requires:
  - phase: 12-lightweight-3d-preview-mvp
    plan: "04"
    provides: PreviewSpec-driven material plan and 3D preview UI
provides:
  - version-scoped 3D screenshot creation API
  - preview_3d_screenshot artifact persistence through object storage
  - generated TypeScript screenshot create contract
  - web capture wrapper and 3D panel save action
affects: [phase-12, api-contracts, web-preview, artifact-ledger]
tech-stack:
  added: []
  patterns:
    - JSON request carries base64 screenshot bytes; persisted artifact metadata omits base64/binary content
    - feature-flag-gated V2 API route
key-files:
  modified:
    - services/api/src/caragent_api/routes/jobs.py
    - services/api/src/caragent_api/schemas.py
    - services/api/tests/test_jobs.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts
    - apps/web/src/lib/api/iteration.ts
    - apps/web/src/lib/api/iteration.test.ts
    - apps/web/src/components/workbench/preview-3d-panel.tsx
key-decisions:
  - "Persist screenshot bytes only in object storage; metadata keeps camera, shell, source artifact, and warnings."
  - "Gate screenshot creation behind `V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED`."
  - "Use a version-scoped route so screenshot artifacts are always linked to the selected design version."
patterns-established:
  - "Preview3D screenshot metadata is validated through `Preview3DScreenshotArtifactMetadata` before artifact creation."
  - "Web screenshot creation uses generated URL contracts through the existing iteration API wrapper."
requirements-progress: ["V2-3D-03", "V2-3D-04"]
duration: 32 min
completed: 2026-06-18
---

# Phase 12 Plan 05 Summary

**Persisted 3D preview screenshots as durable version-linked artifacts**

## Performance

- **Duration:** 32 min
- **Started:** 2026-06-18T16:59:00Z
- **Completed:** 2026-06-18T17:31:00Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Added failing API tests for screenshot creation, feature flag gating, content-type validation, workspace/version ownership, and metadata without raw base64.
- Added `Preview3DScreenshotCreateRequest`.
- Added `POST /workspaces/{workspace_id}/versions/{version_id}/preview-3d-screenshots`.
- Stored screenshot bytes through object storage and created immutable `preview_3d_screenshot` artifacts linked to the selected version.
- Regenerated OpenAPI and TypeScript contracts with the screenshot create endpoint.
- Added web `createPreview3DScreenshot` wrapper and wired the 3D panel capture button to save screenshot artifacts.

## Task Commits

1. **Task 1: Add red API tests for screenshot persistence** - `cadb6cc` (test)
2. **Task 2: Implement screenshot API and generated contracts** - `8e5eb60` (feat)
3. **Task 3: Add red web wrapper test** - `7db4fcb` (test)
4. **Task 3: Wire web capture action and API wrapper** - `43a166b` (feat)

## Verification

- `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_generation.py` - passed, 38 tests.
- `cd services/api && uv run ruff check src tests/test_jobs.py tests/test_generation.py` - passed.
- `cd services/api && .\.venv\Scripts\mypy.exe src` - passed.
- `services\api\.venv\Scripts\python.exe -c "import json; from caragent_api.main import create_app; schema=create_app().openapi(); print(json.dumps(schema, indent=2, sort_keys=True))" > packages\contracts\openapi\openapi.json` - passed.
- `corepack pnpm --filter @caragent/contracts generate` - passed.
- `corepack pnpm --filter @caragent/contracts typecheck` - passed.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `git diff --check` - passed.

## Deviations from Plan

### Environment-limited Verification

**1. [Rule 3 - Blocking] Focused Vitest remains blocked by Windows sandbox process spawning**
- **Found during:** Task 3 verification
- **Issue:** `./node_modules/.bin/vitest.CMD --run src/lib/api/iteration.test.ts apps/web/src/app/page.test.tsx` fails while loading `vitest.config.ts` with `Error: spawn EPERM` from esbuild before tests execute.
- **Fix:** Used web typecheck and lint as available in-sandbox verification. The red typecheck captured the missing wrapper before implementation, and final typecheck/lint passed after implementation.
- **Files modified:** None for the environment issue.
- **Verification:** web typecheck and eslint passed.

### Contract Check Wrapper

**2. [Rule 3 - Blocking] `corepack pnpm contracts:check` wrapper remains unsuitable in this sandbox**
- **Issue:** Earlier Phase 12 verification showed the wrapper can fall back to a minimal client when child-process execution is blocked.
- **Fix:** Used direct OpenAPI export, direct Orval generation, and contracts typecheck.
- **Verification:** Generated endpoint/types are present and contracts typecheck passed.

---

**Total deviations:** 2 environment/tooling constraints.
**Impact on plan:** API behavior, generated contracts, and web type contracts are verified. Focused Vitest should be rerun outside the sandbox when process spawning is available.

## Issues Encountered

- None in product logic.

## User Setup Required

None.

## Next Phase Readiness

Ready for 12-06. The next plan can strengthen persistent warning labels, non-production copy, and safe-zone overlay compatibility.

---
*Phase: 12-lightweight-3d-preview-mvp*
*Completed: 2026-06-18*
