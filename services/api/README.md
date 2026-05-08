# carAgent API Service

FastAPI control-plane foundation for Phase 1. This service owns typed runtime
settings, the foundation `/health` contract, and deterministic OpenAPI export.

## Local Commands

Run commands from `services/api` after installing `uv` and syncing dependencies:

```powershell
uv run uvicorn caragent_api.main:app --reload --host 0.0.0.0 --port 8000
uv run ruff check .
uv run mypy src
uv run pytest -q
uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json
```

Root commands in `package.json` delegate to these service commands.

## Configuration

The API reads configuration from environment variables through
`caragent_api.config.ApiSettings`. Local mode has safe development defaults for
PostgreSQL, Redis, and MinIO. Non-local modes require explicit database, queue,
object-storage, and CORS configuration.

Provider API keys are accepted only as secret configuration values in Phase 1.
The API does not call AI providers or validate provider accounts here.

## Boundaries

This service must not create product tables, call workers, call AI providers, or
store generated artifacts in Phase 1. Later plans consume its OpenAPI contract
from `packages/contracts`.
