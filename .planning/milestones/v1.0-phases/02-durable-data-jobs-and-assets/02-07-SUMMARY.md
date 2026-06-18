---
phase: 02-durable-data-jobs-and-assets
plan: "07"
subsystem: "worker durable job simulation"
tags: ["worker", "celery", "jobs", "events", "simulation", "boundaries"]
requires:
  - ".planning/phases/02-durable-data-jobs-and-assets/02-07-PLAN.md"
  - ".planning/phases/02-durable-data-jobs-and-assets/02-05-SUMMARY.md"
provides:
  - "No-provider local generation simulation Celery task"
  - "Worker durable job status/event/model-run updates through `caragent_core`"
  - "Worker boundary guard for API/provider imports"
  - "Corepack-compatible root test script execution"
key-files:
  created:
    - "services/worker/src/caragent_worker/tasks/jobs.py"
    - "services/worker/tests/test_job_tasks.py"
  modified:
    - "services/worker/src/caragent_worker/app.py"
    - "services/worker/src/caragent_worker/config.py"
    - "services/worker/tests/test_worker_app.py"
    - "package.json"
    - "scripts/validate-all.mjs"
key-decisions:
  - "The Phase 2 worker simulation is explicitly named `local-simulation` / `phase-2-no-provider` and records `external_calls: false`."
  - "Worker task tests call Celery task `.run()` with a SQLite database URL, avoiding a live worker while proving real task behavior."
  - "Root npm scripts use `corepack pnpm` so NVM-managed Node environments do not require a separate pnpm shim on PATH."
requirements-completed: ["DATA-02", "DATA-05", "DATA-06", "DATA-07"]
duration: "in-session"
completed: 2026-06-17
---

# Phase 2 Plan 07: Worker Durable Simulation Summary

Plan 02-07 added a Celery task that performs a clearly labeled no-provider local generation simulation and updates durable job state through the shared core services.

## Tasks Completed

| Task | Result | Evidence |
|------|--------|----------|
| Worker job task tests first | Complete | RED failed on missing `caragent_worker.tasks.jobs`; GREEN passed after implementation. |
| Local simulation task | Complete | Task moves jobs through running to succeeded, records model-run/cost data, and marks failed jobs with sanitized durable errors. |
| Worker app include | Complete | Celery includes both health and jobs task modules. |
| Boundary guard | Complete | Worker source test still forbids `caragent_api`, FastAPI, OpenAI, fal, BFL, and provider SDK imports while allowing `caragent_core`. |
| Root test script compatibility | Complete | Root scripts now invoke `corepack pnpm`, and `validate-all` retries pnpm commands through Corepack when bare pnpm is unavailable. |

## Verification

| Command | Result |
|---------|--------|
| `cd services/worker && uv run pytest -q tests/test_job_tasks.py` | RED first for missing module, then passed, `3 passed`. |
| `cd services/worker && uv run pytest -q` | Passed, `11 passed`. |
| `cd services/worker && uv run ruff check .` | Passed. |
| `cd services/worker && uv run mypy src tests` | Passed, no issues. |
| `corepack pnpm test` | Passed; web `13 passed`, core `21 passed`, API `23 passed`, worker `11 passed`, and contracts typecheck ran. |

## Deviations from Plan

**[Rule 1 - Test Infrastructure] Avoid pytest-asyncio dependency in worker**
- Found during: worker job test run.
- Issue: Worker project did not include pytest-asyncio, so async fixtures emitted pytest warnings treated as errors.
- Fix: Converted worker job tests to synchronous tests that call async setup/read helpers via `asyncio.run`.
- Verification: Worker job tests and full worker suite passed.

**[Rule 1 - Toolchain] Root scripts must not depend on bare pnpm**
- Found during: `corepack pnpm test`.
- Issue: The root `test` script called bare `pnpm`, which was not on PATH under the active NVM Node 22.15.0 shell.
- Fix: Updated root package scripts to call `corepack pnpm`, and added Corepack fallback to `scripts/validate-all.mjs`.
- Verification: `corepack pnpm test` passed.

## Not Run

`pnpm validate` was not used as 02-07 completion evidence because `.node-version` currently requires Node `24.15.0`, while this session is intentionally running under NVM Node `22.15.0` per the user instruction.

## Self-Check: PASSED

Worker durable simulation updates PostgreSQL-backed job state/events through `caragent_core`, records local model-run and zero-cost data without real provider calls, and keeps the API/provider boundary intact.

## Next

Ready for `02-08-PLAN.md`: minimal web refresh/resume and job-status proof.
