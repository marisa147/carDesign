---
gsd_state_version: 1.0
milestone: v3.0
milestone_name: Template Library And Production Readiness
status: ready-for-archive
stopped_at: Completed Phase 20; ready for v3.0 milestone archive
last_updated: "2026-06-20T09:25:00+08:00"
last_activity: "2026-06-20 -- Completed Phase 20 V3 hardening, docs, smoke, UAT, and milestone audit"
progress:
  total_phases: 6
  completed_phases: 6
  total_plans: 33
  completed_plans: 33
  percent: 100
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-20)

**Core value:** 用户能用自然语言快速得到一套可预览、可迭代、可导出的高质量痛车设计方案。
**Current focus:** v3.0 milestone archive

## Current Position

Milestone: v3.0 Template Library And Production Readiness — COMPLETE, READY TO ARCHIVE
Phase: Phase 20 — V3 Hardening, Docs, Smoke, And UAT
Plan: none active
Status: Ready to run `$gsd-complete-milestone`
Last activity: 2026-06-20 -- Completed Phase 20 V3 hardening, docs, smoke, UAT, and milestone audit

Progress: [##########] 100%

## Milestone Archives

- `.planning/milestones/v1.0-ROADMAP.md`
- `.planning/milestones/v1.0-REQUIREMENTS.md`
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md`
- `.planning/milestones/v1.0-phases/`
- `.planning/milestones/v2.0-ROADMAP.md`
- `.planning/milestones/v2.0-REQUIREMENTS.md`
- `.planning/MILESTONES.md`
- `.planning/RETROSPECTIVE.md`

## Current Milestone Scope

v3.0 Template Library And Production Readiness is scoped to the following phase sequence:

| Phase | Focus | Plans | Requirements |
|-------|-------|-------|--------------|
| Phase 15 | Template Source Governance And Compatibility | 5/5 complete | V3-TEMPLATE-01..05 complete |
| Phase 16 | MVP Generic Template Pack | 6/6 complete | V3-PACK-01..06 complete |
| Phase 17 | Template Catalog API And Workbench Selection | 6/6 complete | V3-CATALOG-01..05 complete |
| Phase 18 | Template-Aware Generation, Preview, And Editing | 6/6 complete | V3-INTEGRATION-01..06 complete |
| Phase 19 | Concept Handoff And Production Readiness Preflight | 5/5 complete | V3-PREFLIGHT-01..04 complete |
| Phase 20 | V3 Hardening, Docs, Smoke, And UAT | 5/5 complete | V3-REL-01..05 complete |

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

**v2.0 Velocity:**

- Total plans completed: 48
- Total phases completed: 7
- v2 requirements completed: 34/34
- Source-plus-test scale at close: about 30,301 LOC across `apps/`, `packages/`, `services/`, `scripts/`, and `infra/`, excluding generated contracts and dependency folders.

**v2.0 By Phase:**

| Phase | Plans | Status |
|-------|-------|--------|
| Phase 8 | 5/5 | Complete |
| Phase 9 | 7/7 | Complete |
| Phase 10 | 8/8 | Complete |
| Phase 11 | 7/7 | Complete |
| Phase 12 | 8/8 | Complete |
| Phase 13 | 7/7 | Complete |
| Phase 14 | 6/6 | Complete |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.

Recent decisions affecting v2.0 and v3.0:

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
- [Phase 11 Plan 05]: Reference trace metadata now snapshots roles and rights/source evidence across model runs, artifacts, versions, job metadata/events, and concept export manifests.
- [Phase 11 Plan 06]: Workbench reference UX now shows pre-submit provider role limitations, progress/reference trace diagnostics, generated-version trace evidence, and child iteration reference reuse.
- [Phase 11 Plan 07]: Phase 11 focused validation, provider-off smoke dry run, contracts check, aggregate validation, docs, UAT checklist, and milestone notes now close V2-REF-01..05.
- [Phase 12 Planning]: Lightweight 3D preview is planned around a typed `Preview3DSpec`, one `generic-side-coupe` shell fixture, client-only Three.js viewer, screenshot artifact persistence, explicit 2D fallback, browser canvas-pixel evidence, and persistent non-production labels.
- [Phase 12 Plan 01]: Core `Preview3DSpec`, screenshot metadata, `preview_3d_screenshot` artifact kind, optional typed API response fields, and generated OpenAPI/TypeScript contracts are in place.
- [Phase 12 Plan 02]: `generic-side-coupe-lightweight-v1` is registered for the `generic-side-coupe` side PreviewSpec, unsupported templates produce explicit 2D fallback specs, and frontend compatibility helpers are pure/testable before Three.js rendering.
- [Phase 12 Plan 03]: The workbench now has a 2D/3D preview mode switch, local 3D camera state, client-only dynamic Three.js viewer scaffold, no-WebGL fallback, and persistent non-production 3D labels.
- [Phase 12 Plan 04]: PreviewSpec safe zones and overlays now map to bounded structural material entries with source artifact evidence, visible UV-not-verified warning text, and viewer marker rendering.
- [Phase 12 Plan 05]: 3D preview screenshots now persist through a feature-flagged version-scoped API as immutable `preview_3d_screenshot` artifacts with generated contracts and a web capture action.
- [Phase 12 Plan 06]: Required 3D preview screenshot warnings are now centralized in core contracts and restored server-side, while the web panel exposes persistent non-production labeling through visible text and an accessible region name.
- [Phase 12 Plan 07]: Browser desktop/mobile UAT now has headless Chrome CDP screenshot evidence and screenshot-crop pixel statistics for a nonblank lightweight 3D preview; the viewer constrains WebGL canvas CSS sizing and adjusts camera distance for narrow aspect ratios while keeping non-production labels and accessible controls visible.
- [Phase 12 Plan 08]: Phase 12 closed with focused validation, elevated aggregate `pnpm validate`, worker dry-run smoke, browser UAT evidence, docs, and V2-3D-01..05 traceability complete; lightweight 3D remains concept-only and not production UV proof.
- [Phase 13 Planning]: Enhanced concept handoff package is planned around `enhanced_concept_handoff_zip`, typed schema-versioned manifests, object storage reads, ZIP package building, immutable export artifacts, workbench package preview/history, rights/source guardrails, provider-off validation, and browser UAT.
- [Phase 13 Plan 01]: Handoff package schema helpers, the explicit `enhanced_concept_handoff_zip` export format, and object storage read support are in place for later deterministic report rendering and ZIP assembly.
- [Phase 13 Plan 02]: Core handoff report helpers now build warning, safe-zone, reference, notes, and prompt trace outputs with concept-only disclaimers and sanitizer coverage for secrets, base64, binary markers, and local paths.
- [Phase 13 Plan 03]: Core can now build enhanced handoff ZIP bytes from object storage with stable manifest/report/image paths, required concept-image read failures, optional screenshot warning behavior, and SHA-256 package evidence.
- [Phase 13 Plan 04]: The version-scoped export API now feature-gates `enhanced_concept_handoff_zip`, creates immutable ZIP export artifacts, records succeeded export rows, and has regenerated OpenAPI/TypeScript contracts.
- [Phase 13 Plan 05]: The Workbench now exposes feature-flagged ZIP handoff export mode with package readiness preview, safe request manifests, selected `generated_image` source artifacts, and ZIP history rows with returned package evidence.
- [Phase 13 Plan 06]: Enhanced handoff package creation now blocks missing, rejected, or source-less included reference rights metadata in core/API, while the Workbench shows `缺少版权或来源信息` and keeps missing 3D screenshots as warning-only.
- [Phase 13 Plan 07]: Phase 13 closed with focused validation, regenerated/current contracts, provider-off worker dry-run, elevated aggregate validation, desktop/mobile browser UAT evidence, docs, and V2-HANDOFF-01..05 traceability complete; enhanced handoff ZIPs remain concept-only and not print-ready.
- [Phase 14 Planning]: Release hardening is planned as six plans covering aggregate validation, Docker smoke, manual hosted-provider smoke, desktop/mobile V2 browser UAT, feature-flag/docs reference, and final V2 MVP release evidence.
- [Phase 14 Plan 01]: Fresh release baseline validation passed: aggregate `pnpm validate`, contract drift check, V1 compatibility, migration safety, and provider-off worker dry-run smoke are green; Docker/live smoke remains Phase 14 Plan 02.
- [Phase 14 Plan 02]: Docker-backed `smoke:local` passed for PostgreSQL, Redis, MinIO, Alembic, Phase 2 durable data smoke, and Phase 3 local deterministic generation smoke; hosted-disabled worker dry-run passed; live worker smoke was attempted but not counted as passed.
- [Phase 14 Plan 03]: Hosted-provider release smoke remains manual-only, credentialed, cost-guarded, one-job limited, and reversible; no live hosted output quality/account/pricing/moderation readiness is claimed without explicit evidence.
- [Phase 14 Plan 04]: Desktop/mobile browser UAT passed with no-secret provider-off fixture evidence for hosted guard visibility, targeted edit controls/comparison, reference warnings, lightweight 3D labels, enhanced ZIP handoff preview/history, and no horizontal overflow.
- [Phase 14 Plan 05]: V2 release docs now map service/browser feature flags, hosted provider config, quota/rate/cost guards, manual smoke overrides, rollback, Docker smoke, Browser UAT evidence, and concept-only/not print-ready boundaries.
- [Phase 14 Plan 06]: V2 MVP final validation passed, release notes/milestone notes/verification were created, V2-REL-01..05 were marked complete, and the milestone is ready for archive.
- [Milestone v3.0]: Use `C:/Users/25858/Downloads/MVP_FINAL.md` as the source for the next milestone after v2.0 archive.
- [Milestone v3.0]: Prioritize template source governance, internal generic template pack, catalog selection, and concept-only production readiness before print-ready handoff, verified UV, marketplace, or ordering flows.
- [Milestone v3.0]: Continue phase numbering from v2.0, so V3 work starts at Phase 15.
- [Milestone v3.0]: Keep old v2 phase directories intact for evidence; new v3 planning starts with living `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md`.
- [Phase 15 Plan 01]: Template source policies, source metadata, readiness reports, and audit item models now exist in `caragent_core.generation.templates`.
- [Phase 15 Plan 02]: Template registration now requires reusable source/license state, usage scope, rights notes, and audit timestamp; registry audit exposes readiness and missing asset slots.
- [Phase 15 Plan 03]: Prohibited source types and non-reusable license statuses fail closed before reusable template records can enter the registry.
- [Phase 15 Plan 04]: `generic-side-coupe` remains the stable v1/v2 id, while `generic_coupe_side_v1` resolves as a compatibility alias and new brief/prompt/PreviewSpec payloads carry source/readiness metadata.
- [Phase 15 Plan 05]: Template governance docs, OpenAPI, generated TypeScript contracts, focused validations, and code review now close V3-TEMPLATE-01..05.
- [Phase 16 Plan 01]: The core template registry now loads five package-backed MVP records from `template.json` and `safe_zones.json`, with `generic-side-coupe` preserved as the legacy alias for the canonical coupe id.
- [Phase 16 Plan 02]: A deterministic local generator creates internal-original PNG and JSON assets for coupe, sedan, hatchback, SUV, and van without external vehicle imagery.
- [Phase 16 Plan 03]: `python -m caragent_core.generation.validate_template_pack` validates ids, required slots, PNG dimensions, non-empty masks, metadata, readiness, and normalized safe zones.
- [Phase 16 Plan 04]: Generation briefs and prompt PreviewSpecs preserve selected MVP template id, label, source/license state, readiness, warnings, and safe zones.
- [Phase 16 Plan 05]: Template governance docs now document the MVP pack manifest, asset slots, validation command, and concept-only boundary.
- [Phase 16 Plan 06]: Focused core/API/worker tests, lint, mypy, visual thumbnail checks, verification, and review close V3-PACK-01..06.
- [Phase 17 Plan 01]: FastAPI now exposes typed template catalog list/detail endpoints with canonical id and legacy alias resolution.
- [Phase 17 Plan 02]: Template thumbnails are served from package resources as path-safe PNG responses.
- [Phase 17 Plan 03]: Brief template updates re-resolve selected template payloads and generation/iteration jobs carry selected-template metadata.
- [Phase 17 Plan 04]: Frontend contracts, template API helpers, query keys, Workbench selected-template state, and resume loading are in place.
- [Phase 17 Plan 05]: Workbench parameter panel now has a filterable template selector with thumbnail, source/license, readiness, warning, and disabled states.
- [Phase 17 Plan 06]: Phase 17 focused and aggregate validations passed; V3-CATALOG-01..05 are complete.
- [Phase 18 Planning]: Template-aware generation is scoped around PreviewSpec as the selected-version contract; no print-ready, verified UV, or real vehicle shell claims are added.
- [Phase 18 Plan 01]: Worker generation tests now run local deterministic jobs for every MVP template and assert selected-template trace on model runs, artifacts, versions, job operations, and final events.
- [Phase 18 Plan 02]: Core prompt planning chooses overlay safe zones from the selected template, and Workbench PreviewSpec summary displays template id/view/warnings from the selected version.
- [Phase 18 Plan 03]: Workbench targeted edits use selected-template safe-zone coordinates, clear stale targets on version changes, and worker recomposition preserves template trace.
- [Phase 18 Plan 04]: Reference-guided generation records concise template context alongside reference roles, rights snapshots, provider/model metadata, and cost trace.
- [Phase 18 Plan 05]: Lightweight 3D compatibility resolves both legacy `generic-side-coupe` and canonical `generic_coupe_side_v1`, while unsupported MVP templates fall back with selected-template reason text.
- [Phase 18 Plan 06]: Phase 18 validations, elevated contracts check, web/core/worker typechecks, and archived PreviewSpec regression coverage passed; V3-INTEGRATION-01..06 are complete.
- [Phase 19 Planning]: Concept handoff preflight is scoped as a concept-only report and must not imply print-ready production output.
- [Phase 19 Plan 01]: Core production readiness preflight models now report missing production evidence and template validation while keeping print-ready disallowed.
- [Phase 19 Plan 02]: API now creates version-scoped preflight reports as durable JSON export artifacts and export ledger records.
- [Phase 19 Plan 03]: Workbench export panel now runs preflight, shows concept-only status, and renders missing evidence labels for the selected version.
- [Phase 19 Plan 04]: Enhanced handoff ZIPs now include `production-readiness-preflight.json`, `template-validation.json`, and matching manifest evidence.
- [Phase 19 Plan 05]: Phase 19 validations passed; V3-PREFLIGHT-01..04 are complete and print-ready PSD/AI/PDF exports remain blocked.
- [Phase 20 Plan 01]: V3 aggregate validation, template-pack validation, v1 compatibility, migration safety, and worker smoke dry-run passed without hosted credentials.
- [Phase 20 Plan 02]: Docker/local smoke passed through explicit `infra:up`, `smoke:local`, and `infra:down`; the `--with-compose-if-docker` wrapper issue was limited to a Windows elevated pnpm shim lookup.
- [Phase 20 Plan 03]: Desktop/mobile Browser UAT passed with fixture-backed template catalog, selected van PreviewSpec, targeted edit controls, 3D fallback, enhanced handoff, preflight, concept-only labels, and no horizontal overflow.
- [Phase 20 Plan 04]: V3 release notes and docs now explain template governance, MVP template pack, validation commands, concept-only boundaries, and future production promotions.
- [Phase 20 Plan 05]: V3 milestone audit passed with all 31 v3.0 requirements complete and archive-ready.

### Pending Todos

None.

### Blockers/Concerns

- Real provider-mask hosted calls remain deferred until a mask-specific provider adapter path is explicitly implemented and verified.
- Hosted provider quality, pricing, moderation, account access, quota behavior, and commercial terms must remain guarded before hosted generation rollout.
- Hosted provider calls must stay feature-flagged and quota guarded to avoid accidental cost spikes.
- 3D preview must keep non-production labels and avoid implying verified wrap-shop UV accuracy.
- Enhanced handoff packages must remain concept-only review ZIPs and must not imply print-ready PSD/AI/PDF, verified scale/bleed/color/DPI, production UV, ordering, quoting, payment, marketplace, or installer workflows.
- Frontend Vitest remains blocked in the Codex sandbox by esbuild `spawn EPERM`; targeted runs pass when rerun with approved elevation.
- Hosted reference-image input remains manual-only until provider/model support, credentials, cost approval, and quota guards are verified.
- Contract drift must be checked in each phase because v2.0 extends the v1.0 schema surface.
- V3 template assets must be `internal_original`, licensed, or user-provided-with-rights; web-crawled or third-party reference-only material must not enter reusable template assets, masks, thumbnails, or catalog entries.
- Concept handoff and preflight keep non-production labels and avoid implying print-ready PSD/AI/PDF, verified scale/bleed/color/DPI, production UV, or installer readiness.
- v3.0 is complete and ready to archive; future milestones must keep production handoff, verified UV, marketplace/order flows, hosted-provider production claims, and automated licensing outside scope until their evidence is explicitly added.

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

Items acknowledged by `audit-open` at v2.0 milestone close on 2026-06-19:

| Category | Item | Status |
|----------|------|--------|
| UAT metadata | Phase 08 `08-HUMAN-UAT.md` | partial; 2 pending scenarios |
| UAT metadata | Phase 09 `09-HUMAN-UAT.md` | partial; 0 pending scenarios |
| UAT metadata | Phase 10 `10-HUMAN-UAT.md` | checklist-ready; 0 pending scenarios |
| UAT metadata | Phase 11 `11-HUMAN-UAT.md` | checklist-ready; 0 pending scenarios |
| UAT metadata | Phase 12 `12-HUMAN-UAT.md` | passed; 0 pending scenarios |
| UAT metadata | Phase 13 `13-HUMAN-UAT.md` | passed; 0 pending scenarios |
| UAT metadata | Phase 14 `14-HUMAN-UAT.md` | passed; 0 pending scenarios |

## Session Continuity

Last session: 2026-06-20T09:25:00+08:00
Stopped at: Completed Phase 20; ready for v3.0 milestone archive
Resume files:

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/research/V3-MVP-FINAL-ANALYSIS.md`
- `.planning/phases/15-template-source-governance-and-compatibility/15-VERIFICATION.md`
- `.planning/phases/15-template-source-governance-and-compatibility/15-REVIEW.md`
- `.planning/phases/16-mvp-generic-template-pack/16-VERIFICATION.md`
- `.planning/phases/16-mvp-generic-template-pack/16-REVIEW.md`
- `.planning/phases/17-template-catalog-api-and-workbench-selection/17-CONTEXT.md`
- `.planning/phases/17-template-catalog-api-and-workbench-selection/17-VERIFICATION.md`
- `.planning/phases/17-template-catalog-api-and-workbench-selection/17-REVIEW.md`
- `.planning/phases/18-template-aware-generation-preview-and-editing/18-CONTEXT.md`
- `.planning/phases/18-template-aware-generation-preview-and-editing/18-UI-SPEC.md`
- `.planning/phases/18-template-aware-generation-preview-and-editing/18-VERIFICATION.md`
- `.planning/phases/18-template-aware-generation-preview-and-editing/18-REVIEW.md`
- `.planning/phases/19-concept-handoff-and-production-readiness-preflight/19-CONTEXT.md`
- `.planning/phases/19-concept-handoff-and-production-readiness-preflight/19-UI-SPEC.md`
- `.planning/phases/19-concept-handoff-and-production-readiness-preflight/19-VERIFICATION.md`
- `.planning/phases/19-concept-handoff-and-production-readiness-preflight/19-REVIEW.md`
- `.planning/MILESTONES.md`
- `.planning/RETROSPECTIVE.md`
- `C:/Users/25858/Downloads/MVP_FINAL.md`
- `.planning/milestones/v2.0-ROADMAP.md`
- `.planning/milestones/v2.0-REQUIREMENTS.md`
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
- `.planning/phases/11-reference-guided-generation-mvp/11-05-SUMMARY.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-06-PLAN.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-06-SUMMARY.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-07-PLAN.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-VERIFICATION.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-HUMAN-UAT.md`
- `.planning/phases/11-reference-guided-generation-mvp/11-MILESTONE-NOTES.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-CONTEXT.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-RESEARCH.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-UI-SPEC.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-PATTERNS.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-VALIDATION.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-01-PLAN.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-01-SUMMARY.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-02-PLAN.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-02-SUMMARY.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-03-PLAN.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-03-SUMMARY.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-04-PLAN.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-04-SUMMARY.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-05-PLAN.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-05-SUMMARY.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-06-PLAN.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-06-SUMMARY.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-07-PLAN.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-07-SUMMARY.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-HUMAN-UAT.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-08-PLAN.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-08-SUMMARY.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-VERIFICATION.md`
- `.planning/phases/12-lightweight-3d-preview-mvp/12-MILESTONE-NOTES.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-CONTEXT.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-RESEARCH.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-UI-SPEC.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-PATTERNS.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-VALIDATION.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-01-PLAN.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-01-SUMMARY.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-02-PLAN.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-02-SUMMARY.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-03-PLAN.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-03-SUMMARY.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-04-PLAN.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-04-SUMMARY.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-05-PLAN.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-05-SUMMARY.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-06-PLAN.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-06-SUMMARY.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-07-PLAN.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-VERIFICATION.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-HUMAN-UAT.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-MILESTONE-NOTES.md`
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-07-SUMMARY.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-CONTEXT.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-RESEARCH.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-UI-SPEC.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-PATTERNS.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-VALIDATION.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-01-PLAN.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-02-PLAN.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-03-PLAN.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-04-PLAN.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-05-PLAN.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-06-PLAN.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-BASELINE-VALIDATION.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-01-SUMMARY.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-DOCKER-SMOKE.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-02-SUMMARY.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-HOSTED-SMOKE-RUNBOOK.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-03-SUMMARY.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-HUMAN-UAT.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-04-SUMMARY.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-FEATURE-FLAGS.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-DOCS-CHECK.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-05-SUMMARY.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-VERIFICATION.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-RELEASE-NOTES.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-MILESTONE-NOTES.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-06-SUMMARY.md`
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-browser-metrics.json`

Next recommended command: `$gsd-complete-milestone`
Alternative: `$gsd-new-milestone` after archive
