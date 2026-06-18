---
status: passed
phase: 07-operations-and-provider-strategy
source:
  - 07-VERIFICATION.md
started: 2026-06-18
updated: 2026-06-18
---

# Phase 7 Human UAT

## Current Test

Browser UAT against local web/API/worker services for compact operations status, cancellation, failure metadata, responsive layout, and console cleanliness.

## Environment

- Browser target: `http://127.0.0.1:3000/`
- API target: `http://127.0.0.1:8000`
- Worker command: `uv run celery -A caragent_worker.app worker --loglevel=INFO --pool=solo --concurrency=1`
- Live smoke command: `pnpm smoke:worker`

## Tests

### 1. Live worker queue smoke
expected: A job submitted through the API queue boundary is consumed by the worker and produces durable PreviewSpec output.
result: passed

Evidence:
- workspace: `dee5c4b1-627b-416a-9ead-3d0479bb9d92`
- job: `5f938edf-3daf-40ce-aa99-966ef20f6c70`
- version: `00515f1a-bb3a-4cba-b95a-c74ba94b7553`
- artifact: `41dec787-b3a2-4338-8970-43b1403c57d2`
- events: `6`

### 2. Operations status
expected: Progress panel shows compact provider, worker, queue, and guard state without secrets.
result: passed

Evidence:
- Visible: `运维状态`.
- Visible after refresh: `Provider local-deterministic`, `Worker ok`, `Queue ok`.
- Rendered text scan found no `api_key`, `secret`, bearer token, or Windows path pattern.

### 3. Queued job cancellation
expected: Queued/running job shows cancel; after cancel, terminal state appears and cancel control disappears.
result: passed

Evidence:
- workspace: `f4080584-cef6-4067-98d4-7ebfa6204d74`
- cancel probe job: `069352a8-ebe6-45f9-a893-07d037adee34`
- Before click: visible `取消生成`.
- After click: visible `已取消`.
- After terminal state: `取消生成` no longer visible.

### 4. Failed metadata rendering
expected: Failed jobs show structured failure metadata and retry, without showing cancel.
result: passed

Evidence:
- failed probe job: `90890663-8af2-48be-902d-bf32c6199304`
- Visible: `失败分类 timeout`, `阶段 provider_generate`, `Provider bfl`.
- Visible: `重试生成`.
- Hidden: `取消生成`.
- Rendered text scan found no secret-like or local path pattern.

### 5. Desktop layout
expected: Desktop viewport has no horizontal document scroll and no app console errors.
result: passed

Evidence:
- Requested viewport: `1280 x 720`.
- Measured client width: `1265`.
- `scrollWidth == clientWidth`.
- Browser page console errors: `0`.

### 6. Mobile layout
expected: Mobile viewport has no horizontal document scroll and no app console errors.
result: passed

Evidence:
- Requested viewport: `390 x 844`.
- Measured client width: `375`.
- `scrollWidth == clientWidth`.
- Browser page console errors: `0`.

## Issues Found During UAT

1. Temporary service startup helper argument shadowing
status: resolved

Observed: `uv` printed its help text instead of starting API/worker because a PowerShell helper parameter named `$Args` conflicted with the automatic `$args` variable.

Fix: Reran the temporary launch helper with a non-conflicting `ArgumentArray` parameter. No product code change was needed.

2. Next.js dev argument forwarding
status: resolved

Observed: Passing an extra `--` through pnpm made Next.js treat `--hostname` as a project directory.

Fix: Reran the web dev command as `corepack pnpm --filter @caragent/web dev --hostname 127.0.0.1 --port 3000`.

## Summary

total: 6
passed: 6
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

None for v1 Phase 7. Hosted provider production readiness remains intentionally out of scope until provider quality, price, moderation, account access, and commercial-rights constraints are revalidated.
