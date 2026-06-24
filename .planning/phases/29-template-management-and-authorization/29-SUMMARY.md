# Phase 29 Summary: Template Management And Authorization

## Status

Complete.

## Delivered

- Added `POST /templates/validate-package` for zip-based template package validation without registering uploaded packages.
- Added structured validation schemas with accepted state, checked files, source class, authorization metadata, and path-specific issues.
- Validates package safety, required JSON files, manifest fields, view asset references, PNG/SVG asset extensions, dimensions, export config, and authorization fields including file reference, scope, expiration, commercial-use flag, reviewer, and version history.
- Added `/settings/templates` page for installed template inspection, source class visibility, authorization details, and upload validation results.
- Added frontend template validation API helper and focused tests for API helper/page behavior.
- Exported OpenAPI and manually aligned generated contract types/route helper for the new validation endpoint because the local Orval/Corepack toolchain remains blocked.

## Verification

Passed:

- `cd services/api && uv run pytest -q tests/test_templates.py`
- `cd services/api && uv run pytest -q tests/test_openapi_export.py`
- `cd services/api && uv run ruff check src tests/test_templates.py`
- `cd services/api && uv run mypy src`
- `packages\contracts\node_modules\.bin\tsc.CMD --project packages\contracts\tsconfig.json --noEmit`
- `apps\web\node_modules\.bin\tsc.CMD --noEmit -p apps\web\tsconfig.json`

Blocked by local test runtime:

- `cd apps/web && node_modules\.bin\vitest.CMD run src\lib\api\templates.test.ts src\app\settings\templates\page.test.tsx`
- Sandboxed run fails with `spawn EPERM`.
- Elevated run reaches Vitest but fails before collecting tests with the existing jsdom/CSS dependency `ERR_REQUIRE_ESM` issue from `@asamuzakjp/css-color` requiring `@csstools/css-calc` ESM.

## Requirements Closed

- TMPL-01: Template management page lists installed package details.
- TMPL-02: Users can upload a zip containing SVG/PNG/JSON assets and see validation results.
- TMPL-03: Authorization status displays source, file reference, scope, expiration, commercial-use flag, reviewer, and version history.
- TMPL-04: UI distinguishes maintained internal, user-provided, third-party authorized, and reference-only template classes.

## Next

Phase 30 Construction Brief And Smart Q&A.
