# Phase 1: Foundation And Contracts - Pattern Map

**Mapped:** 2026-05-08  
**Files analyzed:** 9 planned file groups  
**Source analogs found:** 0 / 9  
**Planning analogs found:** 9 / 9

## Pattern Mapping Complete

This is a greenfield repository. The read-only scan found no application source directories (`apps/`, `services/`, `packages/`, `infra/`) and no existing controller, component, service, worker, contract, config, or test implementation to copy.

Pattern assignments therefore use planning artifacts as the closest analogs:

- `.planning/phases/01-foundation-and-contracts/01-CONTEXT.md` for locked boundaries and constraints.
- `.planning/phases/01-foundation-and-contracts/01-RESEARCH.md` for scaffold shape, command surface, contracts, and minimal examples.
- `.planning/phases/01-foundation-and-contracts/01-UI-SPEC.md` for the web shell layout and component rules.
- `.planning/phases/01-foundation-and-contracts/01-VALIDATION.md` for test and validation gates.
- `AGENTS.md` for project stack, four-plane architecture, and repository conventions.

## Existing Codebase Summary

Read-only tree scan:

```text
AGENTS.md
init.MD
UI.png
.planning/**
.git/**
```

Project context checks:

| Check | Result | Pattern Impact |
|-------|--------|----------------|
| `CLAUDE.md` | Not present | No extra project instructions beyond `AGENTS.md`. |
| `.claude/skills/` | Not present | No local skill patterns to load. |
| `.agents/skills/` | Not present | No local skill patterns to load. |
| Application source | Not present | Do not claim source-code analogs. |
| Seed files | `init.MD`, `UI.png` present | Use as reference only; do not modify. |

Relevant existing guidance from `AGENTS.md` lines 50-66:

```markdown
Conventions are not yet established by code. Until the first implementation phase creates project-specific patterns:
- Keep frontend server state in TanStack Query and local workbench UI state in Zustand.
- Treat FastAPI/Pydantic schemas as the API contract source and generate/mirror TypeScript types from OpenAPI.

Use a four-plane architecture:
1. Product plane: Next.js workbench...
2. Control plane: FastAPI service...
3. Work plane: Celery workers...
4. Data plane: PostgreSQL..., MinIO/S3..., Redis...
```

## Planned File Groups

| Planned File Group | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|----------------|---------------|
| `package.json`, `pnpm-workspace.yaml`, `.node-version`, `.python-version`, `.gitignore` | config | batch / command delegation | `01-CONTEXT.md` lines 25-27; `01-VALIDATION.md` lines 65-66 | planning-match |
| `docs/development.md`, optional `README.md` | config / utility | batch / developer workflow | `01-RESEARCH.md` lines 414-419 | planning-match |
| `apps/web/**` | component / hook / provider / test | event-driven UI + request-response health check | `01-UI-SPEC.md` lines 31-43, 66-73, 177-184 | planning-match |
| `services/api/**` | controller / model / config / utility / test | request-response + transform | `01-RESEARCH.md` lines 174-178 and 459-480 | planning-match |
| `services/worker/**` | service / worker / config / test | event-driven / pub-sub / batch | `01-RESEARCH.md` lines 182-185; `AGENTS.md` lines 63-66 | planning-match |
| `packages/contracts/**` | utility / config / generated client | transform / batch | `01-RESEARCH.md` lines 189-193 and 259-304 | planning-match |
| `infra/compose.yml`, `infra/README.md` | config | batch orchestration + request-response health checks | `01-RESEARCH.md` lines 197-202 | planning-match |
| `.env.example`, `apps/web/.env.example`, `services/api/.env.example`, `services/worker/.env.example` | config | file-I/O | `01-CONTEXT.md` lines 44-46; `01-RESEARCH.md` lines 206-209 | planning-match |
| Test configs and tests: `apps/web/vitest.config.ts`, `services/api/tests/**`, `services/worker/tests/**`, contract/smoke checks | test | batch / request-response smoke | `01-VALIDATION.md` lines 20-22, 39-47, 65-72 | planning-match |

## Greenfield Constraints

- No existing source excerpts are available. Executors should scaffold from official tools and the phase research examples, not from invented local patterns.
- Preserve the boundary from `01-CONTEXT.md` lines 19-20: `apps/web`, `services/api`, `services/worker`, `packages/contracts`, and `infra`; worker must not import FastAPI routers; frontend must not import backend internals.
- Do not introduce Turborepo, Nx, Kubernetes, LangGraph, ComfyUI, self-hosted model services, product tables, provider calls, upload flows, generation flows, export flows, or full workbench behavior in Phase 1.
- Commit example environment files only. Real `.env` files and secrets must be ignored.
- Re-verify exact package versions during execution before lockfiles are created; research versions are planning inputs, not permanent truth.
- Do not modify `init.MD` or `UI.png`.

## Closest Analogs

### Root Tooling And Commands

**Planned files:** `package.json`, `pnpm-workspace.yaml`, `.node-version`, `.python-version`, `.gitignore`, root scripts  
**Role / data flow:** config, batch / command delegation  
**Source analog:** none  
**Planning analog:** `01-CONTEXT.md` lines 25-27; `01-VALIDATION.md` lines 65-66; `01-RESEARCH.md` line 414

Pattern to copy:

```markdown
- Use `pnpm` for the frontend workspace and `uv` for Python services.
- Pin runtimes in repo-visible files.
- Prefer root-level convenience commands that delegate to service-specific commands.
- `package.json` and `pnpm-workspace.yaml` provide root validation scripts.
```

Executor should make root commands thin wrappers around service/package commands. Required command families are `dev:web`, `dev:api`, `dev:worker`, `infra:up`, `contracts:generate`, `contracts:check`, `lint`, `typecheck`, `test`, `smoke:local`, and `validate`.

### Monorepo Directory Shape

**Planned directories:** `apps/web`, `services/api`, `services/worker`, `packages/contracts`, `infra`, `docs`  
**Role / data flow:** config / structural boundary, batch  
**Source analog:** none  
**Planning analog:** `01-RESEARCH.md` lines 121-156

Copy this structure as the baseline:

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
      schemas/
      routers/
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
```

### Minimal Web Shell

**Planned files:** `apps/web/**`, shadcn/ui generated files, Tailwind config, `apps/web/vitest.config.ts`, minimal shell tests  
**Role / data flow:** component / hook / provider / test, event-driven UI + request-response health check  
**Source analog:** none  
**Planning analog:** `01-UI-SPEC.md` lines 31-43, 66-73, 177-184; `01-RESEARCH.md` lines 166-170

Layout pattern to copy:

```markdown
Root route `/`: App shell with top bar, compact left rail, and main foundation status region.
Top bar: 56px height, brand text `痛车设计 Agent`, environment badge, and one primary CTA.
Left rail: 280px desktop width; disabled workbench region labels and active `Foundation` item.
Main region: readiness cards for Web, API, Worker, Contracts, and Local Services.
Footer/status strip: 32px desktop height with local mode, API base URL, and contract generation status.
```

Interaction pattern:

```markdown
Primary CTA: `检查堆栈健康` calls the typed API health client or a local mock until the endpoint exists.
Loading: disabled loading state with spinner and `正在检查服务...`.
Error: one inline alert in the main region with recovery context.
Disabled future controls: `aria-disabled="true"` and `后续阶段开放`.
```

Component inventory is limited to official shadcn/ui `button`, `badge`, `card`, `separator`, `tabs`, `alert`, `skeleton`, and `tooltip`. Do not add prompt input, upload button, generate button, export button, canvas controls, or live preview behavior.

### API Foundation

**Planned files:** `services/api/pyproject.toml`, `services/api/src/caragent_api/main.py`, `config.py`, `schemas/**`, `routers/**`, `scripts/export_openapi.py`, `tests/**`, `services/api/.env.example`  
**Role / data flow:** controller / model / config / utility / test, request-response + transform  
**Source analog:** none  
**Planning analog:** `01-RESEARCH.md` lines 174-178 and 459-480

Scaffold pattern:

```markdown
- Scaffold `services/api` as a `uv` Python project exposing `caragent_api.main:app`.
- Use FastAPI and Pydantic models for request/response schemas so OpenAPI is produced from backend code.
- Include a typed `/health` response with API status, runtime mode, version/build placeholder, and dependency status placeholders.
- Use `pydantic-settings` for backend configuration.
- Configure CORS from explicit environment values instead of wildcard defaults.
```

Minimal health contract example from research:

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

Executor should extend this for Phase 1 dependency placeholders (`database`, `redis`, `object_storage`, `worker`, `contracts`) while keeping the endpoint minimal.

### Worker Foundation

**Planned files:** `services/worker/pyproject.toml`, `services/worker/src/caragent_worker/app.py`, `config.py`, `tasks/health.py`, `tests/**`, `services/worker/.env.example`  
**Role / data flow:** service / worker / config / test, event-driven / pub-sub / batch  
**Source analog:** none  
**Planning analog:** `01-RESEARCH.md` lines 182-185; `AGENTS.md` lines 63-66

Pattern to copy:

```markdown
- Scaffold `services/worker` as a separate `uv` Python project or separate package/entrypoint.
- Do not import FastAPI routers from the worker.
- Use Celery with Redis broker configuration to prove worker boot/import and a lightweight health task.
- Do not implement real image generation, prompt planning, provider calls, durable generation jobs, product tables, or artifact persistence in Phase 1.
```

Validation should include import/boot tests. Queue smoke can be optional or conditional on Docker/Redis availability.

### Contract Package

**Planned files:** `packages/contracts/package.json`, `packages/contracts/orval.config.ts`, `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/**`, root contract scripts  
**Role / data flow:** utility / config / generated client, transform / batch  
**Source analog:** none  
**Planning analog:** `01-RESEARCH.md` lines 189-193 and 259-304

Artifact flow to copy:

```text
services/api/src/caragent_api/main.py
  -> app.openapi()
  -> packages/contracts/openapi/openapi.json
  -> packages/contracts/orval.config.ts
  -> packages/contracts/src/generated/*
  -> apps/web imports generated health client/hooks
```

Orval config shape:

```typescript
import { defineConfig } from "orval";

export default defineConfig({
  caragent: {
    input: "./openapi/openapi.json",
    output: {
      target: "./src/generated/client.ts",
      schemas: "./src/generated/model",
      client: "react-query",
    },
  },
});
```

Required contract commands:

```markdown
`uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json`
`pnpm --filter @caragent/contracts generate`
`pnpm contracts:generate`
`pnpm contracts:check`
```

`contracts:check` should regenerate and then fail on changes under `packages/contracts/openapi` or `packages/contracts/src/generated`.

### Infra And Local Services

**Planned files:** `infra/compose.yml`, `infra/README.md`, smoke scripts  
**Role / data flow:** config, batch orchestration + request-response health checks  
**Source analog:** none  
**Planning analog:** `01-RESEARCH.md` lines 197-202

Pattern to copy:

```markdown
- Use Docker Compose for PostgreSQL, Redis, and MinIO local services.
- Use ports `5432`, `6379`, `9000`, and `9001`, interpolated from environment variables.
- Add Compose healthchecks.
- PostgreSQL health should use `pg_isready`.
- Redis health can use `redis-cli ping`.
- MinIO health can use `/minio/health/live`; pin/check the selected image at execution time.
```

Application containers are optional profiles only. The default developer path should run app processes locally and infrastructure through Compose.

### Environment Configuration

**Planned files:** `.env.example`, `apps/web/.env.example`, `services/api/.env.example`, `services/worker/.env.example`, `.gitignore` entries  
**Role / data flow:** config, file-I/O  
**Source analog:** none  
**Planning analog:** `01-CONTEXT.md` lines 44-46; `01-RESEARCH.md` lines 206-209

Pattern to copy:

```markdown
- Commit only example env files.
- Include placeholders for `DATABASE_URL`, `REDIS_URL`, `S3_ENDPOINT_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET`, `CORS_ORIGINS`, `RUNTIME_MODE`, `NEXT_PUBLIC_API_BASE_URL`, and provider key placeholders.
- Do not commit real secrets or test provider credentials.
- Local defaults may be usable from `.env.example`; non-local runtime modes should require explicit values.
```

Provider keys are placeholders only. Do not validate or call AI providers in Phase 1.

### Validation And Tests

**Planned files:** `apps/web/vitest.config.ts`, frontend tests, `services/api/tests/**`, `services/worker/tests/**`, contract check scripts, smoke scripts  
**Role / data flow:** test, batch / request-response smoke  
**Source analog:** none  
**Planning analog:** `01-VALIDATION.md` lines 20-22, 39-47, 65-72; `01-RESEARCH.md` lines 328-354

Validation pattern:

```markdown
Frontend: Vitest + Testing Library.
Backend/worker: pytest + pytest-asyncio.
Contracts: Orval drift check.
Smoke: scripted local checks.
Quick run: `pnpm test && uv run pytest`.
Full suite: `pnpm validate`.
```

Required checks by requirement:

```markdown
FOUND-01: `pnpm infra:up`, `pnpm dev:web`, `pnpm dev:api`, `pnpm dev:worker`, `pnpm smoke:local`
FOUND-02: `pnpm lint`, `pnpm typecheck`, `pnpm test`, `uv run ruff check`, `uv run mypy`, `uv run pytest`
FOUND-03: `pnpm contracts:generate`, `pnpm contracts:check`, frontend test importing generated client
FOUND-04: API config parsing tests and `.env.example` coverage check
```

## Executor Notes

- Treat this file as a greenfield pattern map: there are no local code imports, auth guards, repository classes, UI components, or error wrappers to copy.
- Keep source ownership aligned with `01-RESEARCH.md` lines 430-433: `apps/web` owns shell/client consumption, `services/api` owns settings/health/OpenAPI, `services/worker` owns Celery boot/import, and `packages/contracts` owns OpenAPI/generated TypeScript code.
- Build in the dependency order from `01-RESEARCH.md` lines 414-419: root tooling, API/worker, contracts, infra/smoke, web shell, aggregate validation/docs.
- Any generated files should be reproducible from committed config and scripts. Generated contract artifacts may be committed if the planner/executor chooses that as the drift-check baseline.
- If Docker daemon, `uv`, `pnpm`, or Node/Python pins are unavailable in the sandbox, document the manual prerequisite and keep validation commands deterministic for the host environment.
- Do not expand Phase 1 into durable product schema, real AI generation, upload, chat, preview controls, export, auth, 3D, or provider validation.

## Metadata

**Analog search scope:** repository root, `.planning/phases/01-foundation-and-contracts/**`, `.planning/research/**`, `AGENTS.md`  
**Application files scanned:** 0 source files found  
**Planning files read:** `01-CONTEXT.md`, `01-RESEARCH.md`, `01-UI-SPEC.md`, `01-VALIDATION.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `AGENTS.md`, `.planning/research/ARCHITECTURE.md`, `.planning/research/STACK.md`, `.planning/research/SUMMARY.md`  
**Pattern extraction date:** 2026-05-08
