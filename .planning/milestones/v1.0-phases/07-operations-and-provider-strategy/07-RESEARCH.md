---
phase: 7
slug: operations-and-provider-strategy
type: research
status: complete
created: 2026-06-18
---

# Phase 7 - Operations And Provider Strategy Research

## Scope

Phase 7 hardens the current v1 generation loop after Phase 6 proved the PreviewSpec path end to end. The phase is about operations, not production deployment: provider configuration, worker/queue visibility, failure classification, cancellation, retry/fallback controls, and quota/rate-limit preflight.

Hosted provider behavior is time-sensitive. This research intentionally avoids locking current hosted provider pricing, product names, or policy details. Before enabling any non-local provider in a real environment, the implementer must re-check current official provider docs and account access.

## Current Code Facts

### Durable Job Ledger

- `GenerationJob`, `JobEvent`, and `ModelRun` already exist in `services/core/src/caragent_core/models.py`.
- Job status already includes `queued`, `running`, `succeeded`, `failed`, and `canceled` in `services/core/src/caragent_core/enums.py`.
- `GenerationJob.metadata_json` and `JobEvent.metadata_json` already provide a no-migration place for structured operational metadata.
- API responses currently omit job/event metadata, so structured failure categories cannot yet be inspected through the API/web client.
- `jobs.transition_job_status()` appends events but cannot yet attach metadata to that transition event.

### Queue And Worker

- API enqueues generation tasks through `CeleryQueueClient` in `services/api/src/caragent_api/queue.py`.
- Queue task ids are returned to the API but are not persisted on the job, so later cancel/revoke cannot address a specific Celery task.
- Worker health exists as `caragent_worker.worker_health`, but it returns a static payload and does not expose worker version, provider configuration summary, or registered generation capability.
- Phase 6 UAT found a stale long-running worker process executing old code. Phase 7 must make the active worker/runtime path visible through job events, queue inspection, or smoke evidence.
- On local Windows, Celery prefork is unstable in this environment; the known safe local command uses `--pool=solo --concurrency=1`.

### Provider Boundary

- `select_image_provider()` routes to BFL only when `AI_PROVIDER_DEFAULT` is `bfl` or `black-forest-labs` and `AI_PROVIDER_CALLS_ENABLED=true`.
- Otherwise it returns `LocalDeterministicImageProvider`.
- `BflImageProvider` has bounded polling and secret redaction, but retry/fallback behavior is not orchestrated around provider attempts.
- Provider exceptions are normalized into `ImageProviderError`, `ImageProviderConfigurationError`, and `ImageProviderTimeoutError`.
- Worker failure handling currently sanitizes all failures but does not classify provider/configuration/rights/storage/queue/timeout separately.

### Frontend Surface

- The workbench already has `ProgressPanel`, version history, and future gates.
- `ProgressPanel` already renders current job status, recent events, latest error, refresh, and retry.
- There is no separate operations surface and Phase 7 should not create a large admin app for v1.

## Architecture Approach

Use the existing durable ledger as the source of truth:

- Add small core helpers and enums for failure categories and job/event metadata.
- Expose metadata through typed FastAPI/Pydantic response schemas.
- Add a typed operations endpoint for provider config/capabilities, queue inspection, and recent failures.
- Store queue task ids in job metadata when a generation task is enqueued.
- Implement cancellation by durable state first, then Celery revoke best-effort when a task id is known.
- Make worker provider attempts explicit with model runs and job events.
- Keep local deterministic generation the default and require explicit hosted-provider controls before non-local calls.

No new database tables are required for v1 Phase 7. Existing JSON metadata is sufficient and keeps the plan compatible with prior migrations.

## Plan Breakdown

| Plan | Purpose | Main Requirements |
|------|---------|-------------------|
| 07-01 | Core operational metadata contract and API response visibility | OPS-01, OPS-02, OPS-04 |
| 07-02 | Provider/worker health and operations API | OPS-01, OPS-04 |
| 07-03 | Failure classification and structured worker events | OPS-02, OPS-04 |
| 07-04 | Job cancellation and queue revoke handoff | OPS-05, OPS-04 |
| 07-05 | Provider routing, bounded retries, and visible fallback | OPS-03, OPS-02, OPS-04 |
| 07-06 | Hosted-call quota and rate-limit preflight | OPS-06, OPS-03 |
| 07-07 | Workbench operations UI, docs, smoke, and UAT closure | OPS-01..OPS-06 |

## Key Risks

| Risk | Mitigation |
|------|------------|
| Stale worker still consumes queue tasks | Worker/job events include worker version/config metadata; final smoke proves a current worker consumes a queued job. |
| Provider secrets leak through failures | Preserve `sanitize_provider_error()` and add tests for event/job/model-run metadata redaction. |
| Cancellation promises more than Celery/provider can interrupt | API copy and status semantics say queued cancellation is reliable; running cancellation is best-effort but durable. |
| Fallback hides provider failures | Every attempt creates a failed model run/event before fallback. Successful fallback metadata records `fallback_from_provider`. |
| Hosted provider calls run without cost controls | Hosted route preflight blocks when provider calls are enabled but quota/rate guards are not configured. |
| Operations UI becomes a large admin surface | Reuse the current workbench progress/future-gate areas and keep copy factual. |

## Research Result

Phase 7 can be implemented incrementally without schema migrations:

1. Use `metadata_json` for operational fields.
2. Expose metadata through typed schemas and generated contracts.
3. Add operations endpoints and queue inspection around the existing Celery boundary.
4. Harden the worker attempt lifecycle and local smoke.

The only provider-specific implementation path in v1 remains the existing BFL adapter plus local deterministic fallback. Current BFL details must be re-verified from official docs before enabling hosted calls outside local/testing.
