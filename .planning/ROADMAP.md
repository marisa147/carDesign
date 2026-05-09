# Roadmap: 痛车设计生成 Agent

## Overview

v1 delivers a complete concept-generation loop before expanding into production handoff or true 3D: a developer-runnable foundation, durable workspaces/jobs/assets, one reliable text-to-2D generation slice, an integrated web workbench, versioned iteration and concept export, itasha-aware template controls, and operational guardrails for provider reliability and cost.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation And Contracts** - Establish the runnable monorepo, local services, validation commands, environment configuration, and typed API contract path.
- [ ] **Phase 2: Durable Data, Jobs, And Assets** - Make workspaces, uploads, rights metadata, job state, artifacts, lineage, and cost records durable before spending on real generation.
- [ ] **Phase 3: First Text-To-2D Generation Slice** - Turn a structured natural-language brief into an asynchronous 2D concept render with stored prompt/provider traceability.
- [ ] **Phase 4: Workbench UI Integration** - Connect chat, parameters, upload, progress, preview, variant history, and future-feature gates to canonical backend state.
- [ ] **Phase 5: Iteration, Feedback, And Concept Export** - Let users revise designs without overwriting prior versions, capture feedback, and export clearly labeled concept files.
- [ ] **Phase 6: Itasha And Template Intelligence** - Add domain-specific itasha controls, deterministic text/logo overlays, warnings, safe-zone overlays, and future 3D-ready preview specs.
- [ ] **Phase 7: Operations And Provider Strategy** - Harden provider configuration, failure visibility, cancellation, quotas, logs, retries, fallback, and rate limits.

## Phase Details

### Phase 1: Foundation And Contracts
**Goal**: Developer and operator can run, configure, and validate the frontend/backend/worker stack with shared typed API contracts.
**Depends on**: Nothing (first phase)
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04
**Success Criteria** (what must be TRUE):
  1. Developer can start the frontend, API, worker, PostgreSQL, Redis, and MinIO locally from documented commands.
  2. Developer can run baseline lint, type-check, and test commands for both frontend and backend.
  3. Frontend code consumes generated TypeScript API contracts from FastAPI/Pydantic OpenAPI schemas.
  4. Operator can configure storage, database, queue, AI providers, CORS, and runtime mode without code changes.
**Plans**: 12 plans
Plans:
- [x] 01-01-PLAN.md — Repo tooling, runtime pins, root commands, and developer command index.
- [x] 01-02-PLAN.md — FastAPI API foundation, typed settings, health endpoint, and OpenAPI export.
- [x] 01-03-PLAN.md — Celery worker foundation, typed settings, health task, and boundary tests.
- [x] 01-04-PLAN.md — Docker Compose local services, env examples, and conditional local smoke checks.
- [x] 01-05-PLAN.md — Contract package scaffold and OpenAPI-first generator configuration.
- [x] 01-06-PLAN.md — Generated OpenAPI/client artifacts and contract drift checking.
- [x] 01-07-PLAN.md — Next.js scaffold and design-system baseline.
- [x] 01-08-PLAN.md — Web foundation shell, generated health-client integration, and tests.
- [x] 01-09-PLAN.md — Aggregate validation runner and final developer/operator docs.
- [x] 01-10-PLAN.md — Gap closure: contracts test command and root validation wiring.
- [ ] 01-11-PLAN.md — Gap closure: service env-file loading and provider env-name alignment.
- [ ] 01-12-PLAN.md — Gap closure: truthful health statuses, smoke failures, and contract refresh.
**UI hint**: yes
**Verification**: Gaps found on 2026-05-09. Gap-closure plans 01-10 through 01-12 are ready. See `.planning/phases/01-foundation-and-contracts/01-VERIFICATION.md`.

### Phase 2: Durable Data, Jobs, And Assets
**Goal**: User workspaces, uploaded assets, generation jobs, events, artifacts, versions, feedback, exports, and costs survive refreshes, retries, and worker restarts.
**Depends on**: Phase 1
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, DATA-06, DATA-07
**Success Criteria** (what must be TRUE):
  1. User can create or resume a design workspace and see conversation history preserved.
  2. User can upload reference images, logos, car photos, or inspiration assets with validation, thumbnails, metadata, and required rights/source records.
  3. User can refresh the browser and still see current generation job status from durable state.
  4. System preserves messages, structured briefs, jobs, events, versions, artifacts, model runs, feedback, and exports in PostgreSQL/object storage.
  5. Retryable or duplicate job requests use idempotency keys and record estimated/actual provider costs where available.
**Plans**: TBD

### Phase 3: First Text-To-2D Generation Slice
**Goal**: User can submit a natural-language pain-car brief and receive at least one stored 2D concept render through an asynchronous provider-backed worker.
**Depends on**: Phase 2
**Requirements**: GEN-01, GEN-02, GEN-03, GEN-04, GEN-05, GEN-06, GEN-07
**Success Criteria** (what must be TRUE):
  1. User can describe vehicle/template, character/theme, style, palette, text, coverage, and references in natural language.
  2. User can review, edit, and reuse the structured design brief before generation.
  3. User can select a supported vehicle template and view, submit an asynchronous generation job, and receive at least one 2D concept render.
  4. Generated output is stored as an immutable artifact linked to a design version with exact prompt, parameters, provider, model, and input assets.
  5. User can see clear failure messages and retry eligible failed generation jobs without losing the original brief.
**Plans**: TBD

### Phase 4: Workbench UI Integration
**Goal**: User can operate the end-to-end design workbench through chat, parameters, upload, progress, preview, history, and explicit v2 feature gates.
**Depends on**: Phase 3
**Requirements**: UI-01, UI-02, UI-03, UI-04, UI-05, UI-06, UI-07
**Success Criteria** (what must be TRUE):
  1. User can submit design requests, view assistant/system feedback, and issue follow-up commands in a GPT-style chat panel.
  2. User can inspect and edit structured design parameters while uploading and previewing reference assets from the workbench.
  3. User can see queued, running, succeeded, failed, and recent event states for generation jobs.
  4. User can inspect a selected 2D design with zoom, pan, thumbnail history, and supported view switching.
  5. User can switch generated variants and historical versions while true 3D, print-ready export, and marketplace capabilities are clearly disabled, experimental, or deferred.
**Plans**: TBD
**UI hint**: yes

### Phase 5: Iteration, Feedback, And Concept Export
**Goal**: User can refine generated designs through versioned child iterations, compare lineage, record feedback, and export concept previews.
**Depends on**: Phase 4
**Requirements**: ITER-01, ITER-02, ITER-03, ITER-04, ITER-05, ITER-06
**Success Criteria** (what must be TRUE):
  1. User can regenerate or request targeted style, palette, text, composition, or coverage changes while preserving the previous version.
  2. User can compare parameter differences and lineage between parent and child design versions.
  3. User can rate, approve, reject, or comment on a generated design version.
  4. User can export a selected concept as PNG or JPG plus a metadata JSON manifest.
  5. Exported output clearly labels itself as a concept preview unless production-ready validation is implemented later.
**Plans**: TBD

### Phase 6: Itasha And Template Intelligence
**Goal**: User can apply itasha-specific design controls and template-aware warnings that make outputs more useful than generic car image generation.
**Depends on**: Phase 5
**Requirements**: QUAL-01, QUAL-02, QUAL-03, QUAL-04, QUAL-05
**Success Criteria** (what must be TRUE):
  1. User can choose itasha-oriented presets or fields for character focus, supporting graphics, racing/JDM cues, typography intent, and color harmony.
  2. User can render exact text strings and uploaded logos through deterministic layers or overlays where possible.
  3. User can see lightweight warnings for low resolution, missing template data, unreadable text risk, risky vehicle zones, or uncertain rights metadata.
  4. User can view panel or safe-zone overlays for supported templates.
  5. Developer can inspect stored preview specification data that supports later 3D preview without changing core design/job APIs.
**Plans**: TBD
**UI hint**: yes

### Phase 7: Operations And Provider Strategy
**Goal**: Operator can keep generation reliable, observable, configurable, cancellable, and cost-controlled as users iterate.
**Depends on**: Phase 6
**Requirements**: OPS-01, OPS-02, OPS-03, OPS-04, OPS-05, OPS-06
**Success Criteria** (what must be TRUE):
  1. Operator can inspect provider health, configured capabilities, and recent generation failures.
  2. System classifies provider, validation, storage, queue, and unknown failures separately while emitting structured logs or error events.
  3. Operator can configure provider routing, fallback behavior, retry limits, timeouts, and rate limits without code changes.
  4. User can cancel eligible queued or running jobs and see the final canceled state.
  5. Non-local modes apply quota, credit, or rate-limit controls before expensive provider calls.
**Plans**: TBD

## Research Notes

- Phase 3 planning should validate current image-provider quality, pricing, moderation behavior, and account access for itasha-specific prompts.
- Phase 6 planning should lock the minimum viable vehicle-template format, safe-zone data, text/logo overlay path, and warning strategy.
- Phase 7 planning should re-check provider capabilities and cost controls because model availability and provider terms change over time.

## Future Notes

v2+ scope remains deferred unless explicitly promoted into a later milestone:
- Production handoff: layered source packages, print preflight, PDF/PSD/AI-style handoff, installer notes, scale, bleed, DPI, and color workflow.
- True 3D preview: verified vehicle models, UV/material slots, camera presets, material finish simulation, and screenshot/export consistency tests.
- Advanced generation and orchestration: masks, inpainting, ControlNet/IP-Adapter-style inputs, multi-view consistency, and multi-agent orchestration only after typed pipeline artifacts are proven.
- Business and community: quote/order/payment flows, collaborator sharing, moderated galleries, remixing, and broad licensed template/asset libraries.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation And Contracts | 10/12 | Gap Execution In Progress | - |
| 2. Durable Data, Jobs, And Assets | 0/TBD | Not started | - |
| 3. First Text-To-2D Generation Slice | 0/TBD | Not started | - |
| 4. Workbench UI Integration | 0/TBD | Not started | - |
| 5. Iteration, Feedback, And Concept Export | 0/TBD | Not started | - |
| 6. Itasha And Template Intelligence | 0/TBD | Not started | - |
| 7. Operations And Provider Strategy | 0/TBD | Not started | - |
