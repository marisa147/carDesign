# 痛车设计 Agent

痛车设计 Agent is an AI web workbench for turning natural-language itasha design requests into previewable, iterable, and exportable concept designs. Phase 1 focuses only on the foundation: repository boundaries, local runtime expectations, root command names, and validation vocabulary for later implementation plans.

## Phase 1 Foundation

This repository starts as a small monorepo with these intended boundaries:

- `apps/web` for the Next.js workbench shell.
- `services/api` for the FastAPI control-plane service.
- `services/worker` for the Celery work-plane process.
- `packages/contracts` for OpenAPI and generated TypeScript contract artifacts.
- `infra` for local PostgreSQL, Redis, and MinIO service orchestration.

## Commands

Root commands are defined in `package.json` and documented in [docs/development.md](docs/development.md).

- `pnpm infra:up`
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

Phase 1 foundation work does not implement chat, uploads, design generation, preview controls, export, authentication, provider calls, or production deployment handoff.
