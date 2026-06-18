---
phase: 02-durable-data-jobs-and-assets
plan: "04"
subsystem: "asset uploads and rights metadata"
tags: ["assets", "uploads", "object-storage", "rights", "fastapi"]
requires:
  - ".planning/phases/02-durable-data-jobs-and-assets/02-04-PLAN.md"
  - ".planning/phases/02-durable-data-jobs-and-assets/02-02-SUMMARY.md"
provides:
  - "Workspace-scoped object key generation"
  - "Upload validation and checksum metadata"
  - "Asset create/list/read API routes"
  - "Rights/source metadata update and usability gate"
key-files:
  created:
    - "services/core/src/caragent_core/storage.py"
    - "services/core/src/caragent_core/services/assets.py"
    - "services/core/tests/test_assets.py"
    - "services/api/src/caragent_api/routes/assets.py"
    - "services/api/tests/test_assets.py"
  modified:
    - "services/api/pyproject.toml"
    - "services/api/src/caragent_api/dependencies.py"
    - "services/api/src/caragent_api/main.py"
    - "services/api/src/caragent_api/schemas.py"
    - "services/api/uv.lock"
key-decisions:
  - "Keep storage behind an `ObjectStorage` protocol with in-memory and local-file implementations for tests/local API use."
  - "Return durable asset metadata and object keys from the API, not object-storage credentials."
  - "Require confirmed rights plus source metadata before an asset can be used by later generation/export services."
requirements-completed: ["DATA-02", "DATA-03", "DATA-04"]
duration: "in-session"
completed: 2026-06-17
---

# Phase 2 Plan 04: Asset Upload And Rights Summary

Plan 02-04 implemented durable uploaded asset metadata, workspace-scoped object keys, upload validation, and rights/source enforcement in the shared core service and FastAPI API.

## Tasks Completed

| Task | Result | Evidence |
|------|--------|----------|
| Asset behavior tests first | Complete | API metadata test failed RED with `GET /assets/{id}` returning 404 before the route was added. |
| Storage helpers and asset service | Complete | Object keys include workspace, kind, asset record ID, and sanitized filename; uploads validate type, extension, and byte size before storage writes. |
| Asset API routes | Complete | Added upload, workspace asset list, asset metadata read, and rights/source update routes. |
| Rights/source enforcement | Complete | Core `require_confirmed_rights` blocks unconfirmed assets and stamps confirmation time only for confirmed rights. |

## Verification

| Command | Result |
|---------|--------|
| `cd services/api && uv run pytest -q tests/test_assets.py` | RED first for missing metadata route, then passed, `4 passed`. |
| `cd services/core && uv run pytest -q tests/test_assets.py` | Passed, `5 passed`. |
| `cd services/api && uv run pytest -q` | Passed, `19 passed`. |
| `cd services/api && uv run ruff check .` | Passed. |
| `cd services/api && uv run mypy src` | Passed, no issues. |
| `cd services/core && uv run pytest -q` | Passed, `18 passed`. |
| `cd services/core && uv run ruff check .` | Passed. |
| `cd services/core && uv run mypy src` | Passed, no issues. |
| `cd services/api && uv run python -c "...create_app().openapi()..."` | Passed; asset upload/read/rights paths and asset schemas are present. |

## Deviations from Plan

**[Rule 1 - Dependency] Multipart upload dependency**
- Found during: API route implementation.
- Issue: FastAPI file upload routes require `python-multipart`.
- Fix: Added `python-multipart>=0.0.20,<1` to `services/api/pyproject.toml` and synced the API environment.
- Verification: API asset tests and full API test suite passed.

**[Rule 1 - Coverage] Metadata read route and size-limit tests**
- Found during: plan self-check.
- Issue: The first pass covered upload/list/update but missed the explicit asset metadata read route and API/core size-limit assertions requested by the plan.
- Fix: Added tests for `GET /assets/{asset_id}` and too-large uploads, then implemented the metadata read route.
- Verification: The new metadata test failed RED with 404 before the route, then passed after implementation.

## Self-Check: PASSED

DATA-03 and DATA-04 are covered at the API and core service layer. Uploads persist metadata and object keys, reject unsafe/oversized inputs before storage writes, and keep object storage credentials server-side. Rights/source metadata gates later generation/export usage through the core service.

## Next

Ready for `02-05-PLAN.md`: durable jobs, events, idempotency, model runs, versions, artifacts, feedback, exports, and costs.
