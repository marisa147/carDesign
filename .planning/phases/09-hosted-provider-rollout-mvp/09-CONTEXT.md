# Phase 9: Hosted Provider Rollout MVP - Context

**Gathered:** 2026-06-18
**Status:** Ready for planning
**Mode:** auto-selected defaults from user "继续" after `$gsd-progress --next`

<domain>
## Phase Boundary

Phase 9 enables a controlled hosted image provider rollout behind the existing worker provider boundary. It must let users and operators test at least one real hosted image provider while preserving the V1 local deterministic path, cost controls, quota/rate guards, durable provider trace records, secret redaction, safe failure visibility, and default-off behavior.

This phase may extend configuration, provider capability metadata, API contracts, worker provider routing, operations status, workbench provider selection, tests, documentation, and smoke/UAT evidence. It must not implement targeted masked editing, reference-role guidance, 3D preview, enhanced handoff ZIP packages, marketplace/order flows, or production-ready wrap output.

</domain>

<decisions>
## Implementation Decisions

### Provider Choice And Rollout Shape

- **D-01:** Use BFL as the primary Phase 9 hosted provider candidate because the repo already has `BflImageProvider`, BFL env keys, tests, and operations status scaffolding. OpenAI and fal keys may remain documented placeholders, but Phase 9 should not add extra hosted providers unless needed to complete the BFL path safely.
- **D-02:** Treat the provider implementation as an adapter upgrade, not a direct vendor integration spread across API or UI code. Worker code calls `ImageProvider` implementations; API and web consume typed status and request contracts.
- **D-03:** Hosted provider details, model name, capability map, timeout, polling, retry, fallback, quota, rate limit, and cost ceiling stay config-driven. No provider model, price, or endpoint behavior should be assumed without re-checking official provider docs during planning.

### Enablement Gates And Preflight

- **D-04:** Hosted generation requires all of these gates before a real external call: `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=true`, `AI_PROVIDER_CALLS_ENABLED=true`, a supported non-local provider selected, provider credentials configured, and quota/rate/cost guard values present.
- **D-05:** API submission should run a lightweight preflight before enqueueing a hosted job so users do not queue obviously doomed hosted requests. The worker must repeat the authoritative preflight immediately before provider execution to protect against stale UI/API state.
- **D-06:** Local deterministic generation remains available without hosted credentials and bypasses hosted quota checks. Provider-off mode must still pass the existing deterministic smoke path.

### Per-Job Provider Selection

- **D-07:** Workbench provider selection should become a per-job intent, not only a process-wide worker default. Extend generation submission contracts to allow a safe provider/model/capability selection that is persisted on the job and/or metadata, then have the worker route from that persisted intent with config defaults as fallback.
- **D-08:** Browser-visible controls may expose provider names, active mode, quota/cost warnings, and blocked reasons, but must never expose API keys, raw provider payloads containing secrets, database URLs, Redis URLs, S3 secrets, or bearer tokens.
- **D-09:** If the user selects hosted generation while gates are incomplete, the UI should show a blocked state and keep the submit path deterministic/local rather than silently attempting hosted calls.

### Capability Map And Cost Policy

- **D-10:** Introduce a typed `ProviderCapabilityMap`/`HostedProviderConfig` style contract that records provider name aliases, supported operations, image size/model defaults, estimated cost, supports references/masks flags for later phases, timeout/polling defaults, and user-safe caveats.
- **D-11:** Use estimated cost from config/capability metadata for preflight and model-run records. Record actual cost only when a provider response or trusted adapter calculation can provide it; do not write fake actual hosted cost as if it were billed truth.
- **D-12:** Future Phase 10/11 capabilities such as masks and references may be represented as capability flags now, but unsupported capabilities must remain warnings/blocked reasons, not partially implemented hidden behavior.

### Trace Persistence And Failure Visibility

- **D-13:** Keep `model_runs` as the canonical provider-call trace: provider, model, prompt text, prompt payload, parameters, input artifact ids, estimated cost, actual cost when available, status, output artifact id, and sanitized error message.
- **D-14:** Persist hosted route/fallback metadata consistently on model runs, artifacts, design versions, job operations metadata, and job events when relevant. Fallback from hosted to local must be visible rather than indistinguishable from a normal local generation.
- **D-15:** Normalize hosted failures into user-safe categories. Existing categories cover provider, provider_configuration, timeout, storage, validation_rights, canceled, and unknown; add or map moderation/safety/validation rejection explicitly if provider responses distinguish them.
- **D-16:** Secret redaction is mandatory at every boundary: provider exceptions, job latest_error, model_run.error_message, job event metadata, operations recent failures, and workbench diagnostic rendering.

### UI And Operations Experience

- **D-17:** Add hosted provider UX inside the existing workbench surface instead of building a separate admin dashboard. A provider selector/callout belongs near generation controls or progress/operations status, with compact cost/quota/blocked-state visibility.
- **D-18:** The operations status API should expose capability/guard information needed by the UI: active mode, supported providers, default provider, hosted enabled flag, feature flag state, credential configured booleans, quota/rate/cost guard state, and recent sanitized failures.
- **D-19:** UI copy must keep the product boundary clear: hosted generation is a concept-preview assist feature, not production-ready wrap output and not a guarantee of copyright or model quality.

### Verification And Smoke

- **D-20:** Use TDD for Phase 9 behavior that changes routing, preflight, contracts, cost persistence, failure mapping, and UI state. Start with focused failing tests before implementation for each plan.
- **D-21:** Required verification includes API config/operations/generation tests, worker provider/generation tests, web provider selector/progress tests, OpenAPI contract generation/check, `pnpm validate`, provider-off smoke, and a documented manual provider-on smoke path.
- **D-22:** Manual provider-on smoke must require explicit local credentials and small quota/cost guard values. It should be documented and skippable in default validation so CI/local dev does not make external calls accidentally.

### the agent's Discretion

- Exact schema names, endpoint shape, UI placement, and capability map storage format may be chosen during planning if they respect the decisions above.
- Planner may split BFL official API verification into a research task before adapter changes.
- Planner may decide whether API preflight is a dedicated endpoint, inline validation inside submit generation, or both, as long as the UI gets clear blocked reasons and the worker remains authoritative.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase Scope

- `.planning/ROADMAP.md` — Phase 9 goal, success criteria, plan list, V2 compatibility rules, UI additions, acceptance flow, and risk register.
- `.planning/REQUIREMENTS.md` — V2-PROVIDER-01 through V2-PROVIDER-05 and traceability.
- `.planning/PROJECT.md` — V2 milestone constraints, provider boundary, hosted provider caveats, and product non-goals.
- `.planning/STATE.md` — Current milestone state, blockers/concerns, and deferred scope.
- `.planning/phases/08-v1-closure-and-v2-readiness-gate/08-CONTEXT.md` — Default-off V2 flags, compatibility gate, local-only safety anchor, and hosted-provider boundary carried from Phase 8.
- `.planning/phases/08-v1-closure-and-v2-readiness-gate/08-READINESS-BASELINE.md` — Phase 8 baseline and command inventory.
- `.planning/phases/08-v1-closure-and-v2-readiness-gate/08-VERIFICATION.md` — Latest Phase 8 validation evidence.

### Provider And Worker Code

- `services/worker/src/caragent_worker/providers/base.py` — Image provider protocol, normalized request/result, provider errors, secret sanitization.
- `services/worker/src/caragent_worker/providers/__init__.py` — Provider selection and current BFL/local routing.
- `services/worker/src/caragent_worker/providers/bfl.py` — Current BFL adapter scaffold that must be verified against official docs.
- `services/worker/src/caragent_worker/providers/local.py` — Local deterministic provider and metadata behavior.
- `services/worker/src/caragent_worker/config.py` — Worker provider, retry, fallback, quota, cost, BFL endpoint, secrets, and V2 flag settings.
- `services/worker/src/caragent_worker/tasks/jobs.py` — Generation pipeline, prompt planning, rights check, hosted preflight, provider execution, fallback, persistence, cancellation, and failure mapping.
- `services/worker/tests/test_image_providers.py` — Existing provider adapter selection and BFL mock tests.
- `services/worker/tests/test_generation_tasks.py` — Existing worker preflight, fallback, cost, failure, rights, cancellation, and persistence tests.

### API, Contracts, And Ledger

- `services/api/src/caragent_api/config.py` — API provider flags, quota/cost settings, secrets, and non-local config validation.
- `services/api/src/caragent_api/routes/generation.py` — Generation job submission and iteration submission contracts.
- `services/api/src/caragent_api/routes/jobs.py` — Job, event, version, artifact, model-run, feedback, and export API surfaces.
- `services/api/src/caragent_api/routes/operations.py` — Operations/provider status summary and recent failures.
- `services/api/src/caragent_api/schemas.py` — Pydantic request/response schemas that generate TypeScript contracts.
- `services/core/src/caragent_core/models.py` — Durable ledger tables including generation_jobs, job_events, design_versions, artifacts, model_runs.
- `services/core/src/caragent_core/services/jobs.py` — Job/model-run/artifact/version persistence and error sanitization helpers.
- `services/core/src/caragent_core/enums.py` — Failure categories and job/model run statuses.
- `packages/contracts/openapi/openapi.json` — Generated OpenAPI artifact to update through contract generation.
- `packages/contracts/src/generated/client.ts` — Generated TypeScript client consumed by the web app.

### Web Workbench

- `apps/web/src/lib/config/public-env.ts` — Browser-safe public feature flags.
- `apps/web/src/components/workbench/workbench-app.tsx` — Current generation submission, refresh, and workbench composition.
- `apps/web/src/components/workbench/progress-panel.tsx` — Current operations status and provider failure visibility.
- `apps/web/src/components/workbench/parameter-panel.tsx` — Likely provider selector placement near generation parameters.
- `apps/web/src/lib/api/generation.ts` — Web generation API wrapper.
- `apps/web/src/lib/api/operations.ts` — Web operations status wrapper.
- `apps/web/src/app/page.test.tsx` — Integrated workbench behavior tests.

### Validation And Docs

- `package.json` — Root scripts for validate, contracts, smoke, infra, and Phase 8 gates.
- `scripts/check-v1-compatibility.mjs` — V1 compatibility gate to preserve while extending contracts.
- `scripts/check-migration-safety.mjs` — Migration safety gate.
- `scripts/validate-all.mjs` — Aggregate validation sequence.
- `scripts/smoke-local.mjs` — Local deterministic infrastructure smoke.
- `scripts/smoke-worker-queue.mjs` — Worker queue smoke path.
- `.env.example`, `services/api/.env.example`, `services/worker/.env.example`, `apps/web/.env.example` — Provider, guard, and V2 flag env documentation.
- `README.md` — Developer command index and quickstart.
- `docs/development.md` — Local runbook, provider guardrails, smoke, UAT, and troubleshooting.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `ImageProvider`, `ImageGenerationRequest`, and `ImageGenerationResult` already provide a narrow worker adapter boundary for local and hosted providers.
- `BflImageProvider` already handles submit, poll, result download, bounded timeout, and error sanitization via `httpx.MockTransport` tests, but its payload/endpoint assumptions need current official-doc verification.
- `WorkerSettings` already includes provider calls enabled, provider model/default, retry/fallback, BFL base/path settings, hosted quota/rate/cost guards, provider keys, and Phase 8 V2 flags.
- `_enforce_hosted_preflight` in worker already blocks missing quota/rate/cost guards and counts recent hosted `model_runs` for daily/minute limits.
- The ledger already has `GenerationJob`, `JobEvent`, `ModelRun`, `Artifact`, and `DesignVersion` fields needed for provider/model/cost/prompt/parameters/error tracing.
- `ProviderOperationsSummary` and `ProgressPanel` already show active provider mode, guard summaries, recent classified failures, and sanitized diagnostics.

### Established Patterns

- API schemas in `services/api/src/caragent_api/schemas.py` generate TypeScript contracts; any Phase 9 request/response change must go through `pnpm contracts:check`.
- PostgreSQL/object storage are canonical. Redis/Celery are execution mechanics, not the source of truth for provider state.
- Worker tasks update durable job status/events/model runs and only then return task results.
- Hosted calls are disabled by default. Local deterministic generation must remain the no-credential baseline.
- Web UI keeps operations status inside the workbench/progress flow rather than a separate ops console.

### Integration Points

- Per-job provider selection will likely touch `GenerationJobSubmissionRequest`, `submit_generation_job`, `submit_generation_iteration_job`, web generation wrappers, generated contracts, worker job routing, and workbench tests.
- Provider capability map can live in core/worker-safe typed config first, then be reflected through API operations status for browser-safe display.
- Cost and fallback evidence should be written through existing job/model-run services before UI reads it from job state, model-run list, events, and operations status.
- Failure categories may need enum/schema updates if moderation or validation rejection is represented separately from provider/provider_configuration.

</code_context>

<specifics>
## Specific Ideas

- Prefer a boring, tightly guarded BFL rollout over adding multiple providers.
- Hosted provider smoke should be explicit, manual, and cheap by construction; default CI/local validation must not spend money.
- Use "concept preview" labeling anywhere the hosted feature is visible.
- If provider docs disagree with the current BFL adapter shape, planning should prioritize adapter correctness over preserving the scaffold.

</specifics>

<deferred>
## Deferred Ideas

- Targeted mask-aware edits and region/layer selection — Phase 10.
- Reference role assignment and provider-specific reference usage — Phase 11.
- Lightweight 3D preview and screenshots — Phase 12.
- Enhanced handoff ZIP/package export — Phase 13.
- Production rollout, commercial/legal readiness, and print-ready wrap delivery — future milestones beyond v2.0.

</deferred>

---

*Phase: 09-hosted-provider-rollout-mvp*
*Context gathered: 2026-06-18*
