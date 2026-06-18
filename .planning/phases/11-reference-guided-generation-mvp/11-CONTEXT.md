---
phase: 11
slug: reference-guided-generation-mvp
status: ready-for-planning
source: roadmap-auto-context
created: 2026-06-18
requirements: [V2-REF-01, V2-REF-02, V2-REF-03, V2-REF-04, V2-REF-05]
depends_on: [10-targeted-regeneration-and-masked-editing-mvp]
---

# Phase 11 - Reference-Guided Generation MVP Context

**Gathered:** 2026-06-18
**Status:** Ready for planning
**Source:** ROADMAP Phase 11, REQUIREMENTS V2-REF-01..05, Phase 9 provider rollout notes, Phase 10 targeted editing handoff, and current code inspection.

<domain>
## Phase Boundary

Phase 11 delivers role-based reference guidance for uploaded assets. Users can assign references as character, style, vehicle, logo, palette, or inspiration-only guidance, and generation uses only eligible references with confirmed rights/source metadata and provider-supported roles.

This phase does not promise legal-grade copyright verification, production print readiness, true multi-view consistency, or provider quality guarantees. Default validation remains local/provider-off unless a manual hosted smoke is explicitly run with credentials, low quota guards, and cost approval.

</domain>

<decisions>
## Implementation Decisions

### Reference Roles

- Add a first-class `ReferenceRole` contract with exactly these v2 roles: `character`, `style`, `vehicle`, `logo`, `palette`, `inspiration`.
- Treat `inspiration` as a non-generation role unless a provider explicitly supports inspiration references; it can stay visible in UI and trace metadata without being sent to unsupported provider calls.
- Do not overload `Asset.kind` as the reference role. Asset kind remains upload classification (`reference`, `logo`, `car_photo`, `inspiration`); reference role is usage intent for a generation brief/job.
- Preserve backward compatibility with existing `reference_asset_ids`; plans may bridge old IDs into default reference usage, but new behavior should expose structured role metadata.

### Rights And Source Gates

- Reuse existing `Asset.rights_status`, `source_label`, `source_url`, `rights_notes`, and `rights_confirmed_at`.
- A reference usage is generation-eligible only when the referenced asset belongs to the workspace and has `rights_status == "confirmed"` plus source metadata accepted by the existing rights service.
- Unsupported or ineligible references must produce clear API/UI warnings or validation errors before provider calls. They must not be silently ignored in a way that makes the user believe they were used.
- Rights/source snapshots must be copied into the job/model-run/artifact/version/export-facing metadata used by this phase so later edits and handoff packages can prove what was used at generation time.

### Provider Capability Contract

- Extend the existing browser-safe provider capability map instead of adding provider-specific checks directly in UI or worker call sites.
- Provider capabilities must describe supported reference roles, unsupported roles, and any input requirements by provider/model.
- Local deterministic provider remains the default free path and should not make external calls. It may record reference usage and render deterministic hints, but it should not claim true image-reference fidelity.
- BFL hosted behavior remains guarded. Unless a role-specific reference input path is explicitly implemented and verified, BFL must warn/block unsupported reference roles instead of accepting them silently.

### Prompt And Request Planning

- Add a reference planning layer that converts role assignments into a normalized `ReferenceUsageSnapshot`.
- `build_prompt_plan` should include selected reference usage in `prompt_payload`, `input_artifact_ids`, warnings, and human-readable prompt text.
- Provider request builders should include only roles supported by the selected provider/model. Omitted unsupported roles must be visible in warning metadata.
- Existing targeted edit and parent/child lineage metadata from Phase 10 must remain intact.

### Persistence And Traceability

- Generated artifacts, design versions, model runs, job metadata/events, and later exports must all be able to expose exact reference asset IDs, roles, provider inclusion status, omitted/unsupported reasons, and rights/source snapshots.
- Prefer versioned JSON metadata for v2-only trace surfaces unless a relational table becomes unavoidable. V2 roadmap compatibility explicitly allows typed metadata and versioned JSON with schema markers.
- No binary reference image content should be duplicated into metadata.

### Workbench UX

- Asset library UI should let users assign roles from the six-role set and clearly show whether each asset is eligible for generation.
- Keep controls dense and operational, consistent with the existing workbench. Use icons for actions and restrained badges/status text for eligibility and warnings.
- Parameter/generation UI should show unsupported reference-role warnings alongside provider guard warnings.
- Selecting a provider should not resize or destabilize the asset list or parameter panel.

### Validation Defaults

- Automated validation must not require external provider calls.
- Required focused checks should include core schema/prompt tests, API rights/provider capability tests, worker local/provider-off tests, web workbench tests, and contract generation checks.
- Manual hosted reference smoke remains optional and must be documented with credential/cost/quota prerequisites.

</decisions>

<canonical_refs>
## Canonical References

Downstream agents MUST read these before planning or implementing.

### Planning And Handoff

- `.planning/ROADMAP.md` - Phase 11 goal, success criteria, plan list, V2 data additions, UI additions, risk register.
- `.planning/REQUIREMENTS.md` - V2-REF-01..05 requirement definitions and traceability.
- `.planning/STATE.md` - current milestone status and prior decisions.
- `.planning/phases/09-hosted-provider-rollout-mvp/09-MILESTONE-NOTES.md` - provider capability, preflight, and default-off hosted behavior.
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-MILESTONE-NOTES.md` - targeted edit lineage, capability gates, and Phase 11 handoff.
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-VALIDATION.md` - validation style and provider-off defaults.

### Core Contracts And Ledger

- `services/core/src/caragent_core/enums.py` - AssetKind, RightsStatus, FailureCategory, ArtifactKind enum patterns.
- `services/core/src/caragent_core/models.py` - Asset, GenerationJob, DesignVersion, Artifact, ModelRun metadata surfaces.
- `services/core/src/caragent_core/services/assets.py` - rights/source update and `require_confirmed_rights` gate.
- `services/core/src/caragent_core/provider_capabilities.py` - provider capability map to extend for references.
- `services/core/src/caragent_core/generation/briefs.py` - `GenerationBriefPayload` and existing `reference_asset_ids`.
- `services/core/src/caragent_core/generation/prompts.py` - `PromptPlan`, prompt payload, preview sources, and input artifact handling.

### API And Worker

- `services/api/src/caragent_api/schemas.py` - OpenAPI/Pydantic contracts mirrored into TypeScript.
- `services/api/src/caragent_api/routes/assets.py` - asset upload/list/rights endpoints.
- `services/api/src/caragent_api/routes/generation.py` - brief create/update, provider intent, iteration metadata, provider capability validation.
- `services/worker/src/caragent_worker/config.py` - `V2_REFERENCE_GUIDANCE_ENABLED` feature flag.
- `services/worker/src/caragent_worker/providers/base.py` - normalized image request/result contract.
- `services/worker/src/caragent_worker/providers/local.py` - local deterministic renderer and metadata behavior.
- `services/worker/src/caragent_worker/tasks/jobs.py` - prompt planning, rights checks, provider preflight, model-run/artifact/version persistence.

### Web Workbench

- `apps/web/src/components/workbench/asset-panel.tsx` - asset list, rights confirmation, current reference selection.
- `apps/web/src/components/workbench/parameter-panel.tsx` - provider selector and `reference_asset_ids` editing.
- `apps/web/src/components/workbench/workbench-app.tsx` - selected reference state, brief updates, provider intent submission, export manifest.
- `apps/web/src/lib/api/assets.ts` - asset API client.
- `apps/web/src/lib/api/generation.ts` - generation client and provider intent payload.
- `apps/web/src/lib/api/operations.ts` - provider capability normalization and blocked reason formatting.

### Existing Tests

- `services/core/tests/test_models.py` - enum/model metadata assertions.
- `services/core/tests/test_prompt_plans.py` - prompt payload and input artifact behavior.
- `services/api/tests/test_generation.py` - generation API/provider preflight patterns.
- `services/worker/tests/test_generation_tasks.py` - worker persistence, rights checks, and provider-off behavior.
- `apps/web/src/app/page.test.tsx` - workbench UI behavior fixtures and flow tests.

</canonical_refs>

<specifics>
## Specific Ideas

- Add structured records such as `ReferenceAssignment`, `ReferenceUsageSnapshot`, `ReferenceCapabilityWarning`, or equivalent names in core generation contracts.
- Store a `schema_version: 1` marker in reference usage metadata.
- Include fields that are easy to grep/test: `reference_usage`, `reference_roles`, `rights_snapshot`, `included_reference_asset_ids`, `unsupported_reference_roles`, and `reference_warning_count`.
- Extend provider capability map with `reference_input` or similarly named metadata that lists `supported_roles`, `unsupported_roles`, `content_types`, and `blocked_reason`.
- Web copy should distinguish "not eligible because rights are missing" from "eligible but provider does not support this role".
- Exports in Phase 11 only need to record trace-ready metadata that Phase 13 can later package.

</specifics>

<deferred>
## Deferred Ideas

- Fully automated copyright/licensing verification remains future scope.
- Provider-specific live reference-image quality validation remains manual-only until credentials, cost approval, and supported provider routes are verified.
- Production handoff packaging of references is deferred to Phase 13, though Phase 11 must persist the trace data Phase 13 will need.
- True multi-view or physically aligned reference guidance is future scope.

</deferred>

---

*Phase: 11-reference-guided-generation-mvp*
*Context gathered: 2026-06-18 via roadmap-auto-context*
