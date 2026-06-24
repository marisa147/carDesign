# Requirements: 痛车设计生成 Agent v5

**Defined:** 2026-06-23
**Core Value:** 用户能用自然语言快速得到一套可预览、可迭代、可导出的高质量痛车设计方案。

## v5 Requirements

### Template Truthfulness

- [x] **VIEW-01**: User can switch side/front/rear/top preview controls without seeing fake views; unavailable views show a clear `模板未提供该视图` state.
- [x] **VIEW-02**: User can see which views a selected template package actually provides before generating or reviewing a design.

### GR86/BRZ Vehicle Template

- [x] **TPLG-01**: User can select a maintained Toyota GR86/Subaru BRZ template package as the first deep real-vehicle template.
- [x] **TPLG-02**: The GR86/BRZ package contains distinct side, front, rear, and top view assets with real proportions, version metadata, and package manifest.
- [x] **TPLG-03**: The GR86/BRZ package defines body sections, safe zones, forbidden zones, scale, and real-unit dimensions needed for quasi-construction use.
- [x] **TPLG-04**: Template validation rejects packages missing required views, sections, dimensions, export config, or authorization metadata.

### Template Management And Authorization

- [x] **TMPL-01**: User can open a template management page and inspect installed template package details.
- [x] **TMPL-02**: User can import a template package containing SVG/PNG/JSON assets and see validation results.
- [x] **TMPL-03**: User can review structured authorization status including source, authorization file reference, scope, expiration, commercial-use flag, reviewer, and version history.
- [x] **TMPL-04**: User can distinguish maintained internal templates, user-provided templates, and third-party authorized templates without relying on hidden metadata.

### Construction Brief And Smart Q&A

- [x] **BRIF-01**: User can start a customization conversation where the assistant asks missing core fields one by one.
- [x] **BRIF-02**: User can allow GPT to supplement reasonable design details instead of only classifying the input.
- [x] **BRIF-03**: User can review and edit a right-side construction-order brief grouped by 车型, 范围, 设计, 素材, 导出, and 风险.
- [x] **BRIF-04**: The system treats vehicle template, character/theme, main color, wrap range, and text/logo as required core fields for generation readiness.
- [x] **BRIF-05**: Construction, authorization, and delivery-risk fields show warnings when incomplete but do not block the first v5 generation flow.
- [x] **BRIF-06**: User can create a new conversation, clear the current conversation, save a draft, and discard a draft without losing saved workspace state.

### Section-First Design Workspace

- [x] **SECT-01**: User can choose wrap scope by vehicle sections such as doors, rear quarter, front fender, hood, roof, trunk, bumpers, and side skirt.
- [x] **SECT-02**: User can select a section and see its related side/front/rear/top position plus flat/unfolded construction panel where available.
- [x] **SECT-03**: Preview overlays and local edits are constrained to selected template sections instead of floating over a generic car silhouette.

### GPT Sectioned Generation

- [x] **GPTD-01**: GPT mode can produce an overall design direction from the completed brief and template context.
- [x] **GPTD-02**: The system can split the design direction into section-level prompts and constraints tied to GR86/BRZ template sections.
- [x] **GPTD-03**: User can regenerate an individual section while preserving the remaining section plan and template trace.
- [x] **GPTD-04**: GPT-generated artwork outputs are recorded with prompt, model, section ids, template version, and provider trace.

### Construction Package Export

- [x] **PACK-01**: User can export a quasi-construction package containing layered SVG, PDF, PNG, manifest, template version, scale, safe-zone, forbidden-zone, and warning evidence.
- [x] **PACK-02**: SVG output uses stable layer naming for base/body/window/wheel/handle/panel lines and artwork sections.
- [x] **PACK-03**: PDF and PNG exports preserve visible section boundaries, bleed/safety margins, and concept-vs-construction warnings.

## Future Requirements

### Production And Commerce

- **PROD-01**: User can export print-shop-ready PSD/AI files with verified color profile, installer notes, and production sign-off.
- **PROD-02**: User can use verified UV mapped 3D vehicle shells for production wraps.
- **PROD-03**: User can order, quote, pay, or route a design to an installer network.

### Marketplace And Licensing

- **MRKT-01**: User can browse, purchase, and update a broad licensed vehicle-template marketplace.
- **MRKT-02**: System can automatically verify commercial character, anime, brand, and logo licensing evidence.

### Broad Vehicle Coverage

- **VEHC-01**: System ships many real-vehicle templates beyond GR86/BRZ with the same depth and validation.
- **VEHC-02**: User can calibrate arbitrary uploaded vehicle photos into reusable production templates.

## Out of Scope

| Feature | Reason |
|---------|--------|
| PSD/AI export in v5 | v5 first standardizes SVG/PDF/PNG package structure; native design-tool files need separate QA and library choices. |
| Print-shop production guarantee | v5 targets quasi-construction evidence, not installer-certified output or legal production approval. |
| Broad real-car catalog | The first milestone goes deep on GR86/BRZ so sectioning, validation, and exports become trustworthy before scaling. |
| Marketplace/order/payment/installer flow | Commercial workflow depends on reliable templates, authorization metadata, and export package quality first. |
| Automated copyright verification for character/logo uploads | v5 reminds users about responsibility but does not require full authorization documents for every reference asset. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| VIEW-01 | Phase 27 | Complete |
| VIEW-02 | Phase 27 | Complete |
| TPLG-01 | Phase 28 | Complete |
| TPLG-02 | Phase 28 | Complete |
| TPLG-03 | Phase 28 | Complete |
| TPLG-04 | Phase 28 | Complete |
| TMPL-01 | Phase 29 | Complete |
| TMPL-02 | Phase 29 | Complete |
| TMPL-03 | Phase 29 | Complete |
| TMPL-04 | Phase 29 | Complete |
| BRIF-01 | Phase 30 | Complete |
| BRIF-02 | Phase 30 | Complete |
| BRIF-03 | Phase 30 | Complete |
| BRIF-04 | Phase 30 | Complete |
| BRIF-05 | Phase 30 | Complete |
| BRIF-06 | Phase 30 | Complete |
| SECT-01 | Phase 31 | Complete |
| SECT-02 | Phase 31 | Complete |
| SECT-03 | Phase 31 | Complete |
| GPTD-01 | Phase 32 | Complete |
| GPTD-02 | Phase 32 | Complete |
| GPTD-03 | Phase 32 | Complete |
| GPTD-04 | Phase 32 | Complete |
| PACK-01 | Phase 33 | Complete |
| PACK-02 | Phase 33 | Complete |
| PACK-03 | Phase 33 | Complete |

**Coverage:**
- v5 requirements: 26 total
- Complete: 26
- Mapped to phases: 26
- Unmapped: 0

---
*Requirements defined: 2026-06-23*
*Last updated: 2026-06-23 after Phase 33 implementation*


