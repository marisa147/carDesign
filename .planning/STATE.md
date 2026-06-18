---
gsd_state_version: 1.0
milestone: v2.0
milestone_name: V2 MVP
status: executing
stopped_at: Phase 11 Plan 04 complete; ready to execute 11-05-PLAN.md
last_updated: "2026-06-18T14:40:41Z"
last_activity: "2026-06-18 -- Completed Phase 11 Plan 04 worker/provider reference handling"
progress:
  total_phases: 7
  completed_phases: 3
  total_plans: 48
  completed_plans: 24
  percent: 50
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-18)

**Core value:** 用户能用自然语言快速得到一套可预览、可迭代、可导出的高质量痛车设计方案。
**Current focus:** Phase 11 — Reference-Guided Generation MVP

## Current Position

Milestone: v2.0 V2 MVP — PHASE 11 IN PROGRESS
Phase: 11 (Reference-Guided Generation MVP) — IN PROGRESS
Plan: 11-05-PLAN.md — Reference trace persistence in model runs, artifacts, versions, and exports
Status: Executing Phase 11
Last activity: 2026-06-18 -- Completed Phase 11 Plan 04 worker/provider reference handling

Progress: [#####-----] 50%

## Milestone Archives

- `.planning/milestones/v1.0-ROADMAP.md`
- `.planning/milestones/v1.0-REQUIREMENTS.md`
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.0-phases/`
- `.planning/MILESTONES.md`
- `.planning/RETROSPECTIVE.md`

## Current Milestone Scope

v2.0 MVP is scoped to the following phase sequence:

| Phase | Focus | Plans | Requirements |
|-------|-------|-------|--------------|
| Phase 8 | V1 Closure And V2 Readiness Gate | 5/5 | V2-READY-01..04 |
| Phase 9 | Hosted Provider Rollout MVP | 7/7 | V2-PROVIDER-01..05 |
| Phase 10 | Targeted Regeneration And Masked Editing MVP | 8/8 | V2-EDIT-01..05 |
| Phase 11 | Reference-Guided Generation MVP | 4/7 in progress | V2-REF-01..05 |
| Phase 12 | Lightweight 3D Preview MVP | 0/8 | V2-3D-01..05 |
| Phase 13 | Enhanced Concept Handoff Package MVP | 0/7 | V2-HANDOFF-01..05 |
| Phase 14 | V2 MVP Hardening, Docs, Smoke, And UAT | 0/6 | V2-REL-01..05 |

## Prior Milestone Metrics

**v1.0 Velocity:**

- Total plans completed: 54
- Total phases completed: 7
- v1 requirements completed: 42/42
- Source scale at close: about 112 source files / 17,452 LOC, excluding tests and runtime generated artifacts.

**v1.0 By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| Phase 1 | 12/12 | Complete |
| Phase 2 | 9/9 | Complete |
| Phase 3 | 7/7 | Complete |
| Phase 4 | 7/7 | Complete |
| Phase 5 | 7/7 | Complete |
| Phase 6 | 5/5 | Complete |
| Phase 7 | 7/7 | Complete |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.

Recent decisions affecting v2.0:

- [Milestone v1.0]: Deliver an end-to-end concept-generation MVP before broad templates, production handoff, true 3D, or marketplace flows.
- [Milestone v1.0]: Keep provider/model selection config-driven and re-verify hosted provider production readiness before non-local rollout.
- [Milestone v1.0]: Treat PostgreSQL/object storage as canonical for jobs, artifacts, versions, provider runs, costs, feedback, and exports.
- [Milestone v1.0]: Keep exported files labeled as concept preview until production handoff validation exists.
- [Milestone v2.0]: Use `C:/Users/25858/Downloads/V2_MVP_ROADMAP (1).md` as the milestone source for requirements and roadmap.
- [Milestone v2.0]: Continue phase numbering from v1.0, so V2 work starts at Phase 8.
- [Phase 10 Plan 01]: Targeted edits use shared `caragent_core.editing` Pydantic schemas; iteration jobs persist `edit_intent` with route-derived parent version id.
- [Phase 10 Plan 02]: Workbench targeted edits use selected-version PreviewSpec safe zones and overlay layers; stale target drafts are cleared on selected version changes, and submitted payloads reference the selected generated artifact as mask metadata.
- [Phase 10 Plan 03]: Deterministic recomposition is a local worker route for safe overlay-layer edits; it validates parent PreviewSpec targets, bypasses hosted providers, and writes child version/artifact/model-run trace metadata.
- [Phase 10 Plan 04]: Provider-mask requests now have a normalized `MaskEditRequest` contract and API/worker capability gates; real BFL mask calls remain deferred because current FLUX.2 adapter docs do not verify an explicit mask payload.
- [Phase 10 Plan 05]: Targeted edit executions now write unified route, target, region, mask, prompt-delta, parent-child lineage, and provider/model evidence to durable records already exposed by jobs/version/artifact/model-run APIs.
- [Phase 10 Plan 06]: Targeted edit failures now persist actionable categories, retry eligibility, retry route, blocked reason, and original edit intent; retry API preserves original parent/mask/provider metadata and the workbench hides retry for non-retryable failures.
- [Phase 10 Plan 07]: Targeted edit child versions can now be compared against parents in the workbench with route type, target, prompt delta, provider/model/cost evidence, and metadata-backed region highlighting.
- [Phase 10 Plan 08]: Phase 10 focused regression, provider-off smoke dry run, contracts check, and aggregate validation passed; targeted edit docs, UAT checklist, and milestone notes now close V2-EDIT-01..05.
- [Phase 11 Planning]: Reference guidance is planned around structured `reference_usage`, six explicit roles, rights/source snapshots, provider capability filtering, durable trace metadata, provider-off automated validation, and manual-only hosted reference smoke.
- [Phase 11 Plan 01]: Reference roles, reference assignment helpers, rights/source snapshot contracts, provider reference capability metadata, API passthrough, and generated OpenAPI/TypeScript contracts are in place.
- [Phase 11 Plan 02]: Workbench asset rows now assign six reference roles, rights-missing assets are not generation-eligible, and parameter saves submit structured `reference_usage` while preserving legacy ids.
- [Phase 11 Plan 03]: Prompt planning now normalizes structured/legacy references, records included and omitted ids, and surfaces provider-unsupported reference roles as deterministic warnings.
- [Phase 11 Plan 04]: Worker/provider requests now carry reference usage metadata, local deterministic records prompt-only reference trace, and BFL reference-image usage fails closed before provider execution.

### Pending Todos

None.

### Blockers/Concerns

- Real provider-mask hosted calls remain deferred until a mask-specific provider adapter path is explicitly implemented and verified.
- Hosted provider quality, pricing, moderation, account access, quota behavior, and commercial terms must remain guarded before hosted generation rollout.
- Hosted provider calls must stay feature-flagged and quota guarded to avoid accidental cost spikes.
- 3D preview must keep non-production labels and avoid implying verified wrap-shop UV accuracy.
- Reference usage must preserve rights/source metadata gates and snapshots.
- Contract drift must be checked in each phase because v2.0 extends the v1.0 schema surface.

## Deferred Items

Items acknowledged and deferred beyond v2.0 MVP:

| Category | Item | Status |
|----------|------|--------|
| Production Handoff | Full print-ready PSD/AI/PDF handoff with verified scale, bleed, color profile, DPI, and installer notes | Future milestone |
| 3D Preview | Verified vehicle-specific UV mapping for every supported vehicle | Future milestone |
| Business/Community | Marketplace, public gallery, payments, ordering, quoting, installer network, and collaboration workflows | Future milestone |
| Rights | Fully automated copyright/licensing verification | Future milestone |
| Advanced Generation | Guaranteed physically aligned multi-view generation across side/front/rear/hood | Future milestone |
| Orchestration | Advanced multi-agent orchestration beyond typed generation and worker pipeline | Future milestone |

## Session Continuity

Last session: 2026-06-18T14:40:41Z
Stopped at: Phase 11 Plan 04 complete; ready to execute 11-05-PLAN.md
Resume files:

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/phases/09-hosted-provider-rollout-mvp/09-MILESTONE-NOTES.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-CONTEXT.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-RESEARCH.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-VALIDATION.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-PATTERNS.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-01-PLAN.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-01-SUMMARY.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-02-PLAN.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-02-SUMMARY.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-03-PLAN.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-03-SUMMARY.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-04-PLAN.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-04-SUMMARY.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-05-PLAN.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-05-SUMMARY.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-06-PLAN.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-06-SUMMARY.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-07-PLAN.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-07-SUMMARY.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-08-PLAN.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-VERIFICATION.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-HUMAN-UAT.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-MILESTONE-NOTES.md`
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-08-SUMMARY.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-CONTEXT.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-RESEARCH.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-UI-SPEC.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-PATTERNS.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-VALIDATION.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-01-PLAN.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-01-SUMMARY.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-02-PLAN.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-02-SUMMARY.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-03-PLAN.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-03-SUMMARY.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-04-PLAN.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-04-SUMMARY.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-05-PLAN.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-06-PLAN.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-07-PLAN.md`

Next recommended command: `$gsd-execute-phase 11 --auto --plan 11-05 --no-transition`
Alternative: `$gsd-progress --next`
