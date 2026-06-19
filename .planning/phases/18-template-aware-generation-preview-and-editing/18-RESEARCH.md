# Phase 18 Research

## Existing Anchors

- Core brief resolution already stores `vehicle_template_id`, label, view, safe zones, source metadata, readiness, and warnings in `GenerationBriefPayload`.
- Prompt planning already emits `vehicle_template` and `preview_spec` into `PromptPlan.prompt_payload`.
- Worker generation persists prompt payload, PreviewSpec summaries, reference usage, generated artifact metadata, and design version parameters.
- Local deterministic generation renders from PreviewSpec safe zones and overlay layers.
- Workbench preview already reads `parameters.preview_spec` from the selected version and can select safe-zone or overlay targets.
- Lightweight 3D compatibility reads PreviewSpec template id/view and uses a shell registry.

## Gaps Found

- Overlay layer placement still hard-codes `door-main` and `rear-quarter`; some MVP templates may not define `rear-quarter`.
- Worker durable records expose PreviewSpec summaries but do not consistently surface a `vehicle_template` summary beside reference/provider metadata.
- Local deterministic generation needs regression coverage across every `MVP_TEMPLATE_IDS` record.
- Frontend 3D shell registry only knows the legacy `generic-side-coupe` id, so canonical `generic_coupe_side_v1` can incorrectly fall back.
- Workbench targeted edit should actively clear a selected target when the current PreviewSpec no longer contains it.

## Chosen Approach

- Keep `PreviewSpec` as the cross-plane contract for overlays, safe zones, targeted edit regions, and 3D compatibility.
- Add helper logic in core prompt planning to choose overlay zones from the selected template's available safe zones.
- Add worker metadata helper for concise template trace on model runs, artifacts, versions, operations, and final events.
- Add frontend guards and tests around canonical 3D shell aliasing, fallback messaging, and stale target clearing.

