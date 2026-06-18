---
phase: 5
slug: iteration-feedback-and-concept-export
status: approved
shadcn_initialized: partial
preset: local-minimal
created: 2026-06-17
---

# Phase 5 - UI Design Contract

> Visual and interaction contract for adding iteration, feedback, comparison, and concept export to the existing Phase 4 workbench.

## Design System

| Property | Value |
|----------|-------|
| Tool | Tailwind CSS with local shadcn-style primitives |
| Preset | local-minimal |
| Component library | Existing local `Button`, `Card`, `Badge`, `Alert`; add local primitives only if tests justify them |
| Icon library | `lucide-react` |
| Font | Existing system UI stack |

## Visual Direction

Phase 5 should feel like the same serious design operations surface from Phase 4. Add controls to the existing preview/history and inspector surfaces; do not create a landing page, wizard, marketing hero, or separate export portal.

The UI should make version lineage and export safety obvious. Concept exports must read as "review package" or "concept preview", never as production-ready wrap output.

## Layout Contract

| Region | Desktop | Narrow Screens | Purpose |
|--------|---------|----------------|---------|
| Preview action bar | Inside existing preview panel, below selected version metadata | Stacked below preview controls | Regenerate/iterate, export, approve/reject shortcuts |
| Lineage strip | Near version history | Below history list | Parent/child chain, selected version, lineage depth |
| Comparison panel | Inspector rail or below preview when selected | Stacked after preview/history | Parameter and metadata differences between parent and selected version |
| Feedback panel | Inspector rail, near selected version metadata | Stacked after comparison | Rating, approve/reject, comment, saved feedback history |
| Export panel | Inspector rail, near feedback | Stacked after feedback | PNG/JPG choice, export CTA, manifest/status/history |

Maintain the Phase 4 section order on mobile: chat, preview, progress/history, parameters/assets, feedback/export/future gates. No horizontal document scroll at 320px.

## Typography And Spacing

Reuse Phase 4 typography and spacing:
- Body: 14px
- Labels/metadata: 12-13px
- Panel headings: 18px
- App-level display: 24px maximum
- 4px spacing scale, with 8px gaps inside controls and 16px panel padding

Do not scale fonts with viewport width. Letter spacing remains `0`.

## Color

Reuse Phase 4 color roles:
- Accent `#5B5EF7` for selected version, active export format, and primary iteration CTA.
- Support `#0EA5A4` for export-ready and approved states.
- Warning `#B45309` for concept-preview disclaimers and not-print-ready labels.
- Success `#15803D` for saved feedback/export success.
- Destructive `#DC2626` for rejected state only.

The interface must not become a one-note purple theme.

## Component Contract

| Component | Required Behavior |
|-----------|-------------------|
| Iteration controls | Shows selected version, parent version if present, targeted change textarea, regenerate/iterate CTA, disabled state when no version/brief exists, and idempotent pending state. |
| Lineage/history strip | Shows generated versions with parent/child indicators, lineage depth, selected state, and clear empty state. |
| Comparison panel | Shows parent vs selected fields: title/status, style/palette/text/coverage when available, artifact object key, and prompt/model metadata if loaded. If parent is missing, show "base version". |
| Feedback panel | Supports rating 1-5, approve/reject/neutral state, comment, submit, saved feedback history, and loading/error states. |
| Export panel | Supports PNG and JPG/JPEG format selection, export CTA, concept-preview disclaimer, export history, manifest preview, and disabled state when no selected version/artifact exists. |
| Future gates | Production-ready package, print preflight, layered source export, true 3D, and marketplace publishing remain disabled/deferred. |

## Interaction Contract

- Regeneration from a selected version creates a child generation job and preserves the parent version.
- Targeted changes are captured as request text and supported structured parameters. They do not imply mask/inpainting.
- Selecting a child version updates preview/comparison/feedback/export context without clearing chat, parameters, assets, or progress state.
- Feedback submit records durable feedback against the selected version. Approval/rejection must not delete or overwrite artifacts.
- Export submit records a concept export for the selected version and selected format. It must show a manifest preview and "not print-ready" wording.
- Export controls stay disabled until a selected generated version and matching artifact exist.

## Copywriting Contract

| Element | Copy |
|---------|------|
| Iteration CTA | `基于此版本再生成` |
| Targeted change label | `修改要求` |
| Comparison title | `版本对比` |
| Base version label | `基础版本` |
| Feedback title | `反馈与审批` |
| Approve action | `标记通过` |
| Reject action | `标记退回` |
| Export title | `概念导出` |
| Export CTA | `导出概念包` |
| Export disclaimer | `概念预览，不是生产印刷文件。` |
| Deferred production label | `生产级交付后续开放` |

Visible copy should name state and action. Do not add explanatory feature-tour text inside the workbench.

## Accessibility And Responsiveness

- Rating controls must expose accessible names such as `评分 1` through `评分 5`.
- Approve/reject buttons must expose pressed/selected state.
- Export format choices should use segmented buttons or radio controls with clear selected state.
- Feedback submit and export submit must announce saved/error state in an `aria-live="polite"` region.
- Textareas, comments, and manifest previews must not overflow at 320px width.
- Button labels must remain readable in Chinese on mobile.

## Verification Contract

Phase 5 UI implementation is not complete until all of these have current evidence:

- Web tests prove a selected parent version can submit a child iteration request without overwriting the parent.
- Web tests prove lineage/history and comparison update when selecting versions.
- Web tests prove feedback rating/approval/comment submit to the API and render saved history.
- Web tests prove concept export format selection, manifest/disclaimer display, and export history.
- Web tests prove production-ready/layered/print/3D/marketplace gates remain disabled/deferred.
- Browser verification confirms desktop and mobile layouts remain non-overlapping and no horizontal document scroll appears.
- `corepack pnpm --filter @caragent/web lint`, `typecheck`, `test`, and `build` pass.

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-06-17
