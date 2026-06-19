---
phase: 13
slug: enhanced-concept-handoff-package-mvp
status: complete
created: 2026-06-19
surface: workbench
requirements: [V2-HANDOFF-01, V2-HANDOFF-02, V2-HANDOFF-03, V2-HANDOFF-04, V2-HANDOFF-05]
---

# Phase 13 - UI Design Contract

## Product Surface

Phase 13 extends the existing workbench export area. The first screen remains the operational AI workbench. Do not add a landing page, hero section, marketing copy, or separate showcase route.

## User Goals

- Create a ZIP concept handoff package for the selected generated version.
- Preview what will be included before exporting.
- Understand blocking issues, especially missing rights/source metadata.
- See warnings for optional missing evidence, such as no 3D screenshot.
- See export history and distinguish ZIP handoff packages from PNG/JPG concept exports.
- Keep the concept-only boundary visible.

## Layout Contract

### Export Mode Control

- Keep the export feature inside `ExportPanel`.
- Add a compact segmented control or button group with `PNG`, `JPG`, and `ZIP`.
- `ZIP` represents `enhanced_concept_handoff_zip`.
- Use icons where possible: download/file archive for package, JSON/document for manifest, shield/warning for guardrails.

### Package Preview

Show a compact package preview with these rows:

- `概念图`
- `3D 截图`
- `安全区/警告`
- `Prompt/供应商`
- `引用来源`
- `评审备注`

Each row shows included, warning, or blocked state. Use badges or small status text, not large cards.

### Blocking State

When blocked:

- Show `缺少版权或来源信息` for rights/source failures.
- Keep the primary `生成交接包` button disabled.
- Preserve existing PNG/JPG concept export behavior if those paths are still valid.
- Keep generation, preview, iteration, feedback, and history usable.

### Persistent Labels

Visible text must include:

- `交接包`
- `交接包预览`
- `概念交接包，仅供评审`
- `ZIP`

The concept-only label must appear before export and in export history after export.

## Interaction Contract

- Selecting a different version recalculates package readiness.
- Changing export mode must not clear selected version or existing export history.
- Submitting ZIP calls the same version-scoped export route with `format: "enhanced_concept_handoff_zip"`.
- Successful ZIP export shows a short notice and adds/updates the export history list without a full page reload.
- Failed ZIP export shows inline destructive text and keeps the selected mode.

## Visual Contract

- Use panel-scale typography.
- Keep a quiet workbench density; no oversized promotional layout.
- Do not use gradients, decorative blobs, or ornamental imagery.
- Text must fit on desktop and mobile.
- Avoid cards inside cards. Repeated history entries may remain compact bordered rows.

## Accessibility Contract

- Export mode buttons expose selected state.
- Package readiness rows are readable without color.
- Disabled ZIP action explains why through visible text.
- Buttons have accessible labels.
- Error and notice text is adjacent to the export control.

## Responsive Contract

- Desktop: mode buttons and readiness rows may use two columns if space allows.
- Mobile: controls wrap without horizontal scroll; long object keys and ids break safely.
- Button text must not overflow.

## Empty, Loading, And Error States

- No selected version: ZIP button disabled and preview rows show `-`.
- No concept image artifact: blocking row says selected version has no source concept image.
- No screenshots: warning row says the package will omit 3D screenshots.
- Missing rights/source: blocking row says `缺少版权或来源信息`.
- Feature flag off: show package unavailable state and keep PNG/JPG export path.

## Test Hooks And Verifiable Text

Automated tests should be able to find:

- `交接包`
- `生成交接包`
- `交接包预览`
- `概念交接包，仅供评审`
- `缺少版权或来源信息`
- `ZIP`
- Submitted payload containing `"enhanced_concept_handoff_zip"`.

## UI-SPEC COMPLETE
