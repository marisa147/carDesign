---
phase: 05-iteration-feedback-and-concept-export
plan: "03"
subsystem: contracts-frontend-api
tags: [openapi, orval, contracts, nextjs, api-wrappers, query-keys]

requires:
  - phase: "05-01"
    provides: feedback and concept export create routes
  - phase: "05-02"
    provides: child iteration submission route
provides:
  - refreshed OpenAPI artifact
  - regenerated TypeScript contract client
  - frontend iteration API wrappers
  - frontend feedback/export wrappers
  - expanded generation state loading
  - Phase 5 query keys
affects: [phase-05-04-lineage-ui, phase-05-05-feedback-ui, phase-05-06-export-ui]

tech-stack:
  patterns:
    - OpenAPI exports come from `caragent_api.scripts.export_openapi`
    - generated TypeScript client is produced by Orval in `@caragent/contracts`
    - web API wrappers keep `apiBaseUrl`, `fetch`, and `signal` options consistent
    - wrapper tests assert generated URLs, methods, bodies, and error messages

key-files:
  modified:
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts
    - apps/web/src/lib/api/generation.ts
    - apps/web/src/lib/api/generation.test.ts
    - apps/web/src/lib/api/iteration.ts
    - apps/web/src/lib/api/iteration.test.ts
    - apps/web/src/lib/workbench/query-keys.ts
    - apps/web/src/lib/workbench/store.test.ts
    - apps/web/src/app/page.test.tsx

key-decisions:
  - "Phase 5 wrappers live in `apps/web/src/lib/api/iteration.ts` while generation state loading remains in `generation.ts`."
  - "`loadGenerationState` now includes workspace feedback and exports alongside job, events, artifacts, and versions."
  - "Query keys now include `feedback`, `exports`, and version-scoped `iteration` entries."

patterns-established:
  - "Phase-specific web wrappers use generated URL helpers but expose short domain names to UI code."
  - "Page tests must mock feedback/export reads when resuming a generation state."

requirements-completed:
  - ITER-01
  - ITER-04
  - ITER-05

duration: 30 min
completed: 2026-06-17
---

# Phase 5 Plan 03: Contracts And Frontend API Wrappers Summary

OpenAPI contracts are refreshed and the web app now has typed wrappers for Phase 5 iteration, feedback, and concept export surfaces.

## Accomplishments

- Exported updated FastAPI OpenAPI schema after adding Phase 5 backend routes.
- Regenerated the Orval TypeScript client.
- Added `apps/web/src/lib/api/iteration.ts` with wrappers for child iteration submission, feedback creation, concept export creation, and feedback/export listing.
- Expanded `loadGenerationState` to include workspace feedback and export records.
- Added query keys for feedback, exports, and version-scoped iteration requests.
- Updated page tests to mock the expanded generation state contract.

## Deviations from Plan

- None.

## Verification

- RED: focused web tests failed because `iteration.ts` was missing, generation state did not include feedback/export, and query keys were not defined.
- GREEN: `corepack pnpm --filter @caragent/web test -- iteration.test.ts generation.test.ts store.test.ts` passed, 7 files and 35 tests.
- `corepack pnpm contracts:check` passed.
- `corepack pnpm --filter @caragent/web typecheck` passed.
- `corepack pnpm --filter @caragent/web lint` passed.
- `corepack pnpm --filter @caragent/contracts typecheck` passed.
- `corepack pnpm --filter @caragent/web test` passed, 7 files and 35 tests.

## Next Plan Readiness

Ready for `05-04`: workbench lineage, comparison, and child iteration controls can consume the new wrappers/query keys.
