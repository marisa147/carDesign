# Phase 1 Plan 04 User Setup

## Required Host Setup

Docker Desktop or Docker Engine must be running on the host before the local
PostgreSQL, Redis, and MinIO smoke path can prove FOUND-01 end to end.

The sandbox used for this execution can run static Compose validation, but
`docker info` cannot reach a daemon here. Complete this host check before
marking the local infrastructure runtime path fully verified:

```powershell
docker info
pnpm infra:up
pnpm smoke:local
pnpm infra:down
```

Expected result:

- `docker info` exits 0.
- `pnpm infra:up` starts PostgreSQL, Redis, and MinIO from `infra/compose.yml`.
- `pnpm smoke:local` reports PostgreSQL, Redis, and MinIO checks passed.
- `pnpm infra:down` stops the local services.

## Local Configuration Notes

- `.env.example` contains local-only defaults for ports, database, Redis, MinIO,
  CORS, runtime mode, API base URL, and provider key placeholders.
- Real `.env` files are ignored and must not be committed.
- Provider key values can stay blank in `RUNTIME_MODE=local`; Phase 1 does not
  call AI providers.
- If host ports `5432`, `6379`, `9000`, or `9001` are already in use, set local
  overrides in an ignored `.env` file before starting Compose.
