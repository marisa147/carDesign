# Phase 2: Durable Data, Jobs, And Assets - Pattern Map

**Date:** 2026-06-17
**Status:** Complete

## Existing Patterns To Reuse

### Python Service Shape

- `services/api/pyproject.toml` and `services/worker/pyproject.toml` define strict `uv` projects with `src/` layouts.
- Tests live under each service `tests/` directory and use pytest with `pythonpath = ["src"]`.
- Ruff and mypy are strict enough that new shared Python code should include explicit types from the start.

### API App Pattern

- `services/api/src/caragent_api/main.py` exposes `create_app(settings: ApiSettings | None = None)` and creates route functions inside the app factory.
- `services/api/src/caragent_api/config.py` owns typed settings and `.env` loading.
- Existing tests use `fastapi.testclient.TestClient(create_app(settings))`.

Phase 2 should likely move beyond route functions embedded in `main.py` by adding routers under `caragent_api/routes/`, then include them from `create_app`. Keep `/health` behavior intact.

### Contract Pattern

- `services/api/src/caragent_api/scripts/export_openapi.py` writes deterministic OpenAPI.
- `packages/contracts/orval.config.ts` generates `packages/contracts/src/generated/client.ts`.
- `scripts/check-contracts.mjs` validates generated artifacts.
- `apps/web/src/lib/api/health.ts` wraps generated contract helpers instead of duplicating URLs/types.

Phase 2 frontend code should add similar wrappers for workspace/job APIs.

### Worker Boundary Pattern

- `services/worker/src/caragent_worker/app.py` creates a Celery app with includes.
- `services/worker/src/caragent_worker/tasks/health.py` defines typed task payloads.
- `services/worker/tests/test_worker_app.py` explicitly forbids importing `caragent_api`, FastAPI, or provider SDKs.

Phase 2 worker code must import shared core code, not API routers. Update boundary tests to keep forbidding `caragent_api` and provider imports.

### Frontend Shell Pattern

- `apps/web/src/app/page.tsx` is currently a small client-side foundation shell.
- API access is isolated in `apps/web/src/lib/api/health.ts`.
- Tests use Vitest and Testing Library in `apps/web/src/app/page.test.tsx`.
- UI components live under `apps/web/src/components/ui/`.

Phase 2 should keep frontend additions small: a generated-client wrapper, a minimal panel on the existing shell, and tests proving durable reload behavior.

### Local Infra Pattern

- `infra/compose.yml` owns PostgreSQL, Redis, and MinIO.
- `scripts/smoke-local.mjs` already checks Docker availability and local services.

Phase 2 can extend smoke behavior with a separate data smoke script or add a `--data` path, but it should preserve the existing `pnpm smoke:local` command.

## New Patterns Phase 2 Should Establish

### Shared Core Package

Create a `services/core` Python package named `caragent-core` that both API and worker can depend on. It should own durable data primitives but not FastAPI routers.

Expected responsibilities:

- `caragent_core.database`: async engine/session helpers.
- `caragent_core.models`: SQLAlchemy models and metadata.
- `caragent_core.repositories`: small query helpers.
- `caragent_core.services`: domain operations for workspaces, assets, jobs, and events.
- `caragent_core.storage`: object-key and S3/MinIO helpers.

### Router Modules

Move new product API routes into focused modules:

- `caragent_api.routes.workspaces`
- `caragent_api.routes.assets`
- `caragent_api.routes.jobs`

Shared schema models can live in `caragent_api.schemas`.

### Test Style

Use focused tests:

- Core unit tests for repositories/services with isolated database setup.
- API route tests with dependency overrides for database sessions and storage.
- Worker tests that call task `.run()` or service functions without requiring a live Celery worker.
- Frontend tests with mocked `fetch`, matching the existing health tests.

## Constraints

- Do not add provider SDK calls in Phase 2.
- Do not implement full auth.
- Do not expose S3 secrets to the browser.
- Do not build full chat/upload/preview UI.
- Keep generated contracts refreshed after API route changes.
