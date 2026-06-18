# Phase 10: Targeted Regeneration And Masked Editing MVP - Context

**Gathered:** 2026-06-18
**Status:** Ready for execution planning
**Mode:** auto-selected defaults after `$gsd-progress --next`

<domain>
## Phase Boundary

Phase 10 lets a user select a region or PreviewSpec layer from an existing concept version and request a localized edit while preserving parent/child lineage. The phase covers edit intent schemas, mask assets, deterministic layer recomposition, mask-aware provider request contracts, worker routing, failure states, comparison UI, documentation, and UAT.

This phase must not implement reference-role generation, lightweight 3D preview, enhanced handoff packages, print-ready wrap output, marketplace/order flows, or legal-grade rights verification. Reference roles belong to Phase 11. 3D preview belongs to Phase 12. Handoff ZIP packages belong to Phase 13.
</domain>

<decisions>
## Implementation Decisions

### Product And Ledger Shape

- **D-01:** A targeted edit is a child iteration of an existing `DesignVersion`; parent versions and parent artifacts remain immutable.
- **D-02:** Store Phase 10 edit data through typed API schemas and durable metadata first: job metadata, design version parameters, artifact metadata, and model-run parameters. Add new tables only if metadata cannot preserve queryability or integrity.
- **D-03:** Define an explicit `edit_intent` payload containing edit mode, selected region/layer, prompt delta, recomposition changes, mask artifact reference, provider intent, and schema version.
- **D-04:** Add a mask artifact classification rather than overloading reference uploads. Mask artifacts must link back to workspace, parent version, and selected region or layer.
- **D-05:** A child version must record `parent_version_id`, `edit_intent`, `edit_region`, `prompt_delta`, route (`deterministic_recomposition` or `provider_masked_generation`), provider/model where used, and changed-region metadata.

### UI And Selection Model

- **D-06:** Reuse existing PreviewSpec `safe_zones` and `overlay_layers` as the first selectable primitives. Freeform masks may be represented by normalized rectangular/polygon metadata in v2 MVP, but the UI should not imply production-grade masking precision.
- **D-07:** Region/layer selection belongs in the existing workbench preview surface and iteration controls, not a separate tool page.
- **D-08:** Mask preview must be visible before submission and must clearly show whether the edit will be recomposition-only or provider-generated when known.
- **D-09:** Workbench state for selected edit target, mask visibility, and comparison mode belongs in the existing Zustand workbench store unless the state becomes server-backed.

### Worker Routing

- **D-10:** Deterministic recomposition is preferred for safe layer changes: position, scale, visibility, opacity, text, and logo replacement. It must not call hosted providers or spend quota.
- **D-11:** Provider masked generation is used only when visual content must be regenerated, the selected provider capability supports mask-aware edits, and hosted preflight passes.
- **D-12:** The worker remains authoritative. API/web preflight may block obvious unsupported edits, but the worker must repeat capability, feature flag, quota, and provider checks before execution.
- **D-13:** Provider adapters receive a normalized request contract for mask/edit metadata. Provider-specific mask payloads stay inside adapters, not in route or UI code.
- **D-14:** If a provider does not support masked editing, the system must produce a clear blocked/failure state instead of silently falling back to full regeneration.

### Failure, Retry, And Comparison

- **D-15:** Failure classes must distinguish invalid selection/mask, unsupported provider capability, recomposition conflict, provider failure, quota/rate/cost block, storage failure, timeout, cancellation, and unknown failure.
- **D-16:** Retry must preserve the original edit intent and parent version. It may retry provider execution or recomposition, but must not mutate or replace the parent artifact.
- **D-17:** Version comparison should show parent/child metadata, route type, selected region/layer, prompt delta, and changed-region highlight. It does not need pixel-perfect image diff in MVP.
- **D-18:** Browser-visible diagnostics must remain sanitized. Mask metadata and provider payloads must not expose secrets or raw vendor error bodies.

### Verification

- **D-19:** Use focused TDD for schemas, routing, recomposition, provider capability checks, UI selection, failure states, and comparison.
- **D-20:** Default validation must stay free and local. Mask-aware hosted provider smoke is manual-only unless explicit credentials and cost approval exist.
- **D-21:** Any schema change must keep OpenAPI and generated TypeScript contracts current through `corepack pnpm contracts:check`.

### Agent Discretion

- Exact schema names may be chosen during implementation if they preserve the fields above and generated contracts.
- The deterministic recomposition implementation may start with PreviewSpec overlays and metadata-only PNG output if that is enough to prove the route safely.
- Browser UAT may use local deterministic fixtures for mask preview and recomposition; hosted provider-on masked smoke can remain manual with documented prerequisites.
</decisions>

<canonical_refs>
## Canonical References

Downstream execution must read these before changing code.

### Phase Scope

- `.planning/ROADMAP.md` - Phase 10 goal, success criteria, plan list, V2 compatibility rules, UI additions, acceptance flow, and risk register.
- `.planning/REQUIREMENTS.md` - V2-EDIT-01 through V2-EDIT-05 and traceability.
- `.planning/PROJECT.md` - V2 milestone constraints, canonical data plane, concept-preview boundary, and non-goals.
- `.planning/STATE.md` - Current milestone state, blockers/concerns, and session continuity.
- `.planning/phases/09-hosted-provider-rollout-mvp/09-MILESTONE-NOTES.md` - Provider rollout closure and default-off hosted smoke boundary.
- `.planning/phases/09-hosted-provider-rollout-mvp/09-VERIFICATION.md` - Latest Phase 9 validation evidence.

### Core Ledger And Generation

- `services/core/src/caragent_core/models.py` - `GenerationJob`, `DesignVersion`, `Artifact`, `ModelRun`, parent version, metadata, and artifact linkage.
- `services/core/src/caragent_core/enums.py` - artifact kinds, failure categories, job/model/version status.
- `services/core/src/caragent_core/services/jobs.py` - job/model/artifact/version persistence helpers and sanitized errors.
- `services/core/src/caragent_core/generation/briefs.py` - generation brief payload and safe-zone inputs.
- `services/core/src/caragent_core/generation/prompts.py` - prompt plan and PreviewSpec construction.

### API And Contracts

- `services/api/src/caragent_api/schemas.py` - submission, iteration, job, version, artifact, model-run, and operations schemas.
- `services/api/src/caragent_api/routes/generation.py` - generation and iteration submission routes.
- `services/api/src/caragent_api/routes/jobs.py` - job, events, versions, artifacts, feedback, retry, and export surfaces.
- `services/api/src/caragent_api/routes/operations.py` - provider capability and guard status.
- `packages/contracts/openapi/openapi.json` - generated OpenAPI artifact.
- `packages/contracts/src/generated/client.ts` - generated TypeScript client consumed by web.

### Worker And Provider

- `services/worker/src/caragent_worker/tasks/jobs.py` - generation pipeline, iteration metadata, provider routing, fallback, model-run persistence, and failure mapping.
- `services/worker/src/caragent_worker/providers/base.py` - normalized image request/result protocol.
- `services/worker/src/caragent_worker/providers/local.py` - local deterministic provider and PreviewSpec overlay rendering.
- `services/worker/src/caragent_worker/providers/bfl.py` - hosted provider adapter boundary for future mask-aware calls.
- `services/worker/src/caragent_worker/config.py` - provider, quota, rate, cost, and V2 feature flag settings.

### Web Workbench

- `apps/web/src/lib/workbench/store.ts` - local workbench UI state.
- `apps/web/src/components/workbench/workbench-app.tsx` - workbench composition, selected version, submission, and iteration flow.
- `apps/web/src/components/workbench/preview-panel.tsx` - PreviewSpec rendering, safe-zone/overlay visibility, version history.
- `apps/web/src/components/workbench/parameter-panel.tsx` - provider selector and generation parameters.
- `apps/web/src/lib/api/generation.ts` - generation API wrapper and provider intent helper.
- `apps/web/src/lib/api/iteration.ts` - child iteration, feedback, and export API wrapper.
- `apps/web/src/app/page.test.tsx` - integrated workbench behavior tests.

### Validation And Docs

- `package.json` - root validation, contract, smoke, and dev scripts.
- `scripts/validate-all.mjs` - aggregate validation sequence.
- `README.md` - developer command index and Phase 10 docs target.
- `docs/development.md` - local runbook, smoke, UAT, troubleshooting, and provider guardrails.
</canonical_refs>

<code_context>
## Existing Code Insights

- `DesignVersion.parent_version_id` already supports child lineage and should be reused for targeted edits.
- `GenerationIterationSubmissionRequest` already sends `change_request`, `parameter_overrides`, provider, model, and provider parameters.
- Worker `_generation_iteration_context` already converts iteration metadata into model-run/version parameters.
- `ImageGenerationRequest` already carries prompt payload, provider, model, parameters, input artifact ids, estimated cost, and concept label.
- Local provider already mirrors PreviewSpec metadata and draws overlay layers from `preview_spec.overlay_layers`.
- Workbench preview already parses PreviewSpec safe zones and overlay layers and can be extended for selection and mask preview.
- Operations/provider status already has capability metadata fields from Phase 9; Phase 10 should add mask capability checks there rather than hardcoding UI assumptions.
</code_context>

<deferred>
## Deferred Ideas

- Reference roles, source snapshots, and role-specific provider handling - Phase 11.
- 3D shell preview, camera controls, and screenshot artifacts - Phase 12.
- Enhanced handoff package ZIP, manifest, and final review notes - Phase 13.
- Pixel-perfect image diffs, production-grade masks, and print-shop validation - future milestone.
</deferred>

---

*Phase: 10-targeted-regeneration-and-masked-editing-mvp*
*Context gathered: 2026-06-18*
