# Phase 23 Verification

## Automated Verification

Passed:

- `cd services/core && uv run pytest -q tests/test_models.py tests/test_jobs.py`
- `cd services/core && uv run ruff check src tests/test_models.py tests/test_jobs.py`
- `cd services/api && uv run pytest -q tests/test_generation.py tests/test_migrations.py`
- `cd services/api && uv run ruff check src tests/test_generation.py tests/test_migrations.py`
- `cd services/worker && uv run pytest -q tests/test_generation_tasks.py tests/test_job_tasks.py`
- `cd services/worker && uv run ruff check src tests/test_generation_tasks.py tests/test_job_tasks.py`
- `cd services/core && uv run mypy src`
- `cd services/api && uv run mypy src`
- `cd services/worker && uv run mypy src`
- `cd services/core && uv run pytest -q`
- `cd services/api && uv run pytest -q`
- `cd services/worker && uv run pytest -q`
- `corepack pnpm validate`

## Requirement Evidence

| Requirement | Evidence |
|-------------|----------|
| RELY-01 | API test `test_submit_generation_job_dispatches_only_after_commit_and_marks_outbox` opens a separate session inside enqueue and reads the committed job. |
| RELY-02 | `JobDispatchOutbox` model, migration, and core tests cover pending, failed, dispatched, idempotent duplicate creation, and ready replay listing. |
| RELY-03 | `jobs.claim_queued_job()` uses conditional update on `status == queued`; core and worker tests prove duplicate execution does not create a second output. |
| RELY-04 | Worker commits claim/progress/model-run state before provider calls and commits again before object storage writes; focused worker tests pass. |
| RELY-05 | Worker in-flight provider test reads running job state, prompt event, and running model run from another session while provider is blocked. |

## Manual UAT

No browser UAT was required for Phase 23 because the work is backend reliability and queue consistency. Phase 21 browser UAT remains the user-visible generation-loop checklist.
