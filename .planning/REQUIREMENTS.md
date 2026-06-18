# Requirements: 痛车设计生成 Agent v2.0 V2 MVP

**Defined:** 2026-06-18
**Source:** `C:/Users/25858/Downloads/V2_MVP_ROADMAP (1).md`
**Core Value:** 用户能用自然语言快速得到一套可预览、可迭代、可导出的高质量痛车设计方案。

## v2.0 Requirements

### V2 Readiness

- [x] **V2-READY-01**: Operator can confirm v1.0 is closed, archived, and verified before any V2-only capability is enabled.
- [x] **V2-READY-02**: Developer can run contract drift checks, backend tests, worker tests, frontend tests, Docker smoke, and Browser UAT from a clean checkout.
- [ ] **V2-READY-03**: Operator can keep V2 feature flags disabled by default and verify V1 local-only behavior remains unchanged.
- [ ] **V2-READY-04**: Operator can run the application without hosted provider credentials while retaining the local deterministic provider path.

### Hosted Provider

- [ ] **V2-PROVIDER-01**: Operator can configure hosted image provider credentials, model, capability map, timeout, retry, fallback, and quota policy without code changes.
- [ ] **V2-PROVIDER-02**: User can submit a hosted generation job only when hosted generation is enabled and preflight allows the request.
- [ ] **V2-PROVIDER-03**: System records provider, model, request parameters, prompt plan, input assets, estimated cost, actual cost when available, fallback path, and raw error category.
- [ ] **V2-PROVIDER-04**: User and operator can inspect hosted provider failures without exposing secrets.
- [ ] **V2-PROVIDER-05**: User and developer can keep the local deterministic provider available as a test and fallback path.

### Targeted Editing

- [ ] **V2-EDIT-01**: User can select a concept region or layer and request a targeted edit such as character size, style accent, text placement, decal density, or palette change.
- [ ] **V2-EDIT-02**: System stores edit intent, selected region, mask data, parent version, prompt delta, provider parameters, and generated child version.
- [ ] **V2-EDIT-03**: Worker can use deterministic recomposition when only layer position, scale, visibility, opacity, text, or logo changes are requested.
- [ ] **V2-EDIT-04**: Worker can route mask-aware provider calls when visual content must be regenerated.
- [ ] **V2-EDIT-05**: User can compare parent and child versions and see whether a change was recomposition-only or provider-generated.

### Reference Guidance

- [ ] **V2-REF-01**: User can mark uploaded assets as character reference, style reference, vehicle reference, logo reference, palette reference, or inspiration only.
- [ ] **V2-REF-02**: System enforces rights and source metadata before a reference asset can be used for generation.
- [ ] **V2-REF-03**: Provider request builder includes only reference types supported by the selected provider and model.
- [ ] **V2-REF-04**: User sees a clear warning when a requested reference role is unsupported instead of silent failure.
- [ ] **V2-REF-05**: Generated artifacts store exact reference assets, reference roles, provider parameters, and a rights metadata snapshot.

### Lightweight 3D Preview

- [ ] **V2-3D-01**: Developer can register at least one preview vehicle shell or pseudo-3D template linked to existing vehicle templates and PreviewSpec.
- [ ] **V2-3D-02**: User can open a 3D preview panel for a selected 2D design version.
- [ ] **V2-3D-03**: User can rotate, zoom, reset camera, capture a screenshot, and see persistent non-production labeling in the preview.
- [ ] **V2-3D-04**: System stores 3D preview specs, camera presets, screenshot artifacts, and warning metadata.
- [ ] **V2-3D-05**: User sees a clear 2D fallback when no compatible 3D shell exists, without breaking generation or export.

### Concept Handoff Package

- [ ] **V2-HANDOFF-01**: User can export a concept handoff package for a selected version.
- [ ] **V2-HANDOFF-02**: Package includes concept image, optional 3D screenshots, safe-zone overlay image, warning report, prompt/provider trace summary, template metadata, reference asset manifest, and concept-only disclaimer.
- [ ] **V2-HANDOFF-03**: Package exports as a ZIP with stable manifest JSON and human-readable Markdown or HTML notes.
- [ ] **V2-HANDOFF-04**: Export record is durable, linked to the selected version, immutable, and does not overwrite prior exports.
- [ ] **V2-HANDOFF-05**: System blocks or warns when required rights or source metadata is incomplete.

### V2 Release

- [ ] **V2-REL-01**: Developer can run full aggregate validation from a clean checkout.
- [ ] **V2-REL-02**: Operator can run Docker-backed smoke for local deterministic provider, hosted-provider-disabled mode, and failure/fallback paths.
- [ ] **V2-REL-03**: Operator can run hosted-provider smoke manually with explicit credentials and quota guardrails.
- [ ] **V2-REL-04**: Browser UAT covers desktop and mobile workbench paths for hosted generation, targeted edits, references, 3D preview, and enhanced export.
- [ ] **V2-REL-05**: Documentation and release notes clearly explain V2 feature flags, provider configuration, quota behavior, reference usage, 3D preview limitations, and concept-only handoff boundaries.

## Future Requirements

### Production Handoff

- **V2-FUTURE-PROD-01**: User can export full print-ready PSD/AI/PDF handoff with verified scale, bleed, color profile, DPI, and installer notes.
- **V2-FUTURE-PROD-02**: Operator can validate vehicle-specific production templates against wrap-shop requirements.

### Marketplace And Collaboration

- **V2-FUTURE-BIZ-01**: User can share, collaborate on, order, quote, or pay for designs through marketplace or installer workflows.
- **V2-FUTURE-BIZ-02**: User can publish to or browse a moderated public gallery/template store.

### Advanced Generation

- **V2-FUTURE-GEN-01**: User can generate guaranteed multi-view designs with consistent physical alignment across side, front, rear, and hood views.
- **V2-FUTURE-GEN-02**: System can use advanced agentic orchestration beyond the typed generation and worker pipeline.
- **V2-FUTURE-RIGHTS-01**: System can perform fully automated copyright or licensing verification.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full print-ready PSD/AI/PDF handoff | V2 MVP only exports review-ready concept packages; production validation remains a later milestone. |
| Verified vehicle-specific UV mapping for every supported vehicle | V2 MVP only proves a lightweight preview path against limited fixtures. |
| Marketplace, payments, quotes, orders, installer network, gallery, and collaboration | These are commercial/community workflows outside the design-assist MVP. |
| Fully automated copyright/licensing verification | V2 MVP uses rights/source metadata gates and snapshots, not legal-grade verification. |
| Guaranteed physically aligned multi-view generation | V2 MVP focuses on references, targeted edits, and preview, not full wrap production consistency. |
| Advanced multi-agent orchestration | The typed generation and worker pipeline must remain stable before orchestration expands. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| V2-READY-01 | Phase 8 | Complete |
| V2-READY-02 | Phase 8 | Complete |
| V2-READY-03 | Phase 8 | Pending |
| V2-READY-04 | Phase 8 | Pending |
| V2-PROVIDER-01 | Phase 9 | Pending |
| V2-PROVIDER-02 | Phase 9 | Pending |
| V2-PROVIDER-03 | Phase 9 | Pending |
| V2-PROVIDER-04 | Phase 9 | Pending |
| V2-PROVIDER-05 | Phase 9 | Pending |
| V2-EDIT-01 | Phase 10 | Pending |
| V2-EDIT-02 | Phase 10 | Pending |
| V2-EDIT-03 | Phase 10 | Pending |
| V2-EDIT-04 | Phase 10 | Pending |
| V2-EDIT-05 | Phase 10 | Pending |
| V2-REF-01 | Phase 11 | Pending |
| V2-REF-02 | Phase 11 | Pending |
| V2-REF-03 | Phase 11 | Pending |
| V2-REF-04 | Phase 11 | Pending |
| V2-REF-05 | Phase 11 | Pending |
| V2-3D-01 | Phase 12 | Pending |
| V2-3D-02 | Phase 12 | Pending |
| V2-3D-03 | Phase 12 | Pending |
| V2-3D-04 | Phase 12 | Pending |
| V2-3D-05 | Phase 12 | Pending |
| V2-HANDOFF-01 | Phase 13 | Pending |
| V2-HANDOFF-02 | Phase 13 | Pending |
| V2-HANDOFF-03 | Phase 13 | Pending |
| V2-HANDOFF-04 | Phase 13 | Pending |
| V2-HANDOFF-05 | Phase 13 | Pending |
| V2-REL-01 | Phase 14 | Pending |
| V2-REL-02 | Phase 14 | Pending |
| V2-REL-03 | Phase 14 | Pending |
| V2-REL-04 | Phase 14 | Pending |
| V2-REL-05 | Phase 14 | Pending |

**Coverage:**

- v2.0 requirements: 34 total
- Mapped to phases: 34
- Unmapped: 0

---
*Requirements defined: 2026-06-18*
*Last updated: 2026-06-18 after v2.0 milestone start*
