---
status: complete
phase: 03-first-text-to-2d-generation-slice
source: [03-VERIFICATION.md]
started: 2026-06-17T16:28:00+08:00
updated: 2026-06-17T16:33:00+08:00
---

# Phase 3 Human Verification

## Current Test

[testing complete]

## Tests

### 1. Full aggregate validation
expected: With Node 22.15.0, pnpm 11.0.8, Python 3.13.13, uv available, and Docker smoke handled separately, `pnpm validate` runs host prereqs, env guard, web lint/type/test, core/API/worker Ruff/mypy/pytest, contract drift check, and contracts typecheck successfully.
result: pass
evidence: "Rechecked 2026-06-17T16:25:50+08:00 with host execution. `corepack pnpm validate` completed successfully and printed `Phase 3 aggregate validation passed.` Web tests passed 4 files / 20 tests; core pytest passed 30 tests; API pytest passed 28 tests; worker pytest passed 21 tests."

### 2. Docker local generation smoke
expected: With Docker Desktop or Docker Engine running, `pnpm infra:up`, `pnpm smoke:local`, and `pnpm infra:down` complete. Smoke must validate PostgreSQL, Redis, MinIO, Alembic, Phase 2 data smoke, and Phase 3 local deterministic generation smoke without hosted provider keys.
result: pass
evidence: "Rechecked 2026-06-17T16:23:00+08:00 after Docker was available on the host. `corepack pnpm infra:up` started PostgreSQL, Redis, and MinIO. `corepack pnpm smoke:local` printed `PostgreSQL check passed.`, `Redis check passed.`, `MinIO check passed.`, `Phase 2 durable data smoke passed.`, and `Phase 3 local deterministic generation smoke passed.` `corepack pnpm infra:down` removed the containers and network."

### 3. Browser-visible Phase 3 proof
expected: The web shell loads and exposes the minimal Phase 3 proof without exposing the full deferred workbench. The page should show a Phase 3 concept-generation panel, a `自然语言 brief` input, and a `创建概念任务` button.
result: pass
evidence: "Rechecked 2026-06-17T16:31:00+08:00 with Browser against `http://127.0.0.1:3000/`. Browser URL was `http://127.0.0.1:3000/`, title was `痛车设计 Agent`, locator count for `Phase 3 概念生成证明` was 1, label count for `自然语言 brief` was 1, and button count for `创建概念任务` was 1."

### 4. Web generation request behavior
expected: The web proof creates a structured brief, submits a generation job through generated API routes, avoids provider secrets in browser requests, stores the generation job id, and displays brief/job/artifact/version state from API-backed responses.
result: pass
evidence: "Covered by `apps/web/src/app/page.test.tsx` and `apps/web/src/lib/api/generation.test.ts`. Root `corepack pnpm test` passed 2026-06-17T16:26:56+08:00; web tests passed 4 files / 20 tests, including `creates a Phase 3 structured brief and generation job proof` and wrapper tests that reject provider-secret request bodies."

### 5. Failure and retry path
expected: Failed generation jobs keep durable errors, preserve the original brief, and retry creates a new durable attempt without losing the failed job.
result: pass
evidence: "Covered by API generation retry tests and worker generation failure tests inside `corepack pnpm validate` and `corepack pnpm test`. API pytest passed 28 tests; worker pytest passed 21 tests."

## Summary

total: 5
passed: 5
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

None recorded.

## Recheck History

- 2026-06-17T16:23:00+08:00: Docker-backed `pnpm smoke:local` passed with Phase 3 local deterministic generation smoke and cleanup.
- 2026-06-17T16:25:50+08:00: `pnpm validate` passed the Phase 3 aggregate validation sequence.
- 2026-06-17T16:26:56+08:00: Root `pnpm lint`, `pnpm typecheck`, `pnpm test`, and standalone `pnpm contracts:check` passed.
- 2026-06-17T16:31:00+08:00: Browser confirmed the local Phase 3 web proof surface at `http://127.0.0.1:3000/`.
