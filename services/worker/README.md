# carAgent Worker

Celery worker foundation for the Phase 1 work plane. The worker is a separate Python
project from the FastAPI service and must not import API routers or backend internals.

## Local Commands

Run these commands from `services/worker` after installing Python 3.13 and `uv`:

```powershell
uv sync --dev
uv run celery -A caragent_worker.app worker --loglevel=INFO
uv run ruff check .
uv run mypy src
uv run pytest -q
```

The root `pnpm dev:worker`, `pnpm lint`, `pnpm typecheck`, and `pnpm test` commands
delegate to this project once `uv` is available.

## Configuration

The local default broker is `redis://localhost:6379/0`. Any non-local runtime mode
requires an explicit `REDIS_URL` environment variable so queue configuration is not
accidentally inherited from local defaults.

Supported environment variables:

| Variable | Purpose |
| --- | --- |
| `RUNTIME_MODE` | One of `local`, `development`, `test`, `staging`, or `production`. |
| `REDIS_URL` | Celery broker URL. Required outside `local`. |
| `AI_PROVIDER_OPENAI_API_KEY` | Stored as a redacted secret for later provider adapters. |
| `AI_PROVIDER_FAL_API_KEY` | Stored as a redacted secret for later provider adapters. |
| `AI_PROVIDER_BFL_API_KEY` | Stored as a redacted secret for later provider adapters. |

Redis broker defaults are local-development only. Phase 1 does not create durable
product jobs, call provider SDKs, generate images, persist artifacts, handle uploads,
or implement export work.
