# Phase 5: Iteration, Feedback, And Concept Export - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `05-CONTEXT.md`.

**Date:** 2026-06-17
**Phase:** 05-iteration-feedback-and-concept-export
**Mode:** auto assumptions from `$gsd-progress --next`

## Assumptions Presented

| Area | Assumption | Confidence | Evidence |
|------|------------|------------|----------|
| Iteration model | Use durable `design_versions.parent_version_id` and `lineage_depth` for parent/child iteration. | Confident | `services/core/src/caragent_core/services/jobs.py`; `.planning/REQUIREMENTS.md` ITER-01/ITER-03 |
| Feedback | Add durable feedback creation on top of existing feedback table/service/list route. | Confident | `record_feedback`; `/workspaces/{workspace_id}/feedback`; ITER-04 |
| Export | Add concept-preview export creation and manifest metadata, not print-ready production export. | Confident | `record_export`; `.planning/REQUIREMENTS.md` ITER-05/ITER-06; Phase 4 deferred gates |
| UI integration | Extend Phase 4 workbench preview/history surface rather than redesigning the page. | Confident | `04-UI-SPEC.md`; `workbench-app.tsx`; `preview-panel.tsx` |
| Scope boundary | Do not implement true visual diff, masks/inpainting, print preflight, or production handoff in Phase 5. | Confident | `.planning/ROADMAP.md` Phase 5/6/v2 boundaries |

## Auto-Resolved Choices

- Use metadata/parameter comparison first, not pixel-level visual diff.
- Generate child iteration jobs by recording parent version metadata and letting the existing worker create child `DesignVersion` rows.
- Export PNG/JPG concept records plus manifest data, with explicit "not print-ready" wording.
- Keep Browser storage limited to resume ids and UI preferences.

## Deferred Ideas

- Pixel visual diff and mask-based targeted image editing.
- Print-ready layered packages and preflight.
- Signed download URLs and auth-bound private artifact delivery.
