# Phase 15: Template Source Governance And Compatibility - Context

**Gathered:** 2026-06-19
**Status:** Ready for planning
**Mode:** Autonomous smart discuss, defaults accepted per user auto-execution preference.

<domain>
## Phase Boundary

Phase 15 establishes template provenance governance before reusable template assets enter the product. It covers source policy, license/readiness metadata, prohibited-source blocking, legacy `generic-side-coupe` compatibility, and operator audit visibility. It does not add the five MVP template asset packs or Workbench catalog UI; those are Phase 16 and Phase 17.

</domain>

<decisions>
## Implementation Decisions

### Governance Model
- Use a typed source policy table in core code as the canonical runtime source for allowed and prohibited template source types.
- Use `TemplateSourceMetadata` for per-template source type, license status, evidence, rights notes, allowed usage scope, distribution flag, and audit timestamp.
- Keep policies deterministic and local; no external license verification service is introduced in Phase 15.
- Treat source metadata as provenance evidence, not as legal-grade automated copyright verification.

### Registry And Blocking
- Introduce a core `TemplateRegistry` that validates reusable template records at registration time.
- Reject `third_party_reference_only`, `web_crawled_image`, missing license evidence for licensed templates, and blocked/missing/reference-only license statuses.
- Keep readiness audit separate from registration so incomplete but allowed internal templates can resolve while reporting missing MVP asset slots.
- Expose audit items for operators and future API/catalog phases.

### Compatibility
- Preserve `SUPPORTED_TEMPLATE_ID = "generic-side-coupe"` for archived v1/v2 payload compatibility.
- Add alias bridge from `generic_coupe_side_v1` to the legacy coupe resolver until Phase 16 installs the real MVP template pack.
- Do not change persisted v1/v2 job payload expectations or lightweight 3D fallback behavior in this phase.
- Carry template source/readiness metadata forward in new briefs, prompt payloads, and PreviewSpec.

### Verification
- Cover policy table, disallowed source blocking, licensed-source evidence, legacy alias resolution, brief JSON, and prompt payload metadata with focused core tests.
- Regenerate OpenAPI and TypeScript contracts after Pydantic schema changes.
- Keep print-ready production claims explicitly out of scope.

### the agent's Discretion
Implementation details such as exact class names, helper boundaries, and docs placement are at the agent's discretion as long as the phase requirements and existing code style are honored.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `services/core/src/caragent_core/generation/templates.py` previously owned a single `generic-side-coupe` resolver and safe-zone fixture.
- `GenerationBriefPayload` in `briefs.py` is the source schema for API responses and generated OpenAPI contracts.
- `build_prompt_plan()` in `prompts.py` creates `vehicle_template` and `preview_spec.template` payloads consumed by worker, handoff, web, and 3D paths.

### Established Patterns
- Shared product contracts live in `services/core` Pydantic models and are exported through FastAPI OpenAPI into `packages/contracts`.
- Source/rights guardrails already exist for reference assets; template governance should follow the same explicit metadata and fail-closed spirit.
- Existing compatibility posture favors stable fallback warnings over breaking old payloads.

### Integration Points
- Core: `caragent_core.generation.templates`, `briefs`, `prompts`, `__init__`.
- API/contracts: OpenAPI export and Orval generated TypeScript client.
- Tests: `services/core/tests/test_generation_briefs.py`, `services/core/tests/test_prompt_plans.py`.
- Docs: `docs/template-governance.md`.

</code_context>

<specifics>
## Specific Ideas

`MVP_FINAL.md` explicitly allows `internal_original`, `licensed_template`, and `user_provided_with_rights`, while blocking `third_party_reference_only` and `web_crawled_image` from reusable template assets, masks, thumbnails, and catalog entries.

</specifics>

<deferred>
## Deferred Ideas

- Five-template asset pack (`generic_coupe_side_v1`, `generic_sedan_side_v1`, `generic_hatchback_side_v1`, `generic_suv_side_v1`, `generic_van_side_v1`) is Phase 16.
- Template catalog API and Workbench selection are Phase 17.
- Template-aware generation/editing and 3D fallback expansion are Phase 18.
- Production readiness preflight and handoff evidence are Phase 19.

</deferred>
