# 痛车设计生成 Agent

## What This Is

痛车设计生成 Agent 是一个面向痛车设计需求的 AI Web 工作台。用户通过类似 GPT 的对话输入车型、动漫角色、风格、颜色、文案和参考素材，系统将需求解析为可执行任务，生成痛车设计图，并在 2D/3D 预览区展示、管理和导出方案。

v1 优先做成端到端 MVP：先让一个明确的文字到图像到预览到导出的闭环真实可用，再逐步扩展多车型、多角色组合、复杂 3D 贴图和完整商业化流程。

## Core Value

用户能用自然语言快速得到一套可预览、可迭代、可导出的高质量痛车设计方案。

## Requirements

### Validated

(None yet -- ship to validate)

### Active

- [ ] 用户可以通过对话描述痛车设计需求，包括车型、角色、风格、颜色、文案和参考素材。
- [ ] 系统可以把自然语言需求解析为结构化设计参数，并在生成前暴露关键参数供后续迭代。
- [ ] 系统可以生成至少一种可用的痛车 2D 设计图或渲染图。
- [ ] 用户可以在 Web UI 中查看生成方案、历史方案和基础参数。
- [ ] 用户可以对生成结果执行再生成、局部修改、风格切换或参数调整等迭代操作。
- [ ] 用户可以导出生成结果，至少支持图片下载。
- [ ] 系统记录任务输入、输出、参数、版本和状态，支持回溯。

### Out of Scope

- 完整报价、下单和支付系统 -- v1 先验证设计生成闭环，商业交易能力后置。
- 多车型全量模板库 -- v1 可先支持一个或少量车型/模板，避免贴图控制范围过大。
- 生产级 LoRA 训练平台 -- v1 可使用外部模型/API 或预置模型，训练流程后续补齐。
- 移动原生 App -- v1 Web 优先，移动端采用响应式适配即可。
- 完整 3D 模型自动生成 -- v1 可先做 3D 预览或占位式贴图展示，复杂模型生成后续扩展。

## Context

Seed materials:

- `init.MD` 描述了目标、Agent 模块、系统流程、技术栈、前端布局、风险和原型开发计划。
- `UI.png` 提供了更具体的产品蓝图：Next.js + React + TypeScript 前端、Tailwind CSS + shadcn/ui、Zustand + React Query、FastAPI 后端、Celery + Redis 异步任务、PostgreSQL + MinIO 存储、Three.js / React Three Fiber 预览，以及对话区、方案区、2D/3D 区、参数调整区、素材库、用户中心和导出分享能力。

Expected user experience:

- 左侧是 GPT 风格对话区，承载多轮需求澄清、方案说明和修改指令。
- 右侧是 2D/3D 预览区，支持视角切换、缩放、旋转、参数调整和历史方案切换。
- 顶部工具栏提供模型/模板/渲染模式/导出分享等高频操作。
- 底部或局部状态区展示渲染进度、任务状态、API 状态和资源消耗。

Expected backend flow:

1. 用户输入需求和素材。
2. 需求解析 Agent 输出结构化参数。
3. Prompt / 风格规划 Agent 生成图像提示词、控制条件和任务计划。
4. 文案生成 Agent 生成车身口号、副标题和贴花文案。
5. 图像生成 Agent 输出初稿。
6. 控制与贴图 Agent 处理 mask、局部重绘、ControlNet / IP-Adapter 条件和贴图适配。
7. 后处理 Agent 做增强、修复和超分。
8. 预览输出 Agent 在 2D/3D 区展示并支持下载导出。
9. Feedback & Evaluation Agent 记录用户反馈并驱动下一轮迭代。

## Constraints

- **MVP scope**: v1 优先端到端闭环，而不是一次性完成全部多 Agent、多车型、生产级 3D 和商业化能力 -- 这样能尽早验证核心价值。
- **Frontend stack**: UI 参考明确倾向 Next.js、React、TypeScript、Tailwind CSS、shadcn/ui、Zustand、React Query、Three.js / React Three Fiber -- 后续除非有明确理由，应优先沿用。
- **Backend stack**: Agent 调度和模型调用倾向 Python、FastAPI、Celery、Redis -- 适合异步生成任务和多 Agent 协作。
- **Storage**: 设计稿、车辆模板、用户素材和任务历史需要对象存储与结构化元数据，参考方案为 PostgreSQL + MinIO/S3。
- **AI providers**: 图像生成可从外部 API 或可部署模型开始，后续再引入 SDXL/FLUX、LoRA、ControlNet、IP-Adapter、Real-ESRGAN 等更重能力。
- **Performance**: 图像生成与后处理必须异步执行，前端需要可见的任务状态、进度和失败恢复路径。
- **Traceability**: 每次生成都要保留输入、参数、模型、输出、反馈和版本，避免结果不可复现。

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| v1 选择端到端 MVP | 先验证用户从自然语言到可导出设计方案的核心闭环，降低首个里程碑风险 | Pending |
| Web 优先 | UI.png 已定义完整 Web 工作台，且生成任务适合桌面/浏览器操作 | Pending |
| 前端采用 Next.js + React + TypeScript | seed 方案已明确，适合复杂交互和可维护 UI | Pending |
| 后端采用 Python + FastAPI | 适合 Agent 编排、模型调用、图像处理和异步任务 API | Pending |
| 生成任务异步化 | 图像生成/后处理耗时且可能失败，需要队列、状态和重试 | Pending |
| 先支持有限车型/模板 | 贴图控制和预览质量依赖模板，v1 控制范围更容易交付 | Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):

1. Requirements invalidated? Move to Out of Scope with reason.
2. Requirements validated? Move to Validated with phase reference.
3. New requirements emerged? Add to Active.
4. Decisions to log? Add to Key Decisions.
5. "What This Is" still accurate? Update if drifted.

**After each milestone** (via `$gsd-complete-milestone`):

1. Full review of all sections.
2. Core Value check -- still the right priority?
3. Audit Out of Scope -- reasons still valid?
4. Update Context with current state.

---
*Last updated: 2026-05-07 after initialization*
