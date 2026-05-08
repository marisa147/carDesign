# Development Guide

This guide documents the Phase 1 foundation command surface. Some command targets are filled by later Phase 1 plans, but the root command names are stable from Plan 01-01 onward.

## Prerequisites

Install the repo-visible runtime baselines before running the stack:

| Tool | Version | Source In Repo |
| ---- | ------- | -------------- |
| Node.js | 24.15.0 | `.node-version` |
| pnpm | 11.0.8 | `package.json` `packageManager` |
| Python | 3.13.13 | `.python-version` |
| uv | Current host install | Python service commands |
| Docker Compose | Current host install | Local PostgreSQL, Redis, and MinIO |

Docker Compose defaults and example credentials are for local development only. They are not a production deployment path.

## Repository Layout

| Path | Owner | Purpose |
| ---- | ----- | ------- |
| `apps/web` | Product plane | Next.js workbench shell and generated-client consumption. |
| `services/api` | Control plane | FastAPI settings, health API, and OpenAPI export. |
| `services/worker` | Work plane | Celery worker entrypoint and queue-facing tasks. |
| `packages/contracts` | Shared contracts | OpenAPI files and generated TypeScript client artifacts. |
| `infra` | Data-plane support | Local PostgreSQL, Redis, and MinIO orchestration. |
| `docs` | Project docs | Developer workflow and troubleshooting notes. |

Python services are managed with `uv` and are not pnpm workspace packages.

## Root Commands

| Command | Delegates To | Purpose |
| ------- | ------------ | ------- |
| `pnpm infra:up` | `docker compose --env-file .env.example -f infra/compose.yml up -d` | Start local infrastructure services. |
| `pnpm infra:down` | `docker compose --env-file .env.example -f infra/compose.yml down` | Stop local infrastructure services. |
| `pnpm dev:api` | `cd services/api && uv run uvicorn ...` | Run the FastAPI service locally. |
| `pnpm dev:worker` | `cd services/worker && uv run celery ...` | Run the Celery worker locally. |
| `pnpm dev:web` | `pnpm --filter @caragent/web dev` | Run the Next.js web shell locally. |
| `pnpm contracts:generate` | `pnpm --filter @caragent/contracts generate` | Refresh OpenAPI and generated TypeScript artifacts. |
| `pnpm contracts:check` | `pnpm --filter @caragent/contracts check` | Check generated contracts for drift. |
| `pnpm lint` | Web, contracts, API, and worker lint commands | Run baseline lint checks. |
| `pnpm typecheck` | Web, contracts, API, and worker type checks | Run baseline type checks. |
| `pnpm test` | Web, contracts, API, and worker test commands | Run baseline tests. |
| `pnpm smoke:local` | Web, contracts, API, and worker smoke commands | Run local stack smoke checks. |
| `pnpm validate` | `lint`, `typecheck`, `test`, `contracts:check`, `smoke:local` | Run the aggregate validation surface. |

Root commands are convenience wrappers. Service-specific commands remain independently runnable from their owning directories.

## Local Services

Local PostgreSQL, Redis, and MinIO are owned by Docker Compose under `infra/compose.yml`.

Use:

```powershell
pnpm infra:up
pnpm smoke:local
pnpm infra:down
```

The Compose environment file is `.env.example`. Real `.env` files are ignored and must stay outside source control.

## API And Worker

The API and worker are separate runtime boundaries:

- API commands run from `services/api` through `uv`.
- Worker commands run from `services/worker` through `uv`.
- The worker must not import FastAPI routers.
- Neither service should call AI providers during Phase 1.

Use:

```powershell
pnpm dev:api
pnpm dev:worker
```

## Contracts

FastAPI and Pydantic schemas are the source of truth for API contracts. Contract artifacts live under `packages/contracts`.

Use:

```powershell
pnpm contracts:generate
pnpm contracts:check
```

`contracts:check` is reserved as the drift gate that later plans wire into generated OpenAPI and TypeScript artifacts.

## Web Shell

The web app is owned by `apps/web` and runs through the pnpm workspace filter:

```powershell
pnpm dev:web
```

Phase 1 may provide a minimal foundation shell only. It does not implement chat, upload, design generation, 2D or 3D preview controls, export, authentication, marketplace, or provider-call workflows.

## Validation

Run focused checks while working:

```powershell
pnpm lint
pnpm typecheck
pnpm test
pnpm smoke:local
```

Run the full local validation surface before handing off work:

```powershell
pnpm validate
```

If dependencies are not installed yet, install the prerequisite runtimes first, then run each command again from the repository root.

## Security Notes

- Commit `.env.example` files only. Real `.env`, `.env.local`, service env files, keys, and certificates are ignored.
- Local Docker Compose credentials and ports are for developer machines only.
- Phase 1 does not define a production deployment handoff.
- AI provider key entries may appear in later example config, but Phase 1 must not exercise provider calls.
- Root scripts reserve contract-generation and drift-check command names so later plans can enforce generated-client integrity.

## Troubleshooting

| Symptom | Check |
| ------- | ----- |
| `pnpm` uses the wrong version | Confirm Node 24.15.0 is active and use the package-manager pin in `package.json`. |
| Python commands fail | Confirm Python 3.13.13 and `uv` are available, then rerun from the service directory or root wrapper. |
| Docker smoke checks fail | Run `docker info` on the host and start Docker Desktop or the Docker daemon before `pnpm infra:up`. |
| Contract commands fail | Confirm `packages/contracts` has been created by the contract scaffold plan, then rerun `pnpm contracts:generate`. |
| API or worker commands fail | Confirm the service scaffold plan has created the matching `services/api` or `services/worker` project. |
