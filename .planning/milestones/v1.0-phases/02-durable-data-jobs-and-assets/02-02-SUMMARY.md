---
phase: 02-durable-data-jobs-and-assets
plan: "02"
subsystem: "durable ledger schema"
tags: ["sqlalchemy", "alembic", "schema", "persistence"]
requires:
  - ".planning/phases/02-durable-data-jobs-and-assets/02-02-PLAN.md"
  - ".planning/phases/02-durable-data-jobs-and-assets/02-01-SUMMARY.md"
provides:
  - "Phase 2 durable ledger SQLAlchemy models"
  - "Phase 2 initial Alembic migration"
affects:
  - "services/core/src/caragent_core/models.py"
  - "services/core/src/caragent_core/enums.py"
  - "services/api/alembic/versions/f2d60f906fc6_phase_02_initial_ledger.py"
key-files:
  created:
    - "services/core/src/caragent_core/enums.py"
    - "services/core/tests/test_models.py"
    - "services/api/tests/test_migrations.py"
    - "services/api/alembic/script.py.mako"
    - "services/api/alembic/versions/f2d60f906fc6_phase_02_initial_ledger.py"
  modified:
    - "services/core/src/caragent_core/models.py"
    - "services/core/tests/test_database.py"
key-decisions:
  - "Store enum values as stable lowercase strings instead of database enum types for early migration flexibility."
  - "Use UUID primary keys for externally referenced durable records."
  - "Keep object payloads out of PostgreSQL; assets and artifacts store immutable object keys and metadata."
requirements-completed: ["DATA-01", "DATA-02", "DATA-03", "DATA-04", "DATA-05", "DATA-06", "DATA-07"]
duration: "in-session"
completed: 2026-06-17
---

# Phase 2 Plan 02: Durable Ledger Schema Summary

Plan 02-02 added the initial durable product ledger: workspace history, messages, design briefs, assets and rights metadata, generation jobs, append-only events, design versions, artifacts, model runs, feedback, exports, idempotency constraints, cost fields, and Alembic migration coverage.

## Tasks Completed

| Task | Result | Evidence |
|------|--------|----------|
| Add domain enums | Complete | `tests/test_models.py` verifies required job and rights states. |
| Add SQLAlchemy models | Complete | Metadata contains all Phase 2 ledger tables and constraints. |
| Generate initial migration | Complete | Alembic generated `f2d60f906fc6_phase_02_initial_ledger.py`; upgrade/downgrade/upgrade succeeded. |
| Add schema integrity tests | Complete | API migration tests verify tables and key constraints. |

## Verification

| Command | Result |
|---------|--------|
| `cd services/core && uv run pytest -q tests/test_models.py tests/test_database.py` | Passed, `9 passed`. |
| `cd services/core && uv run pytest -q` | Passed, `9 passed`. |
| `cd services/core && uv run ruff check .` | Passed. |
| `cd services/core && uv run mypy src` | Passed, no issues. |
| `cd services/api && uv run alembic upgrade head` | Passed. |
| `cd services/api && uv run alembic downgrade base` | Passed. |
| `cd services/api && uv run alembic upgrade head` | Passed after downgrade. |
| `cd services/api && uv run alembic current` | Passed, current revision `f2d60f906fc6 (head)`. |
| `cd services/api && uv run pytest -q tests/test_migrations.py tests/test_openapi_export.py tests/test_health.py` | Passed, `8 passed`. |
| `cd services/api && uv run ruff check .` | Passed after formatting migration. |

## Deviations from Plan

**[Rule 1 - Bug] Alembic revision template missing**
- Found during: migration generation.
- Issue: `alembic revision --autogenerate` failed because `services/api/alembic/script.py.mako` was missing from the 02-01 scaffold.
- Fix: Added the standard typed Alembic migration template.
- Verification: Autogenerate produced the initial ledger migration; API ruff and migration tests passed.

**[Rule 1 - Test Robustness] Migration text assertions were quote-format brittle**
- Found during: ruff formatting of generated migration.
- Issue: Tests matched single-line/single-quote generated text and failed after ruff formatted the migration.
- Fix: Updated tests to match the formatted multiline call style.
- Verification: API migration/OpenAPI/health tests passed.

## Self-Check: PASSED

All DATA-02 record categories have tables. Idempotency, event ordering, rights metadata, and immutable object-key constraints are represented in metadata and migration tests. The migration upgrades and downgrades cleanly against local PostgreSQL.

## Next

Ready for `02-03-PLAN.md`: workspace, message, and structured brief services/API.
