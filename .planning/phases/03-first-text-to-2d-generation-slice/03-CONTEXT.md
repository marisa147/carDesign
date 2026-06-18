# Phase 3: First Text-To-2D Generation Slice - Context

**Gathered:** 2026-06-17
**Status:** Ready for planning
**Mode:** auto-selected defaults

<domain>
## Phase Boundary

Phase 3 turns a user-provided natural-language pain-car design request into a reusable structured brief, creates a prompt plan, runs an asynchronous text-to-2D generation job, stores the exact provider/model/prompt trace, persists at least one generated 2D concept artifact, links it to a design version, and exposes clear failure/retry behavior.

This phase is not the full workbench UI. It should provide enough API/contract/minimal proof to satisfy `GEN-01` through `GEN-07`, but GPT-style chat, rich parameter editing UI, upload manager UX, progress timeline, preview workspace, variant history, export UX, itasha safe-zone intelligence, deterministic text/logo overlays, quotas, dashboards, cancellation, and true 3D remain later-phase scope.
</domain>

<decisions>
## Implementation Decisions

### Brief Capture And Structured Payload

- **D-03-01:** Accept a natural-language design request as the source of truth for the first generation slice, then convert it into a structured design brief stored in the existing `design_briefs` ledger.
- **D-03-02:** Keep Phase 3 brief parsing deterministic and inspectable unless current research proves a small AI parsing adapter is worth the added risk. The stored brief must include at least vehicle/template, view, character/theme, style, palette, text, coverage, and reference asset ids where provided.
- **D-03-03:** Brief review/edit/reuse can be API-level and minimal UI-proof level in this phase. A rich parameter panel belongs to Phase 4.
- **D-03-04:** Structured brief schemas should be typed in Pydantic and mirrored through generated TypeScript contracts. Avoid loose arbitrary payloads for new Phase 3 API contracts, even though Phase 2 stored JSON payloads.

### Vehicle Template And View Scope

- **D-03-05:** Start with one supported 2D vehicle template and one default supported view, preferably a generic side-view coupe/sedan concept template. Broad vehicle model coverage and template intelligence remain out of scope.
- **D-03-06:** Store template id, template label, supported view, canvas intent, and any minimal preview hints in the brief/prompt payload so Phase 6 can harden template/safe-zone data later without changing the generation ledger.
- **D-03-07:** If a user asks for an unsupported vehicle or view, normalize to the supported template/view with a clear warning in job events or response metadata instead of pretending broad support exists.

### Provider Strategy And Local Determinism

- **D-03-08:** All provider calls must go through internal provider adapter interfaces. Do not scatter vendor SDK calls through routes, core services, or worker tasks.
- **D-03-09:** Provider and model names stay configuration-driven. Phase 3 planning and research must re-check current official provider documentation before locking exact adapters/models because model availability, pricing, account access, and safety behavior change over time.
- **D-03-10:** Local/test mode must remain deterministic and external-call-free. Provide a local image generator/provider adapter that creates a valid concept artifact for tests, contract checks, Docker smoke, and no-key development.
- **D-03-11:** Hosted provider execution must be gated by explicit runtime settings such as `AI_PROVIDER_CALLS_ENABLED=true` and required provider API keys. Missing keys should fail early with clear configuration errors, not ambiguous worker crashes.

### Async Generation Pipeline

- **D-03-12:** The API creates or reuses durable jobs through the Phase 2 idempotency path, then the worker performs prompt planning, provider execution, artifact persistence, model-run updates, version creation, and job status transitions.
- **D-03-13:** Expensive generation must never run synchronously inside FastAPI request handlers. HTTP routes should validate input, create durable records, enqueue work where applicable, and return pollable job state.
- **D-03-14:** Job events should make the pipeline understandable: brief accepted, prompt planned, provider/model selected, generation running, artifact stored, design version created, succeeded, failed, or retry queued.
- **D-03-15:** The existing Phase 2 no-provider simulation can be replaced or complemented by a Phase 3 local generation task, but the local provider must create real artifact/version/model-run records, not only a succeeded job marker.

### Prompt And Traceability

- **D-03-16:** Store exact prompt text, structured prompt payload, provider, model, parameters, input artifact ids, and estimated/actual cost where available in `model_runs`.
- **D-03-17:** Prompt planning should be explicit and auditable: include the user's original request, normalized brief fields, vehicle template/view constraints, reference asset metadata, and safety/rights notes where relevant.
- **D-03-18:** Do not log secrets, raw API keys, or oversized binary/provider payloads in job events, model-run errors, or application logs. Store only sanitized user-visible errors and trace metadata.

### Artifacts, Design Versions, And Storage

- **D-03-19:** Generated 2D concept images are immutable object-storage artifacts with `kind=generated_image`, content type, byte size, checksum where practical, dimensions, job id, workspace id, and design version link.
- **D-03-20:** Each successful first-generation job creates a `DesignVersion` with `status=generated`, linked to the brief and job. Later iteration/lineage behavior remains Phase 5.
- **D-03-21:** A generated artifact should include enough metadata for later preview/export work, but Phase 3 does not need a polished preview canvas or export manifest.

### Reference Assets And Rights Gate

- **D-03-22:** Reference asset ids may be included in a generation request only when the assets belong to the workspace and have rights metadata confirmed enough for generation use.
- **D-03-23:** Asset source/rights warnings should be surfaced as validation errors or job events. Do not silently send missing-rights assets to a provider.
- **D-03-24:** Uploaded logo/text exact-rendering controls remain Phase 6; Phase 3 can include them in the prompt and trace but should not promise deterministic overlay quality.

### Failure And Retry Behavior

- **D-03-25:** Provider, validation, storage, and unknown failures should lead to durable `failed` job state with a sanitized `latest_error` and readable error event.
- **D-03-26:** Retry of eligible failed generation should reuse the original brief and create a new durable job/idempotency key or explicit retry record without overwriting the failed job, prompt trace, or prior artifacts.
- **D-03-27:** Duplicate requests with the same workspace/idempotency key should keep returning the original durable job, preserving Phase 2 duplicate-work protection.

### Validation And Proof

- **D-03-28:** Tests must cover brief parsing/normalization, unsupported template/view handling, prompt planning trace, provider adapter gating, local deterministic artifact generation, job event ordering, failure paths, retry behavior, contract generation, and worker/API boundaries.
- **D-03-29:** Docker smoke should prove the Phase 3 local generation path end-to-end against PostgreSQL, Redis, and MinIO without external provider keys.
- **D-03-30:** Optional hosted-provider smoke may exist behind explicit env flags, but it must not be required for normal validation.

### The Agent's Discretion

- The planner may split Phase 3 into multiple plans across schemas, brief APIs, prompt planning, provider adapters, worker execution, contracts, minimal frontend proof, and verification.
- The planner may choose whether to add dedicated typed brief tables/columns or keep the Phase 2 `design_briefs.payload` JSON with strict Pydantic schemas at service/API boundaries, provided traceability and contract clarity are not weakened.
- The planner may choose the local deterministic image implementation, such as Pillow-generated PNG, as long as tests can verify actual bytes/dimensions and object storage persistence.
- The planner may decide whether Phase 3 needs a tiny web proof or whether API/contract/Docker smoke is sufficient, but it must not drift into the full Phase 4 workbench.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Definition

- `.planning/PROJECT.md` - Project vision, MVP boundary, stack direction, and non-goals.
- `.planning/REQUIREMENTS.md` - Phase 3 requirements `GEN-01` through `GEN-07` and v1/v2 boundaries.
- `.planning/ROADMAP.md` - Phase 3 goal, dependency on Phase 2, success criteria, and later phase boundaries.
- `.planning/STATE.md` - Current project state, recent Phase 2 completion, and provider/model validation concern.
- `AGENTS.md` - Project-local workflow, architecture, stack, and GSD constraints.

### Prior Phase Outputs

- `.planning/phases/01-foundation-and-contracts/01-CONTEXT.md` - Foundation decisions for monorepo, API, worker, contracts, local infra, and validation.
- `.planning/phases/01-foundation-and-contracts/01-VERIFICATION.md` - Verified foundation evidence and host notes.
- `.planning/phases/02-durable-data-jobs-and-assets/02-CONTEXT.md` - Durable data, job, artifact, model-run, and worker boundary decisions.
- `.planning/phases/02-durable-data-jobs-and-assets/02-VERIFICATION.md` - Verified Phase 2 evidence, Docker smoke, live browser UAT, and known out-of-scope items.
- `.planning/phases/02-durable-data-jobs-and-assets/02-VALIDATION.md` - Phase 2 validation architecture and durable data proof expectations.

### Current Code Integration Points

- `services/core/src/caragent_core/models.py` - Durable tables for workspaces, messages, design briefs, jobs, events, model runs, artifacts, and design versions.
- `services/core/src/caragent_core/enums.py` - Existing status/kind enums for jobs, model runs, artifacts, and design versions.
- `services/core/src/caragent_core/services/workspaces.py` - Workspace/message/brief service boundary to extend or wrap for typed brief creation.
- `services/core/src/caragent_core/services/jobs.py` - Durable job, event, model-run, artifact, version, feedback, and export service boundary.
- `services/api/src/caragent_api/schemas.py` - Pydantic schema style and current API contract source.
- `services/api/src/caragent_api/routes/workspaces.py` - Existing workspace/message/brief routes.
- `services/api/src/caragent_api/routes/jobs.py` - Existing job/status/events/model-runs/artifacts/version routes.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Existing no-provider worker simulation to extend or replace with Phase 3 generation.
- `services/api/src/caragent_api/config.py` - API provider/storage/runtime settings pattern.
- `services/worker/src/caragent_worker/config.py` - Worker provider/runtime settings pattern.
- `packages/contracts/src/generated/client.ts` - Generated TypeScript client artifact that must stay current after API changes.
- `apps/web/src/app/page.tsx` - Current minimal shell if Phase 3 adds a small generation proof before full Phase 4 UI.

### External Research Required During Planning

- Official provider documentation for any selected hosted image-generation adapter, including current image model names, request/response formats, moderation behavior, image input support, pricing/cost reporting, and error semantics.
- Official SDK/API documentation for any newly introduced image generation, image encoding, or object-storage helper library.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- `DesignBrief` already stores structured JSON payloads linked to a workspace and optional source message.
- `GenerationJob` already stores workspace, brief id, idempotency key, operation, status, provider, model, cost fields, latest error, and metadata.
- `JobEvent` already supports ordered append-only status/progress/error/completed records.
- `ModelRun` already stores prompt text, prompt payload, parameters, provider/model, costs, input artifact ids, output artifact id, status, timestamps, and errors.
- `Artifact` already stores immutable object keys, artifact kind, metadata, dimensions, checksums, and job/version links.
- `DesignVersion` already supports generated version records and future parent-child lineage.
- Worker settings already expose provider keys and `AI_PROVIDER_CALLS_ENABLED`.

### Established Patterns

- FastAPI/Pydantic schemas are the contract source, and generated TypeScript clients must be refreshed.
- Shared Python domain logic belongs in `services/core`; API routes and worker tasks should call services rather than duplicating persistence logic.
- PostgreSQL/object storage are canonical; Redis/Celery result state is not authoritative for user-visible state.
- Validation favors focused unit/API/worker tests plus aggregate `corepack pnpm validate` and Docker-backed smoke.
- Provider calls are intentionally absent so far; the first real adapter must be isolated and switchable.

### Integration Points

- Add typed Phase 3 schemas for natural-language generation requests, structured brief payloads, prompt plans, generation submission responses, and retry requests.
- Extend core services with brief normalization/validation, prompt planning, generation orchestration helpers, and provider-safe artifact/model-run updates.
- Add worker provider adapter package/module and a Phase 3 generation task that can run local deterministic mode and optionally hosted mode.
- Add API routes for parsing/updating/reusing briefs and submitting/retrying generation jobs, using existing durable job and idempotency semantics.
- Refresh OpenAPI/contracts and any frontend wrappers after route/schema changes.
- Extend smoke scripts to run a full local generation cycle through Docker-backed PostgreSQL/Redis/MinIO.
</code_context>

<specifics>
## Specific Ideas

- Use an operation name like `generate_2d_concept` for first-generation jobs so Phase 5 can add `regenerate` or `revise` without ambiguity.
- Store unsupported template/view normalization in the prompt payload and a job event so the UI can explain what happened later.
- Let the local deterministic provider generate a simple PNG containing visual blocks and normalized brief labels; it proves bytes/artifact flow without pretending to be design quality.
- Use clear provider labels such as `local-deterministic` for no-key runs and config-provided labels for hosted providers.
- Make failure UAT include a forced provider error and verify job status, event message, model-run error, and retry behavior.
</specifics>

<deferred>
## Deferred Ideas

- Full GPT-style chat and rich parameter-editing panel - Phase 4.
- Full upload/reference asset manager UX - Phase 4.
- Preview canvas with zoom/pan/history/view switching - Phase 4.
- Regeneration lineage comparison and user feedback workflows - Phase 5.
- PNG/JPG plus metadata export UX - Phase 5.
- Itasha presets, deterministic text/logo overlays, safe-zone overlays, and preview-spec hardening - Phase 6.
- Provider health dashboard, cancellation, quotas, fallbacks, rate limits, and operational controls - Phase 7.
- Broad vehicle template library, true 3D UV preview, production wrap handoff, marketplace/community, auth/billing, and licensed asset library - v2+ unless explicitly promoted.
</deferred>

---

*Phase: 03-first-text-to-2d-generation-slice*
*Context gathered: 2026-06-17*
