# Architecture Patterns

**Domain:** AI web workbench for text-to-itasha design generation  
**Project:** Itasha Design Generation Agent  
**Researched:** 2026-05-07  
**Confidence:** MEDIUM-HIGH  
**Scope:** Architecture dimension only. This file recommends system structure, component boundaries, data flow, storage and queue responsibilities, frontend/backend contracts, and roadmap build order.

## Recommended Architecture

Use a four-plane architecture:

1. **Product plane:** Next.js + React + TypeScript workbench for chat, 2D preview, design history, parameters, assets, and export.
2. **Control plane:** FastAPI backend for typed API contracts, validation, auth boundary, job creation, artifact lookup, and status streaming.
3. **Work plane:** Celery workers for long-running generation, post-processing, thumbnail/export production, and later agent orchestration stages.
4. **Data plane:** PostgreSQL for canonical metadata and job state, MinIO/S3 for binary artifacts, Redis for queue/broker and short-lived progress/cache data.

For v1, do not build a complex multi-agent runtime first. Build a single generation pipeline with explicit stages and typed intermediate records. Later, each stage can become an agent node without changing the frontend, job API, storage model, or artifact contract.

```text
Browser / Next.js workbench
  - Chat, parameter editor, 2D preview, history, export
  - React Query for server state
  - Zustand for local workspace state
        |
        | REST for commands and reads
        | WebSocket or SSE for job events
        v
FastAPI control API
  - Validates requests with Pydantic
  - Owns conversations, jobs, designs, assets, exports
  - Writes canonical job/design rows
  - Enqueues background work
        |
        +------------------------+
        |                        |
        v                        v
PostgreSQL                 Redis broker/cache
  - Users                  - Celery broker
  - Conversations          - short-lived progress fanout
  - Messages               - optional locks/rate limits
  - Design briefs
  - Jobs and events
  - Design versions
  - Artifact metadata
        ^                        |
        |                        v
        |                  Celery workers
        |                    - parse/plan/generate/postprocess/preview/export
        |                    - call AI providers or local model services
        |                    - write artifacts and job events
        |                        |
        +------------------------+
                                 v
                          MinIO / S3 object storage
                            - uploads
                            - generated renders
                            - masks/control images
                            - thumbnails
                            - export bundles
                            - future 3D preview assets
```

## Architectural Principles

| Principle | Recommendation | Why |
|-----------|----------------|-----|
| Vertical slice first | Ship one text-to-2D-design-to-history-to-export path before multi-agent or full 3D. | The product value is the closed loop, not agent sophistication. |
| Job ledger is canonical | PostgreSQL job rows and job events are the source of truth. Celery result state is operational only. | Redis/result backends are useful for queue mechanics, but the product needs durable history and reproducibility. |
| Artifacts are immutable | Every generated image, mask, thumbnail, prompt bundle, and export is a new artifact object. | Enables comparison, rollback, history, evaluation, and later re-rendering. |
| Version prompts and params | Store prompt, negative prompt, seed, provider, model, template id, control inputs, and postprocess params per design version. | AI output must be traceable and reproducible enough for iteration. |
| Preview is a contract | Frontend renders a `PreviewSpec`, not raw worker internals. | 2D preview can ship now; future 3D can reuse the same design/version/artifact model. |
| Provider adapters | Workers call internal provider interfaces, not vendor APIs directly throughout the codebase. | Allows switching between external APIs, SDXL/FLUX, ControlNet, or local GPU services. |
| Orchestration is staged | Model the pipeline as named stages now, even if one worker executes them. | Stages can later map to LangGraph/multi-agent nodes without changing job APIs. |

## Component Boundaries

| Component | Responsibility | Owns | Communicates With |
|-----------|----------------|------|-------------------|
| Next.js App Shell | Routes, authenticated workspace layout, top toolbar, responsive split layout. | UI routing, layout state, navigation. | FastAPI API client, auth provider if added. |
| Chat Panel | Conversation messages, user commands, quick actions such as regenerate/edit/style switch. | Message composition and display state. | `POST /conversations`, `POST /generations`, job event stream. |
| Parameter Editor | Structured brief editing: vehicle, character, style, colors, text, references. | Local draft state before submit. | Generation API and design version metadata. |
| 2D Preview Renderer | Displays current design, layers, thumbnails, zoom/pan, view presets. | Client rendering state only. | Design artifacts and `PreviewSpec`. |
| History/Comparison Panel | Shows design versions, thumbnails, status, parent-child relationships. | Selection state. | Design/version APIs. |
| Asset Uploader | Uploads references, vehicle photos, logos, masks. | Client upload flow and progress. | Asset API and object storage URLs/proxy. |
| Export UI | Requests PNG/JPEG/ZIP export and downloads completed artifact. | Export command state. | Export API and job event stream. |
| FastAPI API Layer | External contract, request validation, response models, auth checks, status streaming. | REST/WebSocket/SSE surface. | Postgres repositories, object store service, Celery enqueue service. |
| Domain Services | Business operations: create generation, create iteration, attach artifacts, update status. | Transaction boundaries and invariants. | Repositories, queue adapter, provider-independent schemas. |
| Job Service | Creates jobs, appends events, tracks stage progress, handles cancellation/retry. | Job lifecycle. | Postgres, Celery, event stream. |
| Worker Pipeline | Executes stages: parse brief, plan prompt, generate image, postprocess, build preview, evaluate. | Heavy compute and provider calls. | AI providers/local models, object storage, Postgres events. |
| Provider Adapters | Normalize external image/LLM/model APIs behind internal interfaces. | Provider-specific credentials, request mapping, response mapping. | Worker pipeline. |
| Preview Adapter | Converts design artifacts into 2D `PreviewSpec`; later 3D scene/UV specs. | Preview payload generation. | Worker pipeline, frontend preview renderer. |
| Storage Layer | Repository classes for PostgreSQL and object storage. | Persistence details. | API services and workers. |
| Observability | Logs, traces, job metrics, provider latency/errors, audit trail. | Operational visibility. | API, workers, queue, model adapters. |

## Data Model Boundaries

| Entity | Storage | Purpose | Notes |
|--------|---------|---------|-------|
| `User` | PostgreSQL | Account identity and ownership. | v1 can start with anonymous/local user if auth is deferred, but keep owner fields nullable or system-owned. |
| `Conversation` | PostgreSQL | Chat session containing messages and generated design versions. | One conversation can have many generation jobs and design versions. |
| `Message` | PostgreSQL | User/system/assistant messages and command history. | Store structured command references, not only rendered text. |
| `DesignBrief` | PostgreSQL JSONB plus typed columns for common filters | Structured intent: vehicle, character, style, palette, copy, references. | Generated from chat, editable before execution. |
| `GenerationJob` | PostgreSQL | Canonical task record and current status. | State machine: `queued`, `running`, `waiting_input`, `succeeded`, `failed`, `canceled`. |
| `JobEvent` | PostgreSQL | Append-only stage/progress/error events. | Drives status timeline, debugging, and UI streaming replay. |
| `DesignVersion` | PostgreSQL | A concrete generated candidate. | Parent-child relationship supports regenerate and local edits. |
| `Artifact` | PostgreSQL metadata + MinIO/S3 binary | Input uploads, images, masks, thumbnails, preview specs, exports. | Store object key, mime type, checksum, size, dimensions, role. |
| `ModelRun` | PostgreSQL | Prompt, provider, model, seed, control inputs, costs, latency. | Required for traceability and later evaluation. |
| `PreviewSpec` | MinIO/S3 JSON artifact plus metadata row | Renderer-neutral preview description. | v1: 2D layers. Later: Three.js scene/UV/material slots. |
| `Feedback` | PostgreSQL | Rating, edit intent, user comments, accepted version. | Later feeds evaluation and prompt tuning. |
| `Export` | PostgreSQL metadata + MinIO/S3 binary | Downloadable PNG/JPEG/ZIP package. | Export itself can be an async job when expensive. |

## Queue And Storage Responsibilities

### PostgreSQL

Use PostgreSQL as the durable source of truth for:

- Conversation, message, design brief, design version, and feedback records.
- Generation job state, stage state, event log, retry count, failure reason, and timestamps.
- Artifact metadata, object storage keys, checksums, dimensions, and relationships.
- Model/provider parameters needed to reproduce or explain a version.

Do not store generated image binaries in PostgreSQL. Store metadata and object keys only.

### MinIO / S3

Use object storage for:

- User uploads and reference assets.
- Generated 2D renders, thumbnails, masks, control images, upscaled outputs.
- Prompt bundles or preview specs when they become large JSON artifacts.
- Export bundles and future 3D assets such as GLB files, UV maps, material textures, and environment maps.

Object keys should include owner/conversation/design/job identifiers and immutable artifact ids. Avoid overwriting objects in place.

### Redis

Use Redis for:

- Celery broker.
- Short-lived progress fanout or pub/sub if WebSocket/SSE needs low-latency updates.
- Optional dedupe locks, rate limit counters, and temporary cache.

Do not rely on Redis as the only record of job status, generated results, or user history.

### Celery

Use Celery for:

- Long-running image generation, post-processing, preview generation, thumbnail generation, and export generation.
- Retryable provider calls and stage execution.
- Later separation of worker pools by capability: CPU image ops, GPU/local model jobs, external provider jobs.

Celery task ids should be linked to `GenerationJob.id`, but product status should be read from PostgreSQL. Tasks must be idempotent by stage and job id: if a worker retries after writing an artifact, it should detect the existing successful stage output before creating duplicates.

## Frontend/Backend Contracts

Prefer OpenAPI-first contracts generated from FastAPI/Pydantic models, then generate or hand-maintain a typed TypeScript client. React Query should own server state; Zustand should own only local workspace state such as selected tab, zoom, active version id, unsaved brief draft, and panel sizing.

### Core Endpoints

| Endpoint | Method | Purpose | v1 Required |
|----------|--------|---------|-------------|
| `/api/conversations` | `POST` | Create a workspace conversation. | Yes |
| `/api/conversations/{id}` | `GET` | Load messages, active brief, versions, and jobs. | Yes |
| `/api/conversations/{id}/messages` | `POST` | Add user message or edit command. | Yes |
| `/api/assets` | `POST` | Upload or register a reference asset. | Yes, simple backend-mediated upload is enough. |
| `/api/generations` | `POST` | Create initial generation job from a structured brief and message context. | Yes |
| `/api/designs/{version_id}/iterations` | `POST` | Create regenerate/edit/style-change job from an existing version. | Yes |
| `/api/jobs/{job_id}` | `GET` | Poll canonical job status and recent events. | Yes |
| `/api/jobs/{job_id}/events` | `GET` or stream | SSE/WebSocket event stream for progress. | Yes, polling is acceptable for first slice; streaming should follow quickly. |
| `/api/designs/{version_id}` | `GET` | Load version metadata, artifacts, preview spec, prompt summary. | Yes |
| `/api/exports` | `POST` | Create export artifact from selected version. | Yes |
| `/api/exports/{export_id}` | `GET` | Return export status and download URL. | Yes |
| `/api/templates/vehicles` | `GET` | List supported vehicle templates. | Yes, even if only one template exists. |
| `/api/providers/status` | `GET` | Provider availability and configured capabilities. | Useful for operations, can be basic in v1. |

### Request Shape: Generation

```json
{
  "conversation_id": "uuid",
  "idempotency_key": "client-generated-key",
  "mode": "initial",
  "parent_design_version_id": null,
  "brief": {
    "vehicle_template_id": "sports_coupe_v1",
    "character_description": "blue twin-tail anime idol",
    "style": "cyber racing",
    "palette": ["black", "cyan", "white"],
    "body_text": ["Racing Miku", "01"],
    "views_requested": ["front_3q", "side"],
    "reference_asset_ids": ["uuid"]
  }
}
```

### Response Shape: Job Created

```json
{
  "job_id": "uuid",
  "conversation_id": "uuid",
  "status": "queued",
  "status_url": "/api/jobs/uuid",
  "events_url": "/api/jobs/uuid/events"
}
```

### Response Shape: Job Status

```json
{
  "job_id": "uuid",
  "status": "running",
  "stage": "generate_image",
  "progress": 0.62,
  "message": "Generating primary 2D render",
  "design_version_id": null,
  "events": [
    {
      "event_id": "uuid",
      "stage": "plan_prompt",
      "level": "info",
      "message": "Prompt plan completed",
      "created_at": "2026-05-07T08:30:00Z"
    }
  ]
}
```

### Response Shape: Design Version

```json
{
  "design_version_id": "uuid",
  "conversation_id": "uuid",
  "parent_design_version_id": null,
  "brief_id": "uuid",
  "status": "ready",
  "thumbnail_artifact_id": "uuid",
  "artifacts": [
    {
      "artifact_id": "uuid",
      "kind": "render_2d",
      "mime_type": "image/png",
      "width": 1536,
      "height": 1024,
      "url": "signed-or-proxied-url"
    }
  ],
  "preview_spec": {
    "mode": "2d-template",
    "version": 1,
    "layers": [
      {
        "role": "base_render",
        "artifact_id": "uuid",
        "transform": { "x": 0, "y": 0, "scale": 1, "rotation": 0 }
      }
    ],
    "camera_presets": ["front_3q", "side", "rear_3q"]
  }
}
```

### Future 3D Extension Contract

Do not expose Three.js implementation details in generation APIs. Extend `PreviewSpec`:

```json
{
  "mode": "threejs-car-wrap",
  "version": 1,
  "model_artifact_id": "uuid",
  "uv_layout_artifact_id": "uuid",
  "material_slots": [
    {
      "slot": "left_body",
      "texture_artifact_id": "uuid",
      "wrap_mode": "decal"
    }
  ],
  "camera_presets": ["left", "right", "front", "rear", "free"]
}
```

This keeps the frontend preview renderer swappable: v1 renders `2d-template`; later it adds a Three.js renderer for `threejs-car-wrap`.

## Data Flow

### Initial Generation Flow

1. User types a request and optionally uploads reference assets.
2. Frontend creates/updates a conversation and sends a `GenerationRequest`.
3. FastAPI validates the request, stores the message, creates a `DesignBrief`, creates a `GenerationJob`, appends `queued` event, and enqueues a Celery task.
4. Worker loads the job and brief, marks job/stage `running`, and appends progress events.
5. Worker runs v1 staged pipeline:
   - `parse_brief`: normalize user intent into structured params.
   - `plan_prompt`: build image prompt, style plan, negative prompt, control hints.
   - `generate_image`: call external image provider or local model adapter.
   - `postprocess`: crop, enhance, create thumbnail, optional upscaling.
   - `build_preview`: create v1 2D `PreviewSpec`.
   - `summarize`: create assistant-facing result message and parameter summary.
6. Worker writes artifacts to MinIO/S3 and metadata/events to PostgreSQL.
7. Frontend polls or streams job events and switches preview/history when `DesignVersion` becomes ready.
8. User exports selected version; API either returns existing artifact or enqueues export job.

### Iteration Flow

1. User selects a design version and enters an edit command such as "make the palette red/black and add more side decals."
2. Frontend sends `POST /api/designs/{version_id}/iterations` with edit command and optional parameter overrides.
3. API creates a child `DesignBrief`, child `GenerationJob`, and records parent version linkage.
4. Worker reuses stored context from parent version: original brief, prompt plan, model run metadata, and artifacts.
5. Worker creates a new `DesignVersion`; the previous version remains immutable.

### Export Flow

1. User requests PNG/JPEG or ZIP package for selected version.
2. API checks whether a matching export artifact already exists.
3. If absent, enqueue export job; worker assembles full-size image, thumbnail, prompt summary, and metadata manifest.
4. Export is stored as an artifact; API returns a signed/proxied download URL.

## Patterns To Follow

### Pattern 1: Durable Job State Machine

**What:** Keep job state in PostgreSQL and append events for every meaningful stage transition.

**When:** All generation, iteration, postprocess, preview, and export jobs.

**Example states:**

```text
queued -> running -> succeeded
queued -> running -> failed
queued -> canceled
running -> waiting_input -> running -> succeeded
```

**Why:** Users need reliable history, refresh-safe progress, retry visibility, and failure recovery.

### Pattern 2: Pipeline Stages Before Agents

**What:** Model v1 generation as a sequence of named stages with typed inputs/outputs. Implement them as plain Python services/tasks first.

**When:** v1 MVP through first production validation.

**Example:**

```text
DesignBrief
  -> PromptPlan
  -> ProviderRequest
  -> ProviderResult
  -> PostprocessResult
  -> PreviewSpec
  -> DesignVersion
```

**Why:** It gives traceability and future multi-agent boundaries without paying orchestration complexity before the product loop works.

### Pattern 3: Provider Adapter Interface

**What:** Hide provider-specific calls behind interfaces such as `ImageGenerationProvider`, `LLMProvider`, `UpscaleProvider`, and `ObjectStorage`.

**When:** Any external model/API/local GPU dependency.

**Example interface shape:**

```python
class ImageGenerationProvider:
    def generate(self, request: "ProviderImageRequest") -> "ProviderImageResult":
        ...
```

**Why:** v1 can use a hosted image API. Later SDXL/FLUX/ControlNet/local GPU can replace or coexist behind the same worker contract.

### Pattern 4: PreviewSpec Adapter

**What:** Workers create preview specs; frontend chooses renderer by `preview_spec.mode`.

**When:** All previewable outputs.

**Why:** 2D preview, future 3D preview, and future decal/UV layout tools should not require changing core generation/job APIs.

### Pattern 5: OpenAPI-Typed Frontend Client

**What:** Treat FastAPI/Pydantic schemas as the source for API contracts and generate or manually mirror TypeScript types.

**When:** From the first frontend/backend integration phase.

**Why:** The UI will have many states and versioned artifacts; type drift will be expensive.

### Pattern 6: Idempotent Job Creation And Stage Execution

**What:** Require an `idempotency_key` for job creation and make worker stages detect completed outputs before retrying.

**When:** All commands that can create jobs or artifacts.

**Why:** Image generation calls are costly, slow, and retry-prone; duplicated jobs will confuse history and waste spend.

## Anti-Patterns To Avoid

### Anti-Pattern 1: Synchronous Image Generation In HTTP

**What:** API endpoint calls image generation directly and waits.

**Why bad:** Requests time out, progress is invisible, retries are unsafe, and failures lose context.

**Instead:** API creates a durable job and enqueues Celery work.

### Anti-Pattern 2: Frontend Calls AI Providers Directly

**What:** Browser sends prompts/uploads to model vendors.

**Why bad:** Leaks credentials, bypasses audit/history, and makes costs impossible to control.

**Instead:** Frontend only talks to the FastAPI control API.

### Anti-Pattern 3: Storing Only Final Images

**What:** Save only output PNGs with no prompt, seed, provider, template, source assets, or parent version.

**Why bad:** Users cannot meaningfully iterate, debug, compare, or reproduce results.

**Instead:** Store `ModelRun`, `DesignBrief`, `DesignVersion`, and immutable artifacts.

### Anti-Pattern 4: Building Full 3D Before Stable 2D Template Data

**What:** Start with 3D model generation, UV mapping, and interactive wrap tooling.

**Why bad:** It creates a large uncertain surface before validating whether generated designs satisfy users.

**Instead:** v1 ships 2D preview and `PreviewSpec`; later add Three.js renderer and 3D artifacts behind the same contract.

### Anti-Pattern 5: Premature Multi-Agent Runtime

**What:** Introduce LangGraph or complex agent handoffs before the generation loop, storage, retries, and UI states are stable.

**Why bad:** Orchestration complexity masks product and data-model issues.

**Instead:** Start with pipeline stages, logs, and typed handoff objects. Promote stages into agents only when there is a measured need.

### Anti-Pattern 6: Redis As Product Database

**What:** Store job state/progress only in Redis or Celery result metadata.

**Why bad:** Product history becomes fragile and hard to replay after worker/broker issues.

**Instead:** PostgreSQL owns job state and event history; Redis accelerates queueing and streaming.

## Recommended Build Order

The roadmap should follow dependency order, not visual ambition. Build the durable vertical slice first, then widen the product.

| Phase | Name | Goal | Depends On | Key Deliverables |
|-------|------|------|------------|------------------|
| 0 | Project skeleton and contracts | Establish repo shape, Docker Compose, shared schemas, basic CI, environment config. | None | Next.js app shell, FastAPI app, Postgres/Redis/MinIO services, OpenAPI baseline, health checks. |
| 1 | Data and job backbone | Make jobs, artifacts, conversations, and design versions durable before generation is real. | Phase 0 | Database migrations, repositories, job state machine, artifact service, mock worker, job polling endpoint. |
| 2 | Text-to-image vertical slice | Turn one structured request into one generated 2D artifact. | Phase 1 | Brief parser, prompt planner, provider adapter, Celery task, artifact write, design version creation. |
| 3 | Workbench UI integration | Connect chat and preview/history to real jobs. | Phase 2 | Chat panel, parameter draft, generation submit, progress UI, 2D preview renderer, version thumbnails. |
| 4 | Iteration and export | Support regenerate/edit/style switch and downloadable outputs. | Phase 3 | Parent-child versions, edit commands, export jobs, download URLs, feedback capture. |
| 5 | Preview fidelity and template control | Improve 2D design quality around a limited vehicle/template set. | Phase 4 | Vehicle template registry, view presets, masks/control assets, preview spec hardening, thumbnail comparisons. |
| 6 | Operational hardening | Make failures diagnosable and costs visible. | Phase 2 or 3 | Retry policy, idempotency, provider error taxonomy, logs/metrics, admin status view, rate limits. |
| 7 | 3D preview adapter | Add 3D rendering without changing core job/design APIs. | Phase 5 | Three.js/R3F renderer for `threejs-car-wrap`, GLB asset loading, material slots, camera presets. |
| 8 | Multi-agent orchestration | Promote stable pipeline stages into explicit agents. | Phase 2-6 stable | LangGraph or equivalent orchestration, agent trace view, specialist stages for prompt/copy/eval/control. |

### Ordering Rationale

- **Contracts before UI polish:** Chat, history, progress, and export all depend on durable job/design/artifact contracts.
- **Queue before generation:** Image jobs must be async from the first real provider integration.
- **2D before 3D:** 2D validates design quality and iteration language with far less geometry/UV risk.
- **Pipeline before multi-agent:** Named stages preserve a migration path while keeping v1 understandable and shippable.
- **Observability early:** AI failures are expected; without stage events and model run metadata, debugging will be guesswork.

### Dependency Graph

```text
Project skeleton
  -> Data model and artifact storage
  -> Job queue and status API
  -> Provider adapter and text-to-image worker
  -> Chat/2D preview/history UI
  -> Iteration and export
  -> Template/mask/control improvements
  -> 3D preview adapter
  -> Multi-agent orchestration
```

## Suggested Repository Structure

```text
apps/
  web/
    app/
    components/
      chat/
      preview/
      history/
      parameters/
      assets/
      export/
    lib/
      api/
      preview/
      state/
    types/
services/
  api/
    app/
      main.py
      routers/
      schemas/
      services/
      repositories/
      storage/
      queue/
      auth/
  worker/
    app/
      celery_app.py
      tasks/
      pipeline/
      providers/
      postprocess/
      preview/
packages/
  contracts/
    openapi/
    schemas/
infra/
  docker-compose.yml
  migrations/
```

For a single-repo MVP, keep `services/api` and `services/worker` in the same Python package if that reduces setup friction, but preserve boundaries through modules. The worker should not import FastAPI routers, and the frontend should not import backend internals.

## Scalability Considerations

| Concern | At 100 users | At 10K users | At 1M users |
|---------|--------------|--------------|-------------|
| API scale | One FastAPI instance plus one worker pool is enough. | Separate API replicas and worker pools; add rate limits and provider quotas. | Multi-region API, tenant-level quotas, job sharding, dedicated orchestration services. |
| Queue | Single Redis broker. | Dedicated Redis, separate queues by job type/provider/GPU need. | Managed queue/broker, priority routing, per-tenant throttling, dead-letter handling. |
| Database | Single Postgres with indexes on owner/status/conversation. | Read replicas for history, partition job events if large. | Partition events/artifacts metadata, archive cold history, analytics warehouse. |
| Object storage | MinIO local or S3-compatible bucket. | S3/managed object storage with lifecycle policies and CDN for previews. | Multi-bucket/region strategy, CDN, object lifecycle tiers. |
| AI providers | One hosted provider adapter or one local GPU worker. | Provider routing/fallback, cost tracking, GPU queue separation. | Multi-provider marketplace, autoscaled GPU clusters, model cache service. |
| Preview | 2D image preview in browser. | Add cached thumbnails and optimized preview specs. | CDN-backed previews, progressive loading, WebGPU/3D optimization where needed. |
| Observability | Structured logs and job event UI. | Tracing across API/worker/provider calls, alerting on failure/cost spikes. | Full SLOs, tenant dashboards, anomaly detection, audit exports. |

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|----------------|------------|
| Initial API | Letting frontend invent untyped payloads. | Define Pydantic schemas first and mirror/generate TypeScript types. |
| Worker integration | Duplicate jobs after retries or browser resubmits. | Use idempotency keys and stage-level output checks. |
| Artifact storage | Losing relationship between images, prompts, and parent versions. | Create `DesignVersion`, `ModelRun`, and `Artifact` rows in one domain transaction where possible. |
| 2D preview | Treating preview as just an image tag. | Use `PreviewSpec` from the start, even if it has one layer. |
| Export | Blocking HTTP while generating full-size files. | Use export jobs and reuse existing artifacts when possible. |
| 3D preview | Binding API to Three.js internals. | Keep 3D inside `PreviewSpec` and frontend renderer modules. |
| Multi-agent | Adding orchestration before stage contracts are stable. | Convert only proven pipeline stages into agent nodes. |

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Core architecture | HIGH | Project context, UI blueprint, and official docs align around Next.js, FastAPI, Celery, Redis, PostgreSQL, and object storage. |
| Queue/storage split | HIGH | Long-running generation jobs require async execution and durable product state. Celery/Redis docs support task state/retry patterns, but product state should remain in PostgreSQL. |
| Frontend/backend contract | HIGH | FastAPI's Pydantic/OpenAPI model and Next.js app architecture support typed API-backed UI development. |
| 2D-to-3D extensibility | MEDIUM-HIGH | `PreviewSpec` boundary is a standard adapter approach, but final 3D data details depend on selected vehicle models/UV workflow. |
| Multi-agent path | MEDIUM | Pipeline stage boundaries are clear; exact orchestration library should be chosen after v1 stage behavior stabilizes. |
| AI provider integration | MEDIUM | Provider adapter pattern is solid, but model/vendor choice is not yet validated for itasha-specific quality. |

## Open Questions For Later Research

- Which initial image generation provider/model gives acceptable itasha design quality, controllability, and commercial terms?
- What is the minimum viable vehicle template format: static rendered views, layered PSD-like template, UV map, or GLB plus material slots?
- Should v1 auth be anonymous/local project history, email login, or OAuth? UI.png references NextAuth.js, but auth is not central to the first generation loop.
- What export formats matter first: preview PNG only, print-scale PNG, layered PSD-like package, or ZIP with metadata manifest?
- How much copyright/reference-asset policy handling is needed before external users test the MVP?

## Sources

| Source | Confidence | How Used |
|--------|------------|----------|
| Project context: `.planning/PROJECT.md` | HIGH | MVP scope, constraints, seed stack, and product expectations. |
| Seed plan: `init.MD` | HIGH | Agent module list, system flow, frontend layout, risks, and initial technical choices. |
| UI blueprint: `UI.png` | HIGH | Concrete component layout, system architecture sketch, module list, and roadmap hints. |
| Next.js App Router official docs via Context7: https://github.com/vercel/next.js/blob/canary/docs/01-app/index.mdx | HIGH | Supports App Router, Server Components, Suspense, and route handler framing for the web app shell. |
| Next.js migration/data-fetching docs via Context7: https://github.com/vercel/next.js/blob/canary/docs/01-app/02-guides/migrating/app-router-migration.mdx | HIGH | Supports dynamic API-backed data fetching and modern app directory patterns. |
| FastAPI official docs via Context7: https://github.com/fastapi/fastapi/tree/master/docs | HIGH | Supports Pydantic request/response models and OpenAPI-driven API contracts. |
| Celery official docs via Context7: https://docs.celeryq.dev/en/stable/ | HIGH | Supports distributed task queue, task states, retries, result backend behavior, and Redis broker/backend configuration. |

