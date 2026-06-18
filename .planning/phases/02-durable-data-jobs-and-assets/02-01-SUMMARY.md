---
phase: 02-durable-data-jobs-and-assets
plan: "01"
subsystem: "shared data core"
tags: ["core", "database", "alembic", "validation"]
requires:
  - ".planning/phases/02-durable-data-jobs-and-assets/02-01-PLAN.md"
provides:
  - "services/core"
  - "API/worker local dependency on caragent-core"
  - "Alembic foundation"
affects:
  - "package.json"
  - "scripts/validate-all.mjs"
  - "infra/compose.yml"
tech-stack:
  added:
    - "SQLAlchemy async"
    - "Alembic"
    - "aiosqlite"
    - "asyncpg"
  patterns:
    - "Shared Python core package"
    - "API-owned migrations importing shared metadata"
key-files:
  created:
    - "services/core/pyproject.toml"
    - "services/core/README.md"
    - "services/core/src/caragent_core/__init__.py"
    - "services/core/src/caragent_core/database.py"
    - "services/core/src/caragent_core/models.py"
    - "services/core/tests/test_database.py"
    - "services/api/alembic.ini"
    - "services/api/alembic/env.py"
    - "services/api/alembic/versions/.gitkeep"
  modified:
    - "services/api/pyproject.toml"
    - "services/api/uv.lock"
    - "services/api/src/caragent_api/config.py"
    - "services/worker/pyproject.toml"
    - "services/worker/uv.lock"
    - "package.json"
    - "scripts/validate-all.mjs"
    - "docs/development.md"
    - "infra/compose.yml"
key-decisions:
  - "Use `services/core` as a shared Python package so worker can use durable-data primitives without importing API routers."
  - "Keep migration ownership in `services/api`, with Alembic importing `caragent_core.models.metadata`."
  - "Mount the PostgreSQL 18 local development volume at `/var/lib/postgresql` using a new `postgres18-data` volume."
requirements-completed: ["DATA-01", "DATA-02", "DATA-05"]
duration: "in-session"
completed: 2026-06-17
---

# Phase 2 Plan 01: Shared Data Core Summary

Plan 02-01 created the shared data-core foundation for Phase 2: a `caragent-core` uv package, async SQLAlchemy database helpers, empty shared metadata for Alembic, API/worker local path dependencies, and root validation wiring.

## Tasks Completed

| Task | Result | Evidence |
|------|--------|----------|
| Add shared core package | Complete | `services/core` imports and has independent pytest/ruff/mypy config. |
| Implement async database helpers | Complete | `uv run pytest -q` in `services/core` passed `4 passed`; `uv run mypy src` passed. |
| Wire API and worker local dependencies | Complete | API and worker both imported `caragent_core` and printed `0.1.0`. |
| Add Alembic migration foundation | Complete | `uv run alembic current` connected to PostgreSQL and loaded metadata. |
| Include core in validation commands and docs | Complete | Static checks confirmed `package.json`, `scripts/validate-all.mjs`, and `docs/development.md` include core/Alembic coverage. |

## Verification

| Command | Result |
|---------|--------|
| `cd services/core && uv run pytest -q` | Passed, `4 passed`. |
| `cd services/core && uv run ruff check .` | Passed. |
| `cd services/core && uv run mypy src` | Passed, no issues. |
| `cd services/api && uv run pytest -q` | Passed, `11 passed`. |
| `cd services/worker && uv run pytest -q` | Passed, `8 passed`. |
| `cd services/api && uv run ruff check .` | Passed after import ordering fix. |
| `cd services/worker && uv run ruff check .` | Passed. |
| `cd services/api && uv run mypy src` | Passed, no issues. |
| `cd services/worker && uv run mypy src` | Passed, no issues. |
| `cd services/api && uv run alembic current` | Passed against Docker PostgreSQL. |
| `node scripts/smoke-local.mjs` | Passed in non-sandbox shell: PostgreSQL, Redis, and MinIO checks passed. |

## Deviations from Plan

**[Rule 1 - Bug] PostgreSQL 18 local volume mount failed**
- Found during: Alembic verification.
- Issue: `postgres:18-alpine` restarted because the Compose volume mounted to `/var/lib/postgresql/data`, which is incompatible with PostgreSQL 18 image layout.
- Fix: Changed `infra/compose.yml` to use a new `postgres18-data` volume mounted at `/var/lib/postgresql`, preserving the old volume.
- Verification: Compose `ps` showed PostgreSQL healthy; `node scripts/smoke-local.mjs` passed.

**[Rule 1 - Bug] API local default database password did not match Compose defaults**
- Found during: Alembic verification.
- Issue: `ApiSettings` default `DATABASE_URL` used password `caragent`, while `.env.example` and Compose use `caragent_local_password`.
- Fix: Aligned API local database and MinIO defaults with `.env.example`.
- Verification: API tests passed and Alembic connected successfully.

**[Host Note] pnpm unavailable under current NVM Node 24**
- Found during: attempted `pnpm infra:up`.
- Issue: Current NVM Node 24.11.0 does not expose pnpm; Node 20 Corepack attempted a network download.
- Fix: Used direct equivalent Docker Compose commands for this plan's smoke/Alembic verification. Root scripts were still updated statically.
- Verification: Direct Docker Compose and node smoke commands passed.

## Self-Check: PASSED

The shared core package exists, API and worker can import it, Alembic imports shared metadata, Docker-backed PostgreSQL is healthy after the Compose fix, and validation wiring includes the new package.

## Next

Ready for `02-02-PLAN.md`: durable product ledger models and initial migration.
