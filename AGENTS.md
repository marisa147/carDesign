# AGENTS.md instructions for D:\python\carAgent

<!-- CCG-FAST-CONTEXT-START -->
# fast-context MCP 工具使用指南（辅助模式）

## 核心原则

**主检索工具为 ace-tool（`mcp__ace-tool__search_context`）。当 ace-tool 无法满足语义搜索需求时，使用 `mcp__fast-context__fast_context_search` 作为补充。**

适合使用 fast-context 的场景：
- 用自然语言描述要找的逻辑（如"部署流程"、"事件处理"）
- 跨模块、跨层级的调用链路追踪
- 中文语义搜索（工具支持中英文双语查询）
<!-- CCG-FAST-CONTEXT-END -->

<!-- GSD:project-start source:PROJECT.md -->
## Project

痛车设计生成 Agent 是一个面向痛车设计需求的 AI Web 工作台。用户通过类似 GPT 的对话输入车型、动漫角色、风格、颜色、文案和参考素材，系统将需求解析为可执行任务，生成痛车设计图，并在 2D/3D 预览区展示、管理和导出方案。

Core value: 用户能用自然语言快速得到一套可预览、可迭代、可导出的高质量痛车设计方案。

v1 优先端到端 MVP：先让文字到图像到预览到导出的闭环真实可用，再扩展多车型、多角色组合、复杂 3D 贴图和商业化流程。

Primary planning artifacts:
- `.planning/PROJECT.md` - living project context, constraints, and decisions
- `.planning/REQUIREMENTS.md` - v1/v2 requirements and traceability
- `.planning/ROADMAP.md` - seven-phase v1 roadmap
- `.planning/STATE.md` - current position and session memory
- `.planning/research/` - stack, feature, architecture, pitfalls, and summary research
<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->
## Technology Stack

Planned v1 stack:
- Frontend: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, Zustand, react-konva/Konva, lucide-react.
- Backend/API: Python, FastAPI, Pydantic, SQLAlchemy, Alembic, asyncpg.
- Worker: Celery with Redis broker/progress cache.
- Data: PostgreSQL for canonical metadata and job state; MinIO/S3 for binary artifacts; Redis only for queue/cache/progress.
- AI providers: hosted image providers behind internal adapters first; provider/model names must stay config-driven and re-verified during implementation planning.
- Future 3D: Three.js / React Three Fiber only after 2D template and preview contracts stabilize.

Use `.planning/research/STACK.md` for detailed stack rationale. Treat fast-moving package/model versions in research as planning input, not final implementation truth; verify exact versions from official docs during phase planning.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

Conventions are not yet established by code. Until the first implementation phase creates project-specific patterns:
- Keep frontend server state in TanStack Query and local workbench UI state in Zustand.
- Treat FastAPI/Pydantic schemas as the API contract source and generate/mirror TypeScript types from OpenAPI.
- Keep generated images, uploads, masks, previews, thumbnails, and exports in object storage; store metadata and object keys in PostgreSQL.
- Make generation/export jobs asynchronous and durable; do not run expensive provider calls synchronously inside HTTP handlers.
- Store structured briefs, prompt plans, provider/model parameters, inputs, outputs, costs, feedback, and parent-child version lineage for traceability.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

Use a four-plane architecture:

1. Product plane: Next.js workbench for chat, parameters, asset upload, 2D preview, history, feedback, and export.
2. Control plane: FastAPI service for typed API contracts, validation, sessions/auth boundary, job creation, artifact lookup, and status endpoints.
3. Work plane: Celery workers for prompt planning, provider calls, post-processing, thumbnail/export generation, quality checks, and later agent orchestration.
4. Data plane: PostgreSQL as canonical ledger, MinIO/S3 as artifact storage, Redis as broker/cache/progress layer only.

Core architectural rules:
- PostgreSQL job rows and job events are the source of truth, not Celery or Redis result state.
- Artifacts are immutable. New generation, edit, mask, thumbnail, preview, and export outputs create new artifact records.
- Frontend renders a renderer-neutral `PreviewSpec`; v1 starts with 2D and later adds true Three.js/UV preview behind the same contract.
- Workers call provider adapters, not vendor APIs scattered through the codebase.
- Pipeline stages come before complex multi-agent orchestration.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

No project-local skills found yet. Add skills to any of `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, or `.github/skills/` with a `SKILL.md` index file when repeated project-specific procedures emerge.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `$gsd-discuss-phase 1` - gather phase context and clarify approach for Phase 1
- `$gsd-ui-phase 1` - generate UI design contract for Phase 1 if the implementation is frontend-heavy
- `$gsd-plan-phase 1` - create executable implementation plans for Phase 1
- `$gsd-quick` - small fixes, doc updates, and ad-hoc tasks
- `$gsd-debug` - investigation and bug fixing
- `$gsd-execute-phase` - planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `$gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` - do not edit manually.
<!-- GSD:profile-end -->
