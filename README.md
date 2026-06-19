# 痛车设计 Agent

痛车设计 Agent is an AI web workbench for turning natural-language itasha design requests into previewable, iterable, and exportable concept designs.

Phase 1 established the runnable foundation. Phase 2 adds durable workspaces, messages, asset metadata and rights records, job/event/output ledgers, generated frontend wrappers, worker no-provider simulation, and a minimal web refresh/status proof. Phase 3 adds structured generation briefs, prompt traceability, a local deterministic text-to-2D generation slice, generation API routes, and a compact web proof. Phase 4 integrates those pieces into the first real web workbench: GPT-style chat-to-brief, editable parameters, reference asset upload and rights confirmation, job progress/events, 2D preview controls, version history, and explicit future-feature gates. Phase 5 adds selected-version iteration, parent/child lineage comparison, feedback/rating/approval records, and concept export records with a metadata manifest labeled as not print-ready. Phase 6 adds itasha-specific controls, deterministic text/logo overlay evidence, safe-zone/template warnings, and PreviewSpec metadata for future renderer work while keeping output a concept preview. Phase 7 adds provider/worker operations visibility, classified failures, job cancellation, bounded retry/fallback controls, hosted-call quota guards, and a live worker queue smoke path. Phase 8 starts V2 from a verified V1 baseline. Phase 9 adds a default-off hosted BFL rollout path with explicit provider selection, preflight guards, trace/cost/failure diagnostics, and local deterministic fallback. Phase 10 adds targeted edit selection, mask preview, deterministic recomposition, provider-mask guardrails, retry-safe failure states, and parent/child comparison with metadata-backed changed-region highlighting. Phase 11 adds role-based reference guidance, rights/source snapshots, provider unsupported-role warnings, durable reference trace metadata, workbench diagnostics, and child-iteration reference reuse. Phase 12 adds a feature-flagged lightweight Three.js 3D preview shell, Preview3DSpec contracts, camera controls, screenshot artifact persistence, browser UAT evidence, and persistent non-production/UV-not-verified labels. Phase 13 adds a feature-flagged enhanced concept handoff ZIP with stable manifest, Markdown reports, prompt/provider trace, reference manifest, package export ledger records, Workbench ZIP UX, and rights/source guardrails. Phase 14 hardens the V2 MVP release with fresh aggregate validation, Docker smoke, hosted-provider smoke runbook, Browser UAT evidence, feature-flag docs, and release notes.

The project still does not implement production-ready wrap output, authentication, billing, verified production UV mapping, hosted provider production rollout by default, marketplace/community flows, or production deployment. The lightweight 3D viewer and enhanced handoff ZIP are concept-only review aids, not print-shop proof or print-ready production handoff. `init.MD` and `UI.png` remain seed references for product direction.

## Repository Layout

| Path | Purpose |
| ---- | ------- |
| `apps/web` | Next.js workbench with chat, itasha parameters, assets, progress, 2D preview, PreviewSpec overlays/safe zones, version history, iteration, feedback, concept export, and deferred future gates. |
| `services/core` | Shared SQLAlchemy durable-data models, repositories, and services. |
| `services/api` | FastAPI control-plane service, product/generation routes, Alembic migrations, OpenAPI export, and local smoke scripts. |
| `services/worker` | Celery work-plane process, local deterministic generation, BFL hosted adapter behind guardrails, and text-to-2D generation task. |
| `packages/contracts` | OpenAPI and generated TypeScript contracts. |
| `infra` | Local PostgreSQL, Redis, and MinIO Compose services. |
| `docs/development.md` | Full developer runbook for foundation, durable data, generation, V2 workbench operations, release validation, Docker smoke, hosted-provider smoke, Browser UAT, and troubleshooting. |

## Quickstart

Install prerequisites from `.node-version`, `.python-version`, and `package.json`, then run:

```powershell
pnpm install
cd services/core
uv sync --dev
cd ../api
uv sync --dev
uv run alembic upgrade head
cd ../worker
uv sync --dev
cd ../..
pnpm contracts:generate
pnpm validate
pnpm infra:up
pnpm smoke:local
pnpm smoke:worker -- --dry-run
pnpm dev:api
pnpm dev:worker
pnpm dev:web
```

Use separate terminals for `pnpm dev:api`, `pnpm dev:worker`, and `pnpm dev:web`.

## Phase 8 / V2 Readiness Gate

Phase 8 starts V2 from the archived v1.0 baseline instead of enabling new V2 behavior immediately. The baseline evidence lives in `.planning/phases/08-v1-closure-and-v2-readiness-gate/08-READINESS-BASELINE.md` and references the `v1.0` tag, the v1.0 milestone archive, the audit verdict, and the latest Phase 7 operations closure.

Before enabling any V2 feature flag, prove the V1 local path still runs with the existing command surface:

```powershell
pnpm validate
pnpm contracts:check
pnpm compat:v1
pnpm migration:safety
pnpm infra:up
pnpm smoke:local
pnpm smoke:worker -- --dry-run
```

Use `pnpm smoke:worker` without `--dry-run` only on a host where Docker services, API migrations, the API process, and the worker process are running. Hosted provider production rollout remains Phase 9 scope and must stay disabled by default during Phase 8 readiness work.

For the Phase 2 browser refresh proof, start infrastructure and the API/web services, open the web shell, click `创建持久工作区`, click `创建模拟任务`, refresh the browser, and confirm the same workspace/job state is refetched from the API.

For the Phase 3 concept-generation proof, keep the same workspace, edit `自然语言 brief` if needed, click `创建概念任务`, and confirm the page shows a structured brief, queued/succeeded generation job, generated artifact count, and design version count from API-backed durable state.

For the Phase 4 workbench, start the same API, worker, infrastructure, and web services, then use the first screen as the app surface: submit design text in chat, inspect/save structured parameters, upload reference assets and confirm rights before selecting them for generation, monitor job status/events, inspect 2D preview/version history, and confirm production UV-mapped 3D/export/marketplace gates remain disabled or deferred.

For the Phase 5 iteration/export flow, use a generated version from the workbench, select a version in history, submit a child iteration request, inspect lineage/parameter comparison, save feedback or approval notes, and create a PNG/JPG concept export. The export UI and manifest describe the output as a concept preview and not print-ready; production handoff, layered source packages, print preflight, production UV-mapped 3D, and marketplace flows remain deferred.

For the Phase 6 itasha/template intelligence flow, edit `痛车设计控制` fields in the parameter panel, inspect `质量提示`, select a generated version with `PreviewSpec 摘要`, toggle `文字/Logo 图层` and `安全区`, and inspect the template reference zone. Text/logo overlays and safe zones are concept-preview guidance; they do not create print-ready wrap files or verified production UV output.

For the Phase 7 operations flow, keep Docker infrastructure, API, worker, and web running. Use the progress panel to refresh compact provider/worker status, inspect failure classification, cancel queued/running jobs, and confirm terminal canceled jobs no longer show the cancel control. Use `pnpm smoke:worker` for a live API -> Redis/Celery -> worker -> durable artifact/version smoke once the worker is running.

For the Phase 9 hosted-provider rollout flow, default validation remains provider-off and free. Use the parameter panel `生成模式` selector to confirm `本地概念` is available without credentials, `BFL 托管` is disabled when rollout, calls, credentials, or quota/cost guards are missing, and no API keys/secrets/paths appear in workbench or operations diagnostics. Provider-on BFL smoke is manual-only: put real credentials in ignored service env files, set `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=true`, `AI_PROVIDER_CALLS_ENABLED=true`, `AI_PROVIDER_DEFAULT=bfl`, `AI_PROVIDER_MODEL=flux-2-pro-preview`, and small `AI_HOSTED_DAILY_CALL_LIMIT`, `AI_HOSTED_RATE_LIMIT_PER_MINUTE`, and `AI_MAX_ESTIMATED_COST_PER_JOB` guard values. Submit one concept-preview job, record the job/version/artifact/model-run evidence, then disable hosted flags again.

For the Phase 10 targeted edit flow, use a generated version with PreviewSpec metadata, enable `局部编辑`, select a safe zone or overlay layer, preview the mask, and submit a recomposition-safe edit such as moving or changing text. The worker creates a child version and leaves the parent immutable. Comparison shows parent/child, route (`deterministic_recomposition` or `provider_masked_generation`), target, prompt delta, provider/model evidence when present, and a metadata-backed changed-region highlight. Provider-mask hosted smoke is manual-only and skippable without credentials: keep default validation provider-off, and only run a paid mask edit after explicit cost approval, small quota/rate/cost guards, and verified provider mask support.

For the Phase 11 reference-guided generation flow, upload reference assets, confirm rights/source metadata, assign one of the six roles (`角色`, `风格`, `车辆`, `Logo`, `配色`, `仅灵感`), and save parameters so `reference_usage` is persisted. Local deterministic generation records references as prompt guidance and durable trace metadata only. BFL reference-image input remains unsupported in the current capability map, so unsupported roles show `引用受限` / `供应商不支持` or fail closed before provider execution. Generated versions, progress diagnostics, child iterations, and concept export source data carry compact reference trace evidence. Hosted reference smoke is manual-only and skippable without real credentials, cost approval, quota guards, and verified provider support.

For the Phase 12 lightweight 3D preview flow, set `V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED=true`, generate or seed a version with PreviewSpec metadata, then use the `3D 预览` tab on the selected version. The viewer uses the `generic-side-coupe-lightweight-v1` shell for compatible side-view templates, exposes rotate/zoom/reset/screenshot controls, and stores screenshots as immutable `preview_3d_screenshot` artifacts linked to the version. Unsupported templates show a clear 2D fallback and keep generation, targeted edits, references, and export available. The 3D panel always remains `非生产贴膜参考`; it is not production UV or print-ready wrap evidence.

For the Phase 13 enhanced handoff package flow, set `V2_ENHANCED_HANDOFF_PACKAGE_ENABLED=true` for the API and `NEXT_PUBLIC_V2_ENHANCED_HANDOFF_PACKAGE_ENABLED=true` for the web app, select a generated version with a `generated_image` artifact, confirmed included-reference rights/source metadata, and optional `preview_3d_screenshot` artifacts, then choose `ZIP` in the export panel. The Workbench shows `交接包预览`, concept-only copy, required package files, warnings, and an export history row after `POST /workspaces/{workspace_id}/versions/{version_id}/exports` records an `enhanced_concept_handoff_zip`. Missing or rejected rights/source metadata blocks ZIP creation while PNG/JPG concept export controls remain available. The ZIP is for concept review only and is not a print-ready handoff.

## V2 MVP Release Validation

Phase 14 is the V2 MVP release hardening pass. Release evidence lives under `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/` and should be read together with the source docs:

- Feature flag and provider guard reference: `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-FEATURE-FLAGS.md`
- Hosted-provider smoke checklist: `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-HOSTED-SMOKE-RUNBOOK.md`
- Docker smoke evidence: `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-DOCKER-SMOKE.md`
- Browser UAT evidence: `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-HUMAN-UAT.md`

Run the V2 MVP release command set before claiming a fresh release baseline:

```powershell
pnpm validate
pnpm contracts:check
pnpm compat:v1
pnpm migration:safety
pnpm infra:up
pnpm smoke:local
pnpm smoke:worker -- --dry-run
```

Docker smoke proves local PostgreSQL, Redis, MinIO, Alembic, durable data, and local deterministic generation. `pnpm smoke:worker` without `--dry-run` is optional host evidence and requires Docker, migrated API, running API, and running worker processes.

Hosted-provider smoke is manual-only. Follow `14-HOSTED-SMOKE-RUNBOOK.md`, keep `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED`, `AI_PROVIDER_CALLS_ENABLED`, `AI_HOSTED_DAILY_CALL_LIMIT`, `AI_HOSTED_RATE_LIMIT_PER_MINUTE`, `AI_MAX_ESTIMATED_COST_PER_JOB`, and `AI_PROVIDER_BFL_API_KEY` in ignored env files only, submit at most one job after cost approval, record evidence, then reverse the flags.

Browser UAT should cover desktop and mobile hosted guard visibility, targeted edit controls and comparison, reference warnings, lightweight 3D concept-only labels, enhanced ZIP handoff preview/history, and no horizontal overflow. The V2 MVP remains concept-only and not print-ready; production wrap output, verified production UV mapping, auth, billing, marketplace/community flows, quotes/orders/payments, installer workflows, and production deployment remain deferred.

## Core Commands

- `pnpm infra:up`
- `pnpm infra:down`
- `pnpm dev:api`
- `pnpm dev:worker`
- `pnpm dev:web`
- `pnpm contracts:generate`
- `pnpm contracts:check`
- `pnpm lint`
- `pnpm typecheck`
- `pnpm test`
- `pnpm smoke:local`
- `pnpm smoke:worker`
- `pnpm validate`

Focused durable-data commands:

```powershell
cd services/api
uv run alembic upgrade head
uv run pytest -q tests/test_workspaces.py tests/test_assets.py tests/test_jobs.py
```

Focused Phase 3 commands:

```powershell
cd services/core
uv run pytest -q tests/test_generation_briefs.py tests/test_prompt_plans.py
cd ../api
uv run pytest -q tests/test_generation.py
uv run python -m caragent_api.scripts.phase3_generation_smoke
cd ../worker
uv run pytest -q tests/test_image_providers.py tests/test_generation_tasks.py
```

Focused Phase 4 workbench commands:

```powershell
corepack pnpm --filter @caragent/web lint
corepack pnpm --filter @caragent/web typecheck
corepack pnpm --filter @caragent/web test
corepack pnpm --filter @caragent/web build
corepack pnpm contracts:check
```

Focused Phase 5 iteration/export commands:

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

Focused Phase 6 itasha/template intelligence commands:

```powershell
cd services/core
uv run pytest -q tests/test_generation_briefs.py tests/test_prompt_plans.py
cd ../api
uv run pytest -q tests/test_generation.py tests/test_openapi_export.py
cd ../worker
uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py
cd ../..
corepack pnpm --filter @caragent/web test -- apps/web/src/app/page.test.tsx apps/web/src/lib/workbench/store.test.ts
corepack pnpm --filter @caragent/web lint
corepack pnpm --filter @caragent/web typecheck
corepack pnpm contracts:check
```

Focused Phase 7 operations commands:

```powershell
cd services/api
uv run pytest -q tests/test_operations.py tests/test_generation.py tests/test_jobs.py tests/test_queue.py
cd ../worker
uv run pytest -q tests/test_config.py tests/test_image_providers.py tests/test_generation_tasks.py
cd ../..
corepack pnpm --filter @caragent/web test -- apps/web/src/app/page.test.tsx apps/web/src/lib/api/operations.test.ts apps/web/src/lib/api/jobs.test.ts
corepack pnpm --filter @caragent/web lint
corepack pnpm --filter @caragent/web typecheck
corepack pnpm contracts:check
corepack pnpm smoke:worker -- --dry-run
```

Focused Phase 9 hosted-provider rollout commands:

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

The Phase 9 command set above is provider-off by default. It must not require `AI_PROVIDER_BFL_API_KEY` and must not spend hosted-provider credits. Run live provider-on BFL smoke only from the documented manual checklist in [docs/development.md](docs/development.md).

Focused Phase 10 targeted edit commands:

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

The Phase 10 command set is local and provider-off by default. It validates targeted edit schemas, mask metadata, deterministic recomposition, provider capability guardrails, retry/failure behavior, comparison UI, and aggregate validation without making hosted calls.

Focused Phase 11 reference-guidance commands:

```powershell
cd services/core
uv run pytest -q tests/test_models.py tests/test_prompt_plans.py tests/test_generation_jobs.py
cd ../api
uv run pytest -q tests/test_generation.py tests/test_jobs.py tests/test_operations.py
cd ../worker
uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py tests/test_config.py
cd ../..
corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/workbench/store.test.ts src/lib/api/generation.test.ts src/lib/api/assets.test.ts src/lib/api/iteration.test.ts
corepack pnpm contracts:check
corepack pnpm smoke:worker -- --dry-run
corepack pnpm validate
```

The Phase 11 command set is provider-off by default. It validates role assignment, rights/source gates, provider capability filtering, unsupported-role warnings, durable reference trace, child iteration reuse, export source metadata, and aggregate validation without making hosted calls.

Focused Phase 12 lightweight 3D preview commands:

```powershell
cd services/core
uv run pytest -q tests/test_models.py tests/test_generation_jobs.py
cd ../api
uv run pytest -q tests/test_jobs.py tests/test_generation.py
cd ../..
corepack pnpm --filter @caragent/web test
corepack pnpm --filter @caragent/web lint
corepack pnpm --filter @caragent/web typecheck
corepack pnpm contracts:check
corepack pnpm smoke:worker -- --dry-run
corepack pnpm validate
```

The Phase 12 command set is provider-off by default. It validates Preview3DSpec contracts, shell compatibility, 2D fallback, camera controls, screenshot artifact metadata, browser-safe labels, and aggregate validation without making hosted calls. Browser UAT evidence is recorded in `.planning/phases/12-lightweight-3d-preview-mvp/12-HUMAN-UAT.md`.

Focused Phase 13 enhanced handoff package commands:

```powershell
cd services/core
uv run pytest -q tests/test_models.py tests/test_jobs.py tests/test_generation_jobs.py
cd ../api
uv run pytest -q tests/test_jobs.py tests/test_openapi_export.py
cd ../..
corepack pnpm --filter @caragent/web test
corepack pnpm contracts:check
corepack pnpm smoke:worker -- --dry-run
corepack pnpm validate
```

The Phase 13 command set is provider-off by default. It validates package schemas, report sanitization, ZIP contents, API export ledger records, Workbench ZIP UX, rights/source guardrails, contract drift, worker dry-run wiring, aggregate validation, and desktop/mobile browser UAT without making hosted calls. Browser UAT evidence is recorded in `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-HUMAN-UAT.md`.

Focused Phase 14 V2 MVP release commands:

```powershell
corepack pnpm validate
corepack pnpm contracts:check
corepack pnpm compat:v1
corepack pnpm migration:safety
corepack pnpm infra:up
corepack pnpm smoke:local
corepack pnpm smoke:worker -- --dry-run
```

The Phase 14 command set is provider-off by default. It validates the V2 MVP release baseline, contract drift, V1 compatibility, migration safety, Docker smoke, hosted-disabled worker dry-run wiring, docs token coverage, and Browser UAT evidence. Manual hosted-provider smoke remains credentialed, cost-guarded, reversible, and documented in `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-HOSTED-SMOKE-RUNBOOK.md`.

See [docs/development.md](docs/development.md) for environment setup, command details, requirement coverage, and troubleshooting for blocked host prerequisites such as missing `uv`, Node/Corepack profile `EPERM`, and Docker daemon availability. If `pnpm` cannot start, run `node scripts/check-host-prereqs.mjs` from the repository root for a direct prerequisite report.
