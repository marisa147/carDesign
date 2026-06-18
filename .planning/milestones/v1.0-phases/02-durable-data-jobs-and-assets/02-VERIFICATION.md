---
phase: 02-durable-data-jobs-and-assets
status: passed
verified: 2026-06-17
requirements: ["DATA-01", "DATA-02", "DATA-03", "DATA-04", "DATA-05", "DATA-06", "DATA-07"]
human_uat: passed_agent_driven
gaps: 0
---

# Phase 2 Verification: Durable Data, Jobs, And Assets

Phase 2 is verified. Workspaces, messages, structured briefs, assets/rights metadata, jobs, job events, model runs, artifacts, versions, feedback, exports, costs, generated contracts, worker local simulation, and the minimal web refresh proof are implemented and covered by automated checks.

## Automated Checks

| Command | Result | Evidence |
|---------|--------|----------|
| `corepack pnpm contracts:check` | Passed | Contract artifacts current. |
| `corepack pnpm lint` | Passed | Web/contracts lint and core/API/worker Ruff checks passed. |
| `corepack pnpm typecheck` | Passed | Web/contracts TypeScript and core/API/worker mypy passed: core `12 source files`, API `11 source files`, worker `6 source files`. |
| `corepack pnpm test` | Passed | Web `3 files / 15 tests`, core `21`, API `23`, worker `11`; contracts typecheck ran. |
| `corepack pnpm validate` | Passed | Phase 2 aggregate validation passed, including host prereqs, env guard, web lint/type/test, core/API/worker ruff/mypy/pytest, contracts check, and contracts typecheck. |
| `corepack pnpm infra:up` | Passed | PostgreSQL, Redis, and MinIO containers started. |
| `corepack pnpm smoke:local` | Passed | PostgreSQL, Redis, MinIO checks passed; Alembic ran; Phase 2 durable data smoke passed. |
| `corepack pnpm infra:down` | Passed | Compose containers and network removed after smoke. |

## Browser UAT

Agent-driven browser UAT was run against live API and Docker-backed services:

| Step | Result |
|------|--------|
| Opened web shell at `http://127.0.0.1:3000` | Passed. |
| Clicked `创建持久工作区` | Passed; visible workspace ID appeared and message count became `1`. |
| Clicked `创建模拟任务` | Passed; API-backed job state became visible after refresh. |
| Refreshed browser | Passed; same workspace ID persisted and `消息 1`, `事件 1`, and `任务 queued` were visible. |
| Queried API for created workspace jobs/events | Passed; job count `1`, job status `queued`, event count `1`, event status `queued`. |

Observed workspace during UAT: `26e912ee-af29-49c0-8c38-0719e06b6581`.

## Requirement Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| DATA-01 | Satisfied | Workspace/message services, API routes, web wrappers, page tests, and browser UAT prove create/resume and conversation persistence. |
| DATA-02 | Satisfied | SQLAlchemy ledger models and Alembic migration cover briefs, jobs, events, model runs, versions, artifacts, feedback, exports, and costs. |
| DATA-03 | Satisfied | Asset upload tests and metadata/object-key storage paths are covered; MinIO health is part of Docker smoke. |
| DATA-04 | Satisfied | Asset rights/source metadata enforcement is covered by API asset tests and env/docs guards. |
| DATA-05 | Satisfied | API job tests, worker simulation tests, web tests, and live browser UAT prove durable job status/event visibility after refresh. |
| DATA-06 | Satisfied | API job tests, web idempotency-key behavior, and data smoke prove duplicate job requests reuse the durable job. |
| DATA-07 | Satisfied | Worker job tests and data smoke prove no-provider local simulation updates durable job/model-run/cost state without provider calls. |

## Issues Found And Fixed During Verification

| Issue | Fix | Final Evidence |
|-------|-----|----------------|
| `pnpm validate` initially failed because `validate-all.mjs` tried bare `pnpm` in an NVM/Corepack shell. | Aggregate runner now invokes `corepack pnpm` for pnpm commands. | `corepack pnpm validate` passed. |
| `contracts:check` initially failed because `check-contracts.mjs` used bare `pnpm` during client generation. | Contract checker now invokes Corepack directly. | `corepack pnpm contracts:check` and `corepack pnpm validate` passed. |
| Host prereq check assumed bare Python and old Node `24.15.0`. | `.node-version` is `22.15.0`; prereq check accepts uv-managed Python `3.13.13` and Corepack pnpm `11.0.8`. | `node scripts/check-host-prereqs.mjs` passed inside aggregate validation. |

## Residual Warnings

None blocking.

The project still intentionally does not implement real provider-backed image generation, full chat/upload/preview/export workbench UX, auth, billing, true 3D, or production handoff. Those remain later-phase scope.

## Cleanup

`corepack pnpm infra:down` was run after Docker smoke and again after browser UAT. The temporary API server and web dev server started for UAT were stopped.
