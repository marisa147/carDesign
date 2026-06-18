---
phase: 11
slug: reference-guided-generation-mvp
status: complete
created: 2026-06-18
requirements: [V2-REF-01, V2-REF-02, V2-REF-03, V2-REF-04, V2-REF-05]
---

# Phase 11 - Reference-Guided Generation Research

## Research Question

What does the project need to know to plan reference-guided generation safely, without breaking the Phase 9 provider guardrails or Phase 10 targeted-edit lineage?

## Current Baseline

The codebase already has the right ledger and guardrail primitives:

- `Asset` stores upload kind, object key, checksum, source fields, rights status, rights notes, and confirmation timestamp.
- `assets.require_confirmed_rights()` enforces confirmed rights for a single asset.
- `GenerationBriefPayload` stores legacy `reference_asset_ids` and `overlay_logo_asset_ids`.
- `build_prompt_plan()` places reference IDs into prompt text, `prompt_payload.input_artifact_ids`, `preview_spec.sources.reference_asset_ids`, and `PromptPlan.input_artifact_ids`.
- Worker execution creates `ModelRun`, generated `Artifact`, and `DesignVersion` records with JSON metadata that already carry provider, preview, cost, and targeted-edit trace.
- Provider capability metadata is centralized in `caragent_core.provider_capabilities` and exposed through operations status.
- Workbench asset UI already uploads images, confirms rights/source text, and selects references, but the selection is only a flat ID list.

The missing pieces are role semantics, reference eligibility snapshots, provider-specific role filtering, and user-visible warnings.

## Reference Contract Shape

Plan Phase 11 around a shared core contract, not ad hoc UI-only state:

- `ReferenceRole`: one of `character`, `style`, `vehicle`, `logo`, `palette`, `inspiration`.
- `ReferenceAssignment`: `{asset_id, role, enabled}` or equivalent brief-level usage intent.
- `ReferenceRightsSnapshot`: immutable copy of asset id, object key, original filename, content type, checksum, rights status, source label/url, rights notes, and confirmed timestamp at generation time.
- `ReferenceUsageSnapshot`: versioned metadata that includes all requested references, included references, omitted references, unsupported roles, warnings, and provider/model decision context.
- `ReferenceCapabilityWarning`: machine-readable warning entries for UI, API, worker, and later export manifests.

The contract should preserve backward compatibility by deriving a default assignment from `reference_asset_ids` when structured assignments are absent. A conservative default role such as `inspiration` or `style` is acceptable only if it is explicitly documented and tested.

## Rights Gate Timing

Rights should be checked in more than one place:

1. Asset UI: disable generation eligibility controls when rights are missing and show the source/rights reason.
2. API submission/preflight: reject or warn on clearly ineligible references before enqueue where the brief and workspace assets are available.
3. Worker: repeat authoritative rights and workspace ownership checks immediately before provider execution, because queued jobs can outlive UI state.

The worker currently checks rights after model-run creation. Phase 11 should keep that safety net but also build a snapshot before or during prompt/request planning so model-run parameters and failure events can show the exact reference decision.

## Provider Capability Model

The existing capability map should be extended rather than bypassed:

- Current local provider: supports generation but not true reference-image API input.
- Current BFL provider: hosted calls are guarded; reference-image support is not verified in the current adapter.
- Phase 11 should distinguish role-aware prompt guidance from true provider image-reference input.

Recommended capability fields:

```json
{
  "supports": {
    "generation": true,
    "references": true,
    "reference_image_inputs": false
  },
  "reference_input": {
    "accepted": false,
    "supported_roles": [],
    "prompt_guidance_roles": ["character", "style", "vehicle", "logo", "palette"],
    "unsupported_roles": ["inspiration"],
    "content_types": ["image/png", "image/jpeg", "image/webp"],
    "blocked_reason": "Provider image-reference input is not verified for this adapter."
  }
}
```

For the local deterministic provider, role metadata can influence prompt payload and deterministic preview labels without claiming true visual reference fidelity. For BFL, roles should be included in request metadata only when the adapter has verified support; otherwise warnings must be visible and no unsupported reference input should be sent.

## Prompt And Request Planning

`build_prompt_plan()` is the natural integration point. It should:

- Normalize structured role assignments from the brief.
- Build `ReferenceUsageSnapshot`.
- Add role-aware reference text to `prompt_text`.
- Add `reference_usage` to `prompt_payload`.
- Set `input_artifact_ids` to included generation references plus overlay logo assets, without duplicates.
- Add warnings for unsupported roles and ineligible assets.

The worker request builder should then copy the snapshot into `ImageGenerationRequest` or its parameters so providers never have to inspect arbitrary prompt payload fields.

## Persistence Surfaces

V2 roadmap allows typed metadata or versioned JSON. No new table is required for the MVP if the metadata is explicit and consistently named.

Store reference trace data in:

- `GenerationJob.metadata_json.reference_usage` and job events for validation/warnings.
- `ModelRun.parameters.reference_usage` and `ModelRun.prompt_payload.reference_usage`.
- `Artifact.metadata_json.reference_usage`.
- `DesignVersion.parameters.reference_usage`.
- Export manifest source data when the web export action records a selected version.

Use stable keys that later phases can grep and package:

- `reference_usage`
- `reference_roles`
- `rights_snapshot`
- `included_reference_asset_ids`
- `omitted_reference_asset_ids`
- `unsupported_reference_roles`
- `reference_warning_count`

Do not embed binary image bytes, raw secrets, or unredacted provider error payloads in metadata.

## Workbench UX Findings

Current UI uses compact Tailwind/shadcn style panels and workbench tabs. Keep Phase 11 within that style:

- Asset panel should own role assignment because users choose role while inspecting source/rights state.
- Parameter panel should show selected reference summary and provider warnings, not require manual ID editing as the primary path.
- Provider selector should expose whether selected roles are accepted, prompt-only, or unsupported.
- Progress/failure surfaces should include sanitized reference warnings and rights errors.

Avoid a redesign. The first usable screen remains the workbench.

## Validation Architecture

Automated validation should stay provider-off and local by default.

Required test layers:

- Core: role enum/schema validation, snapshot builder, backward compatibility from `reference_asset_ids`, prompt payload, and provider capability map.
- API: brief create/update with structured references, rights/source preflight, unsupported provider/model role checks, sanitized error responses, OpenAPI contract generation.
- Worker: rights snapshot creation, model-run/artifact/version persistence, local deterministic request metadata, unsupported hosted role warnings/blocks, no external calls in default tests.
- Web: role assignment controls, rights-gated eligibility, provider warning display, generation/iteration payloads, export manifest source trace.
- Contracts: `corepack pnpm contracts:check` after schema changes.
- Aggregate: provider-off smoke dry run and `corepack pnpm validate` in closure plan.

Manual-only verification:

- Hosted provider reference smoke with real credentials, low quota/rate/cost guards, and explicit cost approval.
- Browser UAT with a running API/worker/web stack to visually confirm asset-role assignment and warning presentation.

## Key Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| User believes unsupported references were used | High | Explicit unsupported-role warnings in brief, job, provider status, and UI. |
| Rights metadata changes after generation | High | Snapshot rights/source state into durable generation metadata. |
| Provider docs or behavior change | High | Capability map stays config-driven and default tests do not assume live hosted support. |
| Legacy `reference_asset_ids` break | Medium | Derive structured assignments when old fields exist and keep generated contracts backward-compatible. |
| Metadata drift across job/model-run/artifact/version | Medium | Use a single helper to build trace metadata and assert the same keys across persistence surfaces. |

## Planning Recommendation

Use seven plans matching the roadmap:

1. Schema, snapshot, rights helper, and provider capability contract.
2. Asset UI role assignment and eligibility.
3. Prompt/reference planner and unsupported warning integration.
4. Worker/provider handling and deterministic fallback behavior.
5. Durable trace persistence across records and export manifest source.
6. Workbench generation UX, failure states, and child iteration reuse.
7. Verification, docs, UAT, and Phase 11 closure.

## RESEARCH COMPLETE
