# 痛车设计 Agent

痛车设计 Agent is an AI web workbench for turning natural-language itasha design requests into previewable, iterable, and exportable concept designs.

Phase 1 focuses only on the foundation: monorepo boundaries, local infrastructure, API/worker boot paths, generated API contracts, environment examples, validation commands, and a minimal web shell. It does not implement chat, uploads, design generation, preview controls, export, authentication, provider calls, or production deployment.

`init.MD` and `UI.png` are seed references for the product direction and are not modified by Phase 1.

## Repository Layout

| Path | Purpose |
| ---- | ------- |
| `apps/web` | Next.js foundation shell. |
| `services/api` | FastAPI control-plane service. |
| `services/worker` | Celery work-plane process. |
| `packages/contracts` | OpenAPI and generated TypeScript contracts. |
| `infra` | Local PostgreSQL, Redis, and MinIO Compose services. |
| `docs/development.md` | Full Phase 1 developer runbook. |

## Quickstart

Install prerequisites from `.node-version`, `.python-version`, and `package.json`, then run:

```powershell
pnpm install
cd services/api
uv sync --dev
cd ../worker
uv sync --dev
cd ../..
pnpm contracts:generate
pnpm validate
pnpm infra:up
pnpm smoke:local
pnpm dev:api
pnpm dev:worker
pnpm dev:web
```

Use separate terminals for `pnpm dev:api`, `pnpm dev:worker`, and `pnpm dev:web`.

## Core Commands

- `pnpm infra:up`
- `pnpm infra:down`
- `pnpm dev:api`
- `pnpm dev:worker`
- `pnpm dev:web`
- `pnpm contracts:generate`
- `pnpm contracts:check`
- `pnpm lint`
- `pnpm typecheck`
- `pnpm test`
- `pnpm smoke:local`
- `pnpm validate`

See [docs/development.md](docs/development.md) for environment setup, command details, requirement coverage, and troubleshooting for blocked host prerequisites such as missing `uv`, Node/Corepack profile `EPERM`, and Docker daemon availability. If `pnpm` cannot start, run `node scripts/check-host-prereqs.mjs` from the repository root for a direct prerequisite report.
