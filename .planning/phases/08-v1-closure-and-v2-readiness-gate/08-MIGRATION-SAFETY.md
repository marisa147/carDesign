---
phase: 08-v1-closure-and-v2-readiness-gate
status: no-op-schema
requirements:
  - V2-READY-02
  - V2-READY-03
created: 2026-06-18
---

# Phase 8 Migration Safety Review

Phase 8 is a readiness gate and does not introduce a database schema migration. The changes in this phase are planning docs, root scripts, static checkers, environment examples, and typed runtime configuration flags. No table, column, index, constraint, or Alembic revision is added by Phase 8.

## Current Alembic State

| Item | Value |
|------|-------|
| Alembic versions directory | `services/api/alembic/versions/` |
| Current migration file | `f2d60f906fc6_phase_02_initial_ledger.py` |
| Current revision | `f2d60f906fc6` |
| Down revision | `None` |
| Branch labels | `None` |
| Depends on | `None` |
| Phase 8 schema action | no-op |

The current migration chain is a single root migration. Static Phase 8 evidence can confirm the file and revision chain, but live database proof still requires a prepared host running:

```powershell
cd services/api
uv run alembic upgrade head
uv run alembic current
```

## v1 Canonical Ledger Tables

The v1 durable ledger remains PostgreSQL-backed through `services/core/src/caragent_core/models.py` and `services/api/alembic/versions/f2d60f906fc6_phase_02_initial_ledger.py`.

| Ledger Concept | Table | Compatibility Requirement |
|----------------|-------|---------------------------|
| Workspaces | `workspaces` | Existing workspace ids, status, metadata, and owner/title fields remain readable. |
| Conversation | `messages` | Workspace message history and sequence ordering remain stable. |
| Structured briefs | `design_briefs` | Brief payload JSON remains canonical for generation and iteration inputs. |
| Assets and rights | `assets` | Object keys, thumbnails, source/rights metadata, and rights status remain readable. |
| Generation jobs | `generation_jobs` | Job status, operation, provider/model, costs, idempotency key, latest error, and metadata remain canonical. |
| Job events | `job_events` | Durable event sequence and progress metadata remain readable. |
| Design versions | `design_versions` | Parent lineage, job/brief links, status, title/summary, and `parameters` JSON remain readable. |
| Artifacts | `artifacts` | Immutable object keys, version/job/asset links, dimensions, checksums, and metadata remain readable. |
| Feedback | `feedback` | Rating, approval state, comments, and metadata remain tied to versions. |
| Exports | `exports` | Concept export manifest and selected artifact/version records remain readable. |
| Model runs | `model_runs` | Provider/model/prompt/cost/input/output traceability remains canonical. |

Redis remains queue/cache/progress infrastructure only. It is not the source of truth for job, artifact, version, export, feedback, or provider-run state.

## Schema Change Classification

| Change Type | Phase 8 Status | Notes |
|-------------|----------------|-------|
| Planning docs | yes | No database effect. |
| Root scripts | yes | No database effect. |
| Static checkers | yes | No database effect. |
| Env examples | yes | No database effect. |
| API/worker typed config flags | yes | Runtime settings only, no ORM model or Alembic change. |
| OpenAPI/generated contracts | no schema change | 08-03 verified generated artifacts are current. |
| Alembic revisions | no | No new file under `services/api/alembic/versions/`. |
| SQLAlchemy models | no | Phase 8 does not add or remove ORM models/columns. |

## Future V2 Migration Rules

Future V2 migrations must preserve these boundaries:

1. Prefer additive changes over destructive rewrites.
2. Do not rename or remove v1 ledger tables without a dedicated compatibility migration and data-backfill plan.
3. Preserve `design_versions.parameters` and artifact/job/model-run metadata JSON readability for existing `preview_spec` and prompt trace data.
4. Preserve version lineage through `parent_version_id` and job/brief links.
5. Preserve immutable artifact object keys and export manifests.
6. Keep provider runs, costs, fallbacks, and failures traceable through durable `generation_jobs`, `job_events`, and `model_runs` records.
7. Keep Redis out of canonical durable state.
8. Pair every schema migration with `uv run alembic upgrade head`, `uv run alembic current`, focused API/core tests, and `pnpm contracts:check` when API schemas change.

## Phase 8 No-Op Proof

Phase 8 does not add an Alembic revision and does not modify `services/core/src/caragent_core/models.py`. The static checker added in this phase verifies that the expected Alembic directory, current revision file, revision chain metadata, and v1 ledger tables remain present. A live host must still run Alembic upgrade/current before release sign-off.

## Verification Mapping

| Requirement | Evidence |
|-------------|----------|
| V2-READY-02 | Static migration checker plus documented live Alembic commands. |
| V2-READY-03 | Phase 8 config flags are runtime-only and do not mutate v1 database schema. |
