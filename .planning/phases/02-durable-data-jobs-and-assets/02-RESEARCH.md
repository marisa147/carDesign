# Phase 2: Durable Data, Jobs, And Assets - Research

**Date:** 2026-06-17
**Status:** Complete

## Goal

Research what must be true before planning Phase 2 well: durable product state, database and object-storage integration, idempotent jobs, generated API contracts, worker state updates, and a minimal frontend proof that survives refreshes.

## Current Foundation

- The repo already has separate `apps/web`, `services/api`, `services/worker`, `packages/contracts`, and `infra` boundaries.
- FastAPI/Pydantic owns OpenAPI; generated TypeScript contracts are committed and checked.
- Docker Compose provides PostgreSQL, Redis, and MinIO.
- API and worker are independent Python projects managed by `uv`.
- Existing root validation checks web, contracts, API, worker, env examples, contracts drift, and local smoke.

## Technical Findings

### Shared Data Core

Phase 2 needs both API and worker to update/read durable job state without the worker importing FastAPI routers. The cleanest path is a small shared Python package, for example `services/core`, exposing:

- SQLAlchemy metadata and models.
- Async database engine/session helpers.
- Repository/service functions for workspaces, assets, jobs, events, versions, artifacts, model runs, feedback, and exports.
- Object-storage key helpers and a thin S3/MinIO client.
- Pydantic-free domain enums where practical, with API schemas defined in `services/api`.

The API and worker can depend on this package via local `uv` path dependencies. Root validation must include core lint/type/test once it exists.

### Database And Migrations

Use SQLAlchemy 2 async patterns with Alembic migrations. PostgreSQL remains the production/local target. Tests can use SQLite with `aiosqlite` for fast repository coverage where behavior is portable, while Docker smoke should exercise PostgreSQL for integration confidence.

Migration ownership should live with the API/control plane, because API deployment controls schema compatibility. Alembic `env.py` can import `caragent_core.models.metadata`.

Important planning constraints:

- Use UUID primary keys for externally visible product records.
- Add explicit timestamps and status enums.
- Add uniqueness constraints for idempotency keys and immutable object keys.
- Add indexes for workspace resume, job status polling, and event ordering.
- Keep raw binary data out of PostgreSQL.

### Product Ledger Schema

The minimal Phase 2 ledger should include:

- `workspaces`: resume boundary, display name/status, future owner field, created/updated timestamps.
- `messages`: workspace conversation history, role, content, metadata, ordering.
- `design_briefs`: structured brief payloads linked to workspace and optionally message/job.
- `assets`: uploaded references/logos/car photos/inspiration items, media metadata, object key, checksum, thumbnail key, rights/source state.
- `generation_jobs`: durable job state machine, idempotency key, requested operation, cost fields, latest error, timestamps.
- `job_events`: append-only status/progress/user-message audit trail.
- `design_versions`: immutable version/lineage records with parent-child support.
- `artifacts`: immutable object records for uploads, thumbnails, generated images, previews, and exports.
- `model_runs`: provider/model/parameter/cost trace rows, nullable until real provider integration.
- `feedback`: rating/approval/comment records linked to design versions.
- `exports`: concept export records linked to versions/artifacts.

### Object Storage

MinIO/S3 should store file payloads. PostgreSQL should store metadata and object keys. Phase 2 can keep uploads API-mediated because it is simpler and keeps validation/rights metadata authoritative.

Recommended key shape:

`workspaces/{workspace_id}/{kind}/{record_id}/{safe_filename}`

Do not overwrite keys. New upload, thumbnail, generated output, preview, or export means a new artifact/asset/export record and a new object key.

Validation should check declared content type, extension, byte size, and image decode for supported image types when practical. Rights/source metadata should be explicit and required before assets can be used by generation/export paths.

### API Contracts

FastAPI routes should remain narrow and typed:

- `POST /workspaces`
- `GET /workspaces/{workspace_id}`
- `GET /workspaces/{workspace_id}/messages`
- `POST /workspaces/{workspace_id}/messages`
- `POST /workspaces/{workspace_id}/briefs`
- `GET /workspaces/{workspace_id}/briefs`
- `POST /workspaces/{workspace_id}/assets`
- `PATCH /assets/{asset_id}/rights`
- `GET /workspaces/{workspace_id}/assets`
- `POST /workspaces/{workspace_id}/jobs`
- `GET /workspaces/{workspace_id}/jobs`
- `GET /jobs/{job_id}`
- `GET /jobs/{job_id}/events`
- `GET /workspaces/{workspace_id}/versions`
- `GET /workspaces/{workspace_id}/artifacts`

Export, feedback, and model-run records can have minimal create/list/read routes if needed for DATA-02 coverage, but rich UI behavior remains later.

Because Phase 1 CORS allowed only `GET`, Phase 2 must expand allowed methods to support `POST` and `PATCH`.

### Worker Semantics

Worker tasks should update durable job/event records through shared core services. A local no-provider simulation task can:

1. Claim a queued job.
2. Append a `running` event.
3. Create a local simulation model-run record and optional local simulation artifact/version.
4. Mark the job `succeeded` or `failed`.

This proves the durable state path without implying real design generation. Real provider adapters stay in Phase 3.

### Frontend Proof

Phase 2 should not build the full GPT-style workbench. It only needs a small persistence/status proof:

- Create or resume a workspace ID.
- Create a message/brief or show stored conversation count.
- Create a simulated job with an idempotency key.
- Display status/events using generated contract types.
- Keep enough local storage to remember the workspace ID, but fetch all canonical state from the API after refresh.

### Security And Reliability Notes

- Uploaded files are untrusted input; enforce type/size validation and never reflect object keys as raw HTML.
- Do not expose S3 credentials to the browser in Phase 2.
- Idempotency keys must be scoped to workspace and operation, not global across all users forever.
- Database errors should not leak connection strings or secrets.
- Cost fields are informational and nullable until provider integration.

## Validation Architecture

Phase 2 requires these validation dimensions:

1. Migration/schema validity: metadata imports, Alembic upgrade, constraints exist.
2. Repository/service behavior: create/resume workspace, persist message/brief, list by workspace.
3. Upload/object behavior: validation rejects unsupported input, object keys are immutable, rights metadata is required.
4. Job/idempotency behavior: duplicate keys return the original job and do not create duplicate rows.
5. Event behavior: append-only event ordering and status reads survive process boundaries.
6. Contract behavior: OpenAPI and generated TypeScript client are current.
7. Frontend behavior: refresh/resume proof reads durable API state.
8. Smoke behavior: Docker-backed PostgreSQL/MinIO path works locally.

## Risks

- Adding persistence directly inside route handlers would make worker reuse and tests brittle.
- Adding worker imports from `caragent_api` would violate the established boundary test.
- Building full upload/workbench UI in this phase would steal Phase 4 scope.
- Treating Redis/Celery task state as source of truth would fail DATA-05.
- Storing raw binaries in PostgreSQL would fight the object-storage architecture.

## Research Complete

The phase should be planned around a shared data core, API-owned migrations, narrow typed route slices, API-mediated uploads, durable job/event semantics, generated contracts, a small frontend proof, and Docker-backed final smoke.
