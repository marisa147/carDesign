# Phase 1: Foundation And Contracts - Research

**Researched:** 2026-05-08 [VERIFIED: system current date]
**Domain:** Greenfield monorepo foundation, local development services, FastAPI OpenAPI contracts, generated TypeScript client, and baseline validation architecture. [VERIFIED: 01-CONTEXT.md; VERIFIED: ROADMAP.md]
**Confidence:** HIGH for Phase 1 architecture and contracts; MEDIUM for exact package patches because package versions are fast-moving and must be re-checked during execution. [VERIFIED: .planning/config.json; CITED: npm registry; CITED: PyPI]

<user_constraints>
## User Constraints (from CONTEXT.md)

Source for this copied block: `.planning/phases/01-foundation-and-contracts/01-CONTEXT.md`. [VERIFIED: 01-CONTEXT.md]

### Locked Decisions

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

### Claude's Discretion

- Exact file names for root helper scripts, test filenames, and health-check implementation details are left to the planner/executor as long as the decisions above and Phase 1 success criteria are met.
- The planner may choose whether API and worker live in one shared Python package with separate entrypoints or separate packages, provided the boundary stays clear.
- The planner may include CI if it is low-friction, but must not let CI setup delay the local runnable foundation.

### Deferred Ideas (OUT OF SCOPE)

- Real AI image generation and provider validation - Phase 3.
- Durable product data model for conversations, jobs, assets, artifacts, versions, and costs - Phase 2.
- GPT-style chat, upload, progress, preview, variant history, and feature gates - Phase 4.
- Iteration, feedback capture, and concept export - Phase 5.
- Itasha presets, overlays, warnings, deterministic text/logo layers, and preview-spec hardening - Phase 6.
- Provider fallback, quotas, cancellation, rate limits, and operational dashboards - Phase 7.
- Production handoff, true 3D, broad template libraries, and multi-agent orchestration - v2+ unless explicitly promoted.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| FOUND-01 | Developer can run the frontend, API, worker, PostgreSQL, Redis, and MinIO locally from documented commands. [VERIFIED: REQUIREMENTS.md] | Use a root task surface plus service-specific commands; run app processes locally by default and infra through Docker Compose. [VERIFIED: 01-CONTEXT.md D-06/D-07; CITED: https://docs.docker.com/compose/] |
| FOUND-02 | Developer can validate the project with baseline lint, type-check, and test commands for frontend and backend. [VERIFIED: REQUIREMENTS.md] | Add strict `pnpm` and `uv` commands for lint/type/test, plus smoke and contract commands. [VERIFIED: 01-CONTEXT.md D-17/D-18] |
| FOUND-03 | Frontend and backend share typed API contracts generated from FastAPI/Pydantic OpenAPI schemas. [VERIFIED: REQUIREMENTS.md] | Export FastAPI OpenAPI JSON, store it under `packages/contracts/openapi`, and generate TS client/hooks with Orval. [VERIFIED: 01-CONTEXT.md D-10/D-13; CITED: Context7 /fastapi/fastapi/0.128.0; CITED: Context7 /websites/orval_dev] |
| FOUND-04 | Operator can configure environment settings for storage, database, queue, AI providers, CORS, and runtime mode without code changes. [VERIFIED: REQUIREMENTS.md] | Use committed `.env.example` files, typed backend settings via `pydantic-settings`, and no committed real secrets. [VERIFIED: 01-CONTEXT.md D-14/D-16; CITED: https://pypi.org/project/pydantic-settings/] |
</phase_requirements>

## Executive Summary

Phase 1 should create a small, inspectable monorepo foundation, not a fake product workflow. [VERIFIED: 01-CONTEXT.md D-01/D-03/D-20/D-21] The implementation should scaffold `apps/web`, `services/api`, `services/worker`, `packages/contracts`, and `infra`, then prove local startup, config loading, OpenAPI export, generated TypeScript client usage, and baseline validation commands. [VERIFIED: 01-CONTEXT.md D-01/D-19]

The API contract path is the highest-leverage foundation decision: FastAPI/Pydantic should own schemas, `packages/contracts/openapi/openapi.json` should be generated from the API app, and Orval should generate frontend TypeScript client/hooks consumed by the minimal shell. [VERIFIED: 01-CONTEXT.md D-10/D-13; CITED: Context7 /fastapi/fastapi/0.128.0; CITED: Context7 /websites/orval_dev] The planner should include a contract drift check that fails when generated artifacts differ from the current OpenAPI source. [VERIFIED: 01-CONTEXT.md D-13]

Local infrastructure should be Docker Compose for PostgreSQL, Redis, and MinIO, while API, worker, and web run as local processes by default for faster iteration. [VERIFIED: 01-CONTEXT.md D-07; CITED: https://docs.docker.com/compose/] Docker CLI is installed in this workspace, but the Docker daemon is not accessible from the sandbox, so execution plans need a host-level Docker readiness check before service smoke tests. [VERIFIED: local command `docker --version`; VERIFIED: local command `docker info --format '{{.ServerVersion}}'`]

**Primary recommendation:** Build foundation in four dependent waves: repo/tooling, backend-worker-config, contracts, local services plus validation/UI smoke. [VERIFIED: 01-CONTEXT.md; VERIFIED: ROADMAP.md]

## Project Constraints From AGENTS.md

- Use the planned v1 stack: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, Zustand, react-konva/Konva, lucide-react, FastAPI, Pydantic, SQLAlchemy, Alembic, asyncpg, Celery, PostgreSQL, Redis, and MinIO/S3. [VERIFIED: AGENTS.md]
- Keep frontend server state in TanStack Query and local workbench UI state in Zustand. [VERIFIED: AGENTS.md]
- Treat FastAPI/Pydantic schemas as the API contract source and generate or mirror TypeScript types from OpenAPI. [VERIFIED: AGENTS.md]
- Keep generated images, uploads, masks, previews, thumbnails, and exports in object storage with metadata/object keys in PostgreSQL; Phase 1 only prepares configuration and does not implement product artifact flows. [VERIFIED: AGENTS.md; VERIFIED: 01-CONTEXT.md D-09/D-16]
- Make generation/export jobs asynchronous and durable in later phases; Phase 1 should only prove the Celery worker boot/import path and queue configuration. [VERIFIED: AGENTS.md; VERIFIED: 01-CONTEXT.md D-12/D-16]
- Follow the four-plane architecture: Next.js product plane, FastAPI control plane, Celery work plane, and PostgreSQL/MinIO/Redis data plane. [VERIFIED: AGENTS.md]
- PostgreSQL job rows and job events are the future source of truth, not Celery or Redis result state; Phase 1 should avoid product tables beyond baseline migration setup. [VERIFIED: AGENTS.md; VERIFIED: 01-CONTEXT.md D-09]
- `AGENTS.md` says ace-tool is the primary semantic search tool and fast-context is auxiliary, but no ace-tool MCP is available in this session. [VERIFIED: AGENTS.md; VERIFIED: available tool list]
- No `CLAUDE.md` exists in the working directory, so there are no additional CLAUDE.md directives to include. [VERIFIED: local command `Test-Path .\CLAUDE.md`]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|--------------|----------------|-----------|
| Minimal workbench shell | Browser / Client | Frontend Server | The visible Phase 1 shell is rendered by Next.js/React and only calls a health/contract client. [VERIFIED: 01-UI-SPEC.md; CITED: Context7 /vercel/next.js/v16.2.2] |
| API health and OpenAPI source | API / Backend | Frontend Client | FastAPI owns the `/health` endpoint and OpenAPI schema that the frontend consumes. [VERIFIED: 01-CONTEXT.md D-10/D-12; CITED: Context7 /fastapi/fastapi/0.128.0] |
| Generated TypeScript client | Shared Contract Package | Frontend Client | Orval reads OpenAPI and produces TypeScript client/hooks for frontend use. [VERIFIED: 01-CONTEXT.md D-11/D-13; CITED: Context7 /websites/orval_dev] |
| Worker boot path | Work Plane / Worker | Redis Broker | Celery worker entrypoints prove queue connectivity and import boundaries without real generation tasks. [VERIFIED: 01-CONTEXT.md D-02/D-17; VERIFIED: AGENTS.md] |
| Local infrastructure | Data Plane | Developer CLI | Docker Compose owns PostgreSQL, Redis, and MinIO for local development. [VERIFIED: 01-CONTEXT.md D-07; CITED: https://docs.docker.com/compose/] |
| Environment configuration | API / Backend | Frontend Client, Worker | Backend and worker need typed runtime settings; frontend needs public API base URL state only. [VERIFIED: 01-CONTEXT.md D-14/D-15; CITED: https://pypi.org/project/pydantic-settings/] |

## Technical Approach

### Repo Shape

Use this repository structure as the planning baseline. [VERIFIED: 01-CONTEXT.md D-01; VERIFIED: .planning/research/ARCHITECTURE.md]

```text
apps/
  web/
    src/app/
    src/components/
    src/lib/api/
    src/lib/config/
services/
  api/
    pyproject.toml
    src/caragent_api/
      main.py
      config.py
      scripts/export_openapi.py
    tests/
  worker/
    pyproject.toml
    src/caragent_worker/
      app.py
      config.py
      tasks/health.py
    tests/
packages/
  contracts/
    package.json
    orval.config.ts
    openapi/openapi.json
    src/generated/
infra/
  compose.yml
  README.md
docs/
  development.md
```

- Keep API and worker as separate runtime entrypoints even if a later shared Python package is added. [VERIFIED: 01-CONTEXT.md D-02]
- Do not add Turborepo, Nx, Kubernetes, LangGraph, ComfyUI, self-hosted model services, or provider SDK calls in Phase 1. [VERIFIED: 01-CONTEXT.md D-03/D-16]
- Add root-level commands such as `dev:web`, `dev:api`, `dev:worker`, `infra:up`, `contracts:generate`, `contracts:check`, `lint`, `typecheck`, `test`, `smoke`, and `validate`, while keeping each service command independently runnable. [VERIFIED: 01-CONTEXT.md D-06/D-17]

### Frontend Scaffold

- Scaffold `apps/web` with Next.js App Router, TypeScript, Tailwind CSS, and ESLint. [VERIFIED: 01-CONTEXT.md D-20; CITED: https://nextjs.org/docs/app/api-reference/cli/create-next-app]
- Initialize shadcn/ui from the official registry only and add only `button`, `badge`, `card`, `separator`, `tabs`, `alert`, `skeleton`, and `tooltip` if the shell needs them. [VERIFIED: 01-UI-SPEC.md; CITED: https://ui.shadcn.com/docs/installation/next]
- Keep the `/` route as a minimal foundation shell with top bar, left rail, readiness cards, and status strip. [VERIFIED: 01-UI-SPEC.md]
- The `检查堆栈健康` action should call the generated health client when the API is available and may use a local mock state only until the client is generated. [VERIFIED: 01-UI-SPEC.md; VERIFIED: 01-CONTEXT.md D-12]
- Do not implement chat input, uploads, 2D preview controls, 3D preview, generation, export, or history behavior in Phase 1. [VERIFIED: 01-CONTEXT.md D-21; VERIFIED: 01-UI-SPEC.md]

### Backend API Scaffold

- Scaffold `services/api` as a `uv` Python project exposing `caragent_api.main:app`. [VERIFIED: 01-CONTEXT.md D-04; CITED: https://docs.astral.sh/uv/]
- Use FastAPI and Pydantic models for request/response schemas so OpenAPI is produced from backend code. [VERIFIED: 01-CONTEXT.md D-10; CITED: Context7 /fastapi/fastapi/0.128.0]
- Include a typed `/health` response with at least API status, runtime mode, version/build placeholder, and dependency status placeholders for `database`, `redis`, `object_storage`, `worker`, and `contracts`. [VERIFIED: 01-CONTEXT.md D-12/D-17]
- Use `pydantic-settings` for backend configuration and provide a local mode that loads safe defaults from `.env.example` while failing clearly for missing required non-local settings. [VERIFIED: 01-CONTEXT.md D-14/D-15; CITED: https://pypi.org/project/pydantic-settings/]
- Configure CORS from explicit environment values instead of wildcard defaults. [VERIFIED: 01-CONTEXT.md D-14; CITED: OWASP ASVS sections via https://devguide.owasp.org/en/06-verification/01-guides/03-asvs/]

### Worker Scaffold

- Scaffold `services/worker` as a separate `uv` Python project or as a separate package/entrypoint, but do not import FastAPI routers from the worker. [VERIFIED: 01-CONTEXT.md D-02]
- Use Celery with Redis broker configuration to prove worker boot/import and a lightweight health task. [VERIFIED: AGENTS.md; VERIFIED: 01-CONTEXT.md D-17]
- Do not implement real image generation, prompt planning, provider calls, durable generation jobs, product tables, or artifact persistence in Phase 1. [VERIFIED: 01-CONTEXT.md D-09/D-16; VERIFIED: 01-CONTEXT.md deferred ideas]
- Worker validation should include an import/boot test and, if Docker/Redis is available, a smoke check that can enqueue or inspect a no-op health task. [VERIFIED: 01-CONTEXT.md D-17/D-18]

### Contracts

- Store generated OpenAPI at `packages/contracts/openapi/openapi.json`. [VERIFIED: 01-CONTEXT.md D-10]
- Store generated TypeScript client/hooks under `packages/contracts/src/generated`. [VERIFIED: 01-CONTEXT.md D-11; CITED: Context7 /websites/orval_dev]
- Export OpenAPI from a Python module such as `python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json`. [CITED: Context7 /fastapi/fastapi/0.128.0]
- Generate frontend client/hooks with Orval using `client: 'react-query'`. [CITED: Context7 /websites/orval_dev]
- Make `apps/web` consume contract code only from `packages/contracts`, not copied schema types or backend internals. [VERIFIED: 01-CONTEXT.md D-02/D-10/D-11]

### Infra

- Use Docker Compose for PostgreSQL, Redis, and MinIO local services. [VERIFIED: 01-CONTEXT.md D-07; CITED: https://docs.docker.com/compose/]
- Use conventional ports `5432`, `6379`, `9000`, and `9001`, but interpolate them from environment variables. [VERIFIED: 01-CONTEXT.md D-08]
- Add Compose healthchecks and use `depends_on.condition: service_healthy` only where an app container/profile depends on a service container. [CITED: https://docs.docker.com/compose/how-tos/startup-order/]
- PostgreSQL health should use `pg_isready`. [CITED: https://www.postgresql.org/docs/current/app-pg-isready.html]
- Redis health can use `redis-cli ping` in the official image. [CITED: https://docs.docker.com/compose/gettingstarted/]
- MinIO health can use `/minio/health/live`, but the planner must account for the official Docker Hub image appearing archived with old tags and should pin/check the selected image at execution time. [CITED: https://hub.docker.com/r/minio/minio/tags/; CITED: https://github.com/minio/minio/releases]

### Env And Config

- Commit only example env files such as `.env.example`, `apps/web/.env.example`, `services/api/.env.example`, and `services/worker/.env.example`. [VERIFIED: 01-CONTEXT.md D-14]
- Include placeholders for `DATABASE_URL`, `REDIS_URL`, `S3_ENDPOINT_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET`, `CORS_ORIGINS`, `RUNTIME_MODE`, `NEXT_PUBLIC_API_BASE_URL`, and provider key placeholders. [VERIFIED: 01-CONTEXT.md D-14/D-16]
- Do not commit real secrets or test provider credentials. [VERIFIED: 01-CONTEXT.md D-14/D-16; CITED: https://docs.docker.com/compose/how-tos/use-secrets/]
- Local defaults may be usable from `.env.example`, but non-local runtime modes should require explicit secrets/config values. [VERIFIED: 01-CONTEXT.md D-15; CITED: https://pypi.org/project/pydantic-settings/]

## Architecture Patterns

- Use a four-plane foundation: Next.js product shell, FastAPI control API, Celery work-plane entrypoint, and Docker Compose data-plane services. [VERIFIED: AGENTS.md; VERIFIED: .planning/research/ARCHITECTURE.md]
- Use OpenAPI-first integration: backend schemas produce OpenAPI, Orval produces frontend TypeScript client/hooks, and the web shell imports generated contract code. [VERIFIED: 01-CONTEXT.md D-10/D-13; CITED: Context7 /fastapi/fastapi/0.128.0; CITED: Context7 /websites/orval_dev]
- Use local-first service orchestration: Docker Compose starts infrastructure, while app processes run locally by default. [VERIFIED: 01-CONTEXT.md D-07; CITED: https://docs.docker.com/compose/]
- Use validation as architecture: root commands must delegate to service-specific lint/type/test/contract/smoke commands rather than hiding service ownership. [VERIFIED: 01-CONTEXT.md D-06/D-17]
- Keep future work behind boundaries: Phase 1 may include provider-key placeholders and disabled UI labels, but no provider calls, product job tables, chat, upload, preview, generation, or export workflows. [VERIFIED: 01-CONTEXT.md D-16/D-21; VERIFIED: 01-UI-SPEC.md]

## Standard Stack

| Layer | Standard | Purpose |
|-------|----------|---------|
| Frontend runtime | Node 24 LTS, pnpm 10.x, Next.js 16.x, React 19.2 patched, TypeScript 6.x. [CITED: https://github.com/nodejs/Release; VERIFIED: https://registry.npmjs.org/next/latest; CITED: https://react.dev/versions; VERIFIED: https://registry.npmjs.org/typescript/latest] | Minimal web shell and generated client consumption. [VERIFIED: 01-CONTEXT.md D-20/D-21] |
| Frontend UI/state | Tailwind CSS 4.x, official shadcn/ui, lucide-react, TanStack Query 5.x, optional Zustand 5.x. [CITED: https://tailwindcss.com/docs/guides/nextjs; CITED: https://ui.shadcn.com/docs/installation/next; CITED: https://www.npmjs.com/package/%40tanstack/react-query; CITED: https://www.npmjs.com/package/zustand] | Foundation shell styling, status action, and generated health query state. [VERIFIED: 01-UI-SPEC.md; VERIFIED: AGENTS.md] |
| API runtime | Python 3.13.x, uv, FastAPI 0.136.x, Pydantic 2.13.x, pydantic-settings 2.14.x. [CITED: https://www.python.org/downloads/; CITED: https://pypi.org/pypi/uv; CITED: https://pypi.org/project/fastapi/; CITED: https://pypi.org/project/pydantic/; CITED: https://pypi.org/project/pydantic-settings/] | Health endpoint, typed settings, and OpenAPI source. [VERIFIED: 01-CONTEXT.md D-10/D-15] |
| Worker runtime | Python 3.13.x, uv, Celery 5.6.x, redis-py 7.x. [CITED: https://pypi.org/project/celery/; CITED: https://pypi.org/project/redis/] | Worker boot/import path and Redis broker configuration. [VERIFIED: 01-CONTEXT.md D-02/D-17] |
| Data/local services | PostgreSQL 18.x, Redis 8.x, pinned MinIO-compatible image. [CITED: https://www.postgresql.org/about/press/presskit18/en/; CITED: https://hub.docker.com/_/redis; CITED: https://hub.docker.com/r/minio/minio/tags/] | Local database, broker/cache, and S3-compatible endpoint configuration. [VERIFIED: 01-CONTEXT.md D-07/D-09] |
| Contracts | FastAPI OpenAPI plus Orval React Query client. [VERIFIED: 01-CONTEXT.md D-10/D-13; CITED: Context7 /websites/orval_dev] | Typed API contract sharing between backend and frontend. [VERIFIED: REQUIREMENTS.md FOUND-03] |

## Version And Tooling Recommendations

| Tool / Package | Recommended Family | Current Verification | Planning Guidance |
|----------------|--------------------|----------------------|------------------|
| Node.js | 24 LTS | Node 24 is Active LTS and supported until 2028-04-30. [CITED: https://github.com/nodejs/Release] | Pin with `.node-version`; local workspace has Node `v20.12.0`, which is below the recommended LTS baseline. [VERIFIED: local command `node --version`] |
| pnpm | 10.x | npm package page shows pnpm 10.x as latest/current family. [CITED: https://www.npmjs.com/package/pnpm] | Pin via `packageManager` in root `package.json`; local `pnpm` exists but version command fails in the sandbox due `C:\Users\25858` permission. [VERIFIED: local command `where.exe pnpm`; VERIFIED: local command `pnpm --version`] |
| Next.js | 16.x | npm registry returned `next@16.2.6` and `engines.node >=20.9.0`. [VERIFIED: https://registry.npmjs.org/next/latest] | Use Next 16 App Router; still run `pnpm view next version` or registry check during execution before pinning. [CITED: Context7 /vercel/next.js/v16.2.2] |
| React / React DOM | 19.2.x patched | React docs identify 19.2 as the latest documented version, and React RSC security fixes were backported to 19.2.4. [CITED: https://react.dev/versions; CITED: https://react.dev/blog/2025/12/11/denial-of-service-and-source-code-exposure-in-react-server-components] | Pin latest 19.2 patch available at execution, at minimum 19.2.4 for RSC-related packages. [CITED: React security post] |
| TypeScript | 6.0.x | npm registry returned `typescript@6.0.3`. [VERIFIED: https://registry.npmjs.org/typescript/latest] | Use `strict: true`; pin exact patch in `package.json` and lockfile. [VERIFIED: 01-CONTEXT.md D-18] |
| Tailwind CSS | 4.x | Tailwind official Next.js guide uses Tailwind with `@tailwindcss/postcss` and `@import "tailwindcss"`. [CITED: https://tailwindcss.com/docs/guides/nextjs] | Pin exact patch in the web package; avoid custom theme sprawl beyond UI-SPEC tokens. [VERIFIED: 01-UI-SPEC.md] |
| shadcn/ui CLI | latest official CLI at scaffold time | shadcn/ui official Next docs support `pnpm dlx shadcn@latest init -t next --monorepo` and adding components with `-c apps/web`. [CITED: https://ui.shadcn.com/docs/installation/next] | Use official registry only; commit generated components in `apps/web`. [VERIFIED: 01-UI-SPEC.md] |
| TanStack Query | 5.x | npm package page shows current `@tanstack/react-query` in v5 family. [CITED: https://www.npmjs.com/package/%40tanstack/react-query] | Use only for generated health client/query state in Phase 1. [VERIFIED: AGENTS.md; VERIFIED: 01-UI-SPEC.md] |
| Zustand | 5.x | npm package page shows Zustand 5.x current family. [CITED: https://www.npmjs.com/package/zustand] | Optional for shell-local UI state only; do not store canonical API status outside query cache unless needed. [VERIFIED: AGENTS.md] |
| lucide-react | current | npm package page shows `lucide-react` as the React implementation of Lucide icons. [CITED: https://www.npmjs.com/package/lucide-react] | Use icons in buttons/status indicators per UI-SPEC; pin exact patch in lockfile. [VERIFIED: 01-UI-SPEC.md] |
| Python | 3.13.x | Python.org lists Python 3.13 as bugfix status with 3.13.13 released 2026-04-07. [CITED: https://www.python.org/downloads/] | Pin `.python-version` to Python 3.13.x; local `python` is 3.11.5 and does not match the target. [VERIFIED: local command `python --version`] |
| uv | 0.11.x or current | PyPI shows `uv` 0.11.3 on 2026-04-01. [CITED: https://pypi.org/pypi/uv] | Install/check `uv` before Python scaffolding; local `uv` is missing. [VERIFIED: local command `uv --version`] |
| FastAPI | 0.136.x | PyPI shows FastAPI 0.136.1 on 2026-04-23. [CITED: https://pypi.org/project/fastapi/] | Use `fastapi[standard]` or `uvicorn[standard]` for local API serving; pin exact patch in `uv.lock`. [CITED: https://pypi.org/pypi/fastapi/json] |
| Pydantic | 2.13.x | PyPI shows Pydantic 2.13.4 on 2026-05-06. [CITED: https://pypi.org/project/pydantic/] | Use Pydantic v2 models for OpenAPI and settings compatibility. [CITED: Context7 /fastapi/fastapi/0.128.0] |
| pydantic-settings | 2.14.x | PyPI shows pydantic-settings 2.14.0 on 2026-04-20. [CITED: https://pypi.org/project/pydantic-settings/] | Use for typed config in API and worker. [VERIFIED: 01-CONTEXT.md D-15] |
| SQLAlchemy / Alembic / asyncpg | SQLAlchemy 2.0.x, Alembic 1.18.x, asyncpg 0.31.x | Official/PyPI sources show SQLAlchemy 2.0.49, Alembic 1.18.4, and asyncpg 0.31.0. [CITED: https://docs.sqlalchemy.org/20/intro.html; CITED: https://pypi.org/project/alembic/; CITED: https://pypi.org/pypi/asyncpg] | Include only baseline migration wiring in Phase 1; defer product tables to Phase 2. [VERIFIED: 01-CONTEXT.md D-09] |
| Celery / redis-py | Celery 5.6.x, redis-py 7.x | PyPI shows Celery 5.6.3 and redis-py 7.4.0 as current stable lines. [CITED: https://pypi.org/project/celery/; CITED: https://pypi.org/project/redis/] | Use for worker boot and queue config only in Phase 1. [VERIFIED: 01-CONTEXT.md D-17] |
| PostgreSQL service | 18.x | PostgreSQL official release materials identify PostgreSQL 18 as released 2025-09-25 and current supported 18.x line. [CITED: https://www.postgresql.org/about/press/presskit18/en/] | Pin Docker image to an explicit `postgres:18.x` tag if available during execution. [CITED: Docker Compose docs example uses `postgres:18`] |
| Redis service | 8.x | Docker Hub official Redis image lists Redis 8 tags. [CITED: https://hub.docker.com/_/redis] | Pin `redis:8.x-alpine` or equivalent explicit tag; do not expose Redis beyond local dev. [CITED: https://hub.docker.com/_/redis] |
| MinIO service | pinned local-dev image | Docker Hub `minio/minio` tags page shows recent archived tags ending in 2025, and GitHub release notes mention building container images manually for later security release. [CITED: https://hub.docker.com/r/minio/minio/tags/; CITED: https://github.com/minio/minio/releases] | Keep MinIO for Phase 1 local S3 compatibility per locked decision, but make image selection an executor check and keep production object storage out of scope. [VERIFIED: 01-CONTEXT.md D-07; VERIFIED: 01-CONTEXT.md deferred ideas] |

## Contract Generation Strategy

### Source Of Truth

FastAPI/Pydantic must be the only API schema source in Phase 1. [VERIFIED: 01-CONTEXT.md D-10] FastAPI automatically uses Pydantic models to generate OpenAPI schemas for request and response models. [CITED: Context7 /fastapi/fastapi/0.128.0]

### Artifact Flow

```text
services/api/src/caragent_api/main.py
  -> app.openapi()
  -> packages/contracts/openapi/openapi.json
  -> packages/contracts/orval.config.ts
  -> packages/contracts/src/generated/*
  -> apps/web imports generated health client/hooks
```

This flow keeps the frontend from importing backend internals and keeps generated artifacts in a shared package. [VERIFIED: 01-CONTEXT.md D-02/D-10/D-11]

### Required Commands

| Command | Purpose | Owner |
|---------|---------|-------|
| `uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json` | Export backend OpenAPI from the FastAPI app. [CITED: Context7 /fastapi/fastapi/0.128.0] | `services/api` |
| `pnpm --filter @caragent/contracts generate` | Run Orval against the exported OpenAPI file. [CITED: Context7 /websites/orval_dev] | `packages/contracts` |
| `pnpm contracts:generate` | Root convenience command that delegates OpenAPI export and Orval generation. [VERIFIED: 01-CONTEXT.md D-06/D-13] | repo root |
| `pnpm contracts:check` | Regenerate contracts and fail on a dirty diff in `packages/contracts/openapi` or `packages/contracts/src/generated`. [VERIFIED: 01-CONTEXT.md D-13] | repo root |

### Orval Config Shape

```typescript
import { defineConfig } from "orval";

export default defineConfig({
  caragent: {
    input: "./openapi/openapi.json",
    output: {
      target: "./src/generated/client.ts",
      client: "react-query",
    },
  },
});
```

The `client: "react-query"` setting is documented by Orval for generating TanStack Query hooks. [CITED: Context7 /websites/orval_dev]

### Drift Check

The planner should include a deterministic check that runs contract generation and then verifies no generated files changed. [VERIFIED: 01-CONTEXT.md D-13] A simple implementation is `pnpm contracts:generate` followed by `git diff --exit-code -- packages/contracts/openapi packages/contracts/src/generated`, but the executor must account for this repo's git safe-directory warning. [VERIFIED: local command `git status --short`; VERIFIED: local command `git -c safe.directory=D:/python/carAgent status --short`]

## Local Services Strategy

| Service | Image Family | Port | Healthcheck | Phase 1 Use |
|---------|--------------|------|-------------|-------------|
| PostgreSQL | `postgres:18.x` | `${POSTGRES_PORT:-5432}:5432` | `pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}` [CITED: https://www.postgresql.org/docs/current/app-pg-isready.html] | Prove database connectivity and Alembic baseline only; no durable product tables. [VERIFIED: 01-CONTEXT.md D-09] |
| Redis | `redis:8.x-alpine` | `${REDIS_PORT:-6379}:6379` | `redis-cli ping` [CITED: https://docs.docker.com/compose/gettingstarted/] | Broker/progress-cache configuration for Celery boot smoke only. [VERIFIED: AGENTS.md; VERIFIED: 01-CONTEXT.md D-17] |
| MinIO | pinned local-dev S3-compatible image | `${MINIO_API_PORT:-9000}:9000`, `${MINIO_CONSOLE_PORT:-9001}:9001` | HTTP `GET /minio/health/live` if the selected image includes a suitable client/tooling. [CITED: https://hub.docker.com/r/minio/minio/tags/] | Prove object storage endpoint config and bucket placeholder only; no artifact workflow. [VERIFIED: 01-CONTEXT.md D-14/D-16] |

- Application processes should run locally by default: `pnpm dev:web`, `uv run fastapi dev` or `uv run uvicorn`, and `uv run celery ... worker`. [VERIFIED: 01-CONTEXT.md D-07; CITED: https://pypi.org/pypi/fastapi/json]
- Optional Compose profiles for API/worker are acceptable only if they do not complicate the default local development path. [VERIFIED: 01-CONTEXT.md D-07]
- Use named Docker volumes for local data, and add a documented cleanup command that is clearly marked destructive. [CITED: https://docs.docker.com/compose/]
- Keep all ports configurable through environment variables. [VERIFIED: 01-CONTEXT.md D-08]

## Validation Architecture

Nyquist validation is enabled because `.planning/config.json` sets `workflow.nyquist_validation` to `true`. [VERIFIED: .planning/config.json]

### Test Framework

| Property | Value |
|----------|-------|
| Frontend framework | Vitest plus Testing Library is appropriate for the minimal shell because Phase 1 needs component/unit checks, not browser E2E. [ASSUMED] |
| Backend framework | Pytest with pytest-asyncio for async FastAPI/config tests. [CITED: https://pypi.org/project/pytest/; CITED: https://pypi.org/project/pytest-asyncio/] |
| Contract check | Orval generation plus git diff check. [VERIFIED: 01-CONTEXT.md D-13; CITED: Context7 /websites/orval_dev] |
| Smoke check | Scripted local HTTP checks for web/API plus Docker service health if Docker daemon is available. [VERIFIED: 01-CONTEXT.md D-17; CITED: https://docs.docker.com/compose/how-tos/startup-order/] |

### Phase Requirements To Test Map

| Req ID | Behavior | Test Type | Required Commands |
|--------|----------|-----------|-------------------|
| FOUND-01 | Frontend, API, worker, PostgreSQL, Redis, and MinIO can be started from documented commands. [VERIFIED: REQUIREMENTS.md] | smoke/integration | `pnpm infra:up`, `pnpm dev:web`, `pnpm dev:api`, `pnpm dev:worker`, `pnpm smoke:local` [VERIFIED: 01-CONTEXT.md D-06/D-07/D-17] |
| FOUND-02 | Frontend and backend lint/type/test commands run. [VERIFIED: REQUIREMENTS.md] | static/unit | `pnpm lint`, `pnpm typecheck`, `pnpm test`, `uv run ruff check`, `uv run mypy`, `uv run pytest` [VERIFIED: 01-CONTEXT.md D-17/D-18] |
| FOUND-03 | Frontend consumes generated TS API contracts from FastAPI OpenAPI. [VERIFIED: REQUIREMENTS.md] | contract/unit | `pnpm contracts:generate`, `pnpm contracts:check`, frontend health-card test importing generated client. [VERIFIED: 01-CONTEXT.md D-10/D-13] |
| FOUND-04 | Environment settings configure storage, database, queue, AI provider placeholders, CORS, and runtime mode without code changes. [VERIFIED: REQUIREMENTS.md] | unit/config | API config parsing tests and `.env.example` coverage check. [VERIFIED: 01-CONTEXT.md D-14/D-16] |

### Required Validation Commands

| Command | Expected Scope |
|---------|----------------|
| `pnpm install --frozen-lockfile` | JavaScript dependency reproducibility. [VERIFIED: 01-CONTEXT.md D-05/D-17] |
| `pnpm lint` | Frontend/contracts lint. [VERIFIED: 01-CONTEXT.md D-17] |
| `pnpm typecheck` | TypeScript strict typecheck. [VERIFIED: 01-CONTEXT.md D-18] |
| `pnpm test` | Frontend/contracts unit tests. [VERIFIED: 01-CONTEXT.md D-18] |
| `uv sync --locked` | Python dependency reproducibility. [VERIFIED: 01-CONTEXT.md D-04/D-05] |
| `uv run ruff check .` | Python lint. [CITED: https://pypi.org/pypi/ruff] |
| `uv run mypy src` | Python typecheck. [CITED: https://pypi.org/project/mypy/] |
| `uv run pytest` | Backend/worker unit tests. [CITED: https://pypi.org/project/pytest/] |
| `pnpm contracts:check` | OpenAPI/generated client drift gate. [VERIFIED: 01-CONTEXT.md D-13] |
| `pnpm smoke:local` | API `/health`, web shell response, and local infra reachability. [VERIFIED: 01-CONTEXT.md D-17] |
| `pnpm validate` | Root aggregate command for Phase 1 local gate. [VERIFIED: 01-CONTEXT.md D-06/D-17] |

### Wave 0 Gaps

- No `package.json`, `pnpm-workspace.yaml`, `pyproject.toml`, test config, app source, Docker Compose file, or contract package exists yet. [VERIFIED: local command `rg --files -uu`]
- The planner must create all baseline test infrastructure in Phase 1 rather than assuming any existing tests. [VERIFIED: local command `rg --files -uu`; VERIFIED: 01-CONTEXT.md D-17/D-18]
- Git requires `-c safe.directory=D:/python/carAgent` in this sandbox unless repository ownership is configured outside the sandbox. [VERIFIED: local command `git status --short`; VERIFIED: local command `git -c safe.directory=D:/python/carAgent status --short`]

## Security And Threat Model Inputs

Security enforcement is enabled because `.planning/config.json` sets `workflow.security_enforcement` to `true` and ASVS level `1`. [VERIFIED: .planning/config.json] OWASP ASVS is organized into verification categories such as architecture, authentication, session management, access control, validation, cryptography, error handling/logging, data protection, communications, malicious code, files/resources, API/web service, and configuration. [CITED: https://devguide.owasp.org/en/06-verification/01-guides/03-asvs/]

### Applicable ASVS L1 Categories

| ASVS Category | Applies In Phase 1 | Standard Control |
|---------------|--------------------|------------------|
| V1 Architecture, Design, Threat Modeling | Yes | Document service boundaries and deferred security-sensitive features. [VERIFIED: 01-CONTEXT.md D-01/D-03; CITED: OWASP ASVS] |
| V2 Authentication | No product auth in Phase 1 | Do not add auth placeholders that imply support; leave auth to later explicit planning. [VERIFIED: 01-CONTEXT.md deferred ideas] |
| V3 Session Management | No product sessions in Phase 1 | Do not store secrets or session tokens in the browser shell. [VERIFIED: 01-UI-SPEC.md; CITED: OWASP ASVS] |
| V4 Access Control | Limited | Keep CORS explicit and API surface minimal; no protected product resources exist yet. [VERIFIED: 01-CONTEXT.md D-12/D-14] |
| V5 Validation, Sanitization, Encoding | Yes | Use Pydantic models and typed settings for input/config validation. [VERIFIED: 01-CONTEXT.md D-10/D-15; CITED: Context7 /fastapi/fastapi/0.128.0] |
| V6 Cryptography | Limited | Do not hand-roll crypto; Phase 1 should not implement tokens, signatures, or encryption. [VERIFIED: 01-CONTEXT.md deferred ideas; CITED: OWASP ASVS] |
| V7 Error Handling and Logging | Yes | Health/config errors should be clear but must not leak secret values. [VERIFIED: 01-CONTEXT.md D-14/D-15; CITED: https://docs.docker.com/compose/how-tos/use-secrets/] |
| V8 Data Protection | Yes for config/secrets | Commit examples only; no real secrets. [VERIFIED: 01-CONTEXT.md D-14; CITED: https://docs.docker.com/compose/how-tos/use-secrets/] |
| V9 Communication | Local-only | Local HTTP is acceptable for development, but non-local modes must not be planned without TLS/proxy decisions. [ASSUMED] |
| V13 API and Web Service | Yes | Typed OpenAPI schema, minimal endpoint surface, explicit CORS. [VERIFIED: 01-CONTEXT.md D-10/D-14; CITED: Context7 /fastapi/fastapi/0.128.0] |
| V14 Configuration | Yes | Runtime mode and service credentials come from environment/config, not code changes. [VERIFIED: REQUIREMENTS.md FOUND-04; VERIFIED: 01-CONTEXT.md D-14/D-15] |

### High Severity Threats To Plan Away

| Threat | STRIDE | Why It Matters | Required Mitigation |
|--------|--------|----------------|---------------------|
| Committed secrets in examples or config | Information Disclosure | Phase 1 introduces DB, Redis, S3, CORS, and provider key placeholders. [VERIFIED: 01-CONTEXT.md D-14/D-16] | Commit `.env.example` only, add `.gitignore` for real env files, and include tests/docs that examples are placeholders. [VERIFIED: 01-CONTEXT.md D-14; CITED: https://docs.docker.com/compose/how-tos/use-secrets/] |
| Browser imports backend internals or uses provider keys | Information Disclosure / Elevation | Frontend must not import backend internals and AI provider keys are placeholders only. [VERIFIED: 01-CONTEXT.md D-02/D-16] | Frontend imports generated contracts only and never reads provider key env vars. [VERIFIED: 01-CONTEXT.md D-02/D-11/D-16] |
| Wildcard CORS becomes default | Tampering / Information Disclosure | CORS origins are explicitly listed in Phase 1 configuration requirements. [VERIFIED: 01-CONTEXT.md D-14] | Require `CORS_ORIGINS` parsing and local-only defaults; do not use `"*"` with credentials. [CITED: OWASP ASVS; VERIFIED: 01-CONTEXT.md D-14] |
| Contract drift hides unsafe API changes | Tampering / Repudiation | Phase 1 must fail when generated frontend artifacts drift from backend OpenAPI. [VERIFIED: 01-CONTEXT.md D-13] | Add `contracts:check` as a validation gate. [VERIFIED: 01-CONTEXT.md D-13] |
| Docker services exposed with weak local defaults beyond localhost | Information Disclosure / Tampering | Redis Docker image documentation warns that exposed Redis without password can be reachable if ports are published broadly. [CITED: https://hub.docker.com/_/redis] | Bind for local development only, document non-production defaults, and avoid production handoff in Phase 1. [VERIFIED: 01-CONTEXT.md deferred ideas] |

## Security Domain

Phase 1 security planning should focus on ASVS L1 configuration, API/web-service, validation, data-protection, and error-handling categories because the phase introduces config, local services, OpenAPI, CORS, and a health endpoint but does not introduce authentication, sessions, paid provider calls, uploads, or product data. [VERIFIED: .planning/config.json; VERIFIED: 01-CONTEXT.md D-10/D-17; VERIFIED: 01-CONTEXT.md deferred ideas; CITED: https://devguide.owasp.org/en/06-verification/01-guides/03-asvs/]

## UI Planning Inputs

- The approved Phase 1 UI contract limits the first screen to a foundation shell, not the full workbench. [VERIFIED: 01-UI-SPEC.md]
- Required layout is root route `/` with a 56px top bar, 280px desktop left rail, main foundation status region, and 32px desktop footer/status strip. [VERIFIED: 01-UI-SPEC.md]
- Primary visible action is `检查堆栈健康`; it should enter loading copy `正在检查服务...` and update foundation cards or show one inline alert. [VERIFIED: 01-UI-SPEC.md]
- Use the exact Phase 1 typography sizes, neutral palette, accent `#6D5DF6`, radius cap of 8px, and no gradients/decorative imagery. [VERIFIED: 01-UI-SPEC.md]
- Disabled future regions may be labels or muted panels only, with `aria-disabled="true"` and copy `后续阶段开放`. [VERIFIED: 01-UI-SPEC.md]
- The shell must not include prompt input, upload button, generate button, export button, canvas controls, or live preview interactions. [VERIFIED: 01-UI-SPEC.md]
- Use shadcn official registry components only; third-party registries and remote blocks are blocked for Phase 1. [VERIFIED: 01-UI-SPEC.md; CITED: https://ui.shadcn.com/docs/installation/next]
- Keep cards as individual readiness panels only; do not nest cards or create a marketing landing page. [VERIFIED: 01-UI-SPEC.md]

## Plan Breakdown Recommendation

### Suggested PLAN.md Split

| Plan | Owns | Dependencies | Key Files |
|------|------|--------------|-----------|
| Plan 01-01 - Repo Tooling And Root Commands | Root workspace files, runtime pins, package manager setup, documentation skeleton. [VERIFIED: 01-CONTEXT.md D-01/D-06] | none | `package.json`, `pnpm-workspace.yaml`, `.node-version`, `.python-version`, `.gitignore`, `docs/development.md` |
| Plan 01-02 - API Foundation | FastAPI app, typed settings, health endpoint, OpenAPI export, and API tests. [VERIFIED: 01-CONTEXT.md D-10/D-12/D-15/D-18] | 01-01 | `services/api/**` |
| Plan 01-03 - Worker Foundation | Celery app, typed worker settings, health task, worker tests, and API import boundary checks. [VERIFIED: 01-CONTEXT.md D-02/D-17/D-18] | 01-01 | `services/worker/**` |
| Plan 01-04 - Local Services And Environment Examples | Docker Compose, env examples, service healthchecks, env guard, and conditional smoke scripts. [VERIFIED: 01-CONTEXT.md D-07/D-09/D-14/D-17] | 01-01 | `infra/compose.yml`, `.env.example`, service env examples, smoke scripts |
| Plan 01-05 - Contract Package Scaffold | Contracts package metadata, Orval config, package exports, and artifact directories. [VERIFIED: 01-CONTEXT.md D-10/D-11] | 01-02 | `packages/contracts/package.json`, `packages/contracts/orval.config.ts` |
| Plan 01-06 - Contract Generation And Drift Check | Generated OpenAPI, generated TypeScript client, and drift check script. [VERIFIED: 01-CONTEXT.md D-10/D-13] | 01-05 | `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/client.ts`, `scripts/check-contracts.mjs` |
| Plan 01-07 - Web Scaffold And Design System Baseline | Next.js package, strict frontend tooling, Tailwind/shadcn baseline, and core UI components. [VERIFIED: 01-CONTEXT.md D-20; VERIFIED: 01-UI-SPEC.md] | 01-01 | `apps/web/package.json`, `apps/web/src/app/globals.css`, approved core UI components |
| Plan 01-08 - Web Shell Health Integration And Tests | Phase 1 shell, public env wrapper, generated health client consumption, and UI tests. [VERIFIED: 01-CONTEXT.md D-10/D-13/D-20/D-21; VERIFIED: 01-UI-SPEC.md] | 01-06, 01-07 | `apps/web/src/app/page.tsx`, `apps/web/src/lib/api/health.ts`, `apps/web/src/app/page.test.tsx` |
| Plan 01-09 - Aggregate Validation And Docs | Root `validate`, troubleshooting docs, source coverage, and final local run instructions. [VERIFIED: 01-CONTEXT.md D-06/D-17/D-19] | 01-02, 01-03, 01-04, 01-06, 01-08 | `scripts/validate-all.mjs`, `docs/development.md`, `README.md` |

### Suggested Waves

- **Wave 1:** 01-01. [VERIFIED: dependency reasoning from 01-CONTEXT.md D-01/D-04/D-06]
- **Wave 2:** 01-02, 01-03, and 01-04 in parallel after root commands exist. [VERIFIED: dependency reasoning from 01-CONTEXT.md D-02/D-07/D-10/D-17]
- **Wave 3:** 01-05 and 01-07 in parallel after API/root foundations exist. [VERIFIED: 01-CONTEXT.md D-10/D-20]
- **Wave 4:** 01-06 after the contract package scaffold exists. [VERIFIED: 01-CONTEXT.md D-11/D-13]
- **Wave 5:** 01-08 after generated contracts and the web scaffold exist. [VERIFIED: 01-CONTEXT.md D-11/D-20]
- **Wave 6:** 01-09 after API, worker, local services, contracts, and web shell validation surfaces exist. [VERIFIED: 01-CONTEXT.md D-17/D-19]

### Ownership Boundaries

- `apps/web` owns UI shell and generated-client consumption only. [VERIFIED: 01-CONTEXT.md D-01/D-20/D-21]
- `services/api` owns settings, health endpoint, and OpenAPI export. [VERIFIED: 01-CONTEXT.md D-10/D-15]
- `services/worker` owns Celery entrypoint and health/import smoke only. [VERIFIED: 01-CONTEXT.md D-02/D-17]
- `packages/contracts` owns OpenAPI artifacts and generated TypeScript code. [VERIFIED: 01-CONTEXT.md D-10/D-13]
- `infra` owns Compose infrastructure and local service notes only. [VERIFIED: 01-CONTEXT.md D-07]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| API schema mirroring | Hand-maintained TypeScript interfaces copied from Python models | FastAPI OpenAPI plus Orval generated TypeScript client/hooks. [VERIFIED: 01-CONTEXT.md D-10/D-11; CITED: Context7 /websites/orval_dev] | Avoids type drift at the first frontend/backend boundary. [VERIFIED: 01-CONTEXT.md D-13] |
| Env parsing | Ad hoc `os.environ` reads across modules | Central `pydantic-settings` settings object. [VERIFIED: 01-CONTEXT.md D-15; CITED: https://pypi.org/project/pydantic-settings/] | Gives typed config and clear startup failures. [VERIFIED: 01-CONTEXT.md D-15] |
| Local orchestration | Custom scripts that start databases manually | Docker Compose services with healthchecks. [VERIFIED: 01-CONTEXT.md D-07/D-09; CITED: https://docs.docker.com/compose/how-tos/startup-order/] | Compose provides documented lifecycle and service health behavior. [CITED: https://docs.docker.com/compose/] |
| Worker jobs | FastAPI background tasks for future expensive work | Celery worker entrypoint with Redis broker. [VERIFIED: AGENTS.md; VERIFIED: 01-CONTEXT.md D-17] | The project architecture reserves workers for long-running generation/export work. [VERIFIED: AGENTS.md] |
| UI status | Fake full workbench interactions | Minimal foundation readiness shell. [VERIFIED: 01-UI-SPEC.md] | Prevents Phase 1 from implying unsupported generation/upload/preview/export flows. [VERIFIED: 01-CONTEXT.md D-21] |

## Common Pitfalls

Common pitfalls:

- Letting frontend payloads get invented before backend OpenAPI exists will undermine FOUND-03. [VERIFIED: .planning/research/ARCHITECTURE.md; VERIFIED: 01-CONTEXT.md D-10/D-13]
- Adding product database tables in Phase 1 will blur the boundary with Phase 2. [VERIFIED: 01-CONTEXT.md D-09; VERIFIED: ROADMAP.md]
- Exercising AI provider keys in Phase 1 will move Phase 3 risk into foundation work. [VERIFIED: 01-CONTEXT.md D-16; VERIFIED: 01-CONTEXT.md deferred ideas]
- Building a polished GPT workbench shell in Phase 1 will conflict with the approved UI-SPEC. [VERIFIED: 01-CONTEXT.md D-21; VERIFIED: 01-UI-SPEC.md]
- Assuming Docker works because the CLI exists is unsafe in this workspace because daemon access failed. [VERIFIED: local command `docker --version`; VERIFIED: local command `docker info --format '{{.ServerVersion}}'`]
- Assuming `uv` works is unsafe in this workspace because `uv` is not installed. [VERIFIED: local command `uv --version`]

## Code Examples

### FastAPI Health Contract

```python
from fastapi import FastAPI
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    runtime_mode: str
    api_version: str


app = FastAPI(title="carAgent API")


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok", runtime_mode="local", api_version="0.1.0")
```

FastAPI uses Pydantic request/response models to generate OpenAPI schemas. [CITED: Context7 /fastapi/fastapi/0.128.0]

### Orval React Query Generation

```typescript
import { defineConfig } from "orval";

export default defineConfig({
  caragent: {
    input: "./openapi/openapi.json",
    output: {
      target: "./src/generated/client.ts",
      client: "react-query",
    },
  },
});
```

Orval documents `client: "react-query"` for generating TanStack Query hooks from OpenAPI. [CITED: Context7 /websites/orval_dev]

## Environment Availability

| Dependency | Required By | Available | Version / Status | Fallback |
|------------|-------------|-----------|------------------|----------|
| Node.js | Next.js frontend | Yes, wrong target baseline | `v20.12.0` local. [VERIFIED: local command `node --version`] | Install/pin Node 24 LTS before scaffold. [CITED: https://github.com/nodejs/Release] |
| pnpm | Frontend workspace | Partially | Command exists at `C:\nvm4w\nodejs\pnpm.ps1`, but `pnpm --version` fails due sandbox permission on `C:\Users\25858`. [VERIFIED: local command `Get-Command pnpm`; VERIFIED: local command `pnpm --version`] | Re-run outside sandbox or after Node/npm permission fix; pin in `packageManager`. |
| npm/corepack | pnpm/shadcn bootstrap | Blocked in sandbox | `npm --version` and `corepack --version` fail with EPERM on `C:\Users\25858`. [VERIFIED: local commands] | Use a working Node install or direct pnpm install outside sandbox. |
| Python | API/worker | Yes, wrong target baseline | `Python 3.11.5` local. [VERIFIED: local command `python --version`] | Install Python 3.13 and pin `.python-version`. [CITED: https://www.python.org/downloads/] |
| uv | Python package manager | No | Command not found. [VERIFIED: local command `uv --version`] | Install uv before Python scaffold. [CITED: https://pypi.org/pypi/uv] |
| Docker CLI | Local services | CLI yes, daemon no | Docker CLI `29.2.1`; daemon access denied. [VERIFIED: local command `docker --version`; VERIFIED: local command `docker info --format '{{.ServerVersion}}'`] | Host-level Docker readiness check is required before smoke tests. |
| Docker Compose | Local services | CLI yes | Compose `v5.0.2`; Docker config warning appears. [VERIFIED: local command `docker compose version`] | Same as Docker daemon fallback. |
| PostgreSQL CLI | Optional manual DB check | No | `psql` not found. [VERIFIED: local command `Get-Command psql`] | Use container healthcheck and app smoke instead. |
| redis-cli host binary | Optional manual Redis check | No | `redis-cli` not found on host. [VERIFIED: local command `Get-Command redis-cli`] | Use Redis container healthcheck. |
| MinIO client `mc` | Optional bucket setup | No | `mc` not found on host. [VERIFIED: local command `Get-Command mc`] | Use container entrypoint/init container or API smoke later. |
| Git | Contract drift / commit | Available with repo ownership caveat | Plain `git status` fails dubious ownership; `git -c safe.directory=D:/python/carAgent status --short` works. [VERIFIED: local commands] | Use per-command `-c safe.directory=...` or configure safe directory outside sandbox. |

**Missing dependencies with no fallback:** `uv` and a usable Docker daemon block full Phase 1 validation until installed/enabled. [VERIFIED: local commands]

**Missing dependencies with fallback:** host `psql`, `redis-cli`, and `mc` can be replaced by Compose healthchecks and app-level smoke checks. [VERIFIED: local commands; CITED: Docker Compose docs]

## Open Questions (RESOLVED As Executor Checks)

1. **Exact package patches**
   - What we know: Recommended version families are verified from official docs/registries. [CITED: npm registry; CITED: PyPI; CITED: official docs]
   - What's unclear: Exact latest patches may change before implementation. [VERIFIED: user additional_context]
   - Resolution for planning: Converted into executor checks in plans `01-01`, `01-02`, `01-03`, `01-05`, and `01-07`; executors must re-check package versions through official registries or uv/pnpm resolution before lockfiles are created and record chosen pins in plan summaries. [VERIFIED: 01-CONTEXT.md D-04]

2. **MinIO image selection**
   - What we know: Phase 1 decision locks MinIO/S3-compatible local storage, and Docker Hub `minio/minio` appears archived with old tags. [VERIFIED: 01-CONTEXT.md D-07; CITED: https://hub.docker.com/r/minio/minio/tags/]
   - What's unclear: Which image/tag should be used if the executor wants current security fixes in local dev. [CITED: https://github.com/minio/minio/releases]
   - Resolution for planning: Converted into plan `01-04` Task 2; executor pins a known working local-development MinIO image/tag, validates Compose config, and documents production object storage as outside Phase 1. [VERIFIED: 01-CONTEXT.md deferred ideas]

3. **Docker availability on the host**
   - What we know: Docker CLI exists, but the sandbox cannot connect to the daemon. [VERIFIED: local command `docker --version`; VERIFIED: local command `docker info --format '{{.ServerVersion}}'`]
   - What's unclear: Whether the executor's interactive host can run Docker Desktop/daemon successfully. [VERIFIED: local command failure]
   - Resolution for planning: Converted into plan `01-04` `user_setup` plus Task 3 conditional verification; automated smoke checks run `docker info` first and only run `pnpm infra:up`, `pnpm smoke:local`, and `pnpm infra:down` when the host daemon is available. [VERIFIED: 01-CONTEXT.md D-17]

4. **Frontend unit test runner**
   - What we know: Phase 1 needs small frontend tests, but no test infra exists. [VERIFIED: 01-CONTEXT.md D-18; VERIFIED: local command `rg --files -uu`]
   - What's unclear: Whether the executor prefers Vitest or another Next-compatible runner. [ASSUMED]
   - Resolution for planning: Converted into plans `01-07` and `01-08`; Vitest plus Testing Library is selected for the Phase 1 shell tests. [ASSUMED]

5. **CI inclusion**
   - What we know: CI is allowed if low-friction but local commands are the hard requirement. [VERIFIED: 01-CONTEXT.md D-19]
   - What's unclear: Whether GitHub Actions or another CI target is available. [VERIFIED: 01-CONTEXT.md D-19]
   - Resolution for planning: Converted into plan `01-09`; local `pnpm validate` and documented smoke commands are the hard requirement, and CI is not part of Phase 1 execution unless added outside the critical path. [VERIFIED: 01-CONTEXT.md D-19]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Vitest plus Testing Library is appropriate for the minimal shell. | Validation Architecture | Planner may need to swap frontend test tooling, but Phase 1 validation intent remains unchanged. |
| A2 | Local HTTP is acceptable for development, while non-local modes need TLS/proxy decisions later. | Security And Threat Model Inputs | If non-local deployment is unexpectedly included, security planning must expand before execution. |
| A3 | Vitest is the selected frontend unit test runner for Phase 1. | Open Questions (RESOLVED As Executor Checks) | Low risk because no frontend test infrastructure exists yet. |
| A4 | Research validity windows are 7 days for version/tooling and 30 days for architecture/boundaries. | Metadata | If version churn is faster than expected, executor checks still catch exact pins before implementation. |

## Sources

### Primary (HIGH Confidence)

- `.planning/phases/01-foundation-and-contracts/01-CONTEXT.md` - locked Phase 1 decisions, boundaries, and deferred scope. [VERIFIED: local file]
- `.planning/phases/01-foundation-and-contracts/01-UI-SPEC.md` - approved minimal shell contract. [VERIFIED: local file]
- `.planning/REQUIREMENTS.md` - FOUND-01 through FOUND-04. [VERIFIED: local file]
- `.planning/ROADMAP.md` - Phase 1 goal, success criteria, and boundaries. [VERIFIED: local file]
- `AGENTS.md` - project stack, conventions, architecture, and workflow guidance. [VERIFIED: local file]
- Context7 `/vercel/next.js/v16.2.2` - Next.js App Router/environment docs. [CITED: Context7]
- Context7 `/fastapi/fastapi/0.128.0` - Pydantic/OpenAPI generation and FastAPI model patterns. [CITED: Context7]
- Context7 `/websites/orval_dev` - Orval React Query client generation config. [CITED: Context7]
- Node.js Release Working Group - Node 24 LTS schedule. [CITED: https://github.com/nodejs/Release]
- Python.org downloads - active Python release status. [CITED: https://www.python.org/downloads/]
- Docker Compose docs - Compose lifecycle, healthchecks, service ordering, secrets. [CITED: https://docs.docker.com/compose/]
- OWASP ASVS / Developer Guide - ASVS categories and verification role. [CITED: https://devguide.owasp.org/en/06-verification/01-guides/03-asvs/]

### Secondary (MEDIUM Confidence)

- npm registry/package pages for package families and current versions. [CITED: https://registry.npmjs.org/next/latest; CITED: https://registry.npmjs.org/typescript/latest; CITED: https://www.npmjs.com/package/pnpm]
- PyPI project pages for Python package versions. [CITED: https://pypi.org/project/fastapi/; CITED: https://pypi.org/project/pydantic/; CITED: https://pypi.org/project/celery/]
- Docker Hub image pages for Redis and MinIO tags. [CITED: https://hub.docker.com/_/redis; CITED: https://hub.docker.com/r/minio/minio/tags/]

### Tertiary (LOW Confidence)

- None used as authoritative planning input. [VERIFIED: source review]

## Metadata

**Confidence breakdown:**
- Technical approach: HIGH because Phase 1 decisions and architecture are explicit in local planning artifacts. [VERIFIED: 01-CONTEXT.md; VERIFIED: .planning/research/ARCHITECTURE.md]
- Contract strategy: HIGH because FastAPI OpenAPI and Orval React Query generation are verified through Context7 docs. [CITED: Context7 /fastapi/fastapi/0.128.0; CITED: Context7 /websites/orval_dev]
- Version recommendations: MEDIUM because exact patches are temporally unstable and npm/PyPI checks must be repeated during execution. [VERIFIED: user additional_context; CITED: npm registry; CITED: PyPI]
- Local environment: HIGH for observed tool availability because it was checked directly in the workspace. [VERIFIED: local commands]
- Security inputs: MEDIUM-HIGH because ASVS categories and secret-handling docs are official, but Phase 1 has limited product security surface. [CITED: OWASP ASVS; VERIFIED: 01-CONTEXT.md]

**Research date:** 2026-05-08 [VERIFIED: system current date]
**Valid until:** 2026-05-15 for version/tooling recommendations; 2026-06-07 for architecture and phase-boundary recommendations. [ASSUMED]
