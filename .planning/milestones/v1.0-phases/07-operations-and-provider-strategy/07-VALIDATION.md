---
phase: 7
slug: operations-and-provider-strategy
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-18
---

# Phase 7 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | pytest for core/API/worker; Vitest + Testing Library for web; Orval/TypeScript for contracts; Node smoke scripts |
| Config file | `services/core/pyproject.toml`, `services/api/pyproject.toml`, `services/worker/pyproject.toml`, `apps/web/package.json`, `packages/contracts/package.json` |
| Quick run command | `uv run pytest -q tests/test_jobs.py`; `uv run pytest -q tests/test_generation_tasks.py`; `corepack pnpm --filter @caragent/web test -- --run apps/web/src/app/page.test.tsx` |
| Full suite command | `corepack pnpm validate` |
| Estimated runtime | Targeted tests under 30 seconds each; full validation depends on local cache, Docker, API, and worker startup state |

## Sampling Rate

- After every core task: run the targeted core pytest file plus `uv run ruff check .` and `uv run mypy src` for that service before the plan summary.
- After every API task: run targeted API pytest, `uv run ruff check .`, and `uv run mypy src`.
- After every worker task: run targeted worker pytest, `uv run ruff check .`, and `uv run mypy src`.
- After every contract change: export OpenAPI, regenerate contracts, and run `corepack pnpm contracts:check`.
- After every web task: run targeted Vitest plus web lint/typecheck.
- Before `$gsd-verify-work`: run `corepack pnpm validate`, `corepack pnpm smoke:local`, the new live worker queue smoke, and Browser desktop/mobile UAT.
- Max targeted feedback latency: 30 seconds per focused command.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | OPS-01, OPS-02, OPS-04 | T-07-01 | Operational metadata is typed, sanitized, and exposed without leaking SQLAlchemy internals | unit/API | `uv run pytest -q tests/test_jobs.py`; `uv run pytest -q tests/test_jobs.py tests/test_openapi_export.py` | yes | pending |
| 07-01-02 | 01 | 1 | OPS-04 | T-07-02 | Job/event metadata responses stay JSON-safe and contract-generated | contract | `corepack pnpm contracts:check` | yes | pending |
| 07-02-01 | 02 | 2 | OPS-01, OPS-04 | T-07-03 | Operations endpoint reports configured/disabled/unavailable truthfully without secrets | API/unit | `uv run pytest -q tests/test_operations.py tests/test_health.py` | Wave 0 create | pending |
| 07-02-02 | 02 | 2 | OPS-01, OPS-04 | T-07-04 | Worker health payload exposes current version/capability summary without result backend dependency | worker/unit | `uv run pytest -q tests/test_worker_app.py tests/test_config.py` | yes | pending |
| 07-03-01 | 03 | 2 | OPS-02, OPS-04 | T-07-05 | Worker classifies provider/config/rights/storage/timeout/unknown failures and redacts secrets | worker/unit | `uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py` | yes | pending |
| 07-03-02 | 03 | 2 | OPS-02, OPS-04 | T-07-06 | Recent failure API can filter/render categories from durable job/event state | API/unit | `uv run pytest -q tests/test_operations.py tests/test_jobs.py` | Wave 0 create | pending |
| 07-04-01 | 04 | 3 | OPS-05, OPS-04 | T-07-07 | Queued cancellation transitions durably to canceled and emits structured events | core/API | `uv run pytest -q tests/test_jobs.py`; `uv run pytest -q tests/test_generation.py tests/test_queue.py` | yes | pending |
| 07-04-02 | 04 | 3 | OPS-05 | T-07-08 | Worker respects pre-run and mid-run canceled state before expensive work/storage | worker/unit | `uv run pytest -q tests/test_generation_tasks.py` | yes | pending |
| 07-05-01 | 05 | 3 | OPS-03, OPS-02, OPS-04 | T-07-09 | Provider attempts are bounded and fallback is explicit in events/model-runs | worker/unit | `uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py` | yes | pending |
| 07-05-02 | 05 | 3 | OPS-03 | T-07-10 | Provider routing settings are config-driven and fail fast for unsupported hosted providers | worker/unit | `uv run pytest -q tests/test_config.py tests/test_image_providers.py` | yes | pending |
| 07-06-01 | 06 | 4 | OPS-06, OPS-03 | T-07-11 | Hosted provider calls are blocked before provider execution when quota/rate guards reject | worker/unit | `uv run pytest -q tests/test_generation_tasks.py tests/test_config.py` | yes | pending |
| 07-06-02 | 06 | 4 | OPS-06 | T-07-12 | Local deterministic generation bypasses monetary quota but records zero cost | worker/unit | `uv run pytest -q tests/test_generation_tasks.py` | yes | pending |
| 07-07-01 | 07 | 5 | OPS-01..OPS-06 | T-07-13 | Workbench renders operations/cancel/error metadata as text and never exposes secrets | web/unit | `corepack pnpm --filter @caragent/web test -- --run apps/web/src/app/page.test.tsx apps/web/src/lib/api/*.test.ts` | yes | pending |
| 07-07-02 | 07 | 5 | OPS-01..OPS-06 | T-07-14 | Full validation and live worker queue smoke prove current-code worker consumption | smoke/browser | `corepack pnpm validate`; `corepack pnpm smoke:local`; new worker queue smoke command | yes | pending |

## Wave 0 Requirements

Existing infrastructure covers most phase requirements. Phase 7 must create these new test files before implementation tasks depend on them:

- `services/api/tests/test_operations.py` - provider status, queue/worker inspection, recent failures, and cancel response behavior.
- Optional `scripts/smoke-worker-queue.mjs` or equivalent root script - live queued generation worker smoke with Windows-safe worker startup guidance.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Workbench operations and cancellation controls remain readable on desktop and mobile | OPS-01, OPS-05 | Browser layout and user-facing truthfulness need runtime inspection | Open `http://127.0.0.1:3000`, verify provider/worker status, cancel controls, failure category copy, no horizontal scroll at desktop and 390px mobile, and no console errors |
| Live worker is current-code and Windows-safe | OPS-01, OPS-04 | Local process/pool behavior is environment dependent | Start worker with documented `--pool=solo --concurrency=1`, enqueue a generation job through API, and verify stored worker/job metadata includes current version/capability and PreviewSpec output |

## Validation Sign-Off

- [x] All tasks have automated verify or existing Wave 0 test infrastructure.
- [x] Sampling continuity: no three consecutive implementation tasks lack automated verify.
- [x] Wave 0 infrastructure exists or is explicitly created by the relevant plan.
- [x] No watch-mode flags in planned commands.
- [x] Targeted feedback latency target is below 30 seconds.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-18
