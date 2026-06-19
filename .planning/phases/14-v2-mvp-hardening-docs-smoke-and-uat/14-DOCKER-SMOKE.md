---
phase: 14-v2-mvp-hardening-docs-smoke-and-uat
artifact: docker-smoke
status: passed
created: 2026-06-19
updated: 2026-06-19
requirements: [V2-REL-02]
---

# Phase 14 Docker Smoke

## Verdict

Passed for the required Docker-backed local smoke and hosted-disabled worker dry-run path on 2026-06-19.

The live API/Celery worker smoke was attempted but is not counted as passed because the orchestration attempt did not produce a successful `pnpm smoke:worker` result. The release evidence remains honest: Docker infrastructure smoke is green, worker dry-run is green, and live worker prerequisites remain documented for an operator-prepared shell.

## Docker Availability

| Check | Result | Notes |
|-------|--------|-------|
| `docker info` | pass | Docker Desktop server `29.2.1`, WSL2 Linux engine, 16 CPUs, 14.99 GiB memory. |

## Docker-Backed Local Smoke

| Command | Result | Evidence |
|---------|--------|----------|
| `corepack pnpm infra:up` | pass | Created/started PostgreSQL, Redis, and MinIO containers under `caragent-local_default`. |
| `corepack pnpm smoke:local` | pass | PostgreSQL, Redis, and MinIO checks passed; Alembic migration and Phase 2 durable data smoke passed; Phase 3 local deterministic generation smoke passed. |
| `corepack pnpm infra:down` | pass | Compose services were stopped after live-smoke attempts; `docker compose ... ps` showed no running services. |

## Hosted-Disabled Worker Smoke

| Command | Result | Evidence |
|---------|--------|----------|
| `corepack pnpm smoke:worker -- --dry-run` | pass | Worker queue smoke dry run passed and printed real smoke prerequisites. No hosted provider calls were made. |

## Live Worker Smoke Attempt

Live smoke was attempted twice with local Docker services, API on `127.0.0.1:8000`, and a Windows-safe Celery worker command:

```powershell
cd services/worker
uv run celery -A caragent_worker.app worker --loglevel=INFO --pool=solo --concurrency=1
```

Observed evidence:

- API reached `GET /health` with HTTP 200.
- Celery worker connected to `redis://localhost:6379/0`.
- Celery worker logged `ready`.
- The orchestration attempt returned non-zero before a successful `corepack pnpm smoke:worker` result was captured.
- Cleanup stopped Compose, after which worker logs showed Redis connection loss; this is a cleanup consequence, not a passed live smoke.

Live worker smoke remains a documented operator path requiring Docker services, migrated API database, running API, running worker, and then `corepack pnpm smoke:worker`.

## Cleanup

- Docker Compose services were shut down.
- Temporary API/worker child processes listening on `127.0.0.1:8000` were stopped.
- No real provider credentials were used.

## Release Interpretation

This satisfies the Docker-backed local deterministic and hosted-disabled smoke requirement for Phase 14. It does not claim a passed live API-to-Celery job smoke in this run.

---
*Docker smoke recorded: 2026-06-19*
