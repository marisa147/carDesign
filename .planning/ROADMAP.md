# Roadmap: 痛车设计生成 Agent v2.0 V2 MVP

## Overview

v1.0 已经建立完整概念生成产品闭环：可运行 monorepo、durable workspaces/jobs/assets、异步 text-to-2D generation、workbench UI、版本化迭代、concept export、itasha-aware controls、template warnings、PreviewSpec persistence，以及主要 operations/provider guardrails。

v2.0 MVP 的目标不是一次性实现完整未来愿景，而是把最强的 v1.0 概念工作流升级为更实用的 design-assist product，新增四组受控能力：

1. Safe hosted-provider rollout with real model calls behind quota, routing, moderation, fallback, and cost controls.
2. Advanced 2D generation controls using masks, targeted regeneration, deterministic recomposition, and reference guidance.
3. Lightweight 3D or pseudo-3D preview using existing PreviewSpec and template assets without claiming production-grade UV accuracy.
4. Minimum concept handoff package that remains clearly labeled as pre-production unless full print validation is implemented later.

v2.0 MVP 仍然不是完整 print-shop handoff system、marketplace、payment/order system、collaborator platform 或 verified vehicle-wrap production tool。它是更高质量的 concept and review workflow，并为后续 production handoff 打基础。

## Milestones

- ✅ **v1.0 MVP** — Phases 1-7 shipped on 2026-06-18. Archive: `.planning/milestones/v1.0-ROADMAP.md`.
- ◆ **v2.0 V2 MVP** — Phases 8-14 planned from `C:/Users/25858/Downloads/V2_MVP_ROADMAP (1).md`.

## V2 MVP Goals

v2.0 MVP is successful when:

1. A user can choose between local deterministic generation and at least one hosted image provider in a controlled environment.
2. A user can upload references and apply them to generation with visible rights/source metadata and clear usage gates.
3. A user can perform targeted changes to a specific region or layer without regenerating the entire concept when avoidable.
4. A user can preview a selected concept on a simple 3D vehicle shell or pseudo-3D viewer using the existing 2D concept and PreviewSpec.
5. A user can export a richer concept package containing preview images, metadata, prompt trace, template warnings, safe-zone overlays, and handoff notes.
6. Operators can inspect provider usage, cost, failures, fallbacks, moderation/validation rejections, and quota decisions.
7. The product continues to clearly distinguish concept preview, 3D preview, and production-ready output.

## Non-Goals

- Full print-ready PSD/AI/PDF handoff with verified scale, bleed, color profile, DPI, and installer notes.
- Verified vehicle-specific UV mapping for every supported vehicle.
- Marketplace, template store, public gallery, payments, ordering, quoting, or installer network.
- Multi-user collaboration, comments, permissions, or team workspaces.
- Fully automated copyright/licensing verification.
- Fully consistent multi-view generation across side/front/rear/hood with guaranteed physical alignment.
- Advanced agentic orchestration beyond the typed generation and worker pipeline.

## Phase Numbering

- v2.0 continues from the archived v1.0 roadmap, so planned work starts at Phase 8.
- Integer phases are milestone work.
- Decimal phases are urgent insertions only and must be marked `INSERTED`.
- Phases execute in numeric order.

## Phases

- [x] **Phase 8: V1 Closure And V2 Readiness Gate** — Close remaining V1 operational work, freeze the V1 release baseline, and confirm V2 can build on stable contracts.
- [x] **Phase 9: Hosted Provider Rollout MVP** — Enable controlled real hosted image generation with provider routing, quota, cost, failure, and moderation visibility.
- [x] **Phase 10: Targeted Regeneration And Masked Editing MVP** — Add editable regions, mask-aware regeneration requests, and layer-level iteration without full concept overwrite.
- [x] **Phase 11: Reference-Guided Generation MVP** — Improve character/style/vehicle consistency using uploaded reference assets, rights gates, and provider-specific capability checks.
- [x] **Phase 12: Lightweight 3D Preview MVP** — Add a simple interactive 3D or pseudo-3D preview that consumes existing PreviewSpec and remains clearly labeled non-production.
- [ ] **Phase 13: Enhanced Concept Handoff Package MVP** — Export a richer concept package with overlays, manifest, prompt trace, warnings, and review notes.
- [ ] **Phase 14: V2 MVP Hardening, Docs, Smoke, And UAT** — Close validation, documentation, regression checks, browser UAT, and release evidence.

## Phase Details

### Phase 8: V1 Closure And V2 Readiness Gate

**Goal:** V2 starts from a stable V1 baseline instead of building on unfinished operational work.

**Depends on:** v1.0 archive

**Requirements:** V2-READY-01, V2-READY-02, V2-READY-03, V2-READY-04

**Success Criteria:**

1. V1 Phase 7 is complete, including hosted-call quota/rate-limit preflight and operations UI closure.
2. A V1 release tag or equivalent baseline exists with verification evidence.
3. Contract drift checks, backend tests, worker tests, frontend tests, Docker smoke, and browser UAT pass from a clean checkout.
4. V2 feature flags are introduced but disabled by default.
5. Operators can run V1 in local-only mode without any hosted provider credentials.

**Plans:** 5 plans

- [x] 08-01-PLAN.md — V1 release baseline, verification inventory, and regression command index.
- [x] 08-02-PLAN.md — V2 feature flag scaffold, environment guards, and default-off rollout settings.
- [x] 08-03-PLAN.md — Contract compatibility check for V1 workbench, jobs, artifacts, versions, and PreviewSpec.
- [x] 08-04-PLAN.md — V2 migration safety review and no-op migration proof.
- [x] 08-05-PLAN.md — Phase 8 smoke, docs, UAT checklist, and readiness report.

**UI hint:** no

### Phase 9: Hosted Provider Rollout MVP

**Goal:** Users and operators can safely test at least one real hosted image provider without losing V1 deterministic behavior or cost control.

**Depends on:** Phase 8

**Requirements:** V2-PROVIDER-01, V2-PROVIDER-02, V2-PROVIDER-03, V2-PROVIDER-04, V2-PROVIDER-05

**Success Criteria:**

1. Operator can configure hosted image provider credentials, model, capability map, timeout, retry, fallback, and quota policy without code changes.
2. User can submit a generation job that uses a hosted provider only when hosted generation is enabled and preflight allows it.
3. System records exact provider, model, request parameters, prompt plan, input assets, estimated cost, actual cost where available, fallback path, and raw error category.
4. Hosted failures are visible to the workbench and operations UI without exposing secrets.
5. Local deterministic provider remains available as a test and fallback path.

**Plans:** 7 plans

- [x] 09-01-PLAN.md — Hosted image provider capability map and typed runtime configuration.
- [x] 09-02-PLAN.md — Hosted provider adapter implementation behind existing provider boundary.
- [x] 09-03-PLAN.md — Hosted preflight integration with quota, rate-limit, runtime mode, and provider health.
- [x] 09-04-PLAN.md — Provider request/response trace persistence, cost recording, and secret redaction.
- [x] 09-05-PLAN.md — Moderation/validation rejection mapping and user-safe failure messages.
- [x] 09-06-PLAN.md — Workbench provider selector, hosted-call warning, and cost/quota visibility.
- [x] 09-07-PLAN.md — Phase 9 smoke, provider-off/provider-on tests, docs, and UAT evidence.

**UI hint:** yes

### Phase 10: Targeted Regeneration And Masked Editing MVP

**Goal:** User can request localized edits to a selected concept area or layer while preserving version lineage and minimizing unnecessary full regeneration.

**Depends on:** Phase 9

**Requirements:** V2-EDIT-01, V2-EDIT-02, V2-EDIT-03, V2-EDIT-04, V2-EDIT-05

**Success Criteria:**

1. User can select a concept region or layer from the workbench and request a targeted edit such as character size, style accent, text placement, decal density, or palette change.
2. System stores edit intent, selected region, mask data, parent version, prompt delta, provider parameters, and generated child version.
3. Worker can choose deterministic recomposition when only layer position/scale/visibility changes are requested.
4. Worker can route mask-aware provider calls when visual content must be regenerated.
5. User can compare parent and child versions and see whether the change was recomposition-only or provider-generated.

**Plans:** 8 plans

- [x] 10-01-PLAN.md — EditIntent, EditRegion, mask asset, and prompt-delta schema.
- [x] 10-02-PLAN.md — Workbench region/layer selection model and mask preview controls.
- [x] 10-03-PLAN.md — Deterministic layer recomposition path for scale, move, opacity, text, and logo edits.
- [x] 10-04-PLAN.md — Mask-aware generation request contract and provider capability checks.
- [x] 10-05-PLAN.md — Worker targeted-edit pipeline with parent/child lineage and artifact ledger updates.
- [x] 10-06-PLAN.md — Edit failure classification, retry eligibility, and rollback-safe UX.
- [x] 10-07-PLAN.md — Version comparison UI for targeted edits and changed-region highlighting.
- [x] 10-08-PLAN.md — Phase 10 smoke, docs, regression tests, and Browser UAT.

**UI hint:** yes

### Phase 11: Reference-Guided Generation MVP

**Goal:** User can use uploaded references to guide character, color, style, vehicle, logo, or composition consistency with explicit rights/source controls.

**Depends on:** Phase 10

**Requirements:** V2-REF-01, V2-REF-02, V2-REF-03, V2-REF-04, V2-REF-05

**Success Criteria:**

1. User can mark uploaded assets as character reference, style reference, vehicle reference, logo reference, palette reference, or inspiration only.
2. System enforces existing rights/source metadata before a reference can be used for generation.
3. Provider request builder includes only supported reference types for the selected provider/model.
4. Unsupported reference usage produces a clear warning instead of silent failure.
5. Generated artifacts store exact reference assets, reference roles, provider parameters, and rights metadata snapshot.

**Plans:** 7 plans

- [x] 11-01-PLAN.md — Reference role schema, rights snapshot, and provider capability contract.
- [x] 11-02-PLAN.md — Asset library UI updates for assigning reference roles and generation eligibility.
- [x] 11-03-PLAN.md — Prompt planner/reference planner integration and unsupported-capability warnings.
- [x] 11-04-PLAN.md — Hosted/local provider reference handling and deterministic fallback behavior.
- [x] 11-05-PLAN.md — Reference trace persistence in model runs, artifacts, versions, and exports.
- [x] 11-06-PLAN.md — Reference-guided generation UX, failure states, and reuse in child iterations.
- [x] 11-07-PLAN.md — Phase 11 smoke, docs, rights-gate tests, and Browser UAT.

**UI hint:** yes

### Phase 12: Lightweight 3D Preview MVP

**Goal:** User can inspect a generated concept on a simple 3D or pseudo-3D vehicle preview without claiming physical wrap accuracy.

**Depends on:** Phase 11

**Requirements:** V2-3D-01, V2-3D-02, V2-3D-03, V2-3D-04, V2-3D-05

**Success Criteria:**

1. Developer can register at least one preview vehicle shell or pseudo-3D template linked to existing vehicle templates and PreviewSpec.
2. User can open a 3D preview panel for a selected 2D design version.
3. Preview supports rotate, zoom, reset camera, screenshot capture, and clear non-production labeling.
4. The system stores 3D preview specs, camera presets, screenshot artifacts, and warning metadata.
5. If no compatible 3D shell exists, the UI clearly falls back to 2D preview without breaking generation or export.

**Plans:** 8 plans

- [x] 12-01-PLAN.md — Preview3DSpec schema, compatibility mapping, and artifact contract.
- [x] 12-02-PLAN.md — Minimal vehicle shell asset registration and local fixture pipeline.
- [x] 12-03-PLAN.md — Frontend 3D preview viewer scaffold with camera controls and fallback states.
- [x] 12-04-PLAN.md — Texture/material mapping from PreviewSpec to lightweight preview shell.
- [x] 12-05-PLAN.md — Screenshot capture, artifact persistence, and version linkage.
- [x] 12-06-PLAN.md — 3D preview warnings, non-production labels, and safe-zone overlay compatibility.
- [x] 12-07-PLAN.md — Browser desktop/mobile performance and accessibility pass.
- [x] 12-08-PLAN.md — Phase 12 smoke, docs, fixture tests, and UAT evidence.

**UI hint:** yes

### Phase 13: Enhanced Concept Handoff Package MVP

**Goal:** User can export a richer review package for concept discussion while still avoiding false print-ready claims.

**Depends on:** Phase 12

**Requirements:** V2-HANDOFF-01, V2-HANDOFF-02, V2-HANDOFF-03, V2-HANDOFF-04, V2-HANDOFF-05

**Success Criteria:**

1. User can export a concept handoff package for a selected version.
2. Package includes concept image, optional 3D screenshots, safe-zone overlay image, warning report, prompt/provider trace summary, template metadata, reference asset manifest, and concept-only disclaimer.
3. Package exports as a ZIP with a stable manifest JSON and human-readable Markdown or HTML notes.
4. Export record is durable, linked to the selected version, and does not overwrite prior exports.
5. System blocks or warns if required rights/source metadata is incomplete.

**Plans:** 7 plans

- [x] 13-01-PLAN.md — HandoffPackage schema, manifest version, and export-type taxonomy.
- [x] 13-02-PLAN.md — Safe-zone/warning report renderer and concept-only disclaimer contract.
- [x] 13-03-PLAN.md — ZIP package builder with images, screenshots, manifest, and handoff notes.
- [x] 13-04-PLAN.md — Export ledger updates, immutable package artifacts, and lineage linkage.
- [x] 13-05-PLAN.md — Workbench export dialog, package preview, history, and download UX.
- [x] 13-06-PLAN.md — Rights/source guardrails and blocked-export failure states.
- [ ] 13-07-PLAN.md — Phase 13 smoke, docs, manifest tests, and Browser UAT.

**UI hint:** yes

### Phase 14: V2 MVP Hardening, Docs, Smoke, And UAT

**Goal:** Close V2 MVP with trustworthy validation, rollback clarity, user-facing labels, and operator evidence.

**Depends on:** Phase 13

**Requirements:** V2-REL-01, V2-REL-02, V2-REL-03, V2-REL-04, V2-REL-05

**Success Criteria:**

1. Full aggregate validation passes from a clean checkout.
2. Docker-backed smoke covers local deterministic provider and hosted-provider-disabled mode.
3. Hosted-provider smoke can be run manually with explicit credentials and quota guardrails.
4. Browser UAT covers desktop and mobile workbench paths for hosted generation, targeted edits, references, 3D preview, and enhanced export.
5. Documentation clearly explains V2 feature flags, provider configuration, quota behavior, reference usage, 3D preview limitations, and concept-only handoff boundaries.
6. Release notes clearly state what V2 MVP does and does not guarantee.

**Plans:** 6 plans

- [ ] 14-01-PLAN.md — Root aggregate validation, contract drift, and regression closure.
- [ ] 14-02-PLAN.md — Docker smoke for local-only, hosted-disabled, and failure/fallback paths.
- [ ] 14-03-PLAN.md — Manual hosted-provider smoke checklist and cost-safety runbook.
- [ ] 14-04-PLAN.md — Browser UAT for V2 workbench flows on desktop and mobile.
- [ ] 14-05-PLAN.md — User/operator/developer docs and feature-flag reference.
- [ ] 14-06-PLAN.md — V2 MVP verification report, release notes, and completion evidence.

**UI hint:** yes

## V2 MVP Data And Contract Additions

V2 extends, not replaces, V1 schemas.

**New or extended domain objects:**

- `HostedProviderConfig`
- `ProviderCapabilityMap`
- `HostedCallPreflightResult`
- `EditIntent`
- `EditRegion`
- `MaskAsset`
- `PromptDelta`
- `ReferenceRole`
- `ReferenceUsageSnapshot`
- `Preview3DSpec`
- `Preview3DScreenshotArtifact`
- `HandoffPackage`
- `HandoffManifest`
- `HandoffWarningReport`

**Compatibility Rules:**

1. Existing V1 `workspace`, `asset`, `job`, `artifact`, `version`, `feedback`, `export`, `model_run`, and `PreviewSpec` records remain readable.
2. V2 records must link back to V1 versions and artifacts instead of duplicating the core ledger.
3. New provider-specific fields must be stored in typed metadata or versioned JSON with schema version markers.
4. Frontend TypeScript contracts must continue to be generated from FastAPI/Pydantic OpenAPI schemas.
5. New features must be feature-flagged and safe to disable independently.

## V2 MVP UI Additions

The existing V1 workbench should gain these panels or controls:

1. Provider selector and hosted-call cost/quota visibility.
2. Targeted edit mode for selecting regions/layers and submitting local edits.
3. Reference asset role assignment and usage warnings.
4. 3D preview tab with clear non-production labels.
5. Enhanced export dialog with package preview and manifest summary.
6. Operations/debug drawer for provider, fallback, retry, quota, and failure evidence.

## V2 MVP Acceptance Flow

A single end-to-end V2 MVP UAT should prove:

1. Start from a clean V1-compatible workspace.
2. Upload at least one reference image and assign a reference role with rights metadata.
3. Create or reuse a structured brief.
4. Select a template and hosted provider.
5. Pass hosted preflight and generate a concept render.
6. Perform one targeted edit on a selected region.
7. Compare parent and child versions.
8. Open lightweight 3D preview and capture one screenshot.
9. Export enhanced concept handoff ZIP.
10. Confirm manifest includes provider trace, prompt trace, references, warnings, safe-zone overlay, screenshot, and concept-only disclaimer.
11. Confirm quota, cost, fallback, and failure events are visible to the operator.

## Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hosted provider cost spikes | High | Keep feature flags default-off, require preflight, quotas, rate limits, and manual hosted smoke. |
| Provider behavior changes | High | Store capability maps, version provider adapters, keep local deterministic provider. |
| Users mistake 3D preview for production-ready wrap | High | Persistent non-production labels, export disclaimers, and documentation. |
| Reference asset misuse | High | Rights/source metadata gates, role-based reference usage, and blocked-export states. |
| Masked editing quality varies by provider | Medium | Provider capability checks, deterministic recomposition fallback, visible failure messages. |
| 3D preview scope creep | Medium | Only one lightweight shell/template fixture for MVP; defer verified UV production mapping. |
| Contract drift | Medium | OpenAPI-generated TS contracts and aggregate drift checks in every phase. |

## Progress

**Execution Order:** 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 8. V1 Closure And V2 Readiness Gate | 5/5 | Complete | 2026-06-18 |
| 9. Hosted Provider Rollout MVP | 7/7 | Complete | 2026-06-18 |
| 10. Targeted Regeneration And Masked Editing MVP | 8/8 | Complete | 2026-06-18 |
| 11. Reference-Guided Generation MVP | 7/7 | Complete | 2026-06-18 |
| 12. Lightweight 3D Preview MVP | 8/8 | Complete | 2026-06-19 |
| 13. Enhanced Concept Handoff Package MVP | 6/7 | In Progress | - |
| 14. V2 MVP Hardening, Docs, Smoke, And UAT | 0/6 | Not started | - |

**Coverage:**

- v2.0 requirements: 34 total
- Mapped to phases: 34
- Unmapped: 0

---
*Roadmap created: 2026-06-18 after v2.0 milestone start*
