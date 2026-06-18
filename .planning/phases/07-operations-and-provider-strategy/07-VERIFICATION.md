---
status: passed
phase: 07-operations-and-provider-strategy
verified: 2026-06-18
source:
  - 07-01-SUMMARY.md
  - 07-02-SUMMARY.md
  - 07-03-SUMMARY.md
  - 07-04-SUMMARY.md
  - 07-05-SUMMARY.md
  - 07-06-SUMMARY.md
  - 07-07-PLAN.md
requirements:
  - OPS-01
  - OPS-02
  - OPS-03
  - OPS-04
  - OPS-05
  - OPS-06
---

# Phase 7 Verification

Phase 7 passes automated validation, Docker-backed local smoke, live worker queue smoke, and Browser UAT for operations/provider strategy.

## Automated Evidence

| Command | Result | Evidence |
|---------|--------|----------|
| `corepack pnpm --filter @caragent/web test` | PASS | 8 files, 45 tests passed, including operations status, cancel UI, and failure metadata tests. |
| `corepack pnpm --filter @caragent/web lint` | PASS | ESLint completed with `--max-warnings=0`. |
| `corepack pnpm --filter @caragent/web typecheck` | PASS | TypeScript `tsc --noEmit` passed. |
| `corepack pnpm contracts:check` | PASS | Contract artifacts are current. |
| `cd services/api && uv run pytest -q tests/test_operations.py tests/test_generation.py tests/test_jobs.py tests/test_queue.py tests/test_openapi_export.py` | PASS | 29 tests passed. |
| `cd services/worker && uv run pytest -q tests/test_config.py tests/test_image_providers.py tests/test_generation_tasks.py` | PASS | 37 tests passed. |
| `cd services/core && uv run pytest -q tests/test_jobs.py` | PASS | 10 tests passed. |
| `cd services/api && uv run ruff check . && uv run mypy src` | PASS | Ruff passed; mypy reported no issues in 15 source files. |
| `cd services/worker && uv run ruff check . && uv run mypy src` | PASS | Ruff passed; mypy reported no issues in 10 source files. |
| `cd services/core && uv run ruff check . && uv run mypy src` | PASS | Ruff passed; mypy reported no issues in 16 source files. |
| `corepack pnpm smoke:worker -- --dry-run` | PASS | Worker queue smoke command wiring and deterministic Windows run instructions printed successfully. |
| `corepack pnpm validate` | PASS | Web 45 tests, core 38 tests, API 46 tests, worker 46 tests, contracts check, and contracts typecheck passed. |
| `corepack pnpm infra:up` | PASS | PostgreSQL, Redis, and MinIO containers running. |
| `corepack pnpm smoke:local` | PASS | PostgreSQL, Redis, MinIO, Alembic, durable data smoke, and local deterministic generation smoke passed. |
| `corepack pnpm smoke:worker` | PASS | Live API -> Redis/Celery -> worker -> durable artifact/version smoke passed. |

Live worker queue smoke evidence:
- workspace: `dee5c4b1-627b-416a-9ead-3d0479bb9d92`
- job: `5f938edf-3daf-40ce-aa99-966ef20f6c70`
- version: `00515f1a-bb3a-4cba-b95a-c74ba94b7553`
- artifact: `41dec787-b3a2-4338-8970-43b1403c57d2`
- events: `6`

## Browser UAT Evidence

Browser target: `http://127.0.0.1:3000/` with API `http://127.0.0.1:8000`.

Runtime:
- Docker services running through `infra/compose.yml`.
- API served by `uv run uvicorn caragent_api.main:app --host 127.0.0.1 --port 8000`.
- Worker served by `uv run celery -A caragent_worker.app worker --loglevel=INFO --pool=solo --concurrency=1`.
- Operations status reported `Worker ok`, `Queue ok`, and provider `local-deterministic`.

UAT workspace:
- workspace: `f4080584-cef6-4067-98d4-7ebfa6204d74`
- cancel probe job: `069352a8-ebe6-45f9-a893-07d037adee34`
- failed metadata probe job: `90890663-8af2-48be-902d-bf32c6199304`

Observed Browser checks:
- Workbench progress panel displayed `运维状态`, `Provider local-deterministic`, `Worker ok`, and `Queue ok`.
- Queued job displayed `取消生成`; after clicking it, UI displayed `已取消` and removed `取消生成`.
- Failed job displayed `失败分类 timeout`, `阶段 provider_generate`, `Provider bfl`, and `重试生成`; cancel remained hidden.
- Desktop viewport requested `1280 x 720`; measured client width `1265`, `scrollWidth == clientWidth`, no horizontal overflow.
- Mobile viewport requested `390 x 844`; measured client width `375`, `scrollWidth == clientWidth`, no horizontal overflow.
- Browser page console errors: `0`.
- Secret/path scan in rendered text: no `api_key`, `secret`, bearer token, or Windows path pattern.

## Requirement Evidence

| Requirement | Status | Evidence |
|-------------|--------|----------|
| OPS-01 | PASS | `/operations/provider-status` exposes provider, worker, queue, hosted guard, and recent-failure summary fields. Web operations client and Browser UAT confirmed compact workbench visibility. |
| OPS-02 | PASS | Worker failures are classified with durable `failure_category`, `stage`, and provider metadata. Tests cover provider, validation, storage, queue, timeout, canceled, and unknown paths. |
| OPS-03 | PASS | Provider routing, fallback enablement/name, max attempts, hosted rate/day/cost guards, and timeout settings are config-driven and covered by worker config/provider tests. |
| OPS-04 | PASS | API/worker events and metadata carry structured operational fields; workbench renders structured failure metadata without exposing raw secrets. |
| OPS-05 | PASS | `POST /jobs/{job_id}/cancel` cancels queued/running jobs, revokes queue task when available, and Browser UAT confirmed final `已取消` state with cancel hidden. |
| OPS-06 | PASS | Hosted calls require daily, per-minute, and per-job cost guard settings before provider execution; live worker smoke proves the local queue path still succeeds. |

## Deviations And Fixes

- Initial local service launch attempt failed because a PowerShell helper parameter named `$Args` shadowed PowerShell's automatic `$args` variable, causing `uv` to print help instead of receiving command arguments.
- Root cause was confirmed from API/worker stderr logs; the launch helper was rerun with `ArgumentArray`, and services started correctly.
- One web launch attempt passed an extra `--` to Next.js through pnpm; Next interpreted `--hostname` as a project directory. The command was corrected to pass `--hostname 127.0.0.1 --port 3000` directly.
- A queued cancel Browser UAT probe was created as a generic durable job so it would not be consumed by the worker before the cancel control could be verified. The cancel route and UI path are the same as generation cancellation.

## Sandbox Notes

Some commands required escalated execution on Windows:
- Docker access for `pnpm infra:up`, `pnpm smoke:local`, Docker-backed database queries, and live worker smoke.
- `uv run mypy` and aggregate validation when sandboxed execution could not access uv cache/process resources.
- `corepack pnpm ...` commands that spawn Vite/Next/contract-check child processes.

All escalated commands passed after rerun.

## Verdict

Phase 7 meets the planned goal: provider/worker health is visible, failures are classified, jobs can be canceled durably, provider routing/retry/fallback/quota controls are configuration-driven, and local operations can be verified through aggregate validation, Docker smoke, live worker queue smoke, and Browser UAT.
