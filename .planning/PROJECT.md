# 痛车设计生成 Agent

## What This Is

痛车设计生成 Agent 是一个面向痛车设计需求的 AI Web 工作台。v1.0 已经交付一个可本地运行的端到端 MVP：用户可以通过 GPT 风格对话描述车型、角色、风格、颜色、文案和参考素材，系统将需求解析为结构化参数，经异步 worker 生成 2D 概念图，并在 Web 工作台中展示、迭代、反馈、导出和查看运营状态。

v1.0 的边界是概念设计闭环，不承诺生产级印刷交付、完整 3D UV 预览、商业订单流或托管模型生产可用性。后续里程碑应从已验证的工作台、任务账本、PreviewSpec 和 provider adapter 边界上继续扩展。

## Core Value

用户能用自然语言快速得到一套可预览、可迭代、可导出的高质量痛车设计方案。

## Current Milestone: v2.0 V2 MVP

**Goal:** 将 v1.0 已验证的概念设计闭环升级为更实用的设计辅助产品：在受控 guardrail 下接入 hosted provider，支持局部编辑、参考引导、轻量 3D 预览和增强概念交付包，同时继续明确区分 concept preview、3D preview 和 production-ready wrap。

**Target features:**

- V1 closure and V2 readiness gate: 锁定 v1.0 基线，加入默认关闭的 V2 feature flags，并验证本地-only 模式仍可运行。
- Hosted provider rollout MVP: 在既有 provider adapter 边界后接入至少一个真实 hosted image provider，保留 quota、cost、fallback、moderation 和失败可视性。
- Targeted regeneration and masked editing MVP: 用户可以选择局部区域或图层做定向修改，并保存 mask、edit intent、父子版本和生成方式。
- Reference-guided generation MVP: 上传素材可以标注 character/style/vehicle/logo/palette/inspiration 等参考角色，并带 rights/source gate 与 provider capability checks。
- Lightweight 3D preview MVP: 以现有 PreviewSpec 和模板资产驱动一个轻量 3D 或 pseudo-3D 预览，不承诺生产级 UV 精度。
- Enhanced concept handoff package MVP: 导出包含预览图、overlay、manifest、prompt/provider trace、warnings、handoff notes 和 concept-only disclaimer 的 ZIP 包。
- V2 hardening, docs, smoke, and UAT: 关闭验证、文档、回归、Browser UAT、feature flag 和 release evidence。

## Current State

**Shipped:** v1.0 MVP on 2026-06-18.

**Built and verified:**

- Next.js/React/TypeScript workbench with chat, parameter editing, asset upload, progress/events, 2D preview, version history, feedback, export, itasha controls, and operations status.
- FastAPI/Pydantic API with generated OpenAPI/TypeScript contracts.
- Celery worker pipeline with local deterministic generation, provider adapter boundary, retries/fallback, cancellation, quota/rate preflight, and structured failure metadata.
- PostgreSQL/object-storage-oriented data model for workspaces, messages, briefs, jobs, events, artifacts, versions, model runs, feedback, exports, and cost records.
- Local Docker smoke path for PostgreSQL, Redis, MinIO, API, worker, web, and live worker queue generation.

**Codebase scale at v1.0 close:** about 112 source files / 17,452 LOC, or 120 source-plus-test files / 19,836 LOC across `apps/`, `packages/`, `services/`, `scripts/`, and `infra/` excluding runtime generated artifacts.

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

### Active

- [ ] V2 readiness gate protects the shipped v1.0 baseline before new capabilities are enabled.
- [ ] Hosted provider generation can be tested safely through config-driven adapters, preflight guards, durable trace records, and visible failure/cost/quota state.
- [ ] Targeted edits can update selected regions or layers while preserving immutable artifacts and parent-child version lineage.
- [ ] Reference-guided generation can use uploaded assets with explicit roles, rights/source snapshots, and provider capability warnings.
- [ ] Lightweight 3D preview can consume existing PreviewSpec/template assets and remain labeled as non-production.
- [ ] Enhanced concept handoff export can package concept assets, overlays, traces, warnings, notes, and disclaimers without claiming print readiness.
- [ ] V2 MVP can be validated through aggregate tests, Docker smoke, hosted-provider manual smoke, Browser UAT, docs, and release notes.

### Out of Scope

- 完整报价、下单和支付系统 -- v1.0 已验证设计生成闭环，商业交易能力继续后置。
- 多车型全量模板库 -- v1.0 以有限模板和 PreviewSpec 合同验证方向，广泛模板覆盖需要后续 QA 预算。
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

## Future Candidate Promotions After v2.0

- Full print-ready PSD/AI/PDF-style handoff with verified scale, bleed, color profile, DPI, and installer notes.
- Verified vehicle-specific UV mapping and broad template library coverage.
- Marketplace, template store, public gallery, payment, quoting, ordering, installer network, and collaboration workflows.
- Fully automated copyright/licensing verification.
- Fully consistent multi-view generation across side/front/rear/hood with guaranteed physical alignment.
- Advanced multi-agent orchestration beyond the typed generation and worker pipeline.

## Constraints

- **MVP scope discipline**: v1.0 proved the end-to-end concept loop. Later milestones should keep production handoff, true 3D, marketplace, and broad template libraries as explicit promotions instead of quiet scope creep.
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
| Hosted provider rollout remains opt-in | Provider model availability, costs, moderation, and rights constraints change quickly | ⚠ Revisit — needs current validation before real hosted generation |
| V2 MVP follows the external roadmap file | User supplied `C:/Users/25858/Downloads/V2_MVP_ROADMAP (1).md` as the milestone source of truth | — Pending — v2.0 planning initialized from that file |

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
*Last updated: 2026-06-18 after v2.0 milestone start*
