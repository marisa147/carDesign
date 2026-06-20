# Plan 19.02 Summary: Version-Scoped Preflight API And Durable Report Artifact

## Result

Completed. The API can create a version-scoped production readiness preflight and persist the generated JSON as an immutable export artifact plus export ledger row.

## Evidence

- Added `POST /workspaces/{workspace_id}/versions/{version_id}/production-readiness-preflight`.
- The route writes `production-readiness-preflight.json` to object storage with checksum and `application/json` content type.
- The route records `production_readiness_preflight` exports with succeeded status and report manifest.
- The endpoint can still return a report when the version has no generated concept image, recording `concept_image` as a blocker.

## Files

- `services/api/src/caragent_api/routes/jobs.py`
- `services/api/src/caragent_api/schemas.py`
- `services/api/tests/test_jobs.py`
- `packages/contracts/openapi/openapi.json`
- `packages/contracts/src/generated/client.ts`

