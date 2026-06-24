---
phase: 21-real-generation-entry-and-artifact-preview
plan: 2
subsystem: api
tags: [fastapi, openapi, artifacts, object-storage]
requires:
  - phase: 3
    provides: durable artifact records and object storage keys
provides:
  - ArtifactResponse content_url
  - Workspace-scoped artifact content route
  - Regenerated TypeScript contracts
affects: [api, contracts, workbench-preview]
tech-stack:
  added: []
  patterns: [API streaming content route before presigned URL abstraction]
key-files:
  created:
    - scripts/patch-contract-binary-routes.mjs
  modified:
    - services/api/src/caragent_api/schemas.py
    - services/api/src/caragent_api/routes/jobs.py
    - services/api/tests/test_jobs.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts
    - packages/contracts/package.json
key-decisions:
  - "Use an API route as the first stable content_url implementation."
  - "Return 404 for missing artifacts and cross-workspace artifact content requests."
patterns-established:
  - "Artifact response helpers add derived content URLs at the route layer."
requirements-completed:
  - GENC-03
  - GENC-04
duration: completed-before-gsd-sync
completed: 2026-06-22
---

# Phase 21 Plan 02: Artifact Content API And Generated Contracts Summary

**Workspace-scoped artifact content streaming with generated OpenAPI and TypeScript contract support.**

## Performance

- **Duration:** completed before GSD execution sync
- **Started:** 2026-06-22T00:00:00+08:00
- **Completed:** 2026-06-22T12:00:00+08:00
- **Tasks:** 4
- **Files modified:** 6 modified, 1 created

## Accomplishments

- Added `ArtifactResponse.content_url`.
- Added `GET /workspaces/{workspace_id}/artifacts/{artifact_id}/content`.
- Returned artifact bytes with artifact/storage content type fallback.
- Added API coverage for content URL, byte streaming, and cross-workspace rejection.
- Regenerated OpenAPI and Orval TypeScript client output.
- Declared artifact content as binary media in OpenAPI so 200 responses are not advertised as JSON.
- Added a deterministic contracts post-generation patch so the artifact content client reads successful responses with `res.blob()` and error responses with `res.json()`.

## Task Commits

This execution was synchronized after implementation work had already been applied in the working tree. No per-task GSD commits were created during this fallback run.

## Files Created/Modified

- `services/api/src/caragent_api/schemas.py` - adds `content_url` to artifact responses.
- `services/api/src/caragent_api/routes/jobs.py` - derives content URLs and streams artifact bytes from object storage.
- `services/api/tests/test_jobs.py` - verifies content bytes, content type, and workspace scoping.
- `packages/contracts/openapi/openapi.json` - includes `content_url` and artifact content path.
- `packages/contracts/src/generated/client.ts` - generated client includes the new API surface and blob-aware artifact content implementation.
- `packages/contracts/package.json` - runs the binary-route patch after Orval generation.
- `scripts/patch-contract-binary-routes.mjs` - post-generation guard for the artifact content client operation.

## Decisions Made

- Prefer API streaming for v4 P0 so S3 presigned URLs can remain an implementation detail later.
- Keep object keys internal; browser clients discover content through `content_url`.

## Deviations from Plan

The implementation existed before this GSD execution pass, so the executor verified and documented the plan instead of making fresh code edits.

## Issues Encountered

Running `contracts:check` inside the sandbox triggered the script's fallback client generator and temporarily produced a health-only generated client. The client was restored by running the canonical API OpenAPI export from `services/api` and Orval generation with elevated permissions.

Code review found that Orval still parsed the binary artifact content operation as JSON even after Blob response types were generated. The route OpenAPI metadata, API test, and contracts generation script now guard that route as binary.

## User Setup Required

None.

## Next Phase Readiness

Phase 22 can extend this storage boundary into a shared API/Worker storage factory.

---
*Phase: 21-real-generation-entry-and-artifact-preview*
*Completed: 2026-06-22*
