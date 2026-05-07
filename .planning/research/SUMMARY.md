# Project Research Summary

**Project:** 痛车设计生成 Agent
**Domain:** AI-assisted custom vehicle livery / itasha design generation workbench
**Researched:** 2026-05-07
**Confidence:** MEDIUM-HIGH

## Executive Summary

This product should be built as a wrap-design workflow tool, not a generic image chatbot. The core user loop is conversational brief intake, structured design parameters, asset/reference upload, async image generation, 2D vehicle-template preview, versioned iteration, and concept export. Experts in wrap design do not treat a single generated beauty render as production output; they work around vehicle templates, panel boundaries, safe areas, source assets, revisions, proofs, and print handoff constraints.

The recommended v1 approach is a conventional split web app: Next.js/React workbench, FastAPI control API, Celery workers, PostgreSQL job/artifact ledger, Redis queue/progress layer, and MinIO/S3 object storage. Use hosted image providers first through provider adapters, with OpenAI Images as the primary path and fal/BFL-style providers behind the same interface as fallback or comparison targets. Build typed contracts, durable jobs, immutable artifacts, and provider-run traceability before polishing the UI.

The biggest risks are overpromising print readiness, relying on prompt-only image generation as a layout engine, losing reproducibility across iterations, duplicating expensive async jobs, and mishandling anime character/logo rights. Mitigate these by constraining v1 to concept previews, requiring structured specs and asset rights metadata, storing full generation lineage, making jobs idempotent and observable, rendering exact text/logos as deterministic layers where possible, and deferring true print-ready and 3D claims until template, layer, UV, export, and validation workflows are mature.

## Key Findings

### Recommended Stack

Build v1 as a monorepo with a clear frontend/backend/worker split. The frontend should be a dense interactive workbench; the backend should own typed contracts, validation, auth/session boundaries, job creation, and artifact lookup; workers should own expensive AI/provider/post-processing work; Postgres/object storage should preserve every run and asset needed for iteration and audit.

Use hosted AI image providers before self-hosting diffusion infrastructure. Self-hosted SDXL/FLUX/ComfyUI should stay out of v1 because GPU operations, safety, throughput, model churn, and debugging would dominate the MVP. Preserve an internal provider interface from day one so provider experiments or self-hosting can be added later without rewriting the product model.

**Core technologies:**
- Node.js 24 LTS, pnpm 10.x, Next.js 16 App Router, React 19.2, TypeScript 6.0, Tailwind CSS 4.1, shadcn/ui: frontend workbench, route shell, dense controls, typed UI.
- TanStack Query 5 and Zustand 5: React Query owns server state and polling; Zustand owns local workbench state only.
- Orval 8: generate TypeScript client/hooks from FastAPI OpenAPI instead of hand-maintaining a Python/TS contract boundary.
- react-konva/Konva: 2D vehicle-template preview, layer overlays, transforms, zoom/pan, and export.
- Python 3.13, uv, FastAPI 0.136, Pydantic 2.13, SQLAlchemy 2.0, Alembic, asyncpg: typed API and persistence layer.
- Celery 5.6, Redis 8, PostgreSQL 18, MinIO/S3, Pillow, opencv-python-headless: async jobs, canonical metadata, artifact storage, thumbnails, masks, and export processing.
- OpenAI Images API `gpt-image-2`, OpenAI Responses API, configurable GPT text model, fal/BFL FLUX.2-style adapters: primary generation/editing path plus provider fallback.

Critical version requirements: keep Python on 3.13 rather than 3.14 until dependencies are verified; use current React/Next/Tailwind lines; keep AI model names config-driven because provider availability, verification requirements, moderation behavior, pricing, and account access can change.

### Expected Features

The table stakes converge around a private design workflow: brief, assets, templates, generation, iteration, preview, history, export, and guardrails. The product becomes differentiated when it understands itasha composition and vehicle-wrap constraints, not when it adds generic chat or a broad feature surface.

**Must have for v1:**
- Conversational design brief intake with clarification only for critical missing fields: vehicle/template, coverage, theme/character intent, assets, colors, and text.
- Structured design parameters: vehicle, coverage zones, character count/placement, style preset, palette, typography, finish, negative constraints, and export intent.
- Reference and asset upload with metadata, thumbnails, validation, and user rights assertion.
- One or a few vehicle templates with explicit supported views/zones; do not attempt broad model coverage first.
- Async image generation with visible status, retry/cancel path, failure categories, and durable job records.
- Multi-variant generation where cost allows, with lineage for prompt, provider, model, params, seed if available, inputs, outputs, and parent version.
- 2D preview workspace with zoom/pan, template overlays, view switching for supported panels, thumbnail history, and comparison.
- Iteration controls: regenerate, adjust style/color/text, and create child versions without overwriting prior results.
- Concept export as PNG/JPG plus metadata JSON, with clear "not print-ready" labeling.
- Lightweight quality and risk warnings for resolution, text issues, face/text near panel interruptions, missing template, and asset-rights uncertainty.

**Should have as competitive differentiators:**
- Itasha-aware design director for character focus, supporting graphics, Japanese/romaji copy suggestions, racing/JDM cues, color harmony, and readable layout.
- Panel-aware composition scoring for faces, logos, text, wheel arches, handles, seams, and protected zones.
- Multi-view consistency across side/hood/front/rear once the template model supports it.
- AI critique and comparison using a rubric for visual balance, prompt match, print risk, contrast, text clarity, and theme adherence.
- Rights-aware asset workflow that tracks ownership, license status, commercial clearance, attribution, and user attestations.

**Defer to v2+:**
- Print-ready PDF/PSD/AI handoff packs, production-scale files, bleed/preflight, color-profile workflow, and installer proofing.
- Real 3D preview with UV-mapped vehicle models, material slots, and screenshot/export consistency tests.
- Large vehicle-template library, vehicle-photo-to-outline bootstrap, community gallery/remix, installer marketplace, quote/order/payment flow, and LoRA/training platform.
- Photoshop/Illustrator-style full editor. Build targeted controls and layer primitives first.

### Architecture Approach

Use a four-plane architecture: Next.js product plane, FastAPI control plane, Celery work plane, and PostgreSQL/Redis/MinIO data plane. The central architecture decision is that the job ledger is canonical: Redis and Celery are operational infrastructure, while PostgreSQL stores product state, stage events, artifacts, model runs, versions, and reproducibility data.

**Major components:**
1. Next.js App Shell: routes, authenticated or session-based workspace layout, chat/preview/history/parameter panels, toolbar, export UI.
2. FastAPI API Layer: Pydantic/OpenAPI contracts, validation, conversation/message/job/design/asset/export endpoints, auth/session checks, polling or SSE status.
3. Domain Services: create generation/iteration/export jobs, preserve invariants, attach artifacts, update statuses, own transaction boundaries.
4. Celery Worker Pipeline: parse brief, plan prompt, call provider, postprocess, create thumbnails, build PreviewSpec, summarize results, run evaluations.
5. Provider Adapters: normalize OpenAI/fal/BFL/local-model behavior behind internal generation/editing interfaces.
6. Storage Layer: PostgreSQL repositories for metadata and state; MinIO/S3 object storage for binaries; Redis for broker/progress/rate-limit caches only.
7. Preview Adapter: produce renderer-neutral `PreviewSpec` for 2D now and future Three.js/UV preview later.
8. Observability: structured logs, job events, provider latency/error/cost metrics, audit trails.

Key patterns to follow: OpenAPI-typed frontend client, durable job state machine, append-only job events, immutable artifacts, versioned prompts/params, provider-neutral model runs, idempotency keys for job creation and expensive stages, and pipeline stages before multi-agent orchestration.

### Critical Pitfalls

1. **Prompt-only generation is not a layout engine** - avoid by making structured specs the source of truth and using templates, zones, masks, references, and later layers/control inputs.
2. **Copyright, character IP, trademark, and commercial-use exposure** - avoid by storing asset rights metadata, user attestations, risk flags, and clear concept/export labels.
3. **Pretty images that do not fit vehicle wraps** - avoid by limiting v1 templates, showing panel/safe-zone context, and deferring print-ready claims.
4. **Async failures causing duplicate charges or lost jobs** - avoid by creating durable jobs before dispatch, using idempotency keys, storing artifacts immediately, and exposing retry/cancel/status states.
5. **Loss of reproducibility across iterations** - avoid by storing structured brief, prompt plan, provider/model/seed/params, source asset hashes, masks, outputs, cost, feedback, and parent-child version links.
6. **Preview/export/3D mismatch** - avoid by treating 2D preview as the v1 truth source and using the same stored layers/transforms for preview and export.
7. **Runaway cost and latency** - avoid by adding cost estimates, quotas, draft/final tiers, retry budgets, provider error taxonomy, and retention rules.

## Implications for Roadmap

Based on research, the roadmap should follow dependency order rather than the visual ambition of the UI mockup. The app needs contracts, persistence, queueing, artifacts, and guardrails before a polished AI design surface can be trusted.

### Phase 0: Project Skeleton And Contracts

**Rationale:** Every later feature depends on stable repo shape, environment config, OpenAPI/Pydantic schemas, and local services.
**Delivers:** Monorepo layout, Next.js shell, FastAPI health/API baseline, Docker Compose for Postgres/Redis/MinIO, Alembic baseline, Orval/client generation path, lint/test commands.
**Addresses:** Foundation for brief intake, jobs, assets, preview, history, and export.
**Avoids:** Frontend-invented payloads, type drift, and premature UI work with no backend contract.

### Phase 1: Durable Data, Jobs, Artifacts, And Guardrails

**Rationale:** The system must preserve history, status, assets, rights, and cost before spending on real generation.
**Delivers:** Conversations, messages, design briefs, generation jobs, job events, design versions, artifacts, model/provider run records, asset rights metadata, object storage service, job polling endpoint, mock worker, idempotency keys.
**Addresses:** Project/session persistence, upload metadata, async status, version history, rights gate, cost ledger.
**Avoids:** Lost jobs, external URL rot, duplicate charges, no reproducibility, unsafe asset/export assumptions.

### Phase 2: First Text-To-2D Generation Vertical Slice

**Rationale:** Validate the central value loop with one provider and one/few templates before adding complex controls.
**Delivers:** Structured brief parser, prompt planner, OpenAI image provider adapter, Celery generation task, artifact ingestion, thumbnail creation, design version creation, basic generation failure handling.
**Addresses:** Conversational brief intake, structured params, initial variants, provider traceability, basic retry path.
**Avoids:** Self-hosting complexity, synchronous HTTP generation, frontend provider calls, provider lock-in.

### Phase 3: Workbench UI Integration

**Rationale:** Once jobs and outputs are real, connect the user-facing workbench to canonical state.
**Delivers:** Chat panel, parameter editor, asset uploader, job progress/status UI, 2D Konva preview, history/comparison thumbnails, template selector, coverage selector, disabled/gated future features.
**Addresses:** Table-stakes workbench flow: describe, upload, generate, inspect, compare, and select.
**Avoids:** UX overpromising, fake progress, unreviewed generation spend, and "3D/export/share" affordances that imply unsupported precision.

### Phase 4: Iteration, Export, And Quality Warnings

**Rationale:** Custom wrap workflows are revision-heavy; a single generation is not enough.
**Delivers:** Regenerate/edit/style-change jobs, parent-child version lineage, parameter diffs, export jobs, PNG/JPG plus metadata JSON, quality warnings for low resolution/text/seam risks, feedback capture.
**Addresses:** Iteration controls, version history, export image, lightweight quality checks.
**Avoids:** Overwriting liked options, untraceable tweaks, blocking export requests, and print-ready wording before production validation.

### Phase 5: Itasha And Template Intelligence

**Rationale:** This is where the product becomes domain-specific rather than a generic car image generator.
**Delivers:** Itasha style presets, composition planner, deterministic text/logo overlay path, panel/safe-zone overlays, more template views, masks/control assets, advisory panel-aware scoring, multi-view consistency experiments.
**Addresses:** Itasha-aware design director, local/region editing path, panel-aware scoring, text/logo legibility, better revisions.
**Avoids:** Prompt tweaks masquerading as control, unreadable AI text, faces/logos across risky body interruptions.

### Phase 6: Operational Hardening And Provider Strategy

**Rationale:** Cost, reliability, and provider drift become product risks as soon as users iterate.
**Delivers:** Provider health/capability endpoint, fallback provider adapter, retry policies, cancellation, quota/credits, cost dashboard, rate limits, dead-letter/manual review state, structured provider error taxonomy, Sentry/log/metric coverage.
**Addresses:** Generation status/retry/failure recovery, cost visibility, provider availability.
**Avoids:** Runaway spend, invisible queue failures, single-provider dependency, duplicated provider calls after retries.

### Phase 7: Pro Handoff, 3D, And Multi-Agent Expansion

**Rationale:** These features are valuable only after 2D templates, layers, artifact contracts, and generation quality are stable.
**Delivers:** Layered design model, print preflight, source/print-ready export experiments, collaboration/proofing, Three.js/R3F preview adapter, GLB/UV/material slots, screenshot/export comparison tests, optional LangGraph-style orchestration for proven pipeline stages.
**Addresses:** Print-shop handoff, 3D preview, material simulation, multi-agent evaluation/orchestration.
**Avoids:** Misleading 3D beauty renders, untraceable multi-agent handoffs, and premature production-ready wrap claims.

### Phase Ordering Rationale

- Contracts and persistence come first because chat, history, preview, export, retries, and evaluation all depend on canonical schemas and durable records.
- Queueing comes before real generation because image/edit/upscale/export tasks are slow, failure-prone, and expensive.
- A single-provider vertical slice comes before provider comparison because it validates the product loop and internal adapter contract.
- The workbench UI comes after jobs and artifacts so visible states reflect real backend behavior.
- Iteration and export follow the first UI slice because custom design value depends on revision history and shareable outputs.
- Itasha/template intelligence follows the generic loop because domain controls need stored parameters, assets, versions, and preview specs.
- 3D and multi-agent orchestration are late because they multiply complexity and should reuse proven artifacts, stages, and PreviewSpec contracts.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2:** Provider/model quality, pricing, moderation, commercial terms, and account access for itasha-specific image generation.
- **Phase 5:** Minimum viable vehicle-template format, mask/control strategy, panel-zone scoring, text/logo layer rendering, and multi-view consistency.
- **Phase 7:** Print-shop handoff formats, preflight requirements, UV-mapped vehicle models, Three.js performance, and orchestration library choice.

Phases with standard patterns where research-phase can usually be skipped:
- **Phase 0:** Next.js/FastAPI/Celery/Postgres/Redis/MinIO skeleton and local Docker Compose are well-documented.
- **Phase 1:** Durable job ledger, artifact metadata, idempotency, and object storage follow established backend patterns.
- **Phase 3:** React Query server state, Zustand local state, shadcn/ui controls, and Konva 2D preview are standard implementation work once contracts are known.
- **Phase 6:** Observability, retry policy, quotas, rate limits, and provider health checks are known patterns, though pricing/capability details still need current provider validation.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH for web/backend/storage; MEDIUM for AI provider specifics | Core stack is supported by official docs and common production patterns. Image-provider model availability, pricing, moderation, and account gates change quickly. |
| Features | MEDIUM-HIGH | Current AI wrap tools and professional wrap workflows agree on upload/brief/generate/refine/preview/export. Itasha-specific product evidence is narrower but consistent on composition, panels, high-res art, and rights risk. |
| Architecture | MEDIUM-HIGH | Four-plane architecture and durable job/artifact patterns are strong. 2D-to-3D extensibility is sound but depends on later template/UV decisions. |
| Pitfalls | HIGH for AI/job/IP/cost risks; MEDIUM for exact print specs | Most critical risks are well-supported. Print production requirements vary by vendor, material, printer, and installer. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Initial provider validation:** Run a focused comparison of OpenAI Images, fal/BFL-style FLUX editing, and any local model candidates against itasha prompts, references, text needs, panel constraints, cost, latency, and policy behavior.
- **Initial vehicle-template format:** Decide whether v1 templates are static side/hood canvases, layered design files, rendered views, or early GLB/UV assets. Roadmap should not assume a full library.
- **Auth/session model:** Determine whether v1 starts with anonymous sessions, local prototype storage, email login, or OAuth. The architecture should keep ownership fields from the start either way.
- **Export definition:** Lock what "concept export" means in v1: preview PNG/JPG, metadata JSON, template ID, parameters, rights notes, and explicit non-print-ready language.
- **Rights and policy UX:** Define the asset attestation flow, risky prompt/logo/character flags, and export disclaimers before external testing.
- **Evaluation loop:** Decide which quality warnings can be deterministic in v1 and which need vision-model evaluation after provider outputs exist.

## Sources

### Primary (HIGH Confidence)

- Local research: `.planning/research/STACK.md` - stack, versions, provider interface, infrastructure, key risks.
- Local research: `.planning/research/ARCHITECTURE.md` - four-plane architecture, data model boundaries, queue/storage responsibilities, contracts, build order.
- Local research: `.planning/research/PITFALLS.md` - AI control limits, async reliability, IP/trademark exposure, cost controls, 2D/3D/export mismatch.
- Next.js official docs / Context7 - App Router, route handlers, modern frontend architecture.
- FastAPI official docs / Context7 - Pydantic schemas, OpenAPI contracts, API patterns.
- Celery official docs / Context7 - task queues, retries, state handling, Redis broker patterns.
- OpenAI image generation docs - Images API capabilities, editing flow, model limitations, provider considerations.
- US Copyright Office, USPTO, OpenAI Terms - rights, authorship, trademark, and user responsibility framing.

### Secondary (MEDIUM Confidence)

- Local research: `.planning/research/FEATURES.md` - feature landscape from AI wrap products, wrap-service workflows, itasha design guidance, and print handoff sources.
- WrapStudio AI, CarConceptsAI, WrapsDesigner, 3D Changer - current AI/custom wrap product expectations.
- YesWrap, Alwan Wraps, Gatorprints, 10K Wraps - professional wrap workflow and print-prep constraints.
- fal.ai and Black Forest Labs docs - secondary provider/editing options and FLUX.2-style API direction.

### Tertiary (LOW Confidence)

- None identified as roadmap-driving. Any inference-heavy areas are listed as gaps above and should be validated during phase planning.

---
*Research completed: 2026-05-07*
*Ready for roadmap: yes*
