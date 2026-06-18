---
phase: 10-targeted-regeneration-and-masked-editing-mvp
status: ready
created: 2026-06-18
external_calls: none
---

# Phase 10 Research Notes

Phase 10 planning is repo-grounded. No live external provider documentation was queried during planning because default Phase 10 validation must stay local and free. Implementation plan 10-04 explicitly requires re-checking the selected provider's current mask/edit API docs before enabling hosted masked calls.

## Existing Product Surface

The current workbench already has the right anchors for targeted editing:

- `PreviewPanel` reads `version.parameters.preview_spec` and renders safe zones plus overlay layers.
- `useWorkbenchStore` stores selected version, selected view, zoom, and overlay/safe-zone toggles.
- `workbench-app.tsx` already submits child iterations through `submitChildIteration`.
- `GenerationIterationSubmissionRequest` already includes a natural-language `change_request`, `parameter_overrides`, provider, model, and provider parameters.
- Phase 9 added browser-safe provider status and provider selection helpers.

Planning consequence: Phase 10 should extend the existing iteration flow instead of creating a separate edit endpoint first. A dedicated endpoint can be added later only if route clarity or validation requires it.

## Existing Data Surface

The durable ledger already supports most targeted-edit evidence:

- `DesignVersion.parent_version_id` records lineage.
- `DesignVersion.parameters` can store edit metadata and PreviewSpec deltas.
- `GenerationJob.metadata_json` can store request-time edit intent and selected target.
- `Artifact.metadata_json` can store mask metadata and changed-region summaries.
- `ModelRun.parameters`, `input_artifact_ids`, and `output_artifact_id` can trace provider/recomposition inputs and outputs.

Planning consequence: prefer typed metadata schemas and tests before introducing new database tables. Add an artifact kind for masks if needed.

## Recomposition Route

The local deterministic provider already draws PreviewSpec overlays onto a concept canvas. Phase 10 can add a recomposition helper that:

1. Reads the parent version PreviewSpec and selected artifact metadata.
2. Applies safe changes to overlay layer properties.
3. Writes a new generated/preview artifact and child version.
4. Records route `deterministic_recomposition` in job/model/version metadata.

This route should cover move, scale, visibility, opacity, text, and logo replacement. It should not call hosted providers, consume quota, or require credentials.

## Provider Mask Route

The generic provider contract can be extended with optional mask/edit metadata. Provider adapters then decide how to translate that metadata into vendor-specific payloads.

Required planning guardrails:

- Capability map must include mask-aware edit support per provider/model.
- API and worker preflight must reject unsupported mask edits.
- Worker must repeat capability, flag, quota, rate, and cost checks.
- Hosted provider errors must be sanitized and mapped to user-safe categories.
- Default validation uses mocks or local deterministic route only.

## UI Route

First MVP selectors can use structured targets rather than pixel brush tooling:

- Safe-zone target: door, rear quarter, hood/top, etc.
- Overlay-layer target: text, logo, accent stripe, character layer where represented in PreviewSpec.
- Region geometry: normalized rectangle/polygon attached to selected target.
- Mask preview: visual overlay in `PreviewPanel`, independent of provider execution.

Planning consequence: implement accessible, stable controls and clear state labels. Do not imply production-grade mask precision.

## Failure And Comparison

Comparison can be metadata-first for MVP:

- Parent and child version cards.
- Route label: recomposition-only or provider-generated.
- Selected target and prompt delta.
- Changed-region highlight using mask/region metadata.
- Provider/model/cost when provider-generated.

Pixel diff, side-by-side image analysis, and production proofing are deferred.

## Open Checks For Execution

- Confirm exact current BFL mask/edit payload shape before implementing real hosted mask calls.
- Confirm whether mask artifacts need a new `ArtifactKind.MASK` value or metadata-only kind reuse.
- Confirm whether deterministic recomposition can reuse local provider drawing helpers cleanly or should move common drawing into a core/worker utility.
- Confirm generated TypeScript contract names after schemas are added.
