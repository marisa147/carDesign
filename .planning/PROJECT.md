# 痛车设计生成 Agent

## What This Is

痛车设计生成 Agent 是一个面向痛车设计需求的 AI Web 工作台。v3.0 已经交付一个可本地运行、可验证的概念设计与审阅工作流：用户可以通过 GPT 风格对话描述车型、角色、风格、颜色、文案和参考素材，系统将需求解析为结构化参数，经异步 worker 生成 2D 概念图，并在 Web 工作台中展示、局部编辑、参考引导、轻量 3D 预览、反馈、导出增强概念交付包、运行概念级生产 readiness preflight、选择可信模板并查看运营状态。

v4.0 已经补齐真实生成闭环和可靠性层：明确生成入口、真实 artifact 图片展示、统一对象存储、队列/Worker 短事务可靠性、3D 截图真实性、字段清空、模板 mask 合成、Agent 解析边界和上线加固。v5.0 聚焦用户在 GPT/预览调试中暴露出的产品质量问题：从抽象 generic car preview 进入第一个深度真实车型工作流，以 GR86/BRZ 准施工级模板、智能需求追问、分区设计、GPT 分区生成和 SVG/PDF/PNG 施工包为核心。

## Core Value

用户能用自然语言快速得到一套可预览、可迭代、可导出的高质量痛车设计方案。

## Current Milestone: v5.0 GR86/BRZ Construction Package Customization

**Source:** User-confirmed requirement-completion conversation on 2026-06-23 after GPT provider, chat, and preview-quality debugging.

**Goal:** Move from generic concept-car previews toward a first quasi-construction customization workflow around a maintained Toyota GR86/Subaru BRZ template package, smart requirement Q&A, section-first design, GPT-assisted section generation, and SVG/PDF/PNG handoff packages.

**Target features:**

- Truthful side/front/rear/top view behavior that never shows fake unavailable views.
- Maintained GR86/BRZ real-vehicle template package with four views, sections, safe/forbidden zones, scale, dimensions, export config, and authorization metadata.
- Template management page for package import, validation, authorization status, and version history. ✓
- Smart chat-to-construction-brief flow with new/clear/save/discard conversation controls and GPT design supplementation. ✓
- Section-first workspace for wrap scope, view mapping, flat panels, overlays, and local edits. ✓
- GPT sectioned generation pipeline with per-section regeneration and durable template/provider trace. ✓
- SVG/PDF/PNG quasi-construction package export with layered output, manifest, scale, safety, bleed, and warning evidence. ✓

## Completed Milestone: v3.0 Template Library And Production Readiness

**Source:** `C:/Users/25858/Downloads/MVP_FINAL.md`

**Goal:** Make templates trustworthy and selectable before the product moves toward true production handoff, verified UV, real licensed vehicle templates, or commercial ordering workflows.

**Delivered features:**

- Template source governance, license metadata, readiness audit, and prohibited-source blocking.
- Internal-original MVP side-view template pack: coupe, sedan, hatchback, SUV, and van.
- Template catalog API and Workbench selection with visible source/license/readiness warnings.
- Template-aware generation, PreviewSpec, targeted edit, reference trace, lightweight 3D fallback, and export metadata.
- Concept-only production readiness preflight that explains why a design is not print-ready yet.
- V3 validation, docs, Docker/local smoke, Browser UAT, and milestone audit.

## Current State After v3.0

**Shipped:** v1.0 MVP on 2026-06-18, v2.0 V2 MVP on 2026-06-19, and v3.0 Template Library And Production Readiness on 2026-06-20.

**Current milestone:** v5.0 GR86/BRZ Construction Package Customization is implementation-complete through Phase 33 and ready for milestone verification/archive.

## Current State

**Built and verified:**

- Next.js/React/TypeScript workbench with chat, parameter editing, asset upload, progress/events, 2D preview, version history, feedback, export, itasha controls, operations status, targeted edit UX, reference diagnostics, 3D preview tab, and enhanced ZIP handoff UX.
- FastAPI/Pydantic API with generated OpenAPI/TypeScript contracts.
- Celery worker pipeline with local deterministic generation, provider adapter boundary, BFL hosted adapter guardrails, deterministic recomposition, retries/fallback, cancellation, quota/rate/cost preflight, and structured failure metadata.
- PostgreSQL/object-storage-oriented data model for workspaces, messages, briefs, jobs, events, artifacts, versions, model runs, feedback, exports, and cost records.
- Local Docker smoke path for PostgreSQL, Redis, MinIO, API, worker, web, and worker queue generation.
- V2 evidence for hosted-provider runbooks, targeted edit lineage, reference rights/source snapshots, lightweight 3D screenshots, enhanced handoff packages, release docs, and Browser UAT.
- V3 template governance, internal-original MVP template pack, template catalog API, thumbnail serving, Workbench template selection with source/license/readiness visibility, template-aware generation/preview/editing traceability, concept-only production readiness preflight with enhanced handoff template evidence, V3 release validation, Docker/local smoke, Browser UAT, docs, release notes, and milestone audit.
- V5 template management with installed package inspection, zip package validation, structured authorization display, source class visibility, and OpenAPI/contracts coverage.
- V5 smart requirement completion with missing-field Q&A, GPT supplementation cue, clear/new conversation controls, save/archive controls, and construction-order brief grouping.
- V5 section-first workspace with template detail loading, GR86/BRZ construction sections, view mapping, flat panel dimensions, and targeted-edit section coupling.
- V5 sectioned generation planning with overall design direction, per-section prompts, section regeneration metadata, and durable worker trace.
- V5 construction package export with immutable ZIP artifact, layered SVG, PDF, source PNG, manifest source trace, warnings, and Web `施工包` controls.

**Codebase scale at v3.0 close:** about 35,525 source-plus-test-and-doc lines across `apps/`, `packages/`, `services/`, `scripts/`, `infra/`, `docs/`, and `README.md`, excluding generated contracts and dependency folders.

## Requirements

### Validated

- ✓ User can describe a 痛车 design through chat, including vehicle/template, character/theme, style, palette, text, coverage, and references — v1.0 (FOUND, GEN, UI)
- ✓ System parses intent into structured parameters that can be reviewed, edited, reused, and traced — v1.0 (GEN, UI)
- ✓ System generates at least one stored 2D concept render through an asynchronous worker — v1.0 (GEN)
- ✓ User can view generated concepts, history, progress, job events, and base parameters in the Web UI — v1.0 (DATA, UI)
- ✓ User can regenerate or request targeted style, palette, text, composition, and coverage changes while preserving prior versions — v1.0 (ITER)
- ✓ User can record feedback and export concept preview files with metadata manifests — v1.0 (ITER)
- ✓ System records inputs, outputs, parameters, versions, provider/model metadata, costs, feedback, exports, and job state for traceability — v1.0 (DATA, GEN, OPS)
- ✓ Itasha-aware template controls, safe-zone overlays, deterministic text/logo overlays, quality warnings, and PreviewSpec persistence exist for the concept workflow — v1.0 (QUAL)
- ✓ Operator can inspect provider/worker/queue health, classified failures, cancellation, quota/rate guards, retry/fallback settings, and hosted-provider caveats — v1.0 (OPS)
- ✓ V2 readiness gate protects the shipped v1.0 baseline before new capabilities are enabled — v2.0 (READY)
- ✓ Hosted provider generation can be tested safely through config-driven adapters, preflight guards, durable trace records, and visible failure/cost/quota state — v2.0 (PROVIDER)
- ✓ Targeted edits can update selected regions or layers while preserving immutable artifacts and parent-child version lineage — v2.0 (EDIT)
- ✓ Reference-guided generation can use uploaded assets with explicit roles, rights/source snapshots, and provider capability warnings — v2.0 (REF)
- ✓ Lightweight 3D preview can consume existing PreviewSpec/template assets and remain labeled as non-production — v2.0 (3D)
- ✓ Enhanced concept handoff export can package concept assets, overlays, traces, warnings, notes, and disclaimers without claiming print readiness — v2.0 (HANDOFF)
- ✓ V2 MVP can be validated through aggregate tests, Docker smoke, hosted-provider manual smoke, Browser UAT, docs, and release notes — v2.0 (REL)
- ✓ Template source governance, license metadata, readiness audit, prohibited-source blocking, and legacy template compatibility exist in core contracts — v3.0 Phase 15 (V3-TEMPLATE)
- ✓ Internal-original generic side-view template pack exists for coupe, sedan, hatchback, SUV, and van with required assets, deterministic thumbnails, validation command, and selected-template brief resolution — v3.0 Phase 16 (V3-PACK)
- ✓ Template catalog API and Workbench selection expose filterable templates, thumbnails, source/license/readiness states, selected-template brief persistence, and job/export metadata trace — v3.0 Phase 17 (V3-CATALOG)
- ✓ Selected templates flow through local deterministic generation, PreviewSpec overlays, targeted edit regions, reference/provider trace, durable records, Workbench preview, and 3D compatibility/fallback — v3.0 Phase 18 (V3-INTEGRATION)
- ✓ Concept-only production readiness preflight identifies missing production evidence, persists report artifacts, enriches handoff ZIP evidence, and keeps print-ready export blocked — v3.0 Phase 19 (V3-PREFLIGHT)
- ✓ V3 template and preflight surfaces can be validated through aggregate tests, template-pack validation, Docker/local smoke, worker dry-run smoke, desktop/mobile Browser UAT, docs, release notes, and milestone audit — v3.0 Phase 20 (V3-REL)

### Active

- ✓ User can switch side/front/rear/top controls without seeing fake unavailable views — v5.0 Phase 27 (VIEW)
- ✓ User can select and validate a maintained Toyota GR86/Subaru BRZ quasi-construction template package — v5.0 Phase 28 (TPLG)
- ✓ User can manage, import, validate, and inspect authorization metadata for template packages — v5.0 Phase 29 (TMPL)
- ✓ User can complete requirements through smart Q&A, GPT supplementation, and a right-side construction brief with draft controls — v5.0 Phase 30 (BRIF)
- ✓ User can design by practical vehicle sections and see section-to-view/flat-panel mapping — v5.0 Phase 31 (SECT)
- ✓ GPT mode can create and regenerate section-level design outputs with durable template/provider trace — v5.0 Phase 32 (GPTD)
- ✓ User can export a layered SVG/PDF/PNG quasi-construction package with scale, safety, bleed, manifest, and warnings — v5.0 Phase 33 (PACK)

### Out of Scope
- 完整报价、下单和支付系统 -- v1.0 已验证设计生成闭环，商业交易能力继续后置。
- 真实车型全量模板库和模板商城 -- v3.0 只创建内部原创 generic side-view MVP 模板包；真实授权车型覆盖和商业分发需要后续授权与 QA 预算。
- 生产级 LoRA 训练平台 -- v1.0 使用本地 deterministic provider 与 hosted adapter 边界；训练流程仍后置。
- 移动原生 App -- v1.0 Web 优先，移动端采用响应式工作台验证。
- 完整 3D 模型自动生成 -- v1.0 保存 PreviewSpec 与 future gates；真实 UV/材质/3D 导出仍是后续里程碑。
- Production-ready wrap export -- v1.0 导出明确标注 concept preview，印刷级输出继续后置。
- Hosted provider production rollout -- 需要重新验证当前模型质量、价格、审核、账号权限、限额和商业授权。

## Context

Seed materials:

- `init.MD` 描述了目标、Agent 模块、系统流程、技术栈、前端布局、风险和原型开发计划。
- `UI.png` 提供了产品蓝图：Next.js + React + TypeScript 前端、Tailwind CSS + shadcn/ui、Zustand + React Query、FastAPI 后端、Celery + Redis 异步任务、PostgreSQL + MinIO 存储、Three.js / React Three Fiber 预览，以及对话区、方案区、2D/3D 区、参数调整区、素材库、用户中心和导出分享能力。

Shipped v1.0 experience:

- 左侧 GPT 风格对话区承载需求输入、系统反馈和修改指令。
- 右侧工作台展示结构化参数、素材与权利确认、生成进度、2D 预览、历史版本、反馈、导出和运营状态。
- 顶部/局部状态能力显示 provider、worker、queue、hosted guard、失败分类、取消状态和 future gates。
- 导出能力保持 concept preview 定位，不伪装成印刷级交付。

## Future Candidate Promotions After v3.0

- Full print-ready PSD/AI/PDF-style handoff with verified scale, bleed, color profile, DPI, and installer notes.
- Verified vehicle-specific UV mapping and broad template library coverage.
- Marketplace, template store, public gallery, payment, quoting, ordering, installer network, and collaboration workflows.
- Fully automated copyright/licensing verification.
- Fully consistent multi-view generation across side/front/rear/hood with guaranteed physical alignment.
- Advanced multi-agent orchestration beyond the typed generation and worker pipeline.

## Constraints

- **V5 scope discipline**: v5.0 goes deep on one GR86/BRZ quasi-construction template and SVG/PDF/PNG handoff; PSD/AI, installer-certified print readiness, broad marketplace, payments, and automated copyright verification remain out of scope.
- **Frontend stack**: Continue with Next.js, React, TypeScript, Tailwind CSS, shadcn/ui patterns, TanStack Query, Zustand, and lucide-react unless a future plan justifies a change.
- **Backend stack**: Continue with Python, FastAPI, Pydantic, SQLAlchemy/Alembic, Celery, Redis, PostgreSQL, and object storage boundaries.
- **Provider boundary**: Workers call provider adapters. Hosted provider names, model names, pricing, and safety behavior must remain config-driven and re-verified before production use.
- **Asynchronous work**: Expensive generation/export/provider work must stay asynchronous and durable; PostgreSQL job rows and events remain the source of truth.
- **Traceability**: Artifacts are immutable. New generation, edit, thumbnail, preview, and export outputs create new records rather than overwriting prior versions.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| v1 选择端到端 MVP | 先验证用户从自然语言到可导出设计方案的核心闭环，降低首个里程碑风险 | ✓ Good — v1.0 shipped the concept loop |
| Web 优先 | UI.png 已定义完整 Web 工作台，且生成任务适合桌面/浏览器操作 | ✓ Good — Browser UAT covered desktop and mobile widths |
| 前端采用 Next.js + React + TypeScript | seed 方案已明确，适合复杂交互和可维护 UI | ✓ Good — workbench, tests, lint, typecheck passed |
| 后端采用 Python + FastAPI | 适合 Agent 编排、模型调用、图像处理和异步任务 API | ✓ Good — typed API/contracts and smoke tests passed |
| 生成任务异步化 | 图像生成/后处理耗时且可能失败，需要队列、状态和重试 | ✓ Good — Celery worker queue smoke passed |
| 先支持有限车型/模板 | 贴图控制和预览质量依赖模板，v1 控制范围更容易交付 | ✓ Good — safe-zone/PreviewSpec path shipped without broad template debt |
| PostgreSQL/object storage as canonical state | Job/result state must survive refresh, retry, and worker restarts | ✓ Good — durable ledger and smoke checks passed |
| Keep Redis as queue/cache/progress, not canonical state | Redis task state alone is not enough for traceability | ✓ Good — API status reads durable job/event rows |
| Concept preview before production handoff | Print-ready wrap delivery has real template, scale, bleed, color, and installer risks | ✓ Good — exports are clearly labeled concept preview |
| Hosted provider rollout remains opt-in | Provider model availability, costs, moderation, and rights constraints change quickly | ✓ Good — v2.0 shipped guarded hosted path and manual-only smoke posture |
| V2 MVP follows the external roadmap file | User supplied `C:/Users/25858/Downloads/V2_MVP_ROADMAP (1).md` as the milestone source of truth | ✓ Good — v2.0 requirements and roadmap completed from that source |
| V2 features stay concept-only until production validation exists | Targeted edits, references, 3D preview, and handoff ZIPs can be mistaken for production wrap proof | ✓ Good — Phase 14 release notes and docs preserve not-print-ready boundaries |
| V3 follows the final MVP delivery note | User supplied `C:/Users/25858/Downloads/MVP_FINAL.md` as the source for the next milestone after v2.0 archive | ✓ Good — v3.0 shipped template governance, MVP template pack, catalog selection, preflight, and release evidence |
| Template governance before production handoff | Production handoff, true 3D, licensed templates, marketplace, and ordering all depend on trustworthy template provenance | ✓ Good — Phase 15 established source/license registry, readiness audit, and compatibility bridge |
| Internal generic templates before catalog UI | The Workbench selector needs trustworthy, local, reusable template records and thumbnails before API/UI exposure | ✓ Good — Phase 16 added five internal-original templates and a package validator |
| Catalog selection through brief contract | Template choice should survive refresh and job creation instead of living only in frontend state | ✓ Good — Phase 17 persists selected template id/view through brief create/update, job metadata, and export template trace |
| PreviewSpec remains the template-aware review contract | Generation, 2D overlays, targeted edits, reference traces, and 3D fallback need one durable selected-version source of truth | ✓ Good — Phase 18 carries selected-template context through local provider, worker records, Workbench preview, and canonical/legacy 3D compatibility |
| Preflight explains missing production evidence | Concept handoff should tell users what is absent before production instead of pretending generic concepts are print-ready | ✓ Good — Phase 19 adds durable concept-only preflight and template validation evidence while keeping PSD/AI/PDF exports blocked |
| Release evidence stays provider-off by default | V3 release hardening should prove local template/preflight behavior without accidental cost or hosted-provider claims | ✓ Good — Phase 20 passed aggregate validation, Docker/local smoke, Browser UAT, docs, and audit without hosted calls |
| v4 prioritizes real product closure over new feature breadth | Code review found gaps in the existing loop: hidden generation entry, disconnected storage, object-key-only preview, long transactions, queue race, and fake 3D screenshots | ✓ Good — v4.0 closed the real generation loop, storage, worker reliability, preview correctness, parser/compositor boundary, and hardening work |
| v5 starts with one deep GR86/BRZ template | User feedback showed generic side-view previews and fake view tabs are not credible enough for customization; one maintained real-vehicle package is safer than many shallow templates | ✓ Good — v5.0 implemented GR86/BRZ sections, smart Q&A, GPT section planning, and quasi-construction package export |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition**:

1. Requirements invalidated? Move to Out of Scope with reason.
2. Requirements validated? Move to Validated with phase reference.
3. New requirements emerged? Add to Active.
4. Decisions to log? Add to Key Decisions.
5. "What This Is" still accurate? Update if drifted.

**After each milestone**:

1. Full review of all sections.
2. Core Value check -- still the right priority?
3. Audit Out of Scope -- reasons still valid?
4. Update Context with current state.

---
*Last updated: 2026-06-23 after Phase 33 implementation*
