# Phase 2: Durable Data, Jobs, And Assets - Validation Strategy

**Date:** 2026-06-17
**Status:** Ready for execution

## Must-Have Truths

1. A user can create or resume a workspace and retrieve persisted conversation history.
2. Uploaded assets are validated, stored through object storage, and carry required rights/source metadata before generation/export use.
3. Job status and job events are stored durably in PostgreSQL and can be read after browser refresh or worker restart.
4. Messages, briefs, jobs, events, versions, artifacts, model runs, feedback, exports, and costs have durable records.
5. Duplicate expensive job requests with the same idempotency key return the original job and do not create duplicate work.

## Automated Verification Matrix

| Dimension | Required Evidence | Suggested Command |
|-----------|-------------------|-------------------|
| Core package | Ruff, mypy, and pytest pass for shared data code | `cd services/core && uv run pytest -q` plus ruff/mypy |
| Migrations | Alembic metadata imports and upgrade path work | `cd services/api && uv run alembic upgrade head` against a temp/local DB |
| Workspace/messages | API or service tests prove create/resume/list persistence | `cd services/api && uv run pytest -q tests/test_workspaces.py` |
| Assets/rights | Upload validation and rights gating tests pass | `cd services/api && uv run pytest -q tests/test_assets.py` |
| Jobs/events/idempotency | Duplicate key and append-only event tests pass | `cd services/api && uv run pytest -q tests/test_jobs.py` |
| Worker | Worker can update durable job/event state without importing API routers | `cd services/worker && uv run pytest -q` |
| Contracts | OpenAPI and generated TypeScript client are current | `pnpm contracts:check` |
| Frontend proof | Web tests show resume/status fetches use durable API state | `pnpm --filter @caragent/web test` |
| Aggregate | Root command remains the project verification entry point | `pnpm validate` |
| Docker smoke | PostgreSQL/Redis/MinIO still pass and data smoke exercises DB/object storage | `pnpm infra:up`; `pnpm smoke:local`; `pnpm infra:down` |

## Human UAT

Phase 2 human UAT should be small and evidence-based:

1. Start infrastructure and API/web.
2. Create a workspace from the web shell.
3. Add a message or structured brief.
4. Create a simulated generation job.
5. Refresh the browser.
6. Confirm workspace history and job status are still visible from API-backed state.

No real image generation, polished workbench UI, or production export validation is expected in this phase.

## Blockers

- Any Phase 2 implementation that stores product state only in browser local storage, Redis task state, or Celery result state fails validation.
- Any upload path that allows assets to be used without rights/source metadata fails DATA-04.
- Any duplicate job request that creates a second job for the same workspace/idempotency key fails DATA-06.
- Any route/schema change that leaves generated contracts stale fails the phase gate.
