# Phase 18 UI Spec: Template-Aware Preview And Editing

## Surface

The existing Workbench remains the first screen. Phase 18 updates the generated preview, local layer controls, targeted edit controls, and 3D fallback states. No landing page, marketing hero, or new standalone tool is introduced.

## Preview Requirements

- The 2D preview must show the template label, template id, view, safe-zone count, and warning count from the selected version's PreviewSpec.
- Safe-zone overlays must use the exact normalized coordinates in the selected version's PreviewSpec.
- Text and logo overlay controls must target safe zones that exist in the selected version.
- Template warnings must stay visible near the preview when present.
- The vehicle silhouette is only a concept preview frame; it must not claim physical wrap accuracy.

## Targeted Edit Requirements

- Targeted edit mode can select either a safe zone or an overlay layer from the selected version's PreviewSpec.
- The mask preview must use the selected target's normalized region.
- If the selected version changes or the selected target is no longer present in the current PreviewSpec, the stale target must clear.
- Iteration submission must send the selected target, region, route preference, prompt delta, parent version id, and parent artifact metadata.

## 3D Requirements

- Canonical v3 coupe templates and legacy v1/v2 coupe PreviewSpecs should resolve to the lightweight coupe shell.
- Other MVP templates should fall back to 2D with template-specific reason text and concept-only warnings.
- 3D UI copy must continue to say lightweight/concept-only and avoid production-ready language.

## States To Cover

- Canonical coupe PreviewSpec with compatible lightweight shell.
- Van PreviewSpec with template-specific fallback.
- Template with warnings.
- Safe-zone target selection.
- Overlay-layer target selection.
- Stale target after version switch.

