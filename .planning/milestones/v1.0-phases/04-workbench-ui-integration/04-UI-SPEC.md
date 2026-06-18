---
phase: 4
slug: workbench-ui-integration
status: approved
shadcn_initialized: partial
preset: local-minimal
created: 2026-06-17
---

# Phase 4 - UI Design Contract

> Visual and interaction contract for the frontend workbench phase. Generated in GSD auto mode and checked against the Phase 4 context, `init.MD`, and `UI.png`.

---

## Design System

| Property | Value |
|----------|-------|
| Tool | Tailwind CSS with local shadcn-style primitives |
| Preset | local-minimal |
| Component library | Local `Button`, `Card`, `Badge`, `Alert`; add local primitives only as needed |
| Icon library | `lucide-react` |
| Font | system UI stack from `apps/web/src/app/globals.css` |

## Visual Direction

Phase 4 should feel like a serious design operations surface: dense, calm, scannable, and ready for repeated use. Use `UI.png` as the shape reference: chat on the left, 2D preview in the main workspace, structured controls and assets/history close at hand.

Do not make a hero page. Do not put UI cards inside other cards. Page sections should be unframed layout zones; cards are only for repeated items, panels, status blocks, and modals.

## Layout Contract

| Region | Desktop | Narrow Screens | Purpose |
|--------|---------|----------------|---------|
| App header | 56px fixed-height top bar | 64-72px wrapping bar | Workspace identity, health, mode, future gates |
| Chat rail | 320-380px left rail | First stacked region | Durable messages, prompt input, assistant/system feedback |
| Preview workspace | Flexible center, min width 420px | Second stacked region | 2D artifact preview, progress, view controls |
| Inspector rail | 340-400px right rail | Third stacked region | Parameters, assets, versions, deferred controls |
| Status strip | Compact bottom or preview footer | Inside preview region | Job status, event count, API mode, cost placeholders |

Minimum target widths:
- Desktop: three zones should fit at 1280px without horizontal document scroll.
- Tablet: preview and inspector may stack under chat.
- Mobile: use a single-column flow with stable section ordering and no overlapping text.

## Spacing Scale

Declared values use 4px multiples:

| Token | Value | Usage |
|-------|-------|-------|
| xs | 4px | Icon gaps, status dots, inline metadata |
| sm | 8px | Button gaps, form label gaps, thumbnail gaps |
| md | 16px | Panel padding, form groups, chat message spacing |
| lg | 24px | Workbench zone padding and primary grid gaps |
| xl | 32px | Major vertical breathing room inside stacked mobile layout |
| 2xl | 48px | Reserved for full-page section separation only |

Exceptions: none.

## Typography

| Role | Size | Weight | Line Height | Usage |
|------|------|--------|-------------|-------|
| Body | 14px | 400 | 1.5 | Chat text, descriptions, event messages |
| Label | 12px | 500 | 1.35 | Field labels, tabs, metadata |
| Compact | 13px | 500 | 1.4 | Buttons, nav, status chips |
| Heading | 18px | 600 | 1.25 | Panel titles and workbench region headings |
| Display | 24px | 650 | 1.18 | App-level heading only, rarely used |

Letter spacing remains `0`. Do not scale font size with viewport width.

## Color

| Role | Value | Usage |
|------|-------|-------|
| Dominant (60%) | `#F7F8FB` | App background |
| Secondary (30%) | `#FFFFFF`, `#F1F5F9` | Panels, inputs, muted surfaces |
| Text | `#111827`, `#4B5563`, `#6B7280` | Primary, secondary, muted copy |
| Accent (10%) | `#5B5EF7` | Primary submit, selected nav, active view control |
| Support | `#0EA5A4` | Generated/ready preview markers and non-primary highlights |
| Warning | `#B45309` | Missing rights, deferred/experimental status |
| Success | `#15803D` | Succeeded jobs and confirmed saved state |
| Destructive | `#DC2626` | Failed jobs and destructive actions only |

Accent reserved for: send/generate CTA, selected workbench tab, selected view control, active preview focus ring. Do not tint the whole interface purple.

## Component Contract

| Component | Required Behavior |
|-----------|-------------------|
| Chat panel | Shows durable user/system/assistant messages, prompt input, send button with icon, disabled/working states, and error feedback. |
| Parameter panel | Uses labeled inputs or compact segmented controls for template/view/style/coverage/palette/text. Edits are explicit and saved through API mutation. |
| Asset panel | Upload button, list of assets, rights/source status, and blocked state for assets that cannot be used in generation. |
| Progress panel | Shows status chip, last event, recent event list, retry action for failed retryable jobs, and refresh/polling state. |
| Preview canvas | Stable aspect-ratio 2D preview region with empty/loading/succeeded/failed states, zoom/reset controls, and no layout shift when image state changes. |
| Version strip | Horizontal thumbnail list with selected state, title/status/time metadata, and empty state before generated versions exist. |
| Future gates | Disabled or experimental controls for 3D, print-ready export, marketplace, and production handoff with concise labels. |

## Interaction Contract

- Sending chat text creates a durable user message and creates or updates a structured brief from the current text.
- Generation starts only when the user activates the generation CTA. Parameter edits and asset uploads do not auto-submit generation.
- Refresh/polling reads canonical job/events/artifacts/versions from the API. UI optimistic states may be used only while a mutation is pending.
- Selecting a version changes preview and inspector focus without erasing chat, parameters, assets, or job history.
- Preview zoom/pan/reset are local UI state only. They must not mutate design version data.
- Disabled future gates must be keyboard-focus safe, visibly disabled, and labelled as deferred/experimental.

## Copywriting Contract

| Element | Copy |
|---------|------|
| Primary chat CTA | `发送需求` |
| Generation CTA | `生成 2D 概念` |
| Empty preview heading | `还没有生成图` |
| Empty preview body | `发送设计需求并生成概念后，这里会显示最新 2D 预览。` |
| Empty asset body | `上传参考图、Logo 或车辆照片，并补充来源/权利信息后再用于生成。` |
| Error state | `状态暂不可用。请确认 API、Worker 和本地服务已启动后刷新。` |
| Failed job action | `重试生成` |
| Deferred 3D label | `3D 预览后续开放` |
| Deferred export label | `生产导出后续开放` |

Copy should describe the current state and next action. Do not put visible instructional paragraphs into the workbench.

## Accessibility And Responsiveness

- Every icon-only button must have `aria-label` and a title or tooltip-equivalent name.
- Form fields must have visible labels tied to inputs.
- Status changes that matter to workflow progress should be in an `aria-live="polite"` region.
- Buttons must maintain stable dimensions when loading text or spinner appears.
- Text must not overflow buttons, chips, thumbnails, or panel cards at 320px viewport width.
- The preview region must retain a stable aspect ratio across image/loading/empty states.

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|----------|-------------|-------------|
| shadcn official | none imported during planning | not required |
| local primitives | Button, Card, Badge, Alert | maintain existing APIs or update tests |
| third-party registry | none | blocked unless separately reviewed |

## Verification Contract

Phase 4 UI implementation is not complete until all of these have current evidence:

- Web tests prove chat submission creates a durable user message and brief.
- Web tests prove parameter edits call the update-brief route and refresh canonical state.
- Web tests prove asset upload/list/rights UI calls generated API routes and blocks missing-rights assets from generation selection.
- Web tests prove queued/running/succeeded/failed job states and recent events render distinctly.
- Web tests prove 2D preview/version selection changes selected artifact/version without losing context.
- Web tests prove future 3D/export/marketplace controls are disabled or labelled deferred.
- Browser verification confirms the workbench first screen is visible and non-overlapping on desktop and mobile widths.
- `corepack pnpm --filter @caragent/web lint`, `typecheck`, `test`, and `build` pass.

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-06-17
