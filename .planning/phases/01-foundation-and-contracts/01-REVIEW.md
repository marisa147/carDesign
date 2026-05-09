---
status: issues_found
phase: 01-foundation-and-contracts
reviewed: 2026-05-09T00:47:55Z
depth: standard
files_reviewed: 63
files_reviewed_list:
  - .env.example
  - .gitattributes
  - .gitignore
  - .node-version
  - .python-version
  - apps/web/.env.example
  - apps/web/components.json
  - apps/web/eslint.config.mjs
  - apps/web/package.json
  - apps/web/postcss.config.mjs
  - apps/web/src/app/globals.css
  - apps/web/src/app/layout.tsx
  - apps/web/src/app/page.test.tsx
  - apps/web/src/app/page.tsx
  - apps/web/src/components/ui/alert.tsx
  - apps/web/src/components/ui/badge.tsx
  - apps/web/src/components/ui/button.tsx
  - apps/web/src/components/ui/card.tsx
  - apps/web/src/lib/api/health.ts
  - apps/web/src/lib/config/public-env.ts
  - apps/web/src/lib/utils.ts
  - apps/web/src/test/setup.ts
  - apps/web/tsconfig.json
  - apps/web/vitest.config.ts
  - docs/development.md
  - infra/compose.yml
  - infra/README.md
  - package.json
  - packages/contracts/openapi/.gitkeep
  - packages/contracts/openapi/openapi.json
  - packages/contracts/orval.config.ts
  - packages/contracts/package.json
  - packages/contracts/README.md
  - packages/contracts/src/generated/.gitkeep
  - packages/contracts/src/generated/client.ts
  - packages/contracts/src/index.ts
  - packages/contracts/tsconfig.json
  - pnpm-workspace.yaml
  - README.md
  - scripts/check-contracts.mjs
  - scripts/check-env-examples.mjs
  - scripts/smoke-local.mjs
  - scripts/validate-all.mjs
  - services/api/.env.example
  - services/api/pyproject.toml
  - services/api/README.md
  - services/api/src/caragent_api/__init__.py
  - services/api/src/caragent_api/config.py
  - services/api/src/caragent_api/main.py
  - services/api/src/caragent_api/scripts/export_openapi.py
  - services/api/tests/test_config.py
  - services/api/tests/test_health.py
  - services/api/tests/test_openapi_export.py
  - services/worker/.env.example
  - services/worker/pyproject.toml
  - services/worker/README.md
  - services/worker/src/caragent_worker/__init__.py
  - services/worker/src/caragent_worker/app.py
  - services/worker/src/caragent_worker/config.py
  - services/worker/src/caragent_worker/tasks/__init__.py
  - services/worker/src/caragent_worker/tasks/health.py
  - services/worker/tests/test_config.py
  - services/worker/tests/test_worker_app.py
findings:
  critical: 0
  warning: 5
  info: 1
  total: 6
---

# Phase 1: Code Review Report

**Reviewed:** 2026-05-09T00:47:55Z
**Depth:** standard
**Files Reviewed:** 63
**Status:** issues_found

## Summary

Reviewed the Phase 1 foundation files for correctness, security, broken contracts, and missing critical checks. No critical security issues were found. The main concerns are configuration contracts that do not behave as documented and validation commands that can report success without proving the intended foundation checks.

## Warnings

### WR-01: Documented Python `.env` files are never loaded

**File:** `services/api/src/caragent_api/config.py:24`, `services/worker/src/caragent_worker/config.py:13`, `docs/development.md:39`

**Issue:** The development guide tells users to copy `services/api/.env.example` and `services/worker/.env.example` to `.env`, but neither `ApiSettings` nor `WorkerSettings` configures an `env_file`. Running `pnpm dev:api` or `pnpm dev:worker` from the documented commands will ignore those copied files and silently use in-code defaults unless the shell process already exported the variables.

**Fix:** Either add dotenv loading to both settings classes, or change the docs/scripts to explicitly export env values before launching services. Example:

```python
model_config = SettingsConfigDict(
    case_sensitive=False,
    extra="ignore",
    env_file=".env",
    env_file_encoding="utf-8",
)
```

Add API and worker tests that create a temporary `.env` in the service cwd and prove settings read it.

### WR-02: API health reports dependency success without checking dependencies

**File:** `services/api/src/caragent_api/main.py:28`, `services/api/src/caragent_api/main.py:36`, `apps/web/src/lib/api/health.ts:162`

**Issue:** `/health` marks database, Redis, and object storage as `ok` when the corresponding config strings are non-empty. It does not attempt a database connection, Redis ping, or MinIO health request. The web then renders "PostgreSQL, Redis and MinIO health check passed", so the stack health UI can show success while Docker services are stopped or credentials are wrong. This is especially risky because API in-code local defaults also differ from the Compose/example credentials at `services/api/src/caragent_api/config.py:12`.

**Fix:** Either perform lightweight real checks and return `unavailable` on failure, or rename/downgrade the contract to "configured" and make the web copy match. If Phase 1 avoids service clients, do not map config presence to a "health check passed" UI state.

### WR-03: `pnpm smoke:local` succeeds when Docker is unavailable

**File:** `scripts/smoke-local.mjs:29`, `scripts/smoke-local.mjs:34`

**Issue:** When `docker info` fails, the smoke script prints a host-prerequisite message and exits with status `0`. That makes the Docker-dependent smoke command pass without proving PostgreSQL, Redis, or MinIO are running.

**Fix:** Return a non-zero exit code for Docker unavailability, unless an explicit opt-in flag is provided for sandbox documentation flows. Example:

```javascript
if (!docker.ok) {
  console.error("Docker daemon unavailable; start Docker and rerun pnpm smoke:local.");
  process.exit(1);
}
```

### WR-04: Root `pnpm test` calls a missing contracts test script

**File:** `package.json:15`, `packages/contracts/package.json:20`

**Issue:** The root `test` script runs `pnpm --filter @caragent/contracts test`, but `@caragent/contracts` defines `generate`, `check`, `typecheck`, and `lint` only. The documented root `pnpm test` command will fail before reaching API and worker tests.

**Fix:** Add a contracts `test` script or remove that leg from the root command. Minimal fix:

```json
"test": "tsc --project tsconfig.json --noEmit"
```

### WR-05: Provider env names in examples do not match the settings contract

**File:** `services/api/.env.example:19`, `services/api/src/caragent_api/config.py:48`, `services/worker/.env.example:21`, `services/worker/src/caragent_worker/config.py:21`, `scripts/check-env-examples.mjs:32`

**Issue:** The committed examples and env guard require `OPENAI_API_KEY`, `STABILITY_API_KEY`, `FAL_API_KEY`, and `REPLICATE_API_TOKEN`, but API/worker settings parse `AI_PROVIDER_OPENAI_API_KEY`, `AI_PROVIDER_FAL_API_KEY`, and `AI_PROVIDER_BFL_API_KEY`. A copied example file therefore does not configure the fields that tests assert exist, and the env guard can pass while the services ignore those provider placeholders.

**Fix:** Pick one public env contract and use it everywhere. If keeping the shorter names, use Pydantic alias choices, for example:

```python
from pydantic import AliasChoices

ai_provider_openai_api_key: SecretStr | None = Field(
    default=None,
    validation_alias=AliasChoices("AI_PROVIDER_OPENAI_API_KEY", "OPENAI_API_KEY"),
)
```

Also align FAL/BFL/Stability/Replicate naming across examples, tests, docs, and validators.

## Info

### IN-01: Generated contracts are a sandbox fallback, not verified Orval output

**File:** `packages/contracts/src/generated/client.ts:5`, `packages/contracts/orval.config.ts:10`, `packages/contracts/package.json:26`

**Issue:** The committed TypeScript client says it is a deterministic fallback because package-manager execution was blocked, while Orval is configured for `client: "react-query"`. The contracts package also does not declare `@tanstack/react-query`; only the web app does. Because pnpm is blocked in this environment, I could not verify whether real Orval output matches the committed client or whether package typecheck passes after generation.

**Fix:** On a host where pnpm works, run the real contract generation/check flow and commit the true Orval output. If hooks are intended, declare the needed React Query dependency/peer in `@caragent/contracts`; otherwise switch Orval to a fetch-style client that matches the intended export surface.

## Verification Notes

`node scripts/check-env-examples.mjs` passed.

Full validation was not run because host/tooling prerequisites are blocked in this sandbox:

- `node --version` is `v20.12.0`, while `.node-version` pins `24.15.0`.
- `pnpm --version` fails with `EPERM: operation not permitted, lstat 'C:\Users\25858'`.
- `uv --version` fails because `uv` is not installed or not on `PATH`.
- `docker info` reaches the Docker CLI but cannot access the daemon/config due permission errors.
- `pnpm contracts:check` was not run because it can rewrite generated contract artifacts, and this review was constrained to avoid source modifications.

---

_Reviewed: 2026-05-09T00:47:55Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
