---
phase: 02-durable-data-jobs-and-assets
plan: "03"
subsystem: "workspace persistence API"
tags: ["workspace", "messages", "briefs", "fastapi", "sqlalchemy"]
requires:
  - ".planning/phases/02-durable-data-jobs-and-assets/02-03-PLAN.md"
  - ".planning/phases/02-durable-data-jobs-and-assets/02-02-SUMMARY.md"
provides:
  - "Workspace create/resume service"
  - "Message persistence service"
  - "Structured brief persistence service"
  - "Workspace FastAPI routes"
key-files:
  created:
    - "services/core/src/caragent_core/repositories/__init__.py"
    - "services/core/src/caragent_core/repositories/workspaces.py"
    - "services/core/src/caragent_core/services/__init__.py"
    - "services/core/src/caragent_core/services/workspaces.py"
    - "services/core/tests/test_workspaces.py"
    - "services/api/src/caragent_api/dependencies.py"
    - "services/api/src/caragent_api/routes/__init__.py"
    - "services/api/src/caragent_api/routes/workspaces.py"
    - "services/api/src/caragent_api/schemas.py"
    - "services/api/tests/test_workspaces.py"
  modified:
    - "services/api/src/caragent_api/main.py"
    - "services/core/src/caragent_core/py.typed"
key-decisions:
  - "Use route-independent core services for workspace/message/brief behavior."
  - "Create API database engine/session state in `create_app`, with tests initializing schema explicitly."
  - "Use FastAPI lifespan disposal instead of deprecated `on_event` shutdown handlers."
requirements-completed: ["DATA-01", "DATA-02"]
duration: "in-session"
completed: 2026-06-17
---

# Phase 2 Plan 03: Workspace Persistence API Summary

Plan 02-03 implemented durable workspace, message, and structured brief behavior in the shared core package and exposed typed FastAPI routes for the API.

## Tasks Completed

| Task | Result | Evidence |
|------|--------|----------|
| Workspace service tests first | Complete | RED failed on missing `caragent_core.services`; GREEN passed after implementation. |
| Core repositories/services | Complete | Workspace create/resume, ordered messages, structured briefs, not-found and validation errors implemented. |
| API schemas/routes | Complete | `POST /workspaces`, `GET /workspaces/{id}`, message routes, and brief routes added. |
| API route tests | Complete | API tests prove persistence across a new `TestClient` and 404 behavior for missing workspace. |

## Verification

| Command | Result |
|---------|--------|
| `cd services/core && uv run pytest -q tests/test_workspaces.py` | Passed, `4 passed`. |
| `cd services/core && uv run pytest -q` | Passed, `13 passed`. |
| `cd services/core && uv run ruff check .` | Passed. |
| `cd services/core && uv run mypy src` | Passed, no issues. |
| `cd services/api && uv run pytest -q tests/test_workspaces.py tests/test_health.py` | Passed, `6 passed`. |
| `cd services/api && uv run pytest -q` | Passed, `15 passed`. |
| `cd services/api && uv run ruff check .` | Passed. |
| `cd services/api && uv run mypy src` | Passed, no issues. |

## Deviations from Plan

**[Rule 1 - Compatibility] FastAPI `on_event` warning**
- Found during: API workspace test run.
- Issue: Initial database cleanup used `app.on_event("shutdown")`, which emitted FastAPI deprecation warnings.
- Fix: Switched to FastAPI lifespan handler while keeping `app.state.database_engine` available for tests.
- Verification: API workspace and health tests passed without the deprecation warning.

**[Rule 1 - Type Packaging] Shared package lacked `py.typed`**
- Found during: API mypy.
- Issue: API mypy treated local `caragent-core` imports as untyped.
- Fix: Added `services/core/src/caragent_core/py.typed`.
- Verification: API mypy passed.

## Self-Check: PASSED

DATA-01 is covered by API tests that create a workspace, write messages/briefs, and read them back across a new client. DATA-02 coverage for messages and structured briefs is implemented in core services and API routes.

## Next

Ready for `02-04-PLAN.md`: asset upload, object storage metadata, validation, and rights/source enforcement.
