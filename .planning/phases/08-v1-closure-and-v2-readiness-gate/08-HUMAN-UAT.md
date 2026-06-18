---
status: partial
phase: 08-v1-closure-and-v2-readiness-gate
source:
  - 08-VERIFICATION.md
started: 2026-06-18
updated: 2026-06-18
---

# Phase 8 Human UAT

## Current Test

Host/browser readiness checks for V1 local-only behavior, operations visibility, default-off V2 gates, Docker smoke, worker live smoke, and responsive Browser UAT.

## Environment

- Baseline tag: `v1.0`
- Docker local smoke: `pnpm infra:up`, `pnpm smoke:local`, `pnpm infra:down`
- Worker smoke dry-run: `pnpm smoke:worker -- --dry-run`
- Live worker smoke: `pnpm smoke:worker`
- Browser target: `http://127.0.0.1:3000/`
- API target: `http://127.0.0.1:8000`
- Worker command: `uv run celery -A caragent_worker.app worker --loglevel=INFO --pool=solo --concurrency=1`

## Tests

### 1. V1 baseline evidence
expected: Phase 8 references a concrete v1.0 release marker and archived audit evidence.
result: passed

Evidence:
- `08-READINESS-BASELINE.md` records release tag `v1.0`, tag object `0939ca9`, and tagged commit `f59390e`.
- v1.0 audit status is `passed`.

### 2. Default-off V2 flags
expected: V2 flags exist and default to disabled without requiring hosted provider credentials.
result: passed

Evidence:
- API, worker, and web public env tests passed.
- `.env.example`, service env examples, and web env example all set V2 readiness flags to `false`.

### 3. V1 contract compatibility
expected: Key v1 OpenAPI routes, schemas, generated client helpers, and PreviewSpec-compatible parameter surfaces remain present.
result: passed

Evidence:
- `pnpm compat:v1` passed.
- `pnpm contracts:check` passed.

### 4. Migration safety
expected: Phase 8 is a no-op schema phase and the current Alembic head is valid.
result: passed

Evidence:
- `pnpm migration:safety` passed.
- `pnpm smoke:local` passed, including Alembic migration.
- `uv run alembic current` reported `f2d60f906fc6 (head)`.

### 5. Aggregate validation
expected: Root aggregate validation passes on a host with prerequisites.
result: passed

Evidence:
- `pnpm validate` passed under approved elevated execution.

### 6. Docker local smoke
expected: PostgreSQL, Redis, MinIO, durable data smoke, and local deterministic generation smoke pass.
result: passed

Evidence:
- `pnpm infra:up` passed.
- `pnpm smoke:local` passed.
- `pnpm infra:down` passed.

### 7. Worker live queue smoke
expected: A job submitted through API queue boundary is consumed by the worker and produces durable PreviewSpec output.
result: pending

Host steps:
1. `pnpm infra:up`
2. `cd services/api && uv run alembic upgrade head`
3. `pnpm dev:api`
4. In another terminal: `cd services/worker && uv run celery -A caragent_worker.app worker --loglevel=INFO --pool=solo --concurrency=1`
5. In another terminal: `pnpm smoke:worker`
6. `pnpm infra:down`

### 8. Browser workbench readiness
expected: V1 workbench loads, operations status is visible, future/V2 gates are disabled/default-off, and no hosted provider credentials are required.
result: pending

Host steps:
1. Start infrastructure, API, worker, and web.
2. Open the workbench.
3. Confirm chat, parameters, assets, progress, 2D preview, version history, iteration, feedback, concept export, and operations status still load.
4. Confirm V2/future gates remain disabled, deferred, or clearly labeled.
5. Confirm no provider keys, database URLs, Redis URLs, S3 secrets, bearer tokens, or Windows paths appear in visible text or console output.
6. Repeat desktop and mobile viewport checks.

## Summary

total: 8
passed: 6
issues: 0
pending: 2
skipped: 0
blocked: 0

## Gaps

None. Pending items are host/browser UAT checks, not implementation gaps.
