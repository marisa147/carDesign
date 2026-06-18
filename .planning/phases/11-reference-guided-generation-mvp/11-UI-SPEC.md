---
phase: 11
slug: reference-guided-generation-mvp
status: complete
created: 2026-06-18
surface: workbench
requirements: [V2-REF-01, V2-REF-02, V2-REF-03, V2-REF-04, V2-REF-05]
---

# Phase 11 - UI Design Contract

## Product Surface

Phase 11 extends the existing AI workbench. It must not introduce a landing page, hero section, or separate marketing-style flow. The first screen remains the dense operational workspace with chat, asset library, parameters, preview, history, progress, and export tools.

## User Goals

- Assign a role to each uploaded reference asset.
- Understand whether the asset can be used for generation based on rights/source metadata.
- Understand whether the selected provider/model supports the chosen reference roles.
- Submit generation or child iteration without wondering which references were included.
- Inspect warnings and trace evidence after generation.

## Layout Contract

### Asset Tab

The asset list remains the primary role-assignment surface.

Each asset row must show:

- Filename and upload kind.
- Rights badge: `权利已确认`, `权利信息缺失`, or rejected/pending equivalent if exposed.
- Source label or a concise missing-source status.
- Role control with exactly six options: `角色`, `风格`, `车辆`, `Logo`, `配色`, `仅灵感`.
- Eligibility badge: `可用于生成`, `需确认权利`, `供应商不支持`, or `仅记录`.
- A compact include/exclude control for whether this assignment is active.

Use existing small bordered rows. Do not nest a full card inside another full card. Role controls should not change row height unpredictably.

### Parameters Tab

Replace manual reference ID entry as the primary path with a reference summary block:

- Count by role.
- Unsupported role warning for the selected provider.
- Rights-gate warning if any selected assignment is ineligible.
- A small link-style or icon action to jump back to the asset tab if the shell supports it.

The raw `reference_asset_ids` textarea may remain only as a compatibility/debug affordance if needed, but it must not be the main UX for Phase 11.

### Provider Selector

Provider buttons keep the Phase 9 shape. Add reference capability information below selected provider status:

- `引用支持`: accepted, prompt-only, or unsupported.
- `不支持角色`: comma-separated role labels when non-empty.
- Use warning badge treatment consistent with current `托管调用已阻断`.

### Progress And History

Progress/failure surfaces should show sanitized reference warnings:

- Rights missing.
- Source metadata missing.
- Role unsupported by provider/model.
- Inspiration-only reference recorded but not sent.

The comparison panel does not need a new visual diff mode in Phase 11. If reference trace is present on versions, it may display a compact "references used" row in later plans.

## Interaction Contract

- Selecting a role on an asset with missing rights must not make it generation-eligible.
- Confirming rights with source metadata should immediately update eligibility in the asset list.
- Switching provider must recompute provider warnings for currently selected reference roles.
- Save state should behave like existing parameter saves; avoid sticky success text that never clears in future implementation if the surrounding component already supports transient notices.
- Child iteration should reuse current brief reference assignments unless the user changes them.
- Unsupported role warnings must be visible before submit, not only after the job fails.

## Copy Contract

Use concise Chinese UI labels:

- Roles: `角色`, `风格`, `车辆`, `Logo`, `配色`, `仅灵感`
- Eligibility: `可用于生成`, `需确认权利`, `来源缺失`, `供应商不支持`, `仅记录`
- Provider warning title: `引用受限`
- Rights warning title: `引用素材需要权利确认`
- Prompt-only note: `当前供应商只会把引用作为提示上下文记录，不会发送图片引用。`

Do not add visible tutorial text explaining every feature. The labels and warnings should carry the workflow.

## Visual Contract

- Keep typography at existing panel scale: small headings and `text-sm`/`text-xs` supporting text.
- Use badges for state and icon buttons for actions where possible.
- Use existing semantic colors: warning/destructive/success/primary/muted.
- Avoid dominant single-hue restyling, gradients, decorative imagery, or hero-scale type.
- Stable dimensions: role controls, include toggles, and provider warning rows must not cause list jumps on hover/focus.

## Accessibility Contract

- Every role control needs an accessible label containing the filename.
- Include/exclude controls must expose checked state.
- Warnings should use `role="alert"` only for newly surfaced blocking errors; static eligibility badges should not spam screen readers.
- Provider role warnings must be readable without color.
- Keyboard users must be able to move through asset rows, role selection, rights fields, and save buttons predictably.

## Responsive Contract

- Desktop: asset row header can use two columns, but controls must wrap without truncating the role labels.
- Mobile: asset row stacks filename, badges, role control, and rights fields in a single column.
- Avoid side-by-side controls that force horizontal scrolling at narrow widths.

## Empty, Loading, And Error States

- Empty asset list: keep existing dashed upload guidance, add short reference-role wording after Phase 11 implementation.
- Loading: preserve current spinner row.
- Rights save error: keep inline destructive state near the action.
- Unsupported provider role: show warning in asset row and parameter/provider panel; submission should either block or carry explicit omitted-role metadata according to the capability contract.

## Test Hooks And Verifiable Text

Automated tests should be able to find:

- The six role labels.
- `引用受限`.
- `引用素材需要权利确认`.
- `可用于生成`.
- `供应商不支持`.
- Generated or submitted payload containing `reference_usage`.

## UI-SPEC COMPLETE
