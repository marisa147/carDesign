# Technology Stack

**Project:** 痛车设计生成 Agent  
**Research dimension:** Stack  
**Researched:** 2026-05-07  
**Overall confidence:** HIGH for web/backend/storage, MEDIUM for image-provider details because model availability, moderation behavior, and pricing change quickly.

## Recommendation

Build v1 as a conventional split web app:

- `apps/web`: Next.js workbench for chat, 2D preview, history, export, and job progress.
- `apps/api`: FastAPI API, canonical Pydantic schemas, auth/session boundary, job lifecycle, OpenAPI contract.
- `apps/worker`: Celery workers for image generation, editing, thumbnail/export processing, and provider retries.
- Local infrastructure through Docker Compose: PostgreSQL, Redis, MinIO.

Do **not** self-host SDXL/FLUX/ComfyUI for v1. Use hosted image providers first, store every request/response/version, and design the provider interface so self-hosting can replace it later without rewriting the UI or job model.

## Recommended Stack

### Core Framework

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Node.js | 24 LTS | Frontend runtime | Current Active LTS through 2028; better default than Node 22 for a greenfield app. |
| pnpm | 10.x | JS package manager | Fast, strict installs; good workspace support without adding Turborepo complexity yet. |
| Next.js | 16.x App Router | Web workbench shell, route handlers, SSR/client composition | Matches seed direction and current App Router docs; good fit for a dense interactive UI with server-rendered shell and client-heavy workbench panels. |
| React | 19.2.x | UI runtime | Stable React 19 line with current Suspense, Actions, and performance tooling; pairs with R3F v9 later. |
| TypeScript | 6.0.x | Frontend type safety | Use strict mode from day one in a greenfield repo; do not wait for the future native TypeScript 7 compiler. |
| Tailwind CSS | 4.1.x | Styling system | Current Tailwind line, low ceremony, works with shadcn/ui and dense app surfaces. |
| shadcn/ui | latest CLI/components | Accessible component primitives | Copy-in component model avoids vendor lock-in and fits a custom workbench UI. |
| FastAPI | 0.136.x | Backend API | Current release line, Pydantic/OpenAPI native, async-friendly, and a good boundary for generated TS clients. |
| Python | 3.13.x | Backend runtime | Active, stable CPython line. Avoid Python 3.14 for v1 unless every dependency is verified. |
| uv | current | Python package/env manager | Fast lockfile-based project management; simpler than Poetry for a new service. |

### Frontend Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| TanStack Query | 5.x | Server state, polling job status, cache invalidation | Use for conversations, projects, jobs, variants, and history. Poll `/jobs/{id}` in v1; add SSE later only where it improves UX. |
| Zustand | 5.x | Local UI/workbench state | Use for active selection, panel layout, preview mode, unsaved parameter edits. Do not put canonical job data here. |
| Orval | 8.x | Generate TS clients/hooks from FastAPI OpenAPI | Keeps Python backend and TS frontend in sync. Prefer this over tRPC because the backend is Python. |
| react-konva + konva | React 19-compatible line | 2D preview/composition/export | Use for car template overlays, decal/image layers, transform handles, and high-resolution canvas export. |
| lucide-react | current | Icons | Use with shadcn/ui for toolbars and controls. |
| react-hook-form | 7.x | Parameter forms | Use for structured design parameters; validate server-side with Pydantic. |
| Zod | 4.x | Optional frontend-only validation | Use only for UI forms that need immediate validation; do not duplicate the whole backend schema by hand. |
| @react-three/fiber + three + drei | R3F 9.x / current three | Deferred 3D preview | Do not build in v1 unless explicitly scoped. Keep generated assets and vehicle/template models shaped so 3D can consume them later. |

### Backend Libraries

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| Pydantic | 2.13.x | Canonical request/job/design schemas | Strong validation and JSON schema output for OpenAPI; best place to define `DesignRequest`, `GenerationParams`, `Asset`, `Variant`, and `ProviderRun`. |
| pydantic-settings | 2.x | Config/env parsing | Keeps provider keys, storage endpoints, queue URLs, and CORS config typed. |
| SQLAlchemy | 2.0.x | ORM/Core | Current stable SQLAlchemy line; async support with PostgreSQL and avoids tying schema design to FastAPI-specific abstractions. |
| Alembic | 1.18.x | DB migrations | Standard migration tool for SQLAlchemy. |
| asyncpg | 0.31.x | PostgreSQL async driver | Native asyncio PostgreSQL driver, supports current PostgreSQL versions. |
| Celery | 5.6.x | Background generation queue | Mature retry/time-limit/routing model; fits long-running image jobs better than FastAPI background tasks. |
| Redis | 8.x service + redis-py 7.x | Celery broker/progress cache/rate limits | Use Redis for ephemeral queue/progress only; Postgres remains source of truth. |
| boto3 or MinIO SDK | current | S3-compatible object storage | Use one storage abstraction for local MinIO and production S3/R2. |
| Pillow | current | Image metadata, resizing, thumbnails | Required for export and lightweight post-processing. |
| opencv-python-headless | current | Masks, crop/resize, simple image transforms | Use only in workers; keep UI-facing transformations reproducible in job metadata. |
| openai Python SDK | current | OpenAI text/image APIs | Primary hosted provider client. |
| httpx | current | Provider calls and testable HTTP clients | Use for non-OpenAI providers such as fal/BFL. |
| pytest + pytest-asyncio + respx | current | Backend tests | Mock provider APIs and verify job-state transitions without real generation spend. |
| ruff + mypy | current | Python lint/type checks | Low-friction quality gate. |

### AI Services

| Service | Version/API | Purpose | Why |
|---------|-------------|---------|-----|
| OpenAI Images API | `gpt-image-2` | Primary text-to-image and image-edit provider | Official docs list `gpt-image-2` as the latest GPT Image model, with generation, edits, masks, high-fidelity image inputs, configurable size/quality/format. |
| OpenAI Responses API | current, image generation tool | Conversational/multi-turn image editing | Use when the user is iterating from chat context. Use Image API for one-shot queued jobs. |
| OpenAI text model | config-driven, default to current GPT-5.5 family after account availability check | Requirement parsing, prompt planning, copy generation | Keep model name in config and log it per run; roadmap should not assume a specific mini/flagship tier until cost/rate limits are validated. |
| fal.ai FLUX.2 Flash Edit | `fal-ai/flux-2/flash/edit` | Secondary image-edit provider/fallback | Supports queue/webhook flow and up to 4 reference images on fal; useful for comparing style/edit quality and avoiding single-provider lock-in. |
| Black Forest Labs FLUX.2 API | current | Future direct provider option | BFL docs position FLUX.2 as recommended for text-to-image and multi-reference editing. |

Provider interface for v1:

```python
class ImageProvider(Protocol):
    async def generate(self, request: ImageGenerationRequest) -> ProviderResult: ...
    async def edit(self, request: ImageEditRequest) -> ProviderResult: ...
```

Store these for every run: provider, model, endpoint, prompt, negative/constraint notes, input asset IDs, mask asset IDs, quality/size/format, seed if available, raw provider request ID, raw response metadata, cost estimate, safety/moderation result, output asset IDs, error payload.

### Database

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| PostgreSQL | 18.x | Canonical metadata, users/sessions, projects, tasks, variants, provider runs | Mature relational model plus JSONB for evolving generation parameters. |
| JSONB columns | PostgreSQL built-in | Versioned provider params and structured design specs | Lets v1 evolve without schema churn while preserving exact run traceability. |
| MinIO locally / S3 or Cloudflare R2 in prod | S3-compatible | Originals, references, masks, generated images, thumbnails, exports | Do not store binary assets in Postgres. Use signed URLs and predictable object keys. |
| Redis | 8.x | Broker/cache/progress | Good for queueing and transient status, not authoritative history. |

Minimum v1 tables:

- `users` or `anonymous_sessions`
- `projects`
- `conversations`
- `messages`
- `design_requests`
- `generation_jobs`
- `generation_variants`
- `assets`
- `provider_runs`
- `export_artifacts`
- `feedback_events`

### Infrastructure

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Docker Compose | current | Local dev and first deploy topology | Reproducible Postgres/Redis/MinIO/API/worker stack without Kubernetes. |
| Vercel or Dockerized Next.js | current | Frontend hosting | Vercel is easiest for Next.js; Dockerized Next is better if deploying everything to one VM. |
| Managed Postgres | current | Production DB | Neon/Supabase/RDS are all acceptable; pick based on ops preference. |
| Managed Redis | current | Production broker/cache | Upstash/Redis Cloud/ElastiCache are all acceptable; avoid running Redis on a fragile hobby box if users depend on jobs. |
| S3/R2 | current | Production object storage | Durable, cheap, signed URL support. |
| Sentry | current | Error tracking | Add early for frontend/API/worker errors; generation failures are expensive to debug after the fact. |

## What To Build First

1. Web shell with chat, parameter inspector, job list, 2D preview, history, and export button.
2. FastAPI contract with Pydantic schemas and generated Orval client/hooks.
3. Celery job pipeline: parse request -> plan prompt -> call provider -> store output asset -> emit job status.
4. PostgreSQL/MinIO traceability: every generation has durable inputs, params, provider metadata, outputs, and version links.
5. Konva 2D preview/export using same-origin or correctly CORS-configured asset URLs.

## What Not To Use Yet

| Avoid for v1 | Why | Use Instead |
|--------------|-----|-------------|
| Self-hosted SDXL/FLUX/ComfyUI as primary path | GPU ops, model churn, safety, throughput, and debugging will dominate the MVP. | Hosted OpenAI/fal/BFL provider adapter. |
| Full LangChain/LangGraph multi-agent architecture from day one | The v1 flow is mostly a deterministic job pipeline with a few LLM calls. | Pydantic schemas + small service classes; introduce LangGraph when durable branching/human checkpoints become necessary. |
| tRPC | Great for TS-only stacks, wrong contract boundary for Python FastAPI. | FastAPI OpenAPI + Orval generated TS client. |
| Kubernetes | Adds ops surface before workload shape is known. | Docker Compose locally, managed DB/storage/Redis, simple container deploy for API/workers. |
| Full 3D UV/vehicle mesh pipeline | The hardest part is quality-controlled vehicle templates and UV mapping, not rendering a model. | 2D template preview now; preserve asset metadata for later 3D. |
| Vector DB | No validated retrieval workload yet. | Postgres JSONB and explicit asset tags. Add pgvector only when semantic search/eval needs appear. |
| LoRA training platform | Out of v1 scope and not needed to validate product loop. | Prompt/provider comparison and user feedback logging. |
| Storing base64 images in DB | Bloats DB, slows backup/restore, complicates caching. | Object storage plus asset metadata rows. |

## Key Risks

| Risk | Stack Mitigation |
|------|------------------|
| Image-provider policy/account gating | OpenAI docs mention organization verification may be required for GPT Image models. Build provider fallback and surface provider errors clearly. |
| Latency and job failures | Use Celery jobs, visible status, retries with idempotency keys, and durable `provider_runs`. |
| Prompt/result non-reproducibility | Log model, provider, prompt, params, inputs, masks, output asset IDs, and version parent links every time. |
| Text placement and layout consistency | Treat generated image as draft art; use Konva/text layers for final editable labels where exact typography matters. |
| Canvas export blocked by CORS | Serve image assets through same app/domain or configure object storage CORS before drawing onto canvas. |
| Anime character/IP ambiguity | Add a policy gate and logging. Do not promise that every named copyrighted character request will be accepted by providers or safe for commercial use. |
| Future 3D mismatch | Store car template, side/view metadata, physical dimensions where known, and output aspect/scale assumptions from v1. |

## Installation Shape

```bash
# Frontend
pnpm create next-app@latest apps/web --ts --tailwind --eslint --app --src-dir
cd apps/web
pnpm add @tanstack/react-query zustand lucide-react react-hook-form zod react-konva konva
pnpm add -D orval vitest @testing-library/react @testing-library/user-event playwright
pnpm dlx shadcn@latest init
```

```bash
# Backend
uv init apps/api --app
cd apps/api
uv python pin 3.13
uv add fastapi "uvicorn[standard]" pydantic pydantic-settings sqlalchemy asyncpg alembic celery redis boto3 pillow opencv-python-headless openai httpx python-multipart
uv add --dev pytest pytest-asyncio respx ruff mypy
```

```bash
# Worker can start as the same Python package with a separate process:
uv run celery -A caragent.worker.app worker --loglevel=info
```

## Roadmap Implications

1. **Phase 1 should lock contracts and persistence before UI polish.** Define Pydantic schemas, DB tables, object keys, and provider-run audit data first.
2. **Phase 2 should build the generation loop with one provider.** Use OpenAI `gpt-image-2` first, then add fal/BFL behind the same interface.
3. **Phase 3 should harden 2D preview/export.** Konva export and CORS-safe asset serving are critical for the visible MVP.
4. **Phase 4 can introduce orchestration depth.** Add LangGraph only after the actual workflow needs branching, user approval interrupts, or long-lived agent memory.
5. **3D should be a later phase.** Add R3F/Three after the 2D template and asset model proves stable.

## Sources

- Context7: Next.js `/vercel/next.js/v16.2.2` App Router and route handler docs. Confidence: HIGH.
- Context7: FastAPI `/fastapi/fastapi/0.128.0` docs for Pydantic/OpenAPI/background task patterns. Confidence: HIGH for patterns; version checked separately via FastAPI release sources.
- Context7: LangGraph docs for stateful long-running workflows, checkpointers, and human-in-the-loop interrupts. Confidence: HIGH.
- Next.js docs: https://nextjs.org/docs. Confidence: HIGH.
- React 19.2 release: https://react.dev/blog/2025/10/01/react-19-2. Confidence: HIGH.
- Node.js release schedule: https://nodejs.org/en/about/releases/ and https://github.com/nodejs/Release. Confidence: HIGH.
- TypeScript 6.0 release notes: https://www.typescriptlang.org/docs/handbook/release-notes/typescript-6-0.html. Confidence: HIGH.
- Tailwind CSS v4.1 release/docs: https://tailwindcss.com/blog/tailwindcss-v4-1. Confidence: HIGH.
- shadcn/ui Next installation: https://ui.shadcn.com/docs/installation/next. Confidence: HIGH.
- TanStack Query docs/npm package: https://tanstack.com/query and https://www.npmjs.com/package/@tanstack/react-query. Confidence: MEDIUM for exact patch, HIGH for v5 recommendation.
- Orval docs: https://orval.dev/docs and https://orval.dev/docs/guides/react-query. Confidence: HIGH.
- Konva/react-konva docs: https://new.konvajs.org/docs/react/index.html and https://konvajs.org/docs/data_and_serialization/Stage_Data_URL.html. Confidence: HIGH.
- React Three Fiber docs: https://r3f.docs.pmnd.rs/getting-started/installation. Confidence: HIGH.
- Three.js docs: https://threejs.org/docs/pages/WebGLRenderer.html. Confidence: HIGH.
- uv docs: https://docs.astral.sh/uv/ and https://docs.astral.sh/uv/concepts/projects/workspaces/. Confidence: HIGH.
- FastAPI releases: https://github.com/fastapi/fastapi/releases and PyPI release history. Confidence: HIGH.
- Pydantic PyPI/docs: https://pypi.org/project/pydantic/ and https://docs.pydantic.dev/. Confidence: HIGH.
- SQLAlchemy 2.0 docs: https://docs.sqlalchemy.org/20/intro.html and async docs https://docs.sqlalchemy.org/20/orm/extensions/asyncio.html. Confidence: HIGH.
- Alembic docs: https://alembic.sqlalchemy.org/en/latest/. Confidence: HIGH.
- Celery PyPI/docs: https://pypi.org/project/celery/ and https://docs.celeryq.dev/. Confidence: HIGH.
- asyncpg PyPI: https://pypi.org/project/asyncpg/. Confidence: HIGH.
- PostgreSQL docs/news: https://www.postgresql.org/docs/current/ and PostgreSQL 18 release materials. Confidence: HIGH.
- Redis docs: https://redis.io/docs/latest/. Confidence: HIGH.
- MinIO docs: https://min.io/docs/minio/container/index.html. Confidence: HIGH.
- OpenAI image generation docs: https://developers.openai.com/api/docs/guides/image-generation. Confidence: HIGH.
- fal FLUX.2 Flash Edit API: https://fal.ai/models/fal-ai/flux-2/flash/edit/api. Confidence: HIGH for fal API shape.
- Black Forest Labs FLUX docs: https://docs.bfl.ai/quick_start/introduction. Confidence: HIGH for FLUX.2 positioning.
