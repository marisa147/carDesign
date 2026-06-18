# Phase 1: Foundation And Contracts - Context

**Gathered:** 2026-05-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 establishes the runnable project foundation for later product work. It delivers a greenfield monorepo skeleton, local development services, typed API contract generation, environment configuration, and baseline validation commands for the frontend, API, worker, PostgreSQL, Redis, and MinIO stack.

This phase does not implement real design generation, durable product tables, full workbench behavior, 3D preview, export flows, auth flows, or AI provider calls. Those belong to later roadmap phases.
</domain>

<decisions>
## Implementation Decisions

### Repository Shape

- **D-01:** Use a monorepo with clear product/API/worker/infra boundaries: `apps/web` for the Next.js workbench shell, `services/api` for FastAPI, `services/worker` for Celery worker entrypoints, `packages/contracts` for OpenAPI/generated contract artifacts, and `infra` for Docker Compose and infrastructure notes.
- **D-02:** Keep API and worker boundaries separate even if the first implementation shares Python modules internally. The worker must not import FastAPI routers, and the frontend must not import backend internals.
- **D-03:** Do not introduce Turborepo, Nx, Kubernetes, LangGraph, ComfyUI, or self-hosted model services in Phase 1 unless planning proves a direct foundation requirement. The first scaffold should stay small and inspectable.

### Tooling And Runtime Baseline

- **D-04:** Use `pnpm` for the frontend workspace and `uv` for Python services, matching the project research direction. Exact Node, Python, framework, and package versions must be verified from official docs during planning before implementation locks them.
- **D-05:** Pin runtimes in repo-visible files where practical, such as `.node-version` or equivalent for Node and `.python-version` / `uv` Python pinning for Python, so contributors run the same baseline.
- **D-06:** Prefer root-level convenience commands that delegate to service-specific commands, but keep service commands independently runnable. A developer should be able to validate the entire stack from root and also run frontend/backend checks in isolation.

### Local Development Services

- **D-07:** Docker Compose should own infrastructure services for local development: PostgreSQL, Redis, and MinIO. Application processes may run locally by default for faster iteration, with optional Compose profiles for API/worker if the planner finds that useful.
- **D-08:** Use conventional local ports unless unavailable: web on `3000`, API on `8000`, PostgreSQL on `5432`, Redis on `6379`, MinIO API on `9000`, and MinIO console on `9001`. All ports must be configurable through environment variables.
- **D-09:** Add health checks for the API and infrastructure where low-cost. Phase 1 should prove the services start and can be reached; it should not create product database tables beyond an empty or baseline migration setup.

### API Contract Strategy

- **D-10:** FastAPI/Pydantic is the source of truth for API contracts. Generate OpenAPI from the API service and place contract artifacts under `packages/contracts` so the frontend can consume them.
- **D-11:** Generate a typed TypeScript client/hooks for the frontend from OpenAPI, with Orval or an equivalent OpenAPI-first generator preferred over hand-maintained duplicated types.
- **D-12:** Include at least a minimal health endpoint and a minimal contract surface sufficient to prove contract generation. Do not design the full product API in Phase 1.
- **D-13:** Add a validation check that fails when generated frontend contract artifacts drift from the backend OpenAPI source, or document the exact command planner/executor must run to refresh them.

### Environment And Configuration

- **D-14:** Provide committed example environment files only, never real secrets. Include placeholders for database URL, Redis URL, object storage endpoint/keys, CORS origins, provider keys, runtime mode, and API base URL.
- **D-15:** Backend configuration should be typed with `pydantic-settings` or equivalent and should fail clearly when required non-local settings are missing.
- **D-16:** AI provider keys should be accepted as configuration placeholders but not exercised in Phase 1. Real provider validation belongs to Phase 3 planning and implementation.

### Validation And Quality Gates

- **D-17:** Phase 1 must create baseline validation commands for frontend lint/type/test, backend lint/type/test, contract generation/checking, and local stack smoke checks.
- **D-18:** Prefer strict TypeScript and Python lint/type settings from the start, but keep the initial tests small: health endpoint tests, configuration parsing tests, worker boot/import tests, and contract generation checks.
- **D-19:** CI can be included if straightforward, but the hard requirement is documented local commands that work in this workspace. Planning should not block Phase 1 on cloud CI setup.

### Minimal UI Shell

- **D-20:** Because Phase 1 has a UI hint, create only the minimal Next.js application shell needed to prove the stack: route layout, Tailwind/shadcn baseline, and placeholder workbench regions if useful.
- **D-21:** Do not mock the full GPT-style design workbench in Phase 1. Chat, parameter editing, upload UI, progress, 2D preview, variants, and feature gating are Phase 4 responsibilities unless a tiny placeholder is needed for navigation.

### the agent's Discretion

- Exact file names for root helper scripts, test filenames, and health-check implementation details are left to the planner/executor as long as the decisions above and Phase 1 success criteria are met.
- The planner may choose whether API and worker live in one shared Python package with separate entrypoints or separate packages, provided the boundary stays clear.
- The planner may include CI if it is low-friction, but must not let CI setup delay the local runnable foundation.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Definition

- `.planning/PROJECT.md` - Project vision, core value, constraints, and stack direction.
- `.planning/REQUIREMENTS.md` - Phase 1 requirements `FOUND-01` through `FOUND-04` and v1 scope boundaries.
- `.planning/ROADMAP.md` - Phase 1 goal, dependencies, success criteria, UI hint, and later phase boundaries.
- `.planning/STATE.md` - Current project position and deferred items.
- `AGENTS.md` - Project-local guidance, fast-context instructions, architecture summary, and GSD workflow enforcement.

### Research

- `.planning/research/SUMMARY.md` - Roadmap synthesis and foundation build-order guidance.
- `.planning/research/STACK.md` - Recommended stack families, version-verification notes, and installation shape.
- `.planning/research/ARCHITECTURE.md` - Four-plane architecture, component boundaries, data flow, and suggested repo structure.
- `.planning/research/PITFALLS.md` - Risks to avoid while scaffolding, especially premature provider calls, synchronous generation, and untraceable artifacts.

### Seed Inputs

- `init.MD` - Original project plan, feature modules, architecture sketch, UI layout, and prototype phases.
- `UI.png` - Visual blueprint for the eventual workbench; Phase 1 may use it only for app-shell direction, not full UI implementation.
</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- No application source code exists yet. The reusable assets are the seed docs, `UI.png`, and planning artifacts.
- `.planning/research/ARCHITECTURE.md` includes a suggested repo structure that should be treated as the strongest starting point.

### Established Patterns

- Planning artifacts already lock a Web-first Next.js + FastAPI + Celery + PostgreSQL/Redis/MinIO direction.
- GSD workflow is active; future file-changing work should go through phase planning/execution.
- `init.MD` and `UI.png` are currently untracked seed inputs; do not delete or overwrite them.

### Integration Points

- Phase 1 creates the integration points rather than attaching to existing code: frontend-to-API contract generation, API-to-infra configuration, worker-to-queue boot path, and local service orchestration.
- Later phases depend on Phase 1 outputs for durable jobs, generation, UI integration, export, and operations.
</code_context>

<specifics>
## Specific Ideas

- Keep the first scaffold honest: runnable foundation first, not a fake finished product.
- Use the UI reference to guide high-level app shell layout only; full workbench UX waits for Phase 4.
- Preserve a future path to 3D preview through contracts and repo organization, but do not add Three.js/R3F implementation in Phase 1 unless it is only a harmless dependency placeholder.
</specifics>

<deferred>
## Deferred Ideas

- Real AI image generation and provider validation - Phase 3.
- Durable product data model for conversations, jobs, assets, artifacts, versions, and costs - Phase 2.
- GPT-style chat, upload, progress, preview, variant history, and feature gates - Phase 4.
- Iteration, feedback capture, and concept export - Phase 5.
- Itasha presets, overlays, warnings, deterministic text/logo layers, and preview-spec hardening - Phase 6.
- Provider fallback, quotas, cancellation, rate limits, and operational dashboards - Phase 7.
- Production handoff, true 3D, broad template libraries, and multi-agent orchestration - v2+ unless explicitly promoted.
</deferred>

---

*Phase: 01-foundation-and-contracts*
*Context gathered: 2026-05-08*
