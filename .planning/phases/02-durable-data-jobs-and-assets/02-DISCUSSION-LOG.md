# Phase 2: Durable Data, Jobs, And Assets - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-06-17
**Phase:** 02-durable-data-jobs-and-assets
**Areas discussed:** Data Ownership And Workspace Boundary, Canonical Data Model And Persistence, Uploads And Rights Metadata, Job/Event/Idempotency Semantics, Artifacts/Versions/Costs, API/Contracts/Frontend Proof, Worker Boundary, Verification Gates

---

## Runtime Note

The user requested `$gsd-progress --next` with automatic forward execution and no confirmation prompts. Per that instruction, the discussion phase selected all Phase 2 gray areas and resolved them with conservative defaults from `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/STATE.md`, Phase 1 context, Phase 1 verification, and the current codebase.

No additional user-entered freeform corrections were provided during this discuss phase.

---

## Data Ownership And Workspace Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Anonymous/system-generated workspace IDs | Satisfies resume/history requirements without adding auth before the MVP loop is proven. | yes |
| Full user accounts and login | Useful later but outside Phase 2 and not required for DATA-01. | |
| Browser-only session state | Too weak; would fail refresh/resume and durable history requirements. | |

**Selected choice:** Use durable workspace records with opaque IDs and no full auth.
**Notes:** Schema may leave room for future owner fields, but Phase 2 must not implement accounts, teams, sharing, or billing.

---

## Canonical Data Model And Persistence

| Option | Description | Selected |
|--------|-------------|----------|
| PostgreSQL as canonical ledger with SQLAlchemy/Alembic | Matches architecture and supports jobs, events, lineage, and idempotency. | yes |
| Redis/Celery result state as job truth | Fast initially but loses durable auditability and fails DATA-05. | |
| Object storage metadata only | Cannot support relational queries, idempotency, lineage, and cost records cleanly. | |

**Selected choice:** Add SQLAlchemy/Alembic-backed product tables in the API service.
**Notes:** Required records include workspaces, messages, briefs, assets, jobs, events, versions, artifacts, model runs, feedback, exports, and cost/idempotency fields.

---

## Uploads And Rights Metadata

| Option | Description | Selected |
|--------|-------------|----------|
| API-mediated multipart upload with DB metadata and object storage payloads | Simple for v1 while keeping the API authoritative for validation and rights state. | yes |
| Direct presigned browser uploads first | Scales well later, but adds complexity before the upload model is proven. | |
| Store binaries in PostgreSQL | Simpler to query but poor fit for generated images, thumbnails, previews, and exports. | |

**Selected choice:** Store binary payloads in MinIO/S3 and metadata/object keys in PostgreSQL.
**Notes:** Rights/source metadata must be recorded before assets can be used in generation/export paths.

---

## Job, Event, And Idempotency Semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Durable job state machine plus append-only events | Provides refresh-safe status and auditability for later provider execution. | yes |
| Rely on Celery task result backend | Does not meet the canonical PostgreSQL rule and weakens restart/retry behavior. | |
| Synchronous HTTP generation stubs | Misrepresents the async architecture and creates Phase 3 rework. | |

**Selected choice:** Job rows and job events are the source of truth; Celery/Redis are execution/cache details.
**Notes:** Idempotency keys are required for expensive/retryable job creation and duplicate requests return the existing job.

---

## Artifacts, Versions, Model Runs, Feedback, And Exports

| Option | Description | Selected |
|--------|-------------|----------|
| Add all ledger tables now with minimal behavior | Avoids Phase 3/5 schema churn and satisfies DATA-02. | yes |
| Only create jobs/assets now | Too narrow; later phases would need to retrofit lineage, feedback, exports, and cost records. | |
| Implement rich export/feedback UX now | Belongs to later UI and iteration/export phases. | |

**Selected choice:** Create durable records for artifacts, design versions, model runs, feedback, and exports with minimal API coverage.
**Notes:** Artifacts are immutable and design versions must support parent-child lineage.

---

## API, Contracts, And Frontend Proof

| Option | Description | Selected |
|--------|-------------|----------|
| Narrow typed API plus minimal frontend persistence proof | Meets DATA requirements without building the full workbench early. | yes |
| Backend-only persistence with no frontend proof | Might satisfy storage internally but weakens refresh/status user evidence. | |
| Full chat/upload/preview workbench | Phase 4 scope; too much UI surface for Phase 2. | |

**Selected choice:** Add typed FastAPI routes and generated TypeScript contracts, with only enough frontend integration to prove durable resume/status after refresh.
**Notes:** Generated contracts must be refreshed and checked as part of validation.

---

## Worker Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Worker updates durable job/events through shared service boundaries | Proves async state updates without importing API routers. | yes |
| Worker owns its own separate state | Risks divergence from API-visible job truth. | |
| No worker touch in Phase 2 | Leaves restart/job-status guarantees under-proven. | |

**Selected choice:** Include a no-provider local simulation path if needed to prove durable job/event updates.
**Notes:** No real provider calls or generated design quality claims in Phase 2.

---

## Verification Gates

| Option | Description | Selected |
|--------|-------------|----------|
| Focused migration/API/service/idempotency/storage tests plus root validation | Gives concrete coverage for the durable ledger without over-testing unrelated features. | yes |
| Only static type/lint checks | Too weak for persistence and idempotency behavior. | |
| Manual-only Docker smoke | Useful but insufficient without deterministic tests. | |

**Selected choice:** Require focused automated tests and keep aggregate validation green.
**Notes:** Docker-backed smoke should exercise PostgreSQL and MinIO behavior where practical.

---

## The Agent's Discretion

- Exact table names, endpoint names, and plan split.
- Whether shared persistence code starts inside `services/api` or a small shared package.
- Whether thumbnails are fully generated in Phase 2 or represented through metadata and deferred processing hooks.
- Exact minimal frontend proof UI shape.

## Deferred Ideas

- Real provider calls, real prompt planning, polished workbench UX, true preview/export workflows, auth, billing, sharing, operations dashboards, production handoff, and true 3D preview remain deferred to later roadmap phases.
