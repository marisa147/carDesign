# Roadmap: 痛车设计生成 Agent

## Milestones

- ✅ **v1.0 MVP** — Phases 1-7 shipped on 2026-06-18. Archive: `.planning/milestones/v1.0-ROADMAP.md`.
- ✅ **v2.0 V2 MVP** — Phases 8-14 shipped on 2026-06-19. Archive: `.planning/milestones/v2.0-ROADMAP.md`.
- ✅ **v3.0 Template Library And Production Readiness** — Phases 15-20 shipped on 2026-06-20. Archive: `.planning/milestones/v3.0-ROADMAP.md`.
- ✅ **v4.0 Real Generation Closure And Reliability** — Phases 21-26 implemented on 2026-06-22; archive-ready.
- ✅ **v5.0 GR86/BRZ Construction Package Customization** — Phases 27-33 implemented on 2026-06-23; archive-ready.

## Current Planning State

v5.0 is initialized from the user-confirmed requirement-completion discussion after the GPT/provider and preview-quality fixes. It focuses on replacing generic abstract car output with a first deep real-vehicle customization workflow: GR86/BRZ maintained template package, section-first design, smart Q&A, GPT-assisted design supplementation, template import validation, and SVG/PDF/PNG quasi-construction package export.

**Next up:** v5.0 milestone verification/audit and archive preparation.

## Active Phase Plan

| Phase | Name | Goal | Requirements | Success Criteria |
|-------|------|------|--------------|------------------|
| 27 | View Truthfulness And Current Preview Repair | Stop side/front/rear/top controls from implying fake unavailable views. | VIEW-01..02 | Complete: view controls reflect template capabilities; unavailable views show `模板未提供该视图`; generated previews no longer claim nonexistent multi-view support. |
| 28 | GR86/BRZ Template Package Schema | Create the first deep real-vehicle template contract and maintained GR86/BRZ package. | TPLG-01..04 | Complete: package has four distinct views, sections, safe/forbidden zones, real dimensions, scale, manifest, export config, and validator coverage. |
| 29 | Template Management And Authorization | Let users inspect/import validated template packages and see authorization status. | TMPL-01..04 | Complete: template management page lists package details, validates SVG/PNG/JSON imports, and displays structured authorization/version metadata. |
| 30 | Construction Brief And Smart Q&A | Turn chat into a requirement-completion workflow instead of one-shot classification. | BRIF-01..06 | Complete: assistant asks missing core fields, surfaces GPT supplementation, and writes a right-side construction-order brief with clear/save/discard/new controls. |
| 31 | Section-First Design Workspace | Make vehicle sections the main customization surface. | SECT-01..03 | Complete: section list drives scope; selected section maps to views and flat panels; targeted edits are constrained to selected sections. |
| 32 | GPT Sectioned Generation Pipeline | Convert completed briefs into section-level GPT design plans and regenerable outputs. | GPTD-01..04 | Complete: GPT/provider prompt plan creates overall direction, splits prompts by section, supports section regeneration metadata, and records section/template/provider trace. |
| 33 | SVG/PDF/PNG Construction Package Export | Export a quasi-construction handoff package from the sectioned template design. | PACK-01..03 | Complete: package contains layered SVG, PDF, PNG/source preview, manifest, source trace, template evidence, and clear warnings. |

## Phase Details

### Phase 27: View Truthfulness And Current Preview Repair

Goal: Make the existing workbench honest before building deeper template features.

Success criteria:
1. Side/front/rear/top buttons read available views from the selected template/version.
2. Selecting an unavailable view shows `模板未提供该视图` instead of reusing the side-view composition.
3. Preview metadata exposes available/missing views so UI and export warnings can agree.
4. Regression tests cover templates with side-only assets and templates with multiple views.

### Phase 28: GR86/BRZ Template Package Schema

Goal: Establish a quasi-construction template contract around one real vehicle.

Success criteria:
1. The template schema supports required view files, section ids, safe zones, forbidden zones, real-unit dimensions, scale, export config, and authorization metadata.
2. A maintained GR86/BRZ package exists with distinct side/front/rear/top assets and manifest versioning.
3. Validation rejects missing structural, construction, delivery, or authorization fields with actionable messages.
4. Tests prove real proportions and section geometry are loaded without relying on generic abstract silhouettes.

### Phase 29: Template Management And Authorization

Status: Complete.

Goal: Make template provenance visible and importable through product UI.

Success criteria:
1. A template management page lists installed template packages and validation state.
2. Users can upload/import SVG/PNG/JSON template packages for validation.
3. Authorization status shows source, authorization file reference, scope, expiration, commercial-use flag, reviewer, and version history.
4. Import errors identify missing assets, invalid JSON/SVG structure, unsupported dimensions, and missing authorization fields.

### Phase 30: Construction Brief And Smart Q&A

Status: Complete.

Goal: Make the assistant start a customization process with the user instead of only categorizing a prompt.

Success criteria:
1. The chat flow asks missing core fields one by one: vehicle template, character/theme, main color, wrap range, and text/logo.
2. The GPT parser may propose/supplement style, composition, palette, and section ideas when the user asks it to.
3. The right-side brief groups fields by 车型, 范围, 设计, 素材, 导出, and 风险.
4. Missing construction/auth/delivery details show warnings but do not block the first generation path.
5. Users can clear the chat, create a new conversation, save a draft, and discard unsaved changes.

### Phase 31: Section-First Design Workspace

Status: Complete.

Goal: Put vehicle sections at the center of customization and review.

Success criteria:
1. Users select wrap scope from practical sections including doors, rear quarter, front fender, hood, roof, trunk, front/rear bumper, and side skirt.
2. Selecting a section highlights its related side/front/rear/top position and flat/unfolded panel where the template provides it.
3. PreviewSpec overlays and local edits are clipped or validated against selected section geometry.
4. Section state persists through brief save, generation job submission, version history, and export metadata.

### Phase 32: GPT Sectioned Generation Pipeline

Status: Complete.

Goal: Use GPT for design direction and section decomposition while keeping durable state typed and traceable.

Success criteria:
1. GPT mode generates an overall design direction from the construction brief and template package context.
2. The system derives section-level prompts/constraints from the direction and selected wrap sections.
3. A user can regenerate one section while keeping other sections unchanged.
4. Model runs, artifacts, and versions record prompt, model, section ids, template version, and provider trace.

### Phase 33: SVG/PDF/PNG Construction Package Export

Status: Complete.

Goal: Produce a credible quasi-construction package without claiming final print-shop certification.

Success criteria:
1. Exported package includes layered SVG, PDF, PNG, manifest, template version, scale, safe-zone, forbidden-zone, and warning evidence.
2. SVG layer names are stable for base/body/window/wheel/handle/panel lines and artwork sections.
3. PDF and PNG outputs preserve section boundaries, bleed/safety margins, and readable concept-vs-construction warnings.
4. Tests validate package contents and at least one GR86/BRZ sectioned export fixture.

## Progress

| Milestone | Phases | Requirements | Status | Completed |
|-----------|--------|--------------|--------|-----------|
| v1.0 MVP | 1-7 | 42/42 | Complete | 2026-06-18 |
| v2.0 V2 MVP | 8-14 | 34/34 | Complete | 2026-06-19 |
| v3.0 Template Library And Production Readiness | 15-20 | 31/31 | Complete | 2026-06-20 |
| v4.0 Real Generation Closure And Reliability | 21-26 | 23/23 | Complete | 2026-06-22 |
| v5.0 GR86/BRZ Construction Package Customization | 27-33 | 26/26 | Complete | 2026-06-23 |

## Deferred Future Directions

- Print-shop-ready PSD/AI handoff with verified color profile, installer notes, and production sign-off.
- Verified production UV mapped 3D vehicle shells and broad licensed vehicle-template catalog coverage.
- Marketplace, template store, public gallery, payment, quoting, ordering, installer network, and collaboration workflows.
- Fully automated copyright/licensing verification for character, logo, and third-party reference assets.
- User-calibrated arbitrary vehicle photo templates after the maintained-package workflow is stable.
- Hosted provider production rollout claims after current model quality, pricing, moderation, account status, quota behavior, and commercial terms are re-verified.

---
*Last updated: 2026-06-23 after Phase 33 implementation*


