# Local Infrastructure

`infra/compose.yml` runs the Phase 1 data-plane dependencies for local development:

| Service | Image | Default URL / Port | Healthcheck |
| ------- | ----- | ------------------ | ----------- |
| PostgreSQL | `postgres:18-alpine` | `localhost:${POSTGRES_PORT:-5432}` | `pg_isready` |
| Redis | `redis:8-alpine` | `localhost:${REDIS_PORT:-6379}` | `redis-cli ping` |
| MinIO | `quay.io/minio/minio:RELEASE.2025-04-22T22-12-26Z` | API `localhost:${MINIO_API_PORT:-9000}`, console `localhost:${MINIO_CONSOLE_PORT:-9001}` | `/minio/health/live` |

All published ports bind to `127.0.0.1` and all credentials come from `.env.example`.
Those defaults are intentionally local-only examples, not production secrets or a
deployment hardening guide.

## Commands

Start the local services:

```powershell
pnpm infra:up
```

Run the local smoke checks after the services are healthy:

```powershell
pnpm smoke:local
```

Stop the local services:

```powershell
pnpm infra:down
```

## Docker Prerequisite

The sandbox may have the Docker CLI without access to the Docker daemon. Before
marking FOUND-01 complete on a host machine, enable Docker Desktop or Docker
Engine and run:

```powershell
pnpm infra:up
pnpm smoke:local
pnpm infra:down
```

If `docker info` fails, start Docker Desktop or the Docker daemon first, then
rerun the same commands.

## Boundaries

- Application processes run locally through `pnpm dev:web`, `pnpm dev:api`, and
  `pnpm dev:worker`; Compose does not start app containers in Phase 1.
- Production object storage selection, bucket policies, TLS, credentials,
  backups, network isolation, and managed database/Redis hardening are deferred
  to later operations work.
- AI provider credentials are placeholders only and are not called by these
  services.
