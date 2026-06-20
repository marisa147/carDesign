# Requirements: 痛车设计生成 Agent v3.0 Template Library And Production Readiness

**Defined:** 2026-06-19
**Source:** `C:/Users/25858/Downloads/MVP_FINAL.md`
**Core Value:** 用户能用自然语言快速得到一套可预览、可迭代、可导出的高质量痛车设计方案。

## v3.0 Requirements

v3.0 starts from the final MVP delivery note and focuses on the template/source/licensing foundation required before true production handoff, verified UV, broad template commercialization, or ordering workflows.

### Template Governance

- [x] **V3-TEMPLATE-01**: User or operator can inspect a canonical source policy table that distinguishes `internal_original`, `licensed_template`, `user_provided_with_rights`, `third_party_reference_only`, and `web_crawled_image`.
- [x] **V3-TEMPLATE-02**: Operator can register template records with source type, license status, license evidence, rights notes, allowed usage scope, distribution flag, and audit timestamp.
- [x] **V3-TEMPLATE-03**: System blocks disallowed web-crawled or third-party-reference-only sources from becoming reusable template assets, masks, thumbnails, or catalog entries.
- [x] **V3-TEMPLATE-04**: Existing `generic-side-coupe` PreviewSpec usage remains compatible through migration, aliasing, or a documented bridge without breaking v1/v2 jobs, exports, or 3D fallback.
- [x] **V3-TEMPLATE-05**: Operator can review an audit list of template readiness, source, license, missing files, and blocking issues.

### MVP Template Pack

- [x] **V3-PACK-01**: User can select from an internal-original MVP side-view template pack containing coupe, sedan, hatchback, SUV, and van generic templates.
- [x] **V3-PACK-02**: Each MVP template includes required asset slots: base image, body/window/wheel/handle masks, panel lines, safe-zones JSON, template metadata, and thumbnail.
- [x] **V3-PACK-03**: Developer can validate template package structure, image dimensions, mask bounds, safe-zone coordinates, and metadata schema with one command.
- [x] **V3-PACK-04**: System generates deterministic thumbnails or preview fixtures for template catalog display without relying on unauthorized vehicle imagery.
- [x] **V3-PACK-05**: Generation brief resolution preserves selected template id, label, view, source/license status, warnings, and safe zones.
- [x] **V3-PACK-06**: Existing tests cover all five MVP templates plus the legacy coupe alias.

### Template Catalog

- [x] **V3-CATALOG-01**: User can browse, filter, and select supported templates and side views from the Workbench before generation.
- [x] **V3-CATALOG-02**: API exposes template list/detail endpoints with thumbnail URLs, supported views, safe-zone summary, source/license status, and readiness flags.
- [x] **V3-CATALOG-03**: Workbench shows template source/license warnings, unavailable states, and missing-rights reasons before submission.
- [x] **V3-CATALOG-04**: Selected template is persisted through workspace parameters, generation jobs, prompt plans, versions, artifacts, model runs, and export metadata.
- [x] **V3-CATALOG-05**: User sees stable fallback or block messages when a selected template is unavailable, unsupported, or not licensed for the requested use.

### Template-Aware Generation And Preview

- [x] **V3-INTEGRATION-01**: User can generate a concept on any MVP template through the local deterministic provider path.
- [x] **V3-INTEGRATION-02**: Safe-zone overlays, risk warnings, text/logo layers, and PreviewSpec coordinates align with the selected template in 2D preview.
- [x] **V3-INTEGRATION-03**: Targeted edits use selected template safe zones and masks for region selection, mask preview, and recomposition metadata.
- [x] **V3-INTEGRATION-04**: Reference-guided generation records template context alongside reference roles and rights snapshots.
- [x] **V3-INTEGRATION-05**: Lightweight 3D preview links supported template shells when present and falls back with template-specific non-production labels when absent.
- [x] **V3-INTEGRATION-06**: Contracts and generated TypeScript types expose template catalog, selection, and readiness fields without breaking archived v1/v2 payloads.

### Production Readiness Preflight

- [x] **V3-PREFLIGHT-01**: User can request a concept-only production readiness preflight for a selected version.
- [x] **V3-PREFLIGHT-02**: Preflight report identifies missing production evidence such as verified scale, bleed, color profile, DPI, UV mapping, installer notes, and licensed real-vehicle template.
- [x] **V3-PREFLIGHT-03**: Enhanced concept handoff ZIP includes template source/license summary, template validation report, and explicit non-production status.
- [x] **V3-PREFLIGHT-04**: System keeps print-ready PSD/AI/PDF export blocked unless a future production handoff milestone supplies required evidence.

### V3 Release

- [x] **V3-REL-01**: Developer can run focused backend, worker, frontend, contract, and template-pack validation for V3 from a clean checkout.
- [x] **V3-REL-02**: Operator can run Docker/local smoke that exercises generation, template selection, export, and failure states without hosted credentials.
- [x] **V3-REL-03**: Browser UAT covers desktop and mobile flows for catalog selection, source/license warnings, generation, targeted edit, 3D fallback, handoff, and preflight.
- [x] **V3-REL-04**: Documentation and release notes explain V3 template governance, MVP template pack contents, concept-only boundaries, and next V3+ promotions.
- [x] **V3-REL-05**: V3 milestone audit proves all v3.0 requirements are mapped, tested, documented, and safe to archive.

## Future Requirements

### Production Handoff

- **V3-FUTURE-PROD-01**: User can export full print-ready PSD/AI/PDF handoff with verified scale, bleed, color profile, DPI, and installer notes.
- **V3-FUTURE-PROD-02**: Operator can validate vehicle-specific production templates against wrap-shop requirements and real installer feedback.

### True 3D And UV

- **V3-FUTURE-3D-01**: User can preview verified vehicle-specific UV mapping for supported real templates.
- **V3-FUTURE-3D-02**: System can maintain physically consistent multi-view designs across side, front, rear, hood, and roof views.

### Template Business Layer

- **V3-FUTURE-BIZ-01**: User can browse licensed real-vehicle templates in a marketplace or template store.
- **V3-FUTURE-BIZ-02**: User can quote, order, pay for, or collaborate on installer handoff workflows.

### Advanced Rights And Generation

- **V3-FUTURE-RIGHTS-01**: System can perform automated copyright or licensing verification beyond user/operator metadata gates.
- **V3-FUTURE-GEN-01**: System can use advanced multi-agent orchestration beyond the typed generation and worker pipeline.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Print-ready PSD/AI/PDF export | v3.0 only adds concept-only readiness preflight and keeps production export blocked until verified evidence exists. |
| Real licensed vehicle-specific template library | v3.0 creates an internal generic MVP pack and governance layer; real licensed vehicle coverage needs licensing budget and QA. |
| Verified UV or true 3D wrap simulation | v3.0 preserves lightweight 3D fallback labels and does not claim production geometry accuracy. |
| Marketplace, payments, quotes, orders, installer network, gallery, and collaboration | Commercial/community workflows depend on stable template governance and production handoff contracts first. |
| Fully automated copyright/licensing verification | v3.0 records source/license metadata and blocks prohibited sources, but does not provide legal-grade automation. |
| Hosted provider production rollout claims | Provider quality, price, moderation, account access, quota, and commercial terms must stay separately verified. |
| Guaranteed physically aligned multi-view generation | v3.0 focuses on side-view template pack reliability before multi-view physical alignment. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| V3-TEMPLATE-01 | Phase 15 | Complete |
| V3-TEMPLATE-02 | Phase 15 | Complete |
| V3-TEMPLATE-03 | Phase 15 | Complete |
| V3-TEMPLATE-04 | Phase 15 | Complete |
| V3-TEMPLATE-05 | Phase 15 | Complete |
| V3-PACK-01 | Phase 16 | Complete |
| V3-PACK-02 | Phase 16 | Complete |
| V3-PACK-03 | Phase 16 | Complete |
| V3-PACK-04 | Phase 16 | Complete |
| V3-PACK-05 | Phase 16 | Complete |
| V3-PACK-06 | Phase 16 | Complete |
| V3-CATALOG-01 | Phase 17 | Complete |
| V3-CATALOG-02 | Phase 17 | Complete |
| V3-CATALOG-03 | Phase 17 | Complete |
| V3-CATALOG-04 | Phase 17 | Complete |
| V3-CATALOG-05 | Phase 17 | Complete |
| V3-INTEGRATION-01 | Phase 18 | Complete |
| V3-INTEGRATION-02 | Phase 18 | Complete |
| V3-INTEGRATION-03 | Phase 18 | Complete |
| V3-INTEGRATION-04 | Phase 18 | Complete |
| V3-INTEGRATION-05 | Phase 18 | Complete |
| V3-INTEGRATION-06 | Phase 18 | Complete |
| V3-PREFLIGHT-01 | Phase 19 | Complete |
| V3-PREFLIGHT-02 | Phase 19 | Complete |
| V3-PREFLIGHT-03 | Phase 19 | Complete |
| V3-PREFLIGHT-04 | Phase 19 | Complete |
| V3-REL-01 | Phase 20 | Complete |
| V3-REL-02 | Phase 20 | Complete |
| V3-REL-03 | Phase 20 | Complete |
| V3-REL-04 | Phase 20 | Complete |
| V3-REL-05 | Phase 20 | Complete |

**Coverage:**

- v3.0 requirements: 31 total; 31 complete
- Mapped to phases: 31
- Unmapped: 0

---
*Requirements defined: 2026-06-19*
*Last updated: 2026-06-20 after Phase 20 completion*
