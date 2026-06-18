# Phase 2: Durable Data, Jobs, And Assets - Context

**Gathered:** 2026-06-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 makes the product ledger durable before the project spends time or money on real image generation. It introduces PostgreSQL-backed workspaces, conversation messages, structured briefs, uploaded assets, rights/source metadata, generation job rows, append-only job events, immutable artifacts, design versions, model-run/cost records, feedback, and export records. It also connects object storage for binary payloads and proves that job/status/workspace data survives browser refreshes and worker restarts.

This phase does not implement real AI provider calls, prompt planning quality, finished workbench UX, true 2D/3D design preview, production export packages, authentication, billing, sharing, gallery/community features, or advanced image processing. Those remain assigned to later phases.
</domain>

<decisions>
## Implementation Decisions

### Data Ownership And Workspace Boundary

- **D-02-01:** Phase 2 uses system-generated workspace identifiers as the user-facing resume boundary. Full login/auth is out of scope, but the schema should leave room for a future nullable owner/user boundary without forcing auth into v1.
- **D-02-02:** Workspace resume must not depend on browser-only state. The API must be able to return workspace metadata, conversation history, assets, jobs, events, versions, artifacts, feedback, exports, and cost/model-run records from durable storage.
- **D-02-03:** Keep authorization simple and explicit for local MVP behavior. Do not add accounts, OAuth, teams, collaboration, public sharing, or billing gates in this phase.

### Canonical Data Model And Persistence

- **D-02-04:** PostgreSQL is the source of truth for product metadata and state. Redis/Celery result state must not be treated as canonical for jobs, events, costs, artifacts, or workspace history.
- **D-02-05:** Add SQLAlchemy/Alembic infrastructure in the API service for product tables. Use typed repository/service boundaries rather than embedding SQL directly inside route handlers.
- **D-02-06:** The initial schema must cover workspaces, messages, structured design briefs, uploaded assets, generation jobs, job events, design versions, artifacts, model runs, feedback, exports, and idempotency/cost fields required by DATA-01 through DATA-07.
- **D-02-07:** IDs should be stable, opaque, and API-safe. Prefer UUIDs for externally referenced product records unless an existing local pattern strongly suggests otherwise.
- **D-02-08:** Timestamps, status enums, foreign keys, uniqueness constraints, and indexes must be explicit enough to support status polling, workspace resume, idempotent job creation, and lineage queries.

### Uploads, Object Storage, And Rights Metadata

- **D-02-09:** Object storage stores binary uploads, thumbnails, generated outputs, previews, and exports. PostgreSQL stores object keys, media metadata, rights/source fields, checksum/size/MIME data where practical, and relationships to workspace/job/version records.
- **D-02-10:** Phase 2 may use API-mediated multipart upload for simplicity. Direct browser-to-S3 presigned upload can be deferred unless the planner finds it low-risk and still keeps API metadata authoritative.
- **D-02-11:** Uploaded assets must be validated for MIME/extension/size before persistence. Unsupported or unsafe file types should fail before they can be used by later generation/export paths.
- **D-02-12:** Rights/source metadata is required before an uploaded asset can be attached to generation or export workflows. The field set should be small and practical: source label/URL or freeform source, rights confirmation/state, optional notes, and capture timestamp.
- **D-02-13:** Thumbnails are useful but should stay pragmatic. Generate lightweight thumbnails when the local stack can do so reliably; otherwise store enough metadata and object keys for later thumbnail work without blocking the durable ledger.

### Job, Event, And Idempotency Semantics

- **D-02-14:** Generation job rows are the durable state machine. Celery tasks may execute or simulate execution, but job status shown to users must come from PostgreSQL-backed API reads.
- **D-02-15:** Job events are append-only audit records linked to jobs. Events should preserve status transitions, user-visible messages, retry/failure context, worker/task references when available, and timestamps.
- **D-02-16:** Initial job statuses should cover at least `queued`, `running`, `succeeded`, `failed`, and `canceled` or semantically equivalent values. Later phases may add provider-specific details without changing the core contract.
- **D-02-17:** Expensive or retryable job creation paths must require idempotency keys. Duplicate requests with the same workspace and idempotency key should return the original durable job rather than creating a second expensive unit of work.
- **D-02-18:** Estimated and actual provider cost fields should be present but nullable. Phase 2 records local estimates where available; real provider cost reconciliation waits for provider integration.

### Artifacts, Versions, Model Runs, Feedback, And Exports

- **D-02-19:** Artifacts are immutable records. Never overwrite an artifact object key for a new upload, generated image, preview, thumbnail, or export.
- **D-02-20:** Design versions must support parent-child lineage even before real generation exists. This lets Phase 3 attach the first render and Phase 5 add iteration without reworking the schema.
- **D-02-21:** Model-run records should capture requested provider/model/parameters, prompt or structured inputs when available, cost fields, and linkages to jobs and artifacts. In Phase 2 these records can be created with simulated/local provider identifiers only.
- **D-02-22:** Feedback and export records belong in the durable schema now even if the UI for rich feedback/export arrives later. Minimal API coverage is enough to prove persistence and relationships.

### API, Contracts, And Minimal Frontend Proof

- **D-02-23:** FastAPI/Pydantic remains the source of truth for API contracts. All new product routes must expose typed request/response schemas and refresh generated TypeScript contracts.
- **D-02-24:** The Phase 2 API surface should be narrow but complete enough to satisfy DATA requirements: create/resume/list workspace data, create/list messages or briefs, upload/list assets with rights metadata, create/list jobs and events, and list versions/artifacts/exports/feedback where needed for persistence proof.
- **D-02-25:** The frontend work should be a minimal persistence/status proof, not the full workbench. It may add small service-state hooks or shell regions that demonstrate workspace resume and durable job status after refresh. Full chat/preview/upload UX remains Phase 4.
- **D-02-26:** Contract drift checking must remain part of root validation. Plans that add or change API schemas must refresh OpenAPI/generated client artifacts and keep `pnpm contracts:check` green.

### Worker And Pipeline Boundary

- **D-02-27:** Workers may create or update durable job/event records through shared service/repository code, but they must not import FastAPI routers.
- **D-02-28:** Phase 2 may include a no-provider local job simulation task to prove durable status/event updates. It must not call hosted image providers or imply generation quality is available.
- **D-02-29:** Worker restart tolerance is proven by durable state reads and idempotency behavior, not by relying on Redis result backend contents.

### Validation And Quality Gates

- **D-02-30:** Add focused tests for migrations/schema creation, repository/service behavior, API route contracts, idempotent job creation, rights metadata enforcement, object-key immutability, and job event ordering.
- **D-02-31:** Keep Docker-backed smoke checks relevant. Phase 2 verification should include PostgreSQL-backed API behavior and MinIO/object-storage behavior where feasible.
- **D-02-32:** Root `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm contracts:check`, `pnpm validate`, and a Docker local smoke path should remain passing or have explicit host-gated notes.

### The Agent's Discretion

- The planner may split schema work into multiple plans if it improves reviewability.
- The planner may decide whether to put shared data/service code in `services/api` first or introduce a small shared Python package, provided API/worker boundaries stay clear.
- The planner may use local filesystem/fake object storage for unit tests when that gives faster deterministic coverage, but at least one smoke path should exercise the configured MinIO/S3 integration if practical.
- The planner may choose exact endpoint names and route grouping as long as FastAPI/Pydantic schemas remain the contract source and Phase 2 success criteria are observable.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Definition

- `.planning/PROJECT.md` - Project vision, core value, constraints, and stack direction.
- `.planning/REQUIREMENTS.md` - Phase 2 requirements `DATA-01` through `DATA-07` and v1 scope boundaries.
- `.planning/ROADMAP.md` - Phase 2 goal, dependency on Phase 1, success criteria, and later phase boundaries.
- `.planning/STATE.md` - Current project position, Phase 1 verification status, and deferred concerns.
- `AGENTS.md` - Project-local guidance, architecture summary, fast-context instructions, and GSD workflow enforcement.

### Phase 1 Outputs

- `.planning/phases/01-foundation-and-contracts/01-CONTEXT.md` - Existing repo, API, worker, contract, infra, and validation decisions.
- `.planning/phases/01-foundation-and-contracts/01-VERIFICATION.md` - Verified foundation artifacts, residual warnings, host notes, and command evidence.
- `README.md` - Current project entry point and command overview.
- `docs/development.md` - Developer command reference and local workflow notes.
- `infra/compose.yml` - PostgreSQL, Redis, and MinIO local services.

### Current Code Integration Points

- `services/api/src/caragent_api/config.py` - API settings, local database/Redis/S3/CORS/provider configuration, and dotenv loading pattern.
- `services/api/src/caragent_api/main.py` - FastAPI app factory, health route, Pydantic schema style, and CORS wiring.
- `services/worker/src/caragent_worker/config.py` - Worker settings and Redis/provider configuration pattern.
- `services/worker/src/caragent_worker/app.py` - Celery app factory, task routing, and worker boundary.
- `packages/contracts/orval.config.ts` - OpenAPI-to-TypeScript generation configuration.
- `packages/contracts/src/generated/client.ts` - Generated TypeScript client artifact that must stay refreshed.
- `apps/web/src/lib/api/health.ts` - Existing frontend generated-client wrapper pattern.
- `apps/web/src/app/page.tsx` - Minimal shell where Phase 2 may add a persistence/status proof without implementing the full workbench.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- The monorepo boundaries are established: `apps/web`, `services/api`, `services/worker`, `packages/contracts`, and `infra`.
- `ApiSettings` already exposes local PostgreSQL, Redis, S3/MinIO, CORS, runtime, and provider-key configuration with typed validation.
- `WorkerSettings` already provides Redis and provider-key configuration for Celery.
- `infra/compose.yml` provides PostgreSQL, Redis, and MinIO for local development.
- The contracts package already generates TypeScript artifacts from FastAPI OpenAPI and is wired into root validation.
- The web app already imports generated client types through a small wrapper, which is the preferred pattern for additional Phase 2 API calls.

### Established Patterns

- FastAPI/Pydantic schemas are the API contract source.
- Generated TypeScript contract artifacts are committed and checked for drift.
- API and worker entrypoints are separate; the worker should not depend on API routers.
- Root validation delegates to web, API, worker, contracts, environment checks, and smoke checks.
- Docker-backed smoke is the source of truth for live infrastructure availability; API health should not fake live dependency success.

### Integration Points

- Add API database infrastructure under the API service, likely through SQLAlchemy models, Alembic migrations, repositories/services, and route modules.
- Add object-storage client code that uses existing S3/MinIO settings and creates immutable object keys for uploads/thumbnails/artifacts/exports.
- Add worker task(s) or service calls that can update durable job and job-event records without real provider calls.
- Refresh `packages/contracts/openapi/openapi.json` and generated client code after adding product routes.
- Add frontend hooks/components only where needed to prove durable workspace/job state survives refreshes.
</code_context>

<specifics>
## Specific Ideas

- Start with a schema/migration plan before routes so later API work has stable record shapes.
- Keep route naming boring and inspectable: workspaces, messages, assets, jobs, events, versions, artifacts, feedback, and exports.
- Prefer idempotency tests that prove both the returned job ID and absence of duplicate rows.
- Treat rights metadata as an explicit state on assets, not as a loose optional comment hidden in upload metadata.
- Keep Phase 2 local-provider simulation clearly labeled so Phase 3 can replace it with real provider adapters without changing durable contracts.
</specifics>

<deferred>
## Deferred Ideas

- Real AI image generation, provider adapter selection, provider quality/cost validation, and prompt planning - Phase 3.
- Full GPT-style chat, parameter panel, asset manager UI, progress timeline, preview workspace, and feature gates - Phase 4.
- Regeneration UX, feedback workflows, and concept export UX - Phase 5.
- Itasha presets, deterministic text/logo overlays, safe-zone overlays, warning strategy, and preview-spec hardening - Phase 6.
- Provider health dashboards, cancellation, quota/rate limits, fallback routing, and operations controls - Phase 7.
- Auth, teams, public sharing, billing, marketplace/community flows, production-ready handoff, and true 3D UV preview - v2+ unless explicitly promoted.
</deferred>

---

*Phase: 02-durable-data-jobs-and-assets*
*Context gathered: 2026-06-17*
