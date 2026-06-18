---
phase: 09-hosted-provider-rollout-mvp
status: complete
researched: 2026-06-18
domain: hosted provider rollout, BFL adapter, quota/cost guards, provider traceability
confidence: high
---

# Phase 9: Hosted Provider Rollout MVP - Research

## Research Complete

Phase 9 should roll out one hosted provider path first: BFL behind the existing worker `ImageProvider` boundary. The repository already has a BFL scaffold, hosted guard settings, local deterministic fallback, operations status, durable `model_runs`, and workbench operations rendering. The key work is to align the scaffold with current official BFL API behavior, make provider/model selection durable per job, expose safe preflight and operations metadata, and keep external calls disabled by default.

## What Changed Since The Current Scaffold

The current `BflImageProvider` must be treated as a scaffold, not as verified production behavior:

- Official BFL examples use the `x-key` header, not `Authorization: Bearer`.
- FLUX.2 endpoints are now first-class in the docs. Phase 9 should default to a configured model such as `flux-2-pro-preview`, `flux-2-pro`, or `flux-2-flex` only through typed config/capability metadata.
- BFL submit responses include `id`, `polling_url`, `cost`, `input_mp`, and `output_mp`. The adapter should use `polling_url` when present instead of reconstructing `/v1/get_result`.
- BFL generation is asynchronous: submit, poll, then fetch the result when status is ready.
- Result delivery URLs are short-lived signed URLs, have no CORS, and should be downloaded and stored in project object storage rather than served directly to the browser.
- Result statuses include moderation states such as `Request Moderated` and `Content Moderated`, which should be mapped to explicit user-safe failure categories or metadata.
- BFL docs describe rate and credit failure surfaces, including 402 insufficient credits and 429 rate limit. These should not collapse into unknown failures.
- Pricing is credit and megapixel based. The system should use capability-map estimates before execution and provider response cost when available, not hardcoded fake actual costs.
- There is a small official-doc drift risk around `safety_tolerance` ranges because endpoint pages and error docs differ. Phase 9 should validate conservatively and leave provider-specific caveats in typed capability metadata.

## Recommended Implementation Approach

### Provider Capability Map

Create a typed, browser-safe capability map that can be shared by API operations status and worker provider routing without exposing secrets. It should include:

- provider id and display name
- accepted aliases
- supported operation flags, including generation now and reference/mask placeholders for later phases
- default model and allowed model ids
- configured endpoint family and polling defaults
- supported output formats and image-size constraints
- estimated cost metadata and user-safe cost caveats
- required credential configured booleans, never secret values
- blocked reasons for missing flags, credentials, quotas, rate limits, or model support

This can start as code/config in core/API/worker rather than a database table. The key is typed validation and a single source of safe metadata.

### BFL Adapter

Update `services/worker/src/caragent_worker/providers/bfl.py` against current official docs:

- Submit to the configured BFL generation endpoint using `x-key`.
- Build payloads from normalized `ImageGenerationRequest` and configured model parameters.
- Store provider request parameters without secrets.
- Poll the returned `polling_url` when present.
- Map ready/error/moderation/not-found states into typed provider outcomes.
- Download `result.sample` immediately and return bytes to the worker storage path.
- Record actual cost only from provider response cost or a trusted adapter calculation.
- Keep all exceptions sanitized through the existing provider sanitization helpers.

### API And Worker Routing

Per-job hosted selection should be durable. Extend generation submission contracts with optional provider/model intent and safe provider parameters. API preflight should block obvious hosted failures before enqueueing, but worker preflight remains authoritative immediately before any external call.

The worker should resolve provider in this order:

1. persisted job provider/model intent
2. server defaults from typed settings
3. local deterministic fallback where allowed by config

Hosted fallback must be visible in `model_runs`, job events, artifacts/design-version metadata, and operations status. Silent fallback would make provider testing untrustworthy.

### Trace, Cost, And Failure Mapping

The existing ledger is sufficient if Phase 9 fills it consistently:

- `model_runs.provider`, `model`, `prompt_text`, `prompt_payload`, `parameters`, `input_artifact_ids`, `estimated_cost`, `actual_cost`, `status`, `output_artifact_id`, and sanitized `error_message`
- job `latest_error`, `error_category`, and event metadata
- artifact/design-version metadata showing hosted route and fallback route when applicable
- operations recent failures using safe categories and redacted diagnostics

Add specific failure categories or structured metadata for moderation, rate limits, credits, and provider validation where existing categories are too coarse.

### UI And Operations

Keep UX inside the existing workbench:

- Add provider selection near generation parameters or generation controls.
- Use operations status to show whether hosted mode is enabled, blocked, or local-only.
- Show cost/quota/rate warnings compactly and safely.
- Disable or reroute hosted submission when preflight is blocked.
- Keep labels clear that generated assets are concept previews.

No standalone operations dashboard is needed in Phase 9.

## Validation Architecture

Phase 9 validation should combine focused TDD, contract checks, provider-off smoke, and explicit manual hosted smoke:

1. Provider/config tests for capability map defaults, secret-free status, BFL headers/polling/result download/cost/moderation/error mapping, and local fallback.
2. API tests for generation submission schema, hosted preflight, operations summary, recent failures, and OpenAPI export.
3. Worker tests for per-job provider routing, quota/rate/cost gates, fallback trace persistence, model-run cost/error metadata, and local deterministic path preservation.
4. Web tests for provider selector, blocked hosted state, safe diagnostics, and generation payload shape.
5. Contract check after API schema changes.
6. `pnpm validate` before completion.
7. Manual provider-on smoke only when credentials and small quota/cost guard values are intentionally configured.

## Risks And Mitigations

| Risk | Mitigation |
|------|------------|
| Provider API drift | Keep endpoint/model/payload behavior config-driven and documented with official-source date. |
| Accidental cost | Require V2 flag, provider calls flag, credentials, quota, rate limit, and cost guard before external calls. |
| Secret leakage | Redact provider exceptions, operation failures, job errors, events, and UI diagnostics. |
| Fake billing data | Persist actual cost only from provider response/trusted calculation; otherwise leave actual cost null. |
| Silent fallback confusion | Record hosted attempt and fallback route in model runs, events, and metadata. |
| CI external calls | Keep default validation provider-off; manual hosted smoke must be opt-in. |

## Sources

### Official BFL Documentation

- [BFL generating images quick start](https://docs.bfl.ai/quick_start/generating_images) - async submit/poll flow, endpoint families, `x-key`, result sample handling, active-task rate limit.
- [BFL FLUX.2 Pro API reference](https://docs.bfl.ai/api-reference/models/generate-or-edit-an-image-with-flux2-%5Bpro%5D) - `POST /v1/flux-2-pro`, request fields, response `id`, `polling_url`, `cost`, megapixel metadata.
- [BFL FLUX.2 Flex API reference](https://docs.bfl.ai/api-reference/models/generate-or-edit-an-image-with-flux2-%5Bflex%5D) - flexible FLUX.2 endpoint, prompt upsampling, guidance, steps, response cost fields.
- [BFL get result utility](https://docs.bfl.ai/api-reference/utility/get-result) - result polling statuses including ready, error, and moderation states.
- [BFL integration guidelines](https://docs.bfl.ai/api_integration/integration_guidelines) - use returned polling URL, download short-lived delivery URLs, avoid direct browser serving.
- [BFL errors](https://docs.bfl.ai/api_integration/errors) - HTTP and task-level error surfaces including insufficient credits, rate limits, and moderation.
- [BFL pricing](https://docs.bfl.ai/quick_start/pricing) - credit pricing and megapixel-based FLUX.2 cost model.

### Repository References

- `.planning/phases/09-hosted-provider-rollout-mvp/09-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `services/worker/src/caragent_worker/providers/base.py`
- `services/worker/src/caragent_worker/providers/bfl.py`
- `services/worker/src/caragent_worker/tasks/jobs.py`
- `services/api/src/caragent_api/routes/generation.py`
- `services/api/src/caragent_api/routes/operations.py`
- `services/api/src/caragent_api/schemas.py`
- `services/core/src/caragent_core/models.py`
- `apps/web/src/components/workbench/workbench-app.tsx`
- `apps/web/src/components/workbench/progress-panel.tsx`

## Metadata

**Research date:** 2026-06-18
**Recheck provider docs by:** 2026-07-18 or before changing default hosted model
**Ready for planning:** yes
