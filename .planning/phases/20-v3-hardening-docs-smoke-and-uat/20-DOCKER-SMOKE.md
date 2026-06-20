# Phase 20 Docker And Local Smoke

**Status:** Passed  
**Date:** 2026-06-20  
**Requirement:** V3-REL-02

## Environment

- Docker Desktop was available through the elevated host shell.
- Docker server: 29.2.1, WSL2 backend.
- Smoke stayed provider-off and used local deterministic generation only.

## Commands And Outcomes

| Command | Result | Notes |
|---------|--------|-------|
| `docker info` | Passed | Non-elevated pipe access was denied, but elevated Docker access was healthy. |
| `corepack pnpm smoke:worker -- --dry-run` | Passed | Worker smoke dry run passed before Docker smoke. |
| `corepack pnpm smoke:local -- --with-compose-if-docker` | Blocked by wrapper environment | The script spawned bare `pnpm infra:up`; the elevated process environment did not expose the pnpm shim. This was a host PATH/shim issue, not a product smoke failure. |
| `corepack pnpm infra:up` | Passed | PostgreSQL, Redis, and MinIO started from `infra/compose.yml`. |
| `corepack pnpm smoke:local` | Passed | PostgreSQL, Redis, MinIO, Alembic migration, Phase 2 durable data smoke, and Phase 3 local deterministic generation smoke passed. |
| `corepack pnpm infra:down` | Passed | Compose services were stopped after smoke. |
| `docker compose --env-file .env.example -f infra/compose.yml ps -a` | Passed | No remaining local infrastructure services after cleanup. |

## Result

The V3 local deterministic stack can be smoke-tested without hosted provider credentials. The only failed path was the helper script's child `pnpm` lookup under an elevated Windows environment; the equivalent Compose-managed smoke steps passed end to end and were cleaned up.

