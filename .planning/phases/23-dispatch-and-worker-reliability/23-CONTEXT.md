# Phase 23 Context: Dispatch And Worker Reliability

## Goal

Remove the remaining generation reliability gaps: API job creation must not enqueue before commit, dispatch must be durable and replayable, workers must claim queued jobs atomically, and long provider calls must not hold a database transaction open.

## Requirements

- RELY-01: Generation, iteration, and retry creation cannot enqueue Celery before the job transaction is committed.
- RELY-02: A durable `job_dispatch_outbox` records pending job delivery and supports idempotent resend.
- RELY-03: Worker claims queued jobs with a conditional state transition so duplicate workers cannot both run the same job.
- RELY-04: Worker commits running, progress, failure, success, model run, artifact, and version state in short units of work.
- RELY-05: API-visible job events reflect worker progress while provider calls are still in flight.

## Current Implementation Notes

- `services/api/src/caragent_api/routes/generation.py` creates a job and immediately calls `queue.enqueue_generation_job()` inside the request-scoped transaction.
- `services/api/src/caragent_api/queue.py` owns Celery dispatch.
- `services/worker/src/caragent_worker/tasks/jobs.py` currently runs `run_generate_2d_concept_job()` inside one `session_scope()`, so `running` and progress events commit only after the task returns.
- `GenerationJob` has no state version today.
- `services/core/src/caragent_core/services/jobs.py` is the right place for shared job/outbox/claim helpers.

## Non-Goals

- Do not replace Celery.
- Do not change provider selection or hosted provider guards beyond what short transactions require.
- Do not add hosted Redis quota/rate-limit work; that is Phase 26.
- Do not change the frontend polling contract from Phase 21.
