# Development Guide

This guide is the Phase 1 runbook for the foundation stack. It documents how to install prerequisites, configure local environment files, run the web/API/worker processes, start local infrastructure, generate contracts, run validation, and troubleshoot host setup failures.

`init.MD` and `UI.png` are seed references for the product direction. Phase 1 does not modify those files and does not implement chat, upload, generation, preview controls, export, authentication, provider calls, or production deployment.

## Prerequisites

Install the repo-visible runtime baselines before running commands:

| Tool | Required Baseline | Repo Source | Used For |
| ---- | ----------------- | ----------- | -------- |
| Node.js | `24.15.0` | `.node-version` | Next.js, scripts, generated contracts |
| pnpm | `11.0.8` | `package.json` `packageManager` | Workspace install and root commands |
| Python | `3.13.13` | `.python-version` | FastAPI and Celery services |
| uv | Host install on `PATH` | service commands | Python dependency sync and checks |
| Docker Desktop or Docker Engine | Host install with daemon running | `infra/compose.yml` | PostgreSQL, Redis, and MinIO |

The current sandbox may have Node and Docker CLIs without access to the required host resources. Treat `uv` not installed, pnpm profile `EPERM`, and Docker daemon unavailable as host prerequisites to fix before expecting the full validation command to pass.

## Install And Sync

From the repository root:

```powershell
pnpm install
cd services/api
uv sync --dev
cd ../worker
uv sync --dev
cd ../..
```

No real secrets are required for local mode. Copy example files only when you need local overrides, and keep real `.env` files ignored:

```powershell
Copy-Item .env.example .env
Copy-Item apps/web/.env.example apps/web/.env.local
Copy-Item services/api/.env.example services/api/.env
Copy-Item services/worker/.env.example services/worker/.env
```

Only `.env.example` files belong in source control. Real secrets and local overrides must stay untracked.

## Repository Layout

| Path | Owner | Purpose |
| ---- | ----- | ------- |
| `apps/web` | Product plane | Next.js foundation shell and generated health-client consumption. |
| `services/api` | Control plane | FastAPI settings, `/health`, CORS policy, and OpenAPI export. |
| `services/worker` | Work plane | Celery entrypoint, Redis broker settings, and worker health task. |
| `packages/contracts` | Shared contracts | OpenAPI artifact and generated TypeScript health client. |
| `infra` | Data-plane support | Local PostgreSQL, Redis, and MinIO Compose services. |
| `scripts` | Validation tooling | Env guard, contract drift guard, smoke runner, and aggregate runner. |
| `docs` | Project docs | Developer workflow and troubleshooting notes. |

Python services are managed by `uv` and are intentionally not pnpm workspace packages.

## Root Commands

| Command | Delegates To | Purpose |
| ------- | ------------ | ------- |
| `pnpm infra:up` | `docker compose --env-file .env.example -f infra/compose.yml up -d` | Start local PostgreSQL, Redis, and MinIO. |
| `pnpm infra:down` | `docker compose --env-file .env.example -f infra/compose.yml down` | Stop local infrastructure services. |
| `pnpm dev:api` | `cd services/api && uv run uvicorn caragent_api.main:app --reload --host 0.0.0.0 --port 8000` | Run the FastAPI API. |
| `pnpm dev:worker` | `cd services/worker && uv run celery -A caragent_worker.app worker --loglevel=INFO` | Run the Celery worker. |
| `pnpm dev:web` | `pnpm --filter @caragent/web dev` | Run the Next.js web shell. |
| `pnpm contracts:generate` | `pnpm --filter @caragent/contracts generate` | Refresh generated TypeScript contracts from OpenAPI. |
| `pnpm contracts:check` | `pnpm --filter @caragent/contracts check` | Regenerate/check contract artifacts for drift. |
| `pnpm lint` | Web, contracts, API, and worker lint commands | Run lint checks. |
| `pnpm typecheck` | Web, contracts, API, and worker type checks | Run type checks. |
| `pnpm test` | Web, contracts, API, and worker tests | Run the root unit-test surface. |
| `pnpm smoke:local` | `node scripts/smoke-local.mjs` | Probe local infrastructure after Compose startup. |
| `pnpm validate` | `node scripts/validate-all.mjs` | Run the required Phase 1 aggregate validation sequence. |

Root commands are convenience wrappers. Service-specific commands remain independently runnable from their owning directories.

## Local Services

Local PostgreSQL, Redis, and MinIO are defined in `infra/compose.yml`; see `infra/README.md` for images, ports, and Docker prerequisites.

```powershell
pnpm infra:up
pnpm smoke:local
pnpm infra:down
```

`pnpm smoke:local` expects Docker services to already be running. To let the smoke script manage Compose when Docker is available:

```powershell
node scripts/smoke-local.mjs --with-compose-if-docker
```

Compose credentials and exposed ports bind to local development defaults only. They are not production deployment guidance.

## API

Run the API:

```powershell
pnpm dev:api
```

Focused API checks:

```powershell
cd services/api
uv run ruff check .
uv run mypy src
uv run pytest -q
uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json
```

API settings cover database URL, Redis URL, S3/MinIO endpoint and bucket settings, CORS origins, runtime mode, and AI provider placeholders. Non-local runtime modes must provide explicit required settings instead of relying on local defaults.

## Worker

Run the worker:

```powershell
pnpm dev:worker
```

Focused worker checks:

```powershell
cd services/worker
uv run ruff check .
uv run mypy src
uv run pytest -q
```

The worker boot path is limited to Celery, Redis broker configuration, and the no-op health task. It does not import FastAPI routers and does not call providers during Phase 1.

## Web

Run the web shell:

```powershell
pnpm dev:web
```

Focused web checks:

```powershell
pnpm --filter @caragent/web lint
pnpm --filter @caragent/web typecheck
pnpm --filter @caragent/web test -- --run
```

Browser-visible configuration is limited to public values such as `NEXT_PUBLIC_API_BASE_URL`. Provider keys, database URLs, Redis URLs, and S3 secrets must not be imported by web code.

## Contracts

FastAPI/Pydantic OpenAPI is the source of truth. The generated TypeScript client lives under `packages/contracts` and is consumed by `apps/web`.

```powershell
pnpm contracts:generate
pnpm contracts:check
pnpm --filter @caragent/contracts test
pnpm --filter @caragent/contracts typecheck
```

If `pnpm contracts:check` fails with contract drift, regenerate contracts and review the changed OpenAPI/client artifacts before committing:

```powershell
pnpm contracts:generate
pnpm contracts:check
```

## Validation

Run the root unit-test surface for web, contracts, API, and worker:

```powershell
pnpm test
```

Run the aggregate Phase 1 gate from the root:

```powershell
pnpm validate
```

The aggregate runner executes:

```text
node scripts/check-env-examples.mjs
pnpm --filter @caragent/web lint
pnpm --filter @caragent/web typecheck
pnpm --filter @caragent/web test -- --run
cd services/api && uv run ruff check .
cd services/api && uv run mypy src
cd services/api && uv run pytest -q
cd services/worker && uv run ruff check .
cd services/worker && uv run mypy src
cd services/worker && uv run pytest -q
pnpm contracts:check
pnpm --filter @caragent/contracts typecheck
```

Run Docker-dependent smoke separately after local services are up:

```powershell
pnpm infra:up
pnpm smoke:local
pnpm infra:down
```

## Requirement Coverage

| Requirement | Covered By | Verification |
| ----------- | ---------- | ------------ |
| FOUND-01 | Local run commands for `pnpm infra:up`, `pnpm dev:api`, `pnpm dev:worker`, `pnpm dev:web`, and `pnpm smoke:local`. | Start Docker services, run the app processes, then run `pnpm smoke:local`. |
| FOUND-02 | Aggregate lint, type-check, and test command surface in `pnpm validate`. | Run `pnpm validate`; focused checks are available for web, contracts, API, and worker. |
| FOUND-03 | FastAPI OpenAPI export, `packages/contracts` generated TypeScript client, `pnpm contracts:generate`, `pnpm contracts:check`, and web generated-client import. | Run `pnpm contracts:generate`, `pnpm contracts:check`, and web tests that exercise the generated health wrapper. |
| FOUND-04 | Root/web/API/worker `.env.example` files plus API and worker settings tests. | Run `node scripts/check-env-examples.mjs`, API config tests, and worker settings tests through `pnpm validate`. |

## Source Coverage

| Source | Coverage In Phase 1 |
| ------ | ------------------- |
| Phase 1 goal | `pnpm validate`, `pnpm smoke:local`, `pnpm dev:web`, `pnpm dev:api`, `pnpm dev:worker`, and `pnpm contracts:check` prove the foundation can be configured, run, validated, and understood from root commands. |
| FOUND-01 | `infra/compose.yml`, `infra/README.md`, `scripts/smoke-local.mjs`, and the documented dev commands cover local web, API, worker, PostgreSQL, Redis, and MinIO run paths. |
| FOUND-02 | `scripts/validate-all.mjs` sequences frontend, contract, API, and worker lint/type/test checks from `pnpm validate`. |
| FOUND-03 | `services/api/src/caragent_api/scripts/export_openapi.py`, `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/client.ts`, `scripts/check-contracts.mjs`, and `apps/web/src/lib/api/health.ts` cover generated API contracts. |
| FOUND-04 | `.env.example`, service env examples, API/worker typed settings, env guard, and config tests cover database, queue, storage, provider placeholders, CORS, and runtime mode without code changes. |
| Research constraints | The monorepo keeps `apps/web`, `services/api`, `services/worker`, `packages/contracts`, and `infra` ownership separate; Python stays `uv`-managed; frontend contracts come from OpenAPI; local infrastructure is Docker Compose; validation is root-runnable. |

| Locked Decision | Shipped Command Or File |
| --------------- | ----------------------- |
| D-01 | Monorepo boundaries are represented by `apps/web`, `services/api`, `services/worker`, `packages/contracts`, and `infra`. |
| D-02 | Worker source stays under `services/worker` and web imports generated contracts through `@caragent/contracts`, not backend internals. |
| D-03 | No Turborepo, Nx, Kubernetes, LangGraph, ComfyUI, self-hosted model service, or provider SDK workflow was added. |
| D-04 | `package.json`, `.node-version`, `.python-version`, and service `pyproject.toml` files document pnpm and uv workflows. |
| D-05 | `.node-version`, `.python-version`, and `packageManager` pin the intended runtime baselines. |
| D-06 | Root scripts delegate to package/service owners while local service commands remain independently runnable. |
| D-07 | `infra/compose.yml` owns PostgreSQL, Redis, and MinIO; app processes run locally by default. |
| D-08 | `.env.example` exposes configurable ports for web, API, PostgreSQL, Redis, and MinIO. |
| D-09 | API `/health`, Compose healthchecks, and smoke checks prove foundation health without product tables. |
| D-10 | FastAPI/Pydantic OpenAPI is exported into `packages/contracts/openapi/openapi.json`. |
| D-11 | `packages/contracts/orval.config.ts` and the generated client define the TypeScript contract path. |
| D-12 | `/health` is the minimal contract surface used by the web shell. |
| D-13 | `pnpm contracts:check` and `scripts/check-contracts.mjs` fail on generated artifact drift. |
| D-14 | Only example env files are committed; real env files remain ignored. |
| D-15 | API settings use typed `pydantic-settings` validation and reject unsafe config. |
| D-16 | AI provider keys are placeholders only and are not exercised in Phase 1. |
| D-17 | `pnpm validate` covers lint, type-check, tests, env guard, contract drift, and service checks. |
| D-18 | Web, API, worker, and contract tests stay small and focused on foundation behavior. |
| D-19 | Local commands and docs are the hard requirement; no CI dependency blocks Phase 1. |
| D-20 | `apps/web` contains the minimal Next.js foundation shell and design-system baseline. |
| D-21 | Full GPT-style workbench behavior remains outside Phase 1. |

Deferred items from `01-CONTEXT.md` remain out of scope for this phase: durable product tables, real AI generation, uploads, chat behavior, preview controls, export, feedback, auth, true 3D, provider routing, quotas, marketplace flows, and production handoff.

## Security Notes

- Commit `.env.example` files only; keep real env files, keys, certificates, and local overrides ignored.
- AI provider keys are configuration placeholders in Phase 1. Provider validation and calls belong to Phase 3.
- Docker Compose credentials and ports are local-only and not a production hardening guide.
- CORS origins are explicit configuration values; wildcard CORS is rejected by API settings tests.
- Contract drift is blocked by `pnpm contracts:check` before frontend/backend API changes are accepted.

## Troubleshooting

| Symptom | What It Means | Fix |
| ------- | ------------- | --- |
| `uv not installed` or `uv` is not recognized | Python service dependency manager is missing from `PATH`. | Install `uv`, open a new shell, run `cd services/api && uv sync --dev`, then `cd ../worker && uv sync --dev`. |
| Node or pnpm fails with `EPERM: operation not permitted, lstat 'C:\Users\25858'` | The sandbox cannot access the Windows user profile path used by Node/pnpm. | Re-run the command on a host shell where pnpm can access the user profile, or fix the Node/npm profile permissions. |
| Docker daemon unavailable | Docker CLI exists but Docker Desktop/Engine is not running or not reachable. | Start Docker Desktop/Engine, confirm `docker info`, then run `pnpm infra:up` and `pnpm smoke:local`. |
| Docker Compose image pull failure | Compose cannot pull PostgreSQL, Redis, or MinIO images. | Check network access, registry access, and the pinned image names in `infra/compose.yml`; retry `pnpm infra:up`. |
| Ports already in use | A local process already owns `3000`, `8000`, `5432`, `6379`, `9000`, or `9001`. | Stop the conflicting process or override the matching port in a local env file before restarting services. |
| Contract drift failure | Generated OpenAPI or TypeScript client artifacts differ from the committed baseline. | Run `pnpm contracts:generate`, review the generated files, then re-run `pnpm contracts:check`. |
| Wildcard CORS rejection | API settings rejected `CORS_ORIGINS=*` in an unsafe mode. | Set explicit origins such as `http://localhost:3000`; do not use wildcard origins with credentials. |
| Missing non-local config | `RUNTIME_MODE` is not `local`, but required URLs, secrets, or provider settings are absent. | Add explicit database, Redis, S3, CORS, and provider config through ignored env files or deployment configuration. |

## Phase Boundary

Phase 1 is complete when the foundation can be configured, validated, and smoke-checked from documented commands. Durable product data, real generation, uploads, full workbench behavior, iteration, exports, true 3D, auth, provider routing, quotas, and production deployment remain deferred to later phases.
