---
phase: 6
slug: itasha-and-template-intelligence
status: approved
shadcn_initialized: partial
preset: local-minimal
created: 2026-06-18
---

# Phase 6 - UI Design Contract

> Visual and interaction contract for adding itasha controls, deterministic overlay controls, template warnings, safe-zone overlays, and preview-spec visibility to the existing workbench.

## Design System

| Property | Value |
|----------|-------|
| Tool | Tailwind CSS with local shadcn-style primitives |
| Preset | local-minimal |
| Component library | Existing local `Button`, `Card`, `Badge`, `Alert`; add local `Switch` or segmented controls only if implementation tests justify them |
| Icon library | `lucide-react` |
| Font | Existing system UI stack from `apps/web/src/app/globals.css` |

## Visual Direction

Phase 6 extends the same quiet design-operations surface from Phases 4 and 5. The workbench should feel more domain-aware, not more decorative: new controls are compact editing tools, preview overlays are inspection aids, and warnings are operational risk signals.

Do not create a new landing page, wizard, hero surface, separate editor mode, or marketing explanation page. Do not put cards inside cards. Use `UI.png` only as the workbench shape reference: conversation, plan/preview, parameter adjustment, material management, and export remain parts of one production-minded tool surface.

## Layout Contract

| Region | Desktop | Narrow Screens | Purpose |
|--------|---------|----------------|---------|
| Itasha controls | Existing parameter panel, after base style/coverage fields | Stacked after base fields | Character focus, supporting graphics, racing/JDM cues, typography intent, color harmony |
| Overlay controls | Existing preview action area, near zoom/view controls | Below preview metadata before version history | Toggle deterministic text/logo layers and safe zones |
| Warning strip | Parameter panel and preview panel share the same durable warning list | Appears before action buttons in stacked flow | Low resolution, unsupported template/view, text readability, risky zones, rights uncertainty |
| Safe-zone legend | Compact row or two-column list under preview controls | Wrapped chips below preview | Door/body, window, wheel arch, trim/risky edge zones |
| Preview spec details | Export/manifest area or comparison/history area | Stacked after export manifest | Renderer-neutral spec summary for developer inspection |

Maintain the Phase 4/5 mobile order: chat, preview, progress/history, parameters/assets, iteration/feedback/export/future gates. At 390px and 320px viewport widths there must be no horizontal document scroll, no text overlap, and no controls wider than the viewport.

## Spacing Scale

Reuse Phase 4/5 spacing:

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, status dots, safe-zone swatches |
| sm | 8px | Button gaps, segmented-control gaps, warning chip gaps |
| md | 16px | Panel padding, form groups, overlay legend blocks |
| lg | 24px | Workbench zone padding and main grid gaps |
| xl | 32px | Mobile stacked section separation |
| 2xl | 48px | Reserved for full-page section separation only |

Exceptions: none.

## Typography

| Role | Size | Weight | Line Height | Usage |
|------|------|--------|-------------|-------|
| Body | 14px | 400 | 1.5 | Chat text, warning details, manifest values |
| Label | 12px | 500 | 1.35 | Field labels, overlay labels, metadata |
| Compact | 13px | 500 | 1.4 | Buttons, chips, segmented controls |
| Heading | 18px | 600 | 1.25 | Panel titles only |
| Display | 24px | 650 | 1.18 | App-level heading only, not for Phase 6 controls |

Letter spacing remains `0`. Do not scale font size with viewport width.

## Color

Reuse the existing color roles:

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#F7F8FB` | App background |
| Secondary (30%) | `#FFFFFF`, `#F1F5F9` | Panels, inputs, muted surfaces |
| Text | `#111827`, `#4B5563`, `#6B7280` | Primary, secondary, muted copy |
| Accent (10%) | `#5B5EF7` | Selected overlay toggle, active safe-zone mode, primary save/generate action |
| Support | `#0EA5A4` | Available overlay/spec states and non-blocking readiness |
| Warning | `#B45309` | Template normalization, readability, low resolution, risky-zone warnings |
| Success | `#15803D` | Saved spec/parameter states |
| Destructive | `#DC2626` | Rights-blocked or failed states only |

Safe-zone overlays must use semi-transparent strokes/fills over the preview instead of solid panels. Suggested zone colors: body `rgba(91, 94, 247, 0.20)`, window `rgba(14, 165, 164, 0.18)`, wheel/risky `rgba(180, 83, 9, 0.18)`, blocked/rights `rgba(220, 38, 38, 0.16)`.

The interface must not become a one-note purple theme. Accent is reserved for selected states and primary actions.

## Component Contract

| Component | Required Behavior |
|-----------|-------------------|
| Itasha control group | Adds labeled controls for `角色焦点`, `辅助图形`, `赛车/JDM 元素`, `字体意图`, and `配色协调`. Controls save through the existing brief update flow and keep current defaults when empty. |
| Text/logo overlay editor | Shows exact text strings from the brief and eligible uploaded logo/reference assets as deterministic overlay candidates. Missing rights/source assets stay disabled or blocked. |
| Preview overlay toolbar | Provides compact icon+text or segmented controls for `文字/Logo 图层` and `安全区`. Selected states must be visible and keyboard-accessible. |
| Safe-zone overlay | Draws stable template zones over the existing 2D preview without resizing the preview panel. Zones are guidance only and must not imply installer-accurate production templates. |
| Warning panel | Renders rule-based warnings from backend metadata and frontend preview checks. Rights warnings remain blocking; quality/template warnings are visible but non-blocking unless the API rejects the request. |
| PreviewSpec panel | Shows canvas, template/view, safe-zone count, overlay count, warning count, source version/artifact, and a compact JSON/manifest preview if available. |
| Export manifest | Includes Phase 6 spec and warning summary when present while preserving the concept-preview disclaimer from Phase 5. |
| Future gates | True 3D UV preview, production print preflight, layered source export, broad vehicle templates, and marketplace remain disabled/deferred. |

## Interaction Contract

- Editing itasha fields updates the structured brief. It does not auto-submit generation.
- Existing generation, child iteration, feedback, and concept export behavior must continue to work when Phase 6 fields are absent.
- Enabling text/logo overlays affects preview-layer visibility and stored overlay/spec metadata. It must not claim that the AI raster image rendered exact text.
- Safe-zone overlay toggles are local UI state for visibility; saved preview-spec data records the zones available for the selected template/view.
- Unsupported templates/views continue to normalize to `generic-side-coupe` / `side` and show a concise warning.
- Missing or unconfirmed asset rights block logo overlay use and generation reference selection.
- Selecting a different version updates overlay/spec/warning context for that version without clearing chat, parameters, assets, feedback, or export state.
- Export remains a concept package. Phase 6 metadata can be included in the manifest, but UI copy must not describe it as production-ready.

## Copywriting Contract

| Element | Copy |
|---------|------|
| Itasha controls title | `痛车设计控制` |
| Character focus label | `角色焦点` |
| Supporting graphics label | `辅助图形` |
| Racing cues label | `赛车/JDM 元素` |
| Typography intent label | `字体意图` |
| Color harmony label | `配色协调` |
| Overlay toggle | `文字/Logo 图层` |
| Safe-zone toggle | `安全区` |
| Safe-zone legend title | `模板参考区` |
| Warning title | `质量提示` |
| Rights blocked warning | `素材权利未确认，不能用于生成或 Logo 图层。` |
| Template warning | `当前车型/视角已归一到 generic-side-coupe / side。` |
| Text readability warning | `文字可能过小或靠近复杂区域，建议放大或减少字数。` |
| Risky-zone warning | `角色脸部或文字靠近车窗、轮拱或边缘区域。` |
| Preview spec title | `PreviewSpec` |
| Preview spec empty | `当前版本暂无可检查的 PreviewSpec。` |
| Export disclaimer | `概念预览，不是生产印刷文件。` |
| Deferred 3D label | `真实 3D 贴图后续开放` |
| Deferred production label | `生产级模板与印刷校验后续开放` |

Visible copy should name the current risk or action. Do not add tutorial paragraphs or explain the feature set in the workbench.

## Accessibility And Responsiveness

- Overlay and safe-zone toggles must expose `aria-pressed` or equivalent selected state.
- Icon-only overlay buttons require `aria-label` and a visible tooltip-equivalent title.
- Safe-zone overlays must not be the only source of meaning; the legend must name each zone type.
- Warning updates that affect generation/export eligibility should be in an `aria-live="polite"` region.
- Text inputs and textareas must keep labels visible and must not overflow at 320px width.
- Overlay canvases or absolutely positioned layers must be bounded by the preview container and must not intercept unrelated buttons.
- Preview panel height and aspect ratio must remain stable when overlays are toggled.
- All Chinese button labels must remain readable on mobile; if a control wraps, it wraps to a stable second line without changing neighboring controls.

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none imported during planning | not required |
| local primitives | `Button`, `Card`, `Badge`, `Alert`; optional local `Switch`/segmented primitive | maintain existing APIs or update tests |
| third-party registry | none | blocked unless separately reviewed |

## Verification Contract

Phase 6 UI implementation is not complete until all of these have current evidence:

- Web tests prove the itasha controls render, update the structured brief payload, and preserve existing brief fields.
- Web tests prove overlay and safe-zone toggles render selected state and do not require a generated artifact to avoid runtime errors.
- Web tests prove missing/uncertain asset rights block logo overlay use while non-blocking quality warnings remain visible.
- Web tests prove `PreviewSpec` summary/manifest data renders for a generated version when metadata is present.
- Web tests prove concept export manifest preserves the Phase 5 disclaimer and includes Phase 6 preview-spec/warning summary when available.
- Web tests prove future 3D, production template, print preflight, and layered-source gates remain disabled/deferred.
- Browser verification confirms desktop and mobile layouts remain non-overlapping, no horizontal document scroll appears, and overlay layers stay inside the preview container.
- `corepack pnpm --filter @caragent/web lint`, `typecheck`, `test`, and `build` pass.

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-06-18
