# Phase 23 Summary: Dispatch And Worker Reliability

## Completed

- Added `generation_jobs.state_version` and a durable `job_dispatch_outbox` ledger with pending, dispatched, and failed delivery metadata.
- Added core helpers for idempotent outbox creation, ready-dispatch listing, dispatched/failed marking, and conditional `queued -> running` worker claim.
- Added Alembic migration `9c6f1c1a7e3d_phase_23_dispatch_outbox.py`.
- Updated generation, iteration, and retry routes to create job plus outbox in one transaction, commit, then enqueue Celery and persist queue/outbox metadata.
- Updated the generation worker to claim jobs conditionally and commit running/progress/model-run state before provider calls.
- Added worker commit points so provider calls and object-storage writes are not wrapped in one long DB transaction.

## Tests Added

- Core tests for outbox idempotency, failed resend readiness, dispatched marking, and conditional claim state versioning.
- API test proving enqueue sees the committed job from a separate DB session and outbox is marked dispatched.
- Worker tests proving duplicate worker execution does not create a second output and provider-in-flight state is visible as running.
- Migration static test for the Phase 23 outbox migration.

## Files Touched

- `services/core/src/caragent_core/models.py`
- `services/core/src/caragent_core/repositories/jobs.py`
- `services/core/src/caragent_core/services/jobs.py`
- `services/api/alembic/versions/9c6f1c1a7e3d_phase_23_dispatch_outbox.py`
- `services/api/src/caragent_api/routes/generation.py`
- `services/api/tests/test_generation.py`
- `services/api/tests/test_migrations.py`
- `services/core/tests/test_jobs.py`
- `services/core/tests/test_models.py`
- `services/worker/src/caragent_worker/tasks/jobs.py`
- `services/worker/tests/test_generation_tasks.py`

## Notes

The API keeps the existing `queued` response shape by explicitly committing job/outbox before dispatch, then committing queue metadata after successful enqueue. A future dispatcher process can reuse `list_ready_job_dispatches()` for replay of pending or failed rows.
