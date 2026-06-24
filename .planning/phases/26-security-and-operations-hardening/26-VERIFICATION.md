# Phase 26 Verification

## Commands

- `cd services/api && uv run pytest -q tests/test_workspaces.py tests/test_assets.py`
- `cd services/api && uv run pytest -q`
- `cd services/api && uv run ruff check src tests`
- `cd services/api && uv run mypy src`
- `cd services/core && uv run pytest -q`
- `cd services/core && uv run ruff check src tests`
- `cd services/core && uv run mypy src`
- `cd services/worker && uv run pytest -q`
- `cd services/worker && uv run ruff check src tests`
- `cd services/worker && uv run mypy src`
- `corepack pnpm --filter @caragent/contracts check`
- `corepack pnpm validate`
- `corepack pnpm infra:up`
- `node scripts/smoke-local.mjs`
- `corepack pnpm infra:down`

## Result

Phase 26 verification passed on 2026-06-22. The main run included Docker-backed
local smoke after `infra:up` and cleanup with `infra:down`. `pnpm validate`
initially found stale contract artifacts after auth/OpenAPI changes; OpenAPI and
generated contracts were regenerated, then contract check and full validation
passed.

After adding the Redis-backed hosted quota store, the final follow-up run passed:

- `cd services/worker && uv run ruff check src tests/test_hosted_quota.py --fix`
- `cd services/worker && uv run mypy src`
- `cd services/worker && uv run pytest -q tests/test_hosted_quota.py tests/test_generation_tasks.py tests/test_image_providers.py`
- `git diff --check`
- `corepack pnpm validate`

A final re-run of `corepack pnpm infra:up`/`smoke:local` was attempted after the
Redis quota follow-up, but the desktop approval layer rejected Docker access due
to the current usage limit. No smoke failure was observed.

## Known Warnings

- Frontend Vitest still prints the existing jsdom canvas `getContext` warning.
  The suite passes and the warning is not introduced by Phase 26.

