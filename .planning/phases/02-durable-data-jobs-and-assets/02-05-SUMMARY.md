---
phase: 02-durable-data-jobs-and-assets
plan: "05"
subsystem: "durable jobs and output ledger"
tags: ["jobs", "events", "idempotency", "model-runs", "artifacts", "exports"]
requires:
  - ".planning/phases/02-durable-data-jobs-and-assets/02-05-PLAN.md"
  - ".planning/phases/02-durable-data-jobs-and-assets/02-02-SUMMARY.md"
provides:
  - "Idempotent generation job creation"
  - "Append-only job event service"
  - "Durable model-run, artifact, version, feedback, and export service operations"
  - "FastAPI routes for job status, events, and ledger record reads"
key-files:
  created:
    - "services/core/src/caragent_core/repositories/jobs.py"
    - "services/core/src/caragent_core/services/jobs.py"
    - "services/core/tests/test_jobs.py"
    - "services/api/src/caragent_api/routes/jobs.py"
    - "services/api/tests/test_jobs.py"
  modified:
    - "services/api/src/caragent_api/main.py"
    - "services/api/src/caragent_api/schemas.py"
key-decisions:
  - "Job creation returns an `idempotent_reused` response field so duplicate-key reuse is explicit without creating a second row."
  - "Job creation appends an initial durable `created` event; later status changes append status/completed/error events."
  - "Phase 2 exposes read APIs for model runs, artifacts, versions, feedback, and exports while creation remains in reusable core services for worker/API callers."
requirements-completed: ["DATA-02", "DATA-05", "DATA-06", "DATA-07"]
duration: "in-session"
completed: 2026-06-17
---

# Phase 2 Plan 05: Durable Jobs And Ledger Summary

Plan 02-05 implemented durable generation jobs, append-only events, idempotent creation, nullable cost fields, and reusable core service operations for output ledger records.

## Tasks Completed

| Task | Result | Evidence |
|------|--------|----------|
| Job service tests first | Complete | RED failed on missing `caragent_core.services.jobs`; GREEN passed after repository/service implementation. |
| Core job repository/service | Complete | Added idempotent create, get/list jobs, events, status transitions, cost updates, model runs, artifacts, versions, feedback, and exports. |
| API job routes | Complete | Added create/list/read job routes, event read route, model-run read route, and workspace ledger read routes. |
| API job tests | Complete | Tests cover missing idempotency rejection, duplicate key reuse, durable status/events, nullable costs, and simulation record reads. |

## Verification

| Command | Result |
|---------|--------|
| `cd services/core && uv run pytest -q tests/test_jobs.py` | RED first for missing service, then passed, `3 passed`. |
| `cd services/api && uv run pytest -q tests/test_jobs.py` | RED first with missing job routes, then passed, `3 passed`. |
| `cd services/core && uv run pytest -q` | Passed, `21 passed`. |
| `cd services/core && uv run ruff check .` | Passed. |
| `cd services/core && uv run mypy src` | Passed, no issues. |
| `cd services/api && uv run pytest -q` | Passed, `22 passed`. |
| `cd services/api && uv run ruff check .` | Passed. |
| `cd services/api && uv run mypy src` | Passed, no issues. |
| `cd services/api && uv run python -c "...create_app().openapi()..."` | Passed; job create/read/events/model-run paths and job schemas are present. |

## Deviations from Plan

**[Rule 1 - API Surface] Creation APIs stay narrow**
- Found during: route design.
- Issue: The plan required read visibility for versions/artifacts/model-runs/feedback/exports, but worker simulation and real generation creation paths are later phases.
- Fix: Core services can create all ledger records; API exposes narrow read routes and job creation/status routes. API tests create simulation records through core service calls, then read them back through API routes.
- Verification: API simulation record test passed.

**[Rule 1 - ORM Mutability] Initial cost assertion adjusted**
- Found during: core job test GREEN run.
- Issue: The test asserted initial nullable cost fields after mutating the same ORM instance through `update_job_costs`.
- Fix: Captured initial values before the cost update, then asserted updated numeric values separately.
- Verification: Core job tests passed.

## Self-Check: PASSED

DATA-05 is covered by durable job status and append-only events. DATA-06 is covered by workspace-scoped idempotency and duplicate-key row-count tests. DATA-07 is covered by nullable and numeric cost fields on job/model-run records. DATA-02 supporting records are represented through versions, artifacts, model runs, feedback, and exports.

## Next

Ready for `02-06-PLAN.md`: OpenAPI refresh, generated TypeScript contracts, and frontend API wrappers.
