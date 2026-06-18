# Phase 7: Operations And Provider Strategy - Context

**Gathered:** 2026-06-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 7 hardens the existing generation system so operators can see provider and worker health, understand failures, configure provider routing/fallback/retry/timeouts/rate limits, cancel eligible jobs, and prevent expensive provider calls from running without explicit controls.

This phase does not add authentication, billing, production deployment, marketplace/community flows, broad provider marketplace support, print-ready export, or true 3D. Hosted provider calls remain opt-in and must be re-verified against current provider docs/terms during research before any non-local rollout.

</domain>

<decisions>
## Implementation Decisions

### Operational Priority
- **D-01:** Prioritize local/development operational correctness first: truthful health, clear failure classification, queue/worker visibility, and durable job state. Do not optimize for a large production ops console in v1.
- **D-02:** Treat PostgreSQL job rows, job events, model runs, and artifact/version records as the durable source of truth. Redis/Celery state can be observed but must not become canonical.
- **D-03:** Add explicit visibility for stale worker or runtime drift. Phase 6 UAT found a long-running worker process using old code; Phase 7 should make that visible through health/capability/version checks or a worker self-report event.

### Provider Enablement
- **D-04:** Keep local deterministic generation as the default provider path. Hosted calls stay disabled unless `AI_PROVIDER_CALLS_ENABLED=true` and provider-specific secrets/config are present.
- **D-05:** Start with the existing BFL adapter as the only concrete hosted adapter unless research proves another provider is ready to implement. Existing OpenAI/FAL env names remain placeholders unless corresponding adapters are explicitly planned.
- **D-06:** Provider/model names, timeouts, poll intervals, max attempts, and routing behavior must stay config-driven. Do not hard-code provider choices into API or frontend code.
- **D-07:** Provider errors must be sanitized before storing or showing them. Existing secret redaction in worker/provider code is a required pattern to preserve.

### Failure And Retry Strategy
- **D-08:** Classify failures at least into provider, provider configuration, validation/rights, storage, queue/worker, canceled, timeout, and unknown categories.
- **D-09:** Retries should be bounded and explicit. Retry failed jobs by creating a new durable attempt; do not overwrite the failed job or hide the original failure.
- **D-10:** Fallback behavior must be visible, not silent. If a hosted provider fails and the system falls back to local deterministic generation, the job/model-run metadata and UI/API status should say so.
- **D-11:** Timeouts and transient provider failures can be retried according to config. Validation, rights, missing secret/config, and unsupported provider errors should fail fast.

### Cancellation And Quotas
- **D-12:** Cancellation should first support queued jobs reliably. Running job cancellation can be best-effort and should produce a durable final state even if the provider call cannot actually be interrupted.
- **D-13:** Quota/rate-limit checks must run before expensive hosted provider calls. Local deterministic mode can bypass monetary quota while still recording cost fields as zero.
- **D-14:** Phase 7 should implement operational quota/rate-limit hooks, not full billing or user credit purchase flows.

### Operator/User Surface
- **D-15:** Use small, typed API surfaces and existing workbench panels before adding a separate admin app. Provider health, recent failures, retry/cancel status, and config summaries can appear in the current operational/progress surfaces.
- **D-16:** UI copy must remain truthful: show configured/unavailable/disabled states instead of implying production provider readiness.
- **D-17:** Logs/events should be structured enough for debugging but must not leak secrets, prompt payloads beyond existing durable model-run records, or provider tokens.

### Windows Local Runtime
- **D-18:** Document or encode the Windows worker runtime path. Celery default prefork is unstable in this environment; local Windows worker startup should use `--pool=solo` or an equivalent safe setting.
- **D-19:** Docker smoke remains the baseline infrastructure proof, but Phase 7 should add a live queue/worker smoke that verifies a queued generation task is actually consumed by the running worker with current code.

### the agent's Discretion
- Exact endpoint names and response schema details are up to the planner, as long as FastAPI/Pydantic remains the contract source and TypeScript contracts are regenerated.
- Exact UI placement is flexible, but it should reuse the existing workbench/progress/future-gate surfaces and avoid a large new dashboard unless clearly justified.
- Retry backoff math and rate-limit storage details can be selected during research/planning, provided behavior remains deterministic and testable in local mode.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope And Requirements
- `.planning/ROADMAP.md` - Phase 7 goal, requirements, dependencies, and v1 boundary.
- `.planning/REQUIREMENTS.md` - OPS-01 through OPS-06 and out-of-scope production/auth/billing boundaries.
- `.planning/STATE.md` - Current project position and Phase 6 carry-forward notes.
- `.planning/phases/06-itasha-and-template-intelligence/06-VERIFICATION.md` - Evidence from Phase 6, including worker restart/stale-code finding.
- `.planning/phases/06-itasha-and-template-intelligence/06-HUMAN-UAT.md` - Browser UAT issue notes relevant to worker/runtime operations.

### Existing Runtime And Provider Code
- `services/worker/src/caragent_worker/config.py` - Worker provider, timeout, polling, Redis, and secret settings.
- `services/worker/src/caragent_worker/app.py` - Celery worker app, queue name, and task registration.
- `services/worker/src/caragent_worker/providers/__init__.py` - Provider selection boundary and local-vs-hosted routing.
- `services/worker/src/caragent_worker/providers/base.py` - Provider request/result contracts, normalized errors, and secret sanitization.
- `services/worker/src/caragent_worker/providers/bfl.py` - Existing hosted provider adapter behavior, polling, timeout, and error handling.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Worker generation lifecycle, job transitions, model-run records, artifact/version writes, rights checks, and failure handling.
- `services/api/src/caragent_api/queue.py` - API-to-Celery queue client and task dispatch.
- `services/api/src/caragent_api/routes/generation.py` - Job submission, retry, and iteration routes.
- `services/api/src/caragent_api/routes/jobs.py` - Job/event/version/artifact/model-run/list/export APIs.

### Docs And Runbooks
- `README.md` - Local command index and concept-preview/product boundaries.
- `docs/development.md` - Current local runbook, validation/smoke commands, provider configuration notes, and UAT boundaries.
- `scripts/smoke-local.mjs` - Existing Docker and local deterministic smoke flow.
- `scripts/validate-all.mjs` - Aggregate validation gate and host/toolchain checks.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `GenerationJob.status`, `latest_error`, and `JobEvent` already provide a durable status/event ledger for operational views.
- `ModelRun.status`, `parameters`, `prompt_payload`, `input_artifact_ids`, `error_message`, and cost fields already capture provider-run traceability.
- `sanitize_provider_error()` and `_provider_secrets()` provide the current secret-redaction pattern.
- `WorkerSettings` already contains provider enablement, provider default, provider secrets, timeouts, polling, and local image dimensions.
- `CeleryQueueClient` already centralizes queue dispatch from API to worker.
- Workbench progress/history panels already render job/events/version/export state and should be reused for small operational additions.

### Established Patterns
- API owns typed contracts and OpenAPI export; frontend consumes generated TypeScript contracts.
- Worker calls provider adapters; vendor SDK/API details should not leak into API/frontend/core.
- Jobs are append/transition based. Retrying creates a new job instead of mutating the failed one into success.
- Missing rights and validation errors should block before provider execution.
- Local deterministic generation is the default verification path and records `external_calls=false`.

### Integration Points
- Add provider/worker health or capability endpoints under API routes, backed by typed Pydantic schemas.
- Add cancellation routes near existing job routes and update durable job/event state.
- Add quota/rate-limit preflight before worker provider execution or before API queueing, depending on whether the control is user/workspace based or provider-call based.
- Extend worker tests around provider error classification, cancellation/fallback, and quota preflight.
- Extend web tests only where the existing workbench/progress surface changes.

</code_context>

<specifics>
## Specific Ideas

- Use Phase 6's stale worker incident as a concrete acceptance case: local operator should be able to tell whether the live worker is current and consuming queue jobs.
- Keep Windows local worker guidance practical: `--pool=solo` is the known stable path in this environment.
- Provider operations should feel like a quiet runbook/control surface, not a marketing dashboard.
- Hosted provider details are time-sensitive. During research/planning, verify current official provider docs before implementing or documenting non-local hosted behavior.

</specifics>

<deferred>
## Deferred Ideas

- Authentication and per-user accounts remain outside v1 unless explicitly promoted.
- Billing, credit purchase, payment, and commercial order flow remain out of scope.
- Production deployment, CI/CD release pipelines, and hosted infrastructure rollout remain out of scope unless separately added.
- Broad provider marketplace/support matrix remains out of scope; Phase 7 should harden current/provider-configurable paths first.

</deferred>

---

*Phase: 07-operations-and-provider-strategy*
*Context gathered: 2026-06-18*
