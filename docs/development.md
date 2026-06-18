# Development Guide

This guide is the local runbook for the foundation stack, durable-data work, first text-to-2D generation slice, Phase 4 integrated workbench, Phase 5 iteration/feedback/concept export flow, Phase 6 itasha/template intelligence, Phase 7 operations/provider strategy, and Phase 10 targeted edit workflow. It documents how to install prerequisites, configure local environment files, run the web/API/worker processes, start local infrastructure, run migrations, generate contracts, run validation, perform smoke checks, run browser UAT, and troubleshoot host setup failures.

`init.MD` and `UI.png` are seed references for the product direction. Phase 1 established the runnable foundation; Phase 2 adds durable workspace/message/asset/job data and a minimal web refresh proof; Phase 3 adds structured brief parsing, prompt traceability, local deterministic concept generation, generation API routes, retry behavior, and a compact web proof. Phase 4 replaces the proof-first page with a workbench that connects chat, parameters, asset upload/rights state, progress events, 2D preview, version history, and future gates to canonical API-backed state. Phase 5 adds selected-version iteration, parent/child lineage comparison, durable feedback, approval/rejection comments, and concept export records with a metadata manifest that says the output is not print-ready. Phase 6 adds itasha-specific controls, deterministic text/logo overlay evidence, safe-zone/template warnings, and PreviewSpec metadata for future renderer work. Phase 7 adds operations status, classified failure metadata, cancel/revoke handoff, bounded provider retry/fallback, hosted-call quota preflight, and worker queue smoke checks. Phase 8 starts V2 from a verified V1 baseline. Phase 9 adds a default-off hosted BFL rollout path with provider capability metadata, BFL adapter polling, API/worker preflight, trace/cost/failure diagnostics, a workbench provider selector, and provider-off/provider-on runbooks. Phase 10 adds targeted edit selection, mask preview, deterministic recomposition, provider-mask guardrails, retry-safe failure states, and comparison for parent/child versions with metadata-backed changed-region highlighting. Production-ready wrap output, authentication, hosted provider calls by default, billing, true 3D, marketplace/community flows, and production deployment remain out of scope.

## Prerequisites

Install the repo-visible runtime baselines before running commands. On Windows with NVM, use the Node version from `.node-version`; Python service commands use the uv-managed interpreter selected by `.python-version`.

| Tool | Required Baseline | Repo Source | Used For |
| ---- | ----------------- | ----------- | -------- |
| Node.js | `22.15.0` | `.node-version` | Next.js, scripts, generated contracts |
| pnpm | `11.0.8` | `package.json` `packageManager` | Workspace install and root commands |
| Python | `3.13.13` via `uv run python` | `.python-version` | FastAPI, Celery, Alembic, and shared core services |
| uv | Host install on `PATH` | service commands | Python dependency sync and checks |
| Docker Desktop or Docker Engine | Host install with daemon running | `infra/compose.yml` | PostgreSQL, Redis, and MinIO |

The current sandbox may have Node and Docker CLIs without access to the required host resources. Treat `uv` not installed, Node/Corepack profile `EPERM`, and Docker daemon unavailable as host prerequisites to fix before expecting the full validation command to pass. If `pnpm` itself cannot start, run `node scripts/check-host-prereqs.mjs` for a repository-local prerequisite report.

## Install And Sync

From the repository root:

```powershell
pnpm install
cd services/core
uv sync --dev
cd ../api
uv sync --dev
cd ../worker
uv sync --dev
cd ../..
```

No real secrets are required for local mode. Copy example files only when you need local overrides, and keep real `.env` files ignored:

```powershell
Copy-Item .env.example .env
Copy-Item apps/web/.env.example apps/web/.env.local
Copy-Item services/api/.env.example services/api/.env
Copy-Item services/worker/.env.example services/worker/.env
```

Only `.env.example` files belong in source control. Real secrets and local overrides must stay untracked.

When commands run from `services/api` or `services/worker` (including the root `pnpm dev:api`, `pnpm dev:worker`, and validation delegates), `pydantic-settings` loads the copied service `.env` file from that service directory. Use service `.env` files as the primary local override path instead of manually exporting variables in every shell.

## Repository Layout

| Path | Owner | Purpose |
| ---- | ----- | ------- |
| `apps/web` | Product plane | Next.js workbench, generated contract consumption, chat-to-brief flow, structured and itasha parameters, assets, progress, 2D preview, PreviewSpec overlays/safe zones, history, iteration, feedback, concept export, and future gates. |
| `services/core` | Shared data core | SQLAlchemy metadata, async database helpers, and durable-data services shared by API and worker. |
| `services/api` | Control plane | FastAPI settings, `/health`, product/generation routes, Alembic migrations, OpenAPI export, and smoke scripts. |
| `services/worker` | Work plane | Celery entrypoint, Redis broker settings, health task, local no-provider simulation, and text-to-2D generation task. |
| `packages/contracts` | Shared contracts | OpenAPI artifact and generated TypeScript client used by the web shell. |
| `infra` | Data-plane support | Local PostgreSQL, Redis, and MinIO Compose services. |
| `scripts` | Validation tooling | Env guard, contract drift guard, smoke runner, and aggregate runner. |
| `docs` | Project docs | Developer workflow and troubleshooting notes. |

Python services and the shared core package are managed by `uv` and are intentionally not pnpm workspace packages.

## Root Commands

| Command | Delegates To | Purpose |
| ------- | ------------ | ------- |
| `pnpm infra:up` | `docker compose --env-file .env.example -f infra/compose.yml up -d` | Start local PostgreSQL, Redis, and MinIO. |
| `pnpm infra:down` | `docker compose --env-file .env.example -f infra/compose.yml down` | Stop local infrastructure services. |
| `pnpm dev:api` | `cd services/api && uv run uvicorn caragent_api.main:app --reload --host 0.0.0.0 --port 8000` | Run the FastAPI API. |
| `pnpm dev:worker` | `cd services/worker && uv run celery -A caragent_worker.app worker --loglevel=INFO` | Run the Celery worker. |
| `pnpm dev:web` | `pnpm --filter @caragent/web dev` | Run the Next.js web shell. |
| `pnpm contracts:generate` | `pnpm --filter @caragent/contracts generate` | Refresh generated TypeScript contracts from OpenAPI. |
| `pnpm contracts:check` | `pnpm --filter @caragent/contracts check` | Regenerate/check contract artifacts for drift. |
| `pnpm compat:v1` | `node scripts/check-v1-compatibility.mjs` | Verify key v1 routes, schemas, generated helpers, and PreviewSpec-compatible parameter surfaces still exist before V2 schema work. |
| `pnpm migration:safety` | `node scripts/check-migration-safety.mjs` | Statically verify Alembic revision files, current migration head, and v1 durable ledger tables. |
| `pnpm lint` | Web, contracts, core, API, and worker lint commands | Run lint checks. |
| `pnpm typecheck` | Web, contracts, core, API, and worker type checks | Run type checks. |
| `pnpm test` | Web, contracts, core, API, and worker tests | Run the root unit-test surface. |
| `pnpm smoke:local` | `node scripts/smoke-local.mjs` | Probe local infrastructure after Compose startup and run Phase 2/3 database smoke checks. |
| `pnpm smoke:worker` | `node scripts/smoke-worker-queue.mjs` | Submit a live generation job through the API/queue boundary and verify worker-produced PreviewSpec output. |
| `pnpm validate` | `node scripts/validate-all.mjs` | Run the aggregate validation sequence for the implemented local foundation through current web/API/worker checks. |

Root commands are convenience wrappers. Service-specific commands remain independently runnable from their owning directories.

## Phase 8 / V2 Readiness Gate

Phase 8 is a readiness gate before V2 product expansion. It starts from the archived v1.0 evidence in `.planning/phases/08-v1-closure-and-v2-readiness-gate/08-READINESS-BASELINE.md`, which records the `v1.0` tag, the v1.0 milestone archive paths, the passed audit verdict, and the latest Phase 7 operations closure.

Use these commands as the Phase 8 readiness vocabulary:

| Command | Readiness Purpose |
| ------- | ----------------- |
| `pnpm validate` | Aggregate lint, typecheck, tests, env guard, and contract drift checks. |
| `pnpm contracts:check` | Confirms generated OpenAPI and TypeScript contracts are in sync. |
| `pnpm compat:v1` | Confirms key v1 workbench, job, artifact, version, operations, feedback/export/iteration, and PreviewSpec-compatible contract surfaces still exist. |
| `pnpm migration:safety` | Statically confirms the current Alembic head and v1 durable ledger tables are present. |
| `pnpm infra:up` | Starts PostgreSQL, Redis, and MinIO for live local smoke. |
| `pnpm smoke:local` | Proves Docker-backed local infrastructure, migrations, durable data, and local deterministic generation smoke. |
| `pnpm smoke:worker -- --dry-run` | Proves worker smoke command wiring without requiring live API/worker processes. |
| `pnpm smoke:worker` | Proves the live API -> Redis/Celery -> worker -> durable artifact/version path on a prepared host. |

`pnpm compat:v1` does not replace `pnpm contracts:check`: run compatibility first to confirm required v1 surfaces are still present, then run contract drift checks to confirm generated artifacts remain synchronized with FastAPI/Pydantic OpenAPI.

`pnpm migration:safety` is a static check for sandbox and review flows. It does not replace live Alembic verification. On a prepared host, run:

```powershell
cd services/api
uv run alembic upgrade head
uv run alembic current
```

Browser readiness UAT for Phase 8 is host-only: start local infrastructure, run API migrations, start the API, a Windows-safe worker, and web, then confirm the V1 workbench loads and future/V2 gates remain disabled or clearly deferred. Phase 8 must not imply hosted provider calls are enabled by default. Hosted provider production rollout, provider quality, pricing, moderation, account access, and commercial-rights checks remain Phase 9 scope.

Phase 8 closure evidence is recorded in `.planning/phases/08-v1-closure-and-v2-readiness-gate/08-VERIFICATION.md` and `.planning/phases/08-v1-closure-and-v2-readiness-gate/08-HUMAN-UAT.md`. Static checks, aggregate validation, Docker local smoke, and Alembic current passed; worker live smoke and Browser desktop/mobile UAT remain host-run checklist items.

## Local Services

Local PostgreSQL, Redis, and MinIO are defined in `infra/compose.yml`; see `infra/README.md` for images, ports, and Docker prerequisites.

```powershell
pnpm infra:up
pnpm smoke:local
pnpm infra:down
```

`pnpm smoke:local` is a required live local-services check. It fails when the
Docker daemon is unavailable because PostgreSQL, Redis, MinIO, Alembic, Phase 2
durable data smoke, and Phase 3 local deterministic generation smoke were not
validated. After PostgreSQL, Redis, and MinIO health pass, the smoke script runs
`uv run alembic upgrade head`, a small workspace/message/job/artifact metadata
round trip, and a local deterministic structured brief -> prompt trace -> model
run -> generated image artifact -> design version round trip against the local
database. To let the smoke script manage Compose when Docker is available:

```powershell
node scripts/smoke-local.mjs --with-compose-if-docker
```

For sandbox or report-writing flows where Docker is known to be inaccessible,
the script has an explicit non-verification escape hatch:

```powershell
node scripts/smoke-local.mjs --allow-docker-unavailable
```

That command only records that Docker checks were not performed; it is not Phase 2 or Phase 3 completion evidence. Use `pnpm infra:up`, `pnpm smoke:local`, and
`pnpm infra:down` on a Docker-enabled host for verification.

`pnpm smoke:worker` is the Phase 7 live queue check. It requires Docker infrastructure, migrated API database, a running API process, and a running Celery worker. It calls `/operations/provider-status`, creates a workspace and generation brief, submits a generation job through the API queue boundary, polls durable job state, and verifies the worker produced an artifact plus a design version with `PreviewSpec` metadata.

```powershell
pnpm smoke:worker -- --dry-run
pnpm smoke:worker
```

Use `--dry-run` for command wiring and documentation checks when services are not running. Real smoke evidence requires the non-dry-run command to pass.

Compose credentials and exposed ports bind to local development defaults only. They are not production deployment guidance.

PostgreSQL 18 uses a version-aware data directory. The local Compose file mounts the development volume at `/var/lib/postgresql`, not `/var/lib/postgresql/data`.

## Core

Run focused checks for shared durable-data primitives:

```powershell
cd services/core
uv run ruff check .
uv run mypy src
uv run pytest -q
```

The core package is imported by API and worker through local uv path dependencies. It must not import FastAPI routers, Celery app instances, web code, or provider SDKs.

## API

Run the API:

```powershell
pnpm dev:api
```

Focused API checks:

```powershell
cd services/api
uv run ruff check .
uv run mypy src
uv run pytest -q
uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json
uv run alembic upgrade head
uv run alembic current
```

API settings cover database URL, Redis URL, S3/MinIO endpoint and bucket settings, CORS origins, runtime mode, and the provider placeholder contract: `AI_PROVIDER_DEFAULT`, `AI_PROVIDER_CALLS_ENABLED`, `AI_PROVIDER_OPENAI_API_KEY`, `AI_PROVIDER_FAL_API_KEY`, and `AI_PROVIDER_BFL_API_KEY`. The API exposes Phase 2 workspace, message, asset, rights, job, event, version, artifact, feedback, export, and cost/idempotency contract surfaces plus Phase 3 structured brief creation/update, generation submission, and failed-job retry routes through FastAPI and generated OpenAPI. Phase 5 adds workspace/version-scoped creation routes for feedback, concept export, and child iteration submission. Phase 6 extends existing generation brief create/update contracts with itasha fields for character focus, supporting graphics, racing/JDM cues, typography intent, color harmony, and overlay logo asset ids. Phase 7 adds `/operations/provider-status` and `POST /jobs/{job_id}/cancel`. Phase 10 extends iteration submission with typed targeted edit intent, mask metadata, route preference, and parent-version validation while keeping provider calls disabled in local mode.

## Worker

Run the worker:

```powershell
pnpm dev:worker
```

On Windows, use solo pool mode for deterministic local smoke and easier process shutdown:

```powershell
cd services/worker
uv run celery -A caragent_worker.app worker --loglevel=INFO --pool=solo --concurrency=1
```

Focused worker checks:

```powershell
cd services/worker
uv run ruff check .
uv run mypy src
uv run pytest -q
```

The worker boot path includes Celery, Redis broker configuration, service `.env` loading, provider setting parsing/redaction, the health task, a local no-provider job simulation task, and the Phase 3 `generate_2d_concept_job` task. It updates durable job state through `caragent_core`, does not import FastAPI routers, and defaults to local deterministic image generation without hosted provider calls. For Phase 5 child iterations, the worker reads durable generation job metadata such as `parent_version_id`, `change_request`, and `parameter_overrides`, then creates a child design version instead of overwriting the parent. For Phase 6 PreviewSpec support, the worker persists overlay/safe-zone/warning metadata into generated version parameters and artifact metadata, and checks confirmed rights for both reference assets and overlay logo assets before generation. For Phase 7 operations, the worker emits structured failure categories/stages, observes canceled jobs before and during generation, records provider attempt metadata, applies bounded retry/fallback rules, and blocks non-local hosted calls before provider execution unless daily, per-minute, and per-job cost guards are configured. For Phase 9 hosted BFL calls, the worker uses the BFL adapter only after API/worker preflight passes; it stores provider/model/parameter/cost/fallback traces and maps moderation, validation, credits, rate-limit, timeout, and provider errors into safe diagnostics. For Phase 10 targeted edit jobs, the worker reads durable `edit_intent`, validates parent version and mask metadata, uses deterministic recomposition for safe layer edits, blocks unsupported provider-mask routes, and records route/target/region/prompt/provider evidence for comparison.

## Phase 3 Generation

Phase 3 starts from a natural-language request and creates a reusable structured brief with template/view, character/theme, style, palette, text, coverage, reference asset ids, warnings, and canvas dimensions. Prompt planning records exact prompt text, prompt payload, provider, model, parameters, input artifact ids, estimated cost, and concept label in `model_runs`.

Local deterministic generation is the baseline verification path. It requires no hosted provider keys and records `external_calls=false` in local smoke/test evidence. Hosted provider enablement is optional: set `AI_PROVIDER_CALLS_ENABLED=true`, choose a supported `AI_PROVIDER_DEFAULT`, provide the matching ignored secret key, and keep timeout/poll settings explicit. Worker retry/fallback behavior is bounded by `AI_GENERATION_MAX_ATTEMPTS`, `AI_PROVIDER_FALLBACK_ENABLED`, and `AI_PROVIDER_FALLBACK_NAME`; fallback defaults to disabled and only local deterministic fallback is supported in v1. Hosted calls also require `AI_HOSTED_DAILY_CALL_LIMIT`, `AI_HOSTED_RATE_LIMIT_PER_MINUTE`, and `AI_MAX_ESTIMATED_COST_PER_JOB`; missing or exceeded guards block before provider execution. Do not commit real keys.

Focused Phase 3 checks:

```powershell
cd services/core
uv run pytest -q tests/test_generation_briefs.py tests/test_prompt_plans.py
cd ../api
uv run pytest -q tests/test_generation.py
uv run python -m caragent_api.scripts.phase3_generation_smoke
cd ../worker
uv run pytest -q tests/test_image_providers.py tests/test_generation_tasks.py
```

Retry behavior is API-owned: retry is limited to failed generation jobs and creates a new durable attempt tied to the original brief. The original failed job, error message, and model-run status remain inspectable.

## Phase 4 Workbench

Phase 4 turns the proof page into the first integrated workbench. The first screen is the product surface, not a landing page: a left chat rail submits durable user messages and creates or updates a structured generation brief; the parameter panel saves supported brief fields through the generation brief update route; the asset panel uploads references, shows source/rights state, and blocks missing-rights assets from generation selection; the progress panel renders queued, running, succeeded, failed, retry, and recent event state from durable jobs/events; the 2D preview and history panel show generated artifact/version metadata with local zoom, reset, supported-view switching, and version selection.

Phase 4 browser storage is limited to safe resume identifiers: `caragent.workbench.workspaceId` and `caragent.workbench.briefId`. Chat text, generated payloads, provider keys, storage secrets, and database/Redis/S3 URLs must not be stored in browser storage or imported by web code.

Focused Phase 4 checks:

```powershell
corepack pnpm --filter @caragent/web lint
corepack pnpm --filter @caragent/web typecheck
corepack pnpm --filter @caragent/web test
corepack pnpm --filter @caragent/web build
corepack pnpm contracts:check
```

Future gates are intentional product boundaries. True 3D preview, print-ready export, marketplace/community flows, payment/order flows, hosted provider production rollout, auth, billing, and production handoff must be disabled, experimental, or documented as deferred until later phases implement and verify them.

## Phase 5 Iteration, Feedback, And Concept Export

Phase 5 keeps the workbench as the product surface and adds version-scoped actions near history: child iteration submission, lineage/parameter comparison, feedback/rating/approval records, and concept export. A selected generated version is the context for all Phase 5 actions.

Child iteration requests call `POST /workspaces/{workspace_id}/versions/{version_id}/iterations` and create a new durable generation job with parent-version metadata. The worker creates a child `design_versions` row with `parent_version_id` and `lineage_depth`; the parent version and source artifact remain immutable and visible.

Feedback calls `POST /workspaces/{workspace_id}/versions/{version_id}/feedback` and records rating, approval state, comment, and metadata against the selected version. Approval and rejection are lightweight review records; they do not delete or mutate generated artifacts.

Concept export calls `POST /workspaces/{workspace_id}/versions/{version_id}/exports` with the selected version's matching generated artifact, a PNG/JPG format, and a JSON manifest. The manifest includes selected version/artifact identity and the disclaimer `概念预览，不是生产印刷文件。`; server-side export records also carry concept-preview safety fields. This is a concept export for review, not print-ready production handoff.

Focused Phase 5 checks:

```powershell
cd services/core
uv run pytest -q tests/test_jobs.py
cd ../api
uv run pytest -q tests/test_jobs.py tests/test_generation.py
cd ../worker
uv run pytest -q tests/test_generation_tasks.py
cd ../..
corepack pnpm --filter @caragent/web test
corepack pnpm --filter @caragent/web typecheck
corepack pnpm --filter @caragent/web lint
corepack pnpm --filter @caragent/web build
corepack pnpm contracts:check
```

Phase 5 Browser UAT requires local infrastructure, migrations, API, worker, and web services running. Use a workspace that has at least one generated design version and artifact when you want to exercise the enabled iteration/export paths; the empty-state controls must remain disabled before a version/artifact exists.

## Phase 6 Itasha And Template Intelligence

Phase 6 keeps the same workbench surface and adds itasha-specific control and preview intelligence. The parameter panel includes `痛车设计控制` fields for character focus, supporting graphics, racing/JDM cues, typography intent, color harmony, and overlay logo asset ids. The core brief schema and API contracts store these fields through the existing generation brief create/update routes.

The core prompt payload includes a renderer-neutral `PreviewSpec` with canvas, template, safe zones, overlay layers, warnings, and source asset ids. The worker persists that spec into generated design version parameters and generated artifact metadata. The local deterministic provider draws concept-preview text/logo overlay evidence where possible and records overlay, safe-zone, and warning counts. Uploaded logo assets follow the same confirmed-rights gate as reference assets.

The web preview reads `DesignVersion.parameters.preview_spec`, renders a compact `PreviewSpec 摘要`, and exposes local `文字/Logo 图层` and `安全区` toggles. These toggles are local UI state; they do not mutate selected versions or artifacts. The export panel can display PreviewSpec summaries from the selected version and saved export manifest metadata. All Phase 6 output remains a concept preview. It does not prove print-ready wrap files, vector text/logo conversion, verified production templates, broad vehicle-template libraries, or true UV-mapped 3D preview.

Focused Phase 6 checks:

```powershell
cd services/core
uv run pytest -q tests/test_generation_briefs.py tests/test_prompt_plans.py
cd ../api
uv run pytest -q tests/test_generation.py tests/test_openapi_export.py
uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json
cd ../worker
uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py
cd ../..
corepack pnpm --filter @caragent/web test -- apps/web/src/app/page.test.tsx apps/web/src/lib/workbench/store.test.ts
corepack pnpm --filter @caragent/web lint
corepack pnpm --filter @caragent/web typecheck
corepack pnpm contracts:check
```

Phase 6 Browser UAT requires local infrastructure, migrations, API, worker, and web services running. Use a workspace with at least one generated design version whose parameters include `preview_spec` when you want to exercise overlay/safe-zone display.

## Phase 7 Operations And Provider Strategy

Phase 7 keeps local deterministic generation as the baseline and makes operations behavior visible without adding a separate admin dashboard. The API exposes `/operations/provider-status` for provider/worker/queue status and recent failure summaries. The workbench progress panel can refresh that compact status, render structured failure metadata, cancel queued/running jobs, and hide cancel controls once a job reaches a terminal state.

Cancellation is durable first: `POST /jobs/{job_id}/cancel` marks eligible queued/running jobs as `canceled`, records operations metadata, and asks Celery to revoke the queued task when a task id exists. Terminal jobs cannot be canceled. Workers also check durable canceled state before provider execution and before final persistence so late cancels do not create fresh artifacts.

Hosted provider calls remain opt-in and guarded. To attempt non-local calls, set `AI_PROVIDER_CALLS_ENABLED=true`, choose a supported `AI_PROVIDER_DEFAULT`, configure the provider key in an ignored env file, and set all three hosted guards:

```powershell
AI_HOSTED_DAILY_CALL_LIMIT=25
AI_HOSTED_RATE_LIMIT_PER_MINUTE=4
AI_MAX_ESTIMATED_COST_PER_JOB=0.7500
```

Missing or exceeded hosted guards fail before provider execution. Bounded retry/fallback is controlled by `AI_GENERATION_MAX_ATTEMPTS`, `AI_PROVIDER_FALLBACK_ENABLED`, and `AI_PROVIDER_FALLBACK_NAME`; v1 only supports local deterministic fallback after eligible hosted provider/timeout failures. Hosted provider quality, price, moderation, account access, and commercial rights must be revalidated before using non-local output as product evidence.

Focused Phase 7 checks:

```powershell
cd services/api
uv run pytest -q tests/test_operations.py tests/test_generation.py tests/test_jobs.py tests/test_queue.py
uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json
cd ../worker
uv run pytest -q tests/test_config.py tests/test_image_providers.py tests/test_generation_tasks.py
cd ../..
corepack pnpm contracts:check
corepack pnpm --filter @caragent/web test -- apps/web/src/app/page.test.tsx apps/web/src/lib/api/operations.test.ts apps/web/src/lib/api/jobs.test.ts
corepack pnpm --filter @caragent/web lint
corepack pnpm --filter @caragent/web typecheck
corepack pnpm smoke:worker -- --dry-run
```

Live worker queue smoke:

```powershell
pnpm infra:up
cd services/api
uv run alembic upgrade head
cd ../..
pnpm dev:api
# second terminal
cd services/worker
uv run celery -A caragent_worker.app worker --loglevel=INFO --pool=solo --concurrency=1
# third terminal
pnpm smoke:worker
```

The non-dry-run smoke fails clearly when the API, worker, database, Redis, or object storage path is unavailable. It is the Phase 7 proof that a live worker consumed an API-enqueued generation task and persisted PreviewSpec output.

## Phase 9 Hosted Provider Rollout

Phase 9 keeps the default path provider-off, local, and free. `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=false`, `AI_PROVIDER_CALLS_ENABLED=false`, and `AI_PROVIDER_DEFAULT=disabled` are the default example values. Provider-off validation must pass without `AI_PROVIDER_BFL_API_KEY` and must not make paid external calls.

The workbench parameter panel includes `生成模式` with `本地概念` and `BFL 托管`. Local deterministic remains available even when hosted status is blocked or unrefreshed. BFL is selectable only when operations capability metadata says it is enabled. The panel shows concept-preview labeling, hosted quota/rate/cost guard values, and safe blocked reasons such as `BFL 凭据未配置`; it must not render raw keys, tokens, secret names, or local paths.

Provider-on BFL smoke is manual-only because it requires real credentials and may spend money. Use ignored service env files, keep the smoke cheap, and disable hosted settings immediately afterward:

```powershell
# services/api/.env and services/worker/.env, never committed
V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=true
AI_PROVIDER_DEFAULT=bfl
AI_PROVIDER_MODEL=flux-2-pro-preview
AI_PROVIDER_CALLS_ENABLED=true
AI_HOSTED_DAILY_CALL_LIMIT=1
AI_HOSTED_RATE_LIMIT_PER_MINUTE=1
AI_MAX_ESTIMATED_COST_PER_JOB=0.25
AI_PROVIDER_BFL_API_KEY=replace-with-real-key-in-ignored-env
```

Manual provider-on smoke prerequisites:

1. Confirm the BFL account, model access, pricing, moderation policy, and credit status are acceptable for a one-job concept-preview smoke.
2. Start Docker services, run API migrations, and start API, worker, and web processes from shells that load the ignored service env files.
3. Open the workbench, refresh operations status, and confirm `BFL 托管` is enabled with small quota/cost values visible.
4. Submit one hosted concept-preview generation or child iteration.
5. Record workspace id, job id, model run id if available, version id, artifact id, provider, model, estimated/actual cost where available, and operations/failure status.
6. Disable `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED` and `AI_PROVIDER_CALLS_ENABLED`, remove the real BFL key from active shells, restart API/worker, and confirm local deterministic mode remains available.

Focused Phase 9 provider-off checks:

```powershell
cd services/api
uv run pytest -q tests/test_config.py tests/test_operations.py tests/test_generation.py tests/test_jobs.py
cd ../worker
uv run pytest -q tests/test_config.py tests/test_image_providers.py tests/test_generation_tasks.py
cd ../..
corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/api/generation.test.ts src/lib/api/operations.test.ts
corepack pnpm --filter @caragent/web lint
corepack pnpm --filter @caragent/web typecheck
corepack pnpm contracts:check
corepack pnpm smoke:worker -- --dry-run
corepack pnpm validate
```

If provider-on smoke is skipped because credentials are absent or cost approval is not available, record that skip explicitly in `.planning/phases/09-hosted-provider-rollout-mvp/09-HUMAN-UAT.md`. Do not claim live hosted success without a real provider-on run.

## Phase 10 Targeted Editing

Phase 10 keeps default validation local, provider-off, and free. Targeted edit requests are child iterations with a durable `edit_intent`: parent version id, selected target, normalized region, mask artifact metadata, prompt delta, route preference, and provider intent where applicable. Parent versions and artifacts remain immutable.

The web workbench uses PreviewSpec safe zones and overlay layers as selectable targets. In a generated version, enable `局部编辑`, select a safe zone or overlay layer, preview the mask, and submit a targeted edit from the iteration panel. Deterministic recomposition is used for safe layer edits such as text, logo, opacity, visibility, position, or scale changes. Provider-mask generation is guarded by feature flags, provider capability metadata, hosted preflight, quota/rate/cost guards, and worker-side validation.

Failure and retry behavior is metadata-driven. Invalid target or mask failures are non-retryable; provider, timeout, and storage failures may be retryable while preserving the original edit intent, parent version, mask artifact, route, and provider intent. The progress panel shows safe failure category, route, target, blocked reason, and retry eligibility without exposing provider secrets or raw vendor payloads.

Comparison is metadata-first. Targeted child versions expose a compare affordance in version history. The comparison panel shows parent/child labels, route (`deterministic_recomposition` or `provider_masked_generation`), selected target, prompt delta, changed fields, provider/model/cost evidence when present, and a normalized changed-region highlight. The highlight is not a pixel-perfect diff and does not imply print-ready or production validation.

Focused Phase 10 checks:

```powershell
cd services/api
uv run pytest -q tests/test_generation.py tests/test_jobs.py tests/test_operations.py
cd ../core
uv run pytest -q tests/test_models.py tests/test_generation_jobs.py tests/test_prompt_plans.py
cd ../worker
uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py tests/test_config.py
cd ../..
corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/workbench/store.test.ts src/lib/api/iteration.test.ts
corepack pnpm contracts:check
corepack pnpm smoke:worker -- --dry-run
corepack pnpm validate
```

Manual hosted mask smoke is optional and must be skipped unless all prerequisites are explicit: real credentials in ignored service env files, small quota/rate/cost guards, operator cost approval, account/model access, and verified provider mask support. If it is run, submit exactly one small masked edit, record job/version/artifact/model-run/provider/cost/route evidence, then disable hosted flags and remove active credentials. A skipped hosted mask smoke is acceptable local evidence; it is not proof of live hosted quality or account readiness.

## Web

Run the web workbench:

```powershell
pnpm dev:web
```

Focused web checks:

```powershell
pnpm --filter @caragent/web lint
pnpm --filter @caragent/web typecheck
pnpm --filter @caragent/web test
```

Browser-visible configuration is limited to public values such as `NEXT_PUBLIC_API_BASE_URL`. Provider keys, database URLs, Redis URLs, and S3 secrets must not be imported by web code. The workbench stores only workspace/brief resume ids in browser local storage. Canonical workspace, message, brief, asset, job, event, artifact, version, feedback, and export state is refetched from API-backed durable state.

## Contracts

FastAPI/Pydantic OpenAPI is the source of truth. The generated TypeScript client lives under `packages/contracts` and is consumed by `apps/web` wrappers for health, workspaces, messages, jobs, events, assets, asset rights, artifacts, versions, Phase 3/4 generation routes, Phase 5 iteration/feedback/export routes, and Phase 7 operations/cancel routes.

```powershell
pnpm contracts:generate
pnpm contracts:check
pnpm --filter @caragent/contracts test
pnpm --filter @caragent/contracts typecheck
```

If `pnpm contracts:check` fails with contract drift, regenerate contracts and review the changed OpenAPI/client artifacts before committing:

```powershell
pnpm contracts:generate
pnpm contracts:check
```

## Validation

Run the root unit-test surface for web, contracts, core, API, and worker:

```powershell
pnpm test
```

Run the aggregate validation gate from the root:

```powershell
pnpm validate
```

The aggregate runner executes:

```text
node scripts/check-host-prereqs.mjs
node scripts/check-env-examples.mjs
pnpm --filter @caragent/web lint
pnpm --filter @caragent/web typecheck
pnpm --filter @caragent/web test
cd services/api && uv run ruff check .
cd services/api && uv run mypy src
cd services/api && uv run pytest -q
cd services/core && uv run ruff check .
cd services/core && uv run mypy src
cd services/core && uv run pytest -q
cd services/worker && uv run ruff check .
cd services/worker && uv run mypy src
cd services/worker && uv run pytest -q
pnpm contracts:check
pnpm --filter @caragent/contracts typecheck
```

Run Docker-dependent smoke separately after local services are up; run worker smoke after API and worker processes are also running:

```powershell
pnpm infra:up
pnpm smoke:local
pnpm smoke:worker
pnpm infra:down
```

## Phase 10 Targeted Editing UAT

Use this browser UAT after `pnpm infra:up`, `uv run alembic upgrade head`, `pnpm dev:api`, a Windows-safe worker command with `--pool=solo --concurrency=1`, and `pnpm dev:web` are running:

1. Open or create a workspace and generate a local concept preview.
2. Select a generated version, enable `局部编辑`, toggle `安全区`, and select a safe zone such as `door-main`.
3. Select an overlay layer such as `text-1`, toggle mask preview, and confirm the mask is bounded inside the 2D preview.
4. Submit a recomposition-safe targeted edit such as moving text or changing the text content.
5. Confirm a child iteration job is created and the parent version remains visible and immutable.
6. After completion, compare parent and child versions and confirm route, target, prompt delta, provider/model evidence when present, and metadata-backed changed-region highlight are visible.
7. Trigger or inspect invalid-target/mask and unsupported-provider failures; confirm safe failure category, blocked reason, target, and retry eligibility are visible without secrets.
8. Confirm non-retryable targeted edit failures hide retry, while retryable provider/timeout/storage failures preserve edit intent on retry.
9. Repeat the visibility checks at desktop and mobile widths. There should be no horizontal document scroll, incoherent overlap, or hidden critical controls.

Optional hosted mask smoke follows the Phase 10 runbook above and is manual-only. If skipped, record the reason such as missing credentials, no cost approval, no hosted account access, or no verified mask-capable provider route.

## Phase 9 Hosted Provider Rollout UAT

Provider-off UAT uses the normal local setup with hosted flags disabled:

1. Start Docker infrastructure, run API migrations, and start API, worker, and web services.
2. Open the workbench and create or resume a workspace.
3. Refresh operations status and confirm `本地概念` is available without provider credentials.
4. Confirm `BFL 托管` is disabled when rollout, calls, credentials, or quota/cost guards are missing.
5. Confirm blocked hosted reasons are safe labels and the page does not show API keys, secrets, bearer tokens, or Windows paths.
6. Submit a local deterministic concept generation or child iteration and confirm provider/model intent is not sent for local mode.
7. Inspect progress/events and confirm generated output remains labeled as a concept preview.

Provider-on BFL UAT is optional and manual:

1. Meet the manual provider-on prerequisites in the Phase 9 runbook.
2. Refresh operations status and confirm `BFL 托管` is enabled, with daily/rate/cost guard values visible.
3. Select `BFL 托管`, submit exactly one concept-preview job, and wait for completion or a classified provider failure.
4. Record provider, model, job id, model run id if available, version id, artifact id, estimated cost, actual cost if returned, and whether fallback ran.
5. Confirm operations and workbench diagnostics show only safe failure/status labels.
6. Disable hosted flags and restart API/worker to return to provider-off mode.

If provider-on BFL UAT is skipped, record the exact reason such as missing credentials, no cost approval, or no hosted account access. A skipped provider-on UAT is acceptable for local verification, but it is not evidence of live hosted output quality or account readiness.

## Phase 7 Operations And Provider Strategy UAT

Use this browser UAT after `pnpm infra:up`, `uv run alembic upgrade head`, `pnpm dev:api`, a Windows-safe worker command with `--pool=solo --concurrency=1`, and `pnpm dev:web` are running:

1. Open the workbench and resume or create a workspace.
2. Refresh the progress panel and confirm `运维状态` shows compact provider, worker, queue, and hosted guard values without secrets or local file paths.
3. Submit a generation job and confirm queued/running status appears from durable job state.
4. While the job is queued or running, confirm `取消生成` is visible; after canceling, confirm the state becomes `已取消` and the cancel button is removed.
5. Force or inspect a failed generation path and confirm failure category, stage, provider, and recent event text are visible without raw API keys, secrets, tokens, or Windows paths.
6. Confirm failed jobs still expose retry, while succeeded, failed, and canceled terminal jobs do not expose cancel.
7. Run `pnpm smoke:worker` and record the workspace id, job id, version id, artifact id, and event count printed by the script.
8. Repeat the visibility checks at desktop and mobile widths. There should be no horizontal document scroll, incoherent overlap, or fresh console errors.

This UAT covers Phase 7 operational visibility, cancellation, and local worker smoke. It does not prove hosted provider production readiness, hosted image quality, commercial rights, auth, billing, production deployment, true 3D, or print-ready wrap output.

## Phase 6 Itasha And Template Intelligence UAT

Use this browser UAT after `pnpm infra:up`, `uv run alembic upgrade head`, `pnpm dev:api`, `pnpm dev:worker`, and `pnpm dev:web` are running:

1. Open the web workbench and resume or create a workspace.
2. Confirm the parameter panel shows `痛车设计控制`, `角色焦点`, `辅助图形`, `赛车/JDM 元素`, `字体意图`, and `配色协调`.
3. Edit at least one Phase 6 field and save it; confirm no generation job is automatically submitted by the parameter save.
4. Confirm `质量提示` appears when the brief or template produces warnings.
5. Select a generated version with PreviewSpec metadata and confirm `PreviewSpec 摘要` shows overlay, safe-zone, and warning counts.
6. Toggle `文字/Logo 图层`; confirm selected state changes and deterministic overlay labels remain bounded inside the 2D preview region.
7. Toggle `安全区`; confirm safe-zone labels such as `door-main` appear inside the preview and `模板参考区` remains visible.
8. Inspect concept export and export history; confirm PreviewSpec summary can appear with manifest context and the UI still says `概念预览，不是生产印刷文件。`.
9. Confirm missing-rights reference/logo assets are not used for generation and future true 3D, production handoff, print-ready export, broad template library, and marketplace/community gates remain disabled or deferred.
10. Repeat the visibility checks at desktop and mobile widths. There should be no horizontal document scroll, incoherent overlap, or fresh console errors.

This UAT covers Phase 6 itasha/template intelligence. It does not prove production-ready wrap files, vector logo/text conversion, broad vehicle-template coverage, true UV-mapped 3D, hosted provider quality, auth, billing, quotas, marketplace/community flows, or production deployment.

## Phase 5 Iteration And Export UAT

Use this browser UAT after `pnpm infra:up`, `uv run alembic upgrade head`, `pnpm dev:api`, `pnpm dev:worker`, and `pnpm dev:web` are running:

1. Open the web workbench and resume or create a workspace with at least one generated version and generated artifact.
2. Select a generated version from version history and confirm the comparison panel shows the current version, parent/base state, and parameter differences when a parent exists.
3. Enter an iteration request and submit it; confirm the UI reports a child iteration submission while the parent version remains visible.
4. Select the child version after the worker completes and confirm lineage depth/parent context is visible.
5. Add a rating, approval or rejection state, and comment; confirm feedback history renders the saved record for the selected version.
6. Select PNG or JPG in concept export, create the export, and confirm export history renders the saved record.
7. Inspect the manifest preview and confirm it includes the selected version/artifact context and the disclaimer `概念预览，不是生产印刷文件。`.
8. Confirm true 3D, production handoff, print preflight, layered source export, and marketplace/community gates remain disabled or deferred.
9. Repeat the visibility checks at desktop and mobile widths. The iteration, feedback, concept export, manifest, history, and future-gate controls should have no horizontal document scroll or incoherent overlap.

This UAT covers Phase 5 iteration, feedback, and concept export. It does not prove print-ready wrap production files, layered source packages, true UV-mapped 3D, hosted provider quality, auth, billing, quotas, marketplace/community flows, or production deployment.

## Phase 4 Workbench UAT

Use this browser UAT after `pnpm infra:up`, `uv run alembic upgrade head`, `pnpm dev:api`, `pnpm dev:worker`, and `pnpm dev:web` are running:

1. Open the web workbench.
2. Confirm the first screen shows the chat rail, 2D preview workspace, parameters, asset controls, progress/events, version history, and deferred future gates.
3. Submit a design request in chat and confirm a durable user message plus structured brief feedback appears.
4. Edit supported parameters and save them without automatically submitting a generation job.
5. Upload or inspect a reference asset; confirm missing-rights assets cannot be selected for generation until rights/source details are confirmed.
6. Start generation from the current brief and confirm queued/running/succeeded/failed states and recent events are visible.
7. Select a generated version/history item and confirm the selected 2D preview context changes without clearing chat, parameters, assets, or progress state.
8. Confirm true 3D, print-ready export, marketplace/community, and production handoff controls are disabled, experimental, or explicitly deferred.
9. Repeat the visibility checks at desktop and mobile widths; there should be no incoherent text or panel overlap, and the chat input should remain reachable.

This UAT covers the Phase 4 MVP workbench. It does not prove production-ready wrap export, true UV-mapped 3D, hosted provider quality, auth, billing, marketplace/community flows, quotas, or production deployment.

## Phase 3 Generation UAT

Use this browser UAT after `pnpm infra:up`, `uv run alembic upgrade head`, `pnpm dev:api`, `pnpm dev:worker`, and `pnpm dev:web` are running:

1. Open the web shell.
2. Click `创建持久工作区`.
3. Confirm a workspace ID appears.
4. Edit `自然语言 brief` or keep the sample.
5. Click `创建概念任务`.
6. Confirm `结构化 brief`, `生成任务`, `生成素材`, and `设计版本` metrics update from API state.
7. Refresh the browser and confirm the stored workspace/job state can be refreshed.
8. For retry behavior, use API tests or a forced failed worker test; do not rely on hosted provider failure during baseline UAT.

This UAT does not cover the full GPT-style workbench, upload manager, rich 2D preview controls, export UX, production handoff, true 3D, auth, billing, quotas, or hosted provider quality.

## Phase 2 Durable UAT

Use this browser UAT after `pnpm infra:up`, `uv run alembic upgrade head`, `pnpm dev:api`, and `pnpm dev:web` are running:

1. Open the web shell.
2. Click `创建持久工作区`.
3. Confirm a workspace ID appears and message count becomes `1`.
4. Click `创建模拟任务`.
5. Confirm a queued job status and at least one event appear.
6. Refresh the browser.
7. Confirm the same workspace ID, message count, job status, and event count are refetched.
8. Click `刷新状态` and repeat `创建模拟任务` to confirm the idempotency key returns the same durable job state.

This UAT does not cover real image generation, full workbench chat, uploads in the web UI, 2D/3D preview, export, auth, billing, or production handoff.

## Requirement Coverage

| Requirement | Covered By | Verification |
| ----------- | ---------- | ------------ |
| FOUND-01 | Local run commands for `pnpm infra:up`, `pnpm dev:api`, `pnpm dev:worker`, `pnpm dev:web`, and `pnpm smoke:local`. | Start Docker services, run the app processes, then run `pnpm smoke:local`. |
| FOUND-02 | Aggregate lint, type-check, and test command surface in `pnpm validate`. | Run `pnpm validate`; focused checks are available for web, contracts, API, and worker. |
| FOUND-03 | FastAPI OpenAPI export, `packages/contracts` generated TypeScript client, `pnpm contracts:generate`, `pnpm contracts:check`, and web generated-client import. | Run `pnpm contracts:generate`, `pnpm contracts:check`, and web tests that exercise the generated health wrapper. |
| FOUND-04 | Root/web/API/worker `.env.example` files plus service `.env` loading and API/worker settings tests. | Run `node scripts/check-env-examples.mjs`, API config tests, and worker settings tests through `pnpm validate`. |
| DATA-01 | Workspace and conversation persistence services/routes plus web refresh proof. | Run API workspace tests and the Phase 2 durable UAT. |
| DATA-02 | Structured brief, artifact, version, feedback, export, model-run, and cost ledger models. | Run core/API job tests and Alembic migration smoke. |
| DATA-03 | Asset upload validation and object-key metadata records. | Run API asset tests and MinIO-backed `pnpm smoke:local`. |
| DATA-04 | Rights/source metadata is required before assets can be accepted. | Run API asset rights tests. |
| DATA-05 | Durable job status and events are stored in PostgreSQL and exposed to web wrappers. | Run API job tests, worker job tests, and web page tests. |
| DATA-06 | Idempotency keys reuse duplicate job requests. | Run API job tests and Phase 2 durable UAT repeat-job step. |
| DATA-07 | Worker local simulation updates durable job/model-run/cost state without provider calls. | Run worker tests and `pnpm smoke:local`. |
| GEN-01 | Natural-language request creates a reusable structured generation brief. | Run core generation brief tests, API generation tests, and Phase 3 web UAT. |
| GEN-02 | Prompt plan records template/view, prompt text, prompt payload, provider/model, parameters, and inputs. | Run `services/core` prompt plan tests and inspect model run rows from Phase 3 smoke. |
| GEN-03 | Supported template/view and local deterministic provider produce a 2D concept job path. | Run worker generation task tests and `pnpm smoke:local`. |
| GEN-04 | Generated output is stored as immutable artifact and design version linked to prompt/model-run trace. | Run worker generation task tests and Phase 3 smoke. |
| GEN-05 | Missing-rights reference assets are blocked before provider execution. | Run worker generation task tests for missing rights. |
| GEN-06 | Web proof can submit a brief/generation request and display durable result state. | Run `pnpm --filter @caragent/web test` and Phase 3 web UAT. |
| GEN-07 | Failed generation jobs expose durable errors and retry creates a new attempt. | Run API generation retry tests and worker failure tests. |
| UI-01 | GPT-style chat panel creates durable user messages, updates/creates the current brief, and shows assistant/system feedback from canonical state. | Run `corepack pnpm --filter @caragent/web test` and Phase 4 Workbench UAT. |
| UI-02 | Parameter panel displays and saves supported structured brief fields through the update-brief route. | Run `corepack pnpm --filter @caragent/web test` and Phase 4 Workbench UAT. |
| UI-03 | Asset panel uploads/lists reference assets, records rights/source details, previews metadata, and blocks missing-rights assets from generation selection. | Run `corepack pnpm --filter @caragent/web test` and Phase 4 Workbench UAT. |
| UI-04 | Progress panel renders queued/running/succeeded/failed job states, retry action, and recent durable events. | Run `corepack pnpm --filter @caragent/web test` and Phase 4 Workbench UAT. |
| UI-05 | 2D preview workspace supports selected artifact/version context, local zoom/reset, thumbnail history, and supported view switching. | Run `corepack pnpm --filter @caragent/web test` and Phase 4 Workbench UAT at desktop/mobile widths. |
| UI-06 | Version history selection changes preview context without clearing chat, parameters, assets, or job history. | Run `corepack pnpm --filter @caragent/web test` and Phase 4 Workbench UAT. |
| UI-07 | True 3D, print-ready export, marketplace/community, and production handoff are disabled, experimental, or explicitly deferred. | Run `corepack pnpm --filter @caragent/web test` and Phase 4 Workbench UAT. |
| ITER-01 | Child iteration submission preserves the parent version by creating a new job/version lineage instead of overwriting existing versions. | Run API generation tests, worker generation task tests, web tests, and Phase 5 UAT. |
| ITER-02 | Targeted style/palette/text/composition/coverage changes are captured as child iteration request metadata and worker version parameters. | Run API generation tests, worker generation task tests, and Phase 5 UAT. |
| ITER-03 | Lineage and parameter comparison render parent/current version context in the workbench. | Run `corepack pnpm --filter @caragent/web test` and Phase 5 UAT. |
| ITER-04 | Feedback supports rating, approval/rejection/neutral state, comments, durable API submission, and selected-version history. | Run core/API job tests, web tests, and Phase 5 UAT. |
| ITER-05 | Concept export supports selected-version PNG/JPG records with a metadata JSON manifest. | Run core/API job tests, web tests, and Phase 5 UAT. |
| ITER-06 | Export UI and manifest clearly label the output as a concept preview and not print-ready. | Run core/API job tests, web tests, docs token check, and Phase 5 UAT. |
| QUAL-01 | Itasha controls for character focus, supporting graphics, racing/JDM cues, typography intent, and color harmony are stored in core/API contracts and editable in the workbench. | Run core/API/web Phase 6 tests and Phase 6 UAT. |
| QUAL-02 | Text/logo overlays are represented as deterministic PreviewSpec layers, rendered by the local provider where possible, and visible through workbench toggles. | Run worker/web Phase 6 tests and Phase 6 UAT. |
| QUAL-03 | Template normalization, readability, and preview warnings are stored and shown as lightweight `质量提示`. | Run core/web Phase 6 tests and Phase 6 UAT. |
| QUAL-04 | Supported template safe zones are stored in core data and displayed through the workbench `安全区` toggle and `模板参考区`. | Run core/web Phase 6 tests and Phase 6 UAT at desktop/mobile widths. |
| QUAL-05 | PreviewSpec metadata is persisted in prompt payloads, generated version parameters, artifact metadata, contracts, and export manifest views for later renderer work. | Run core/API/worker/web/contract Phase 6 checks and `pnpm contracts:check`. |
| OPS-01 | `/operations/provider-status` exposes provider configuration, worker/queue status, and recent failure summaries without secrets. | Run API operations tests, web operations tests, Phase 7 UAT, and `pnpm smoke:worker`. |
| OPS-02 | Worker failures are classified into structured categories/stages and persisted as job/event/model-run metadata. | Run worker generation task tests and inspect failed progress metadata in web tests/UAT. |
| OPS-03 | Provider routing, bounded retry attempts, local fallback, timeout settings, and hosted guard settings are configuration-driven. | Run worker config/provider tests and env example checks. |
| OPS-04 | Queued/running generation jobs can be canceled through API/UI and terminal jobs reject or hide cancellation. | Run API generation/job tests, web page tests, and Phase 7 UAT. |
| OPS-05 | Hosted calls require daily, per-minute, and estimated per-job cost guards before provider execution. | Run worker hosted preflight tests and API operations summary tests. |
| OPS-06 | Live local queue smoke proves API-enqueued jobs are consumed by the worker and produce durable PreviewSpec output. | Run `pnpm smoke:worker` with Docker, API, and worker running. |
| V2-PROVIDER-01 | Hosted provider credentials, model, capability map, timeout, retry, fallback, and quota policy are configuration-driven and documented. | Run API/worker config tests, env example checks, `pnpm contracts:check`, and Phase 9 provider-off verification. |
| V2-PROVIDER-02 | Hosted generation can be submitted only when rollout, calls, credentials, quota/rate/cost guards, and supported provider/model checks allow it. | Run API generation/preflight tests, worker generation task tests, web provider selector tests, and Phase 9 UAT. |
| V2-PROVIDER-03 | Provider/model/request parameters, prompt plan, input assets, estimated/actual cost, fallback path, and error category are durable. | Run worker generation task tests, API job/operations tests, and inspect Phase 9 verification notes. |
| V2-PROVIDER-04 | Hosted failures are visible to user/operator surfaces without exposing secrets. | Run BFL adapter tests, worker failure classification tests, API operations tests, web diagnostics tests, and Phase 9 UAT. |
| V2-PROVIDER-05 | Local deterministic provider stays available as the free default test/fallback path. | Run provider-off web tests, worker local deterministic tests, `pnpm smoke:worker -- --dry-run`, and provider-off UAT. |
| V2-EDIT-01 | Users can select safe zones or overlay layers in the workbench and preview a targeted edit mask. | Run Phase 10 web tests and Targeted Editing UAT. |
| V2-EDIT-02 | Edit intent, selected region, mask data, parent version, prompt delta, provider parameters, and child version evidence are durable. | Run API generation/jobs tests, worker generation tests, and inspect Phase 10 verification notes. |
| V2-EDIT-03 | Deterministic recomposition handles safe layer edits without hosted provider calls. | Run worker generation/provider tests and provider-off targeted edit UAT. |
| V2-EDIT-04 | Provider-mask routes are capability-gated, feature-flagged, quota-guarded, and fail closed when unsupported. | Run API operations/generation tests, worker config/generation tests, and optional hosted mask smoke only with approval. |
| V2-EDIT-05 | Parent/child comparison shows recomposition versus provider-generated route evidence and changed-region metadata. | Run Phase 10 web comparison tests and Targeted Editing UAT. |

## Source Coverage

| Source | Coverage In Current Milestone |
| ------ | ------------------- |
| Phase 1 goal | `pnpm validate`, `pnpm smoke:local`, `pnpm dev:web`, `pnpm dev:api`, `pnpm dev:worker`, and `pnpm contracts:check` prove the foundation can be configured, run, validated, and understood from root commands. |
| Phase 2 goal | `services/core`, API product routes, Alembic migrations, generated contracts, worker local simulation, web refresh proof, and `pnpm smoke:local` prove durable workspace, asset, job, event, and output-ledger paths. |
| Phase 3 goal | Core generation brief/prompt planning, worker generation task, API generation routes, generated contracts, web concept proof, and Phase 3 smoke prove the first text-to-2D slice without hosted keys. |
| Phase 4 goal | Workbench components, TanStack Query-backed API wrappers, local preview state, web tests, focused checks, and Browser UAT prove chat, parameters, assets, progress, 2D preview, history, and future gates. |
| Phase 5 goal | Backend create routes, worker lineage metadata, generated contracts, workbench iteration/comparison/feedback/export panels, web tests, focused backend checks, and Browser UAT prove versioned iteration, feedback, and concept export. |
| Phase 6 goal | Core itasha fields, safe-zone helpers, PreviewSpec prompt payloads, worker/provider metadata persistence, generated contracts, workbench controls/toggles, docs, verification, and Browser UAT prove itasha/template intelligence as concept-preview guidance. |
| Phase 7 goal | Operations API, structured worker failures, cancel/revoke handoff, retry/fallback settings, hosted quota guards, workbench operations UI, docs, Browser UAT, and `pnpm smoke:worker` prove the local operational path. |
| Phase 8 goal | Archived v1.0 baseline, compatibility checks, migration safety checks, and default-off V2 flags prove V2 starts from a stable baseline. |
| Phase 9 goal | Provider capability contracts, BFL adapter tests, API/worker preflight gates, provider trace/failure diagnostics, workbench selector tests, docs, verification, and provider-off/provider-on UAT runbooks prove controlled hosted rollout readiness without enabling hosted calls by default. |
| Phase 10 goal | Edit intent contracts, workbench selection/mask preview, deterministic recomposition, provider-mask guardrails, retry/failure diagnostics, comparison UI, docs, verification, and UAT checklists prove targeted editing without enabling hosted calls by default. |
| FOUND-01 | `infra/compose.yml`, `infra/README.md`, `scripts/smoke-local.mjs`, and the documented dev commands cover local web, API, worker, PostgreSQL, Redis, and MinIO run paths. |
| FOUND-02 | `scripts/validate-all.mjs` sequences frontend, contract, API, and worker lint/type/test checks from `pnpm validate`. |
| FOUND-03 | `services/api/src/caragent_api/scripts/export_openapi.py`, `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/client.ts`, `scripts/check-contracts.mjs`, and `apps/web/src/lib/api/health.ts` cover generated API contracts. |
| FOUND-04 | `.env.example`, service env examples, service `.env` loading, API/worker typed settings, env guard, and config tests cover database, queue, storage, provider placeholders, CORS, and runtime mode without code changes. |
| OPS-06 | `scripts/smoke-worker-queue.mjs`, `pnpm smoke:worker`, and Phase 7 docs cover the live worker queue smoke path. |
| Research constraints | The monorepo keeps `apps/web`, `services/api`, `services/worker`, `packages/contracts`, and `infra` ownership separate; Python stays `uv`-managed; frontend contracts come from OpenAPI; local infrastructure is Docker Compose; validation is root-runnable. |

| Locked Decision | Shipped Command Or File |
| --------------- | ----------------------- |
| D-01 | Monorepo boundaries are represented by `apps/web`, `services/api`, `services/worker`, `packages/contracts`, and `infra`. |
| D-02 | Worker source stays under `services/worker` and web imports generated contracts through `@caragent/contracts`, not backend internals. |
| D-03 | No Turborepo, Nx, Kubernetes, LangGraph, ComfyUI, self-hosted model service, or provider SDK workflow was added. |
| D-04 | `package.json`, `.node-version`, `.python-version`, and service `pyproject.toml` files document pnpm and uv workflows. |
| D-05 | `.node-version`, `.python-version`, and `packageManager` pin the intended runtime baselines. |
| D-06 | Root scripts delegate to package/service owners while local service commands remain independently runnable. |
| D-07 | `infra/compose.yml` owns PostgreSQL, Redis, and MinIO; app processes run locally by default. |
| D-08 | `.env.example` exposes configurable ports for web, API, PostgreSQL, Redis, and MinIO. |
| D-09 | API `/health`, Compose healthchecks, and smoke checks prove foundation health plus Phase 2 migration/data smoke and Phase 3 local deterministic generation smoke. |
| D-10 | FastAPI/Pydantic OpenAPI is exported into `packages/contracts/openapi/openapi.json`. |
| D-11 | `packages/contracts/orval.config.ts` and the generated client define the TypeScript contract path. |
| D-12 | `/health` remains the baseline contract surface; Phase 2 adds generated workspace/message/job/event wrappers. |
| D-13 | `pnpm contracts:check` and `scripts/check-contracts.mjs` fail on generated artifact drift. |
| D-14 | Only example env files are committed; real env files remain ignored. |
| D-15 | API and worker settings use typed `pydantic-settings` validation, load service `.env` files, and reject unsafe config. |
| D-16 | AI provider keys use the `AI_PROVIDER_*` contract, are parsed and redacted as placeholders only, and hosted calls remain opt-in. |
| D-17 | `pnpm validate` covers lint, type-check, tests, env guard, contract drift, and service checks. |
| D-18 | Web, API, worker, core, and contract tests stay small and focused on the current phase behavior. |
| D-19 | Local commands and docs are the hard requirement; no CI dependency blocks local milestone validation. |
| D-20 | `apps/web` contains the Next.js shell, design-system baseline, durable-state proof, generation proof, and Phase 4 integrated workbench. |
| D-21 | Full GPT-style workbench behavior moved from deferred Phase 3 scope into the Phase 4 MVP surface. |
| D-22 | Hosted provider calls remain opt-in, quota-guarded, and revalidation-dependent; local deterministic generation is the baseline evidence path. |
| D-23 | Phase 9 hosted BFL smoke is manual-only, credential-gated, cost-guarded, and reversible; provider-off validation remains the default completion path. |
| D-24 | Phase 10 targeted edits are child iterations with immutable parents, metadata-backed comparison, deterministic recomposition for safe layer edits, and provider-mask smoke as manual-only. |

Deferred items after Phase 10 remain out of scope for this milestone until later phases implement them: production-ready export UX, true 3D/UV preview, broad reference-guided generation, enhanced handoff packaging, auth, billing, marketplace/community flows, and production handoff. Hosted output quality, pricing, moderation, account status, mask support, and commercial terms must still be rechecked before any non-local output is treated as production-ready evidence.

## Security Notes

- Commit `.env.example` files only; keep real env files, keys, certificates, and local overrides ignored.
- AI provider keys use `AI_PROVIDER_OPENAI_API_KEY`, `AI_PROVIDER_FAL_API_KEY`, and `AI_PROVIDER_BFL_API_KEY` as configuration placeholders. They are parsed and redacted; hosted calls require explicit `AI_PROVIDER_CALLS_ENABLED=true` in ignored env files.
- Hosted BFL calls also require `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=true`, explicit daily, per-minute, and estimated cost guards before provider execution; missing guard values block the job before any provider call.
- Provider-on smoke should use the lowest practical daily/rate/cost guard values and must be reversed after the one-job smoke.
- Provider-mask targeted edit smoke is manual-only; unsupported mask capability must fail closed instead of falling back to full regeneration.
- Workbench operational text should render structured category/stage/provider values and sanitize raw diagnostic text before displaying it.
- Local deterministic generation remains the baseline verification path and must not require hosted keys.
- Docker Compose credentials and ports are local-only and not a production hardening guide.
- CORS origins are explicit configuration values; wildcard CORS is rejected by API settings tests.
- Contract drift is blocked by `pnpm contracts:check` before frontend/backend API changes are accepted.

## Troubleshooting

| Symptom | What It Means | Fix |
| ------- | ------------- | --- |
| `uv not installed` or `uv` is not recognized | Python service dependency manager is missing from `PATH`. | Install `uv`, open a new shell, run `cd services/api && uv sync --dev`, then `cd ../worker && uv sync --dev`. |
| Node/Corepack/pnpm fails with `EPERM: operation not permitted` under a Windows user profile path | The shell resolves Node or Corepack through a user-profile directory that the current sandbox cannot access. | Use an unrestricted host shell with Node `22.15.0`, or in the current shell set `NODE_OPTIONS="--preserve-symlinks --preserve-symlinks-main"` and `COREPACK_HOME` to a writable directory before running `corepack prepare pnpm@11.0.8 --activate`. Then run `pnpm install` and `pnpm validate`. |
| Docker daemon unavailable | Docker CLI exists but Docker Desktop/Engine is not running or not reachable; `pnpm smoke:local` fails by design because live services were not checked. | Start Docker Desktop/Engine, confirm `docker info`, then run `pnpm infra:up`, `pnpm smoke:local`, and `pnpm infra:down`. Use `node scripts/smoke-local.mjs --allow-docker-unavailable` only to document a sandbox blocker, not as completion evidence. |
| Docker Compose image pull failure | Compose cannot pull PostgreSQL, Redis, or MinIO images. | Check network access, registry access, and the pinned image names in `infra/compose.yml`; retry `pnpm infra:up`. |
| Ports already in use | A local process already owns `3000`, `8000`, `5432`, `6379`, `9000`, or `9001`. | Stop the conflicting process or override the matching port in a local env file before restarting services. |
| Contract drift failure | Generated OpenAPI or TypeScript client artifacts differ from the committed baseline. | Run `pnpm contracts:generate`, review the generated files, then re-run `pnpm contracts:check`. |
| Wildcard CORS rejection | API settings rejected `CORS_ORIGINS=*` in an unsafe mode. | Set explicit origins such as `http://localhost:3000`; do not use wildcard origins with credentials. |
| Missing non-local config | `RUNTIME_MODE` is not `local`, but required URLs, secrets, or provider settings are absent. | Add explicit database, Redis, S3, CORS, and `AI_PROVIDER_*` config through ignored service `.env` files or deployment configuration. |
| `pnpm smoke:worker` reports worker unavailable | API is reachable but `/operations/provider-status` cannot see a live worker. | Start the worker in a separate shell with `uv run celery -A caragent_worker.app worker --loglevel=INFO --pool=solo --concurrency=1`, then rerun the smoke. |
| Hosted generation fails during `hosted_preflight` | A hosted provider was selected, but daily, per-minute, or estimated per-job cost guard values are missing or exceeded. | Configure `AI_HOSTED_DAILY_CALL_LIMIT`, `AI_HOSTED_RATE_LIMIT_PER_MINUTE`, and `AI_MAX_ESTIMATED_COST_PER_JOB`, or switch back to the local deterministic provider. |
| `BFL 托管` is disabled in the workbench | Operations status reports that rollout, calls, credentials, or quota/cost guards are missing. | Keep using `本地概念`, or configure all Phase 9 provider-on smoke prerequisites in ignored service env files and refresh operations status. |
| BFL returns moderation, validation, credit, or rate-limit failures | The provider call reached BFL but failed under provider policy, request validation, account credit, or rate limits. | Inspect safe `provider_failure_kind` and `provider_status` in operations/job metadata, adjust the request or account state, keep secrets out of screenshots/logs, and disable hosted flags when done. |

## Phase Boundary

Phase 10 is complete when the foundation, durable data/job/asset surfaces, structured brief/prompt trace, local deterministic generation task, API generation routes, integrated web workbench, selected-version iteration, lineage comparison, feedback, concept export manifest, itasha controls, PreviewSpec metadata, safe-zone overlays, operations API, structured failures, cancellation, retry/fallback settings, hosted provider capability map, BFL adapter, hosted preflight, provider trace/cost/failure diagnostics, workbench provider selector, targeted edit schemas, mask preview, deterministic recomposition, provider-mask guardrails, retry-safe targeted failures, comparison UI, provider-off validation, hosted smoke runbooks, and Browser UAT checklists can be run from documented commands. Production-ready wrap output, layered source packages, print preflight, true UV-mapped 3D, broad vehicle-template libraries, reference-guided generation, enhanced handoff packages, auth, billing, marketplace/community flows, and production deployment remain deferred to later phases.
