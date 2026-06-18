---
phase: 02-durable-data-jobs-and-assets
plan: "09"
subsystem: "phase validation smoke docs and verification"
tags: ["validation", "smoke", "docs", "env", "docker", "uat"]
requires:
  - ".planning/phases/02-durable-data-jobs-and-assets/02-09-PLAN.md"
  - ".planning/phases/02-durable-data-jobs-and-assets/02-VALIDATION.md"
provides:
  - "Corepack-compatible aggregate Phase 2 validation runner"
  - "Docker-backed smoke with Alembic and durable data round trip"
  - "Phase 2 env/doc updates"
  - "Phase 2 code review and verification report"
  - "Live API-backed browser UAT evidence"
key-files:
  created:
    - "services/api/src/caragent_api/scripts/phase2_data_smoke.py"
    - ".planning/phases/02-durable-data-jobs-and-assets/02-REVIEW.md"
    - ".planning/phases/02-durable-data-jobs-and-assets/02-VERIFICATION.md"
  modified:
    - ".node-version"
    - ".env.example"
    - "services/api/.env.example"
    - "services/worker/.env.example"
    - "scripts/check-contracts.mjs"
    - "scripts/check-host-prereqs.mjs"
    - "scripts/check-host-prereqs.test.mjs"
    - "scripts/smoke-local.mjs"
    - "scripts/validate-all.mjs"
    - "README.md"
    - "docs/development.md"
    - ".planning/ROADMAP.md"
    - ".planning/STATE.md"
    - ".planning/phases/02-durable-data-jobs-and-assets/02-HUMAN-UAT.md"
key-decisions:
  - "The repo Node pin now matches the active NVM runtime, `22.15.0`."
  - "Host prereq validation treats Corepack pnpm and uv-managed Python as the authoritative local toolchain."
  - "Docker smoke applies Alembic and runs a bounded durable data smoke after PostgreSQL, Redis, and MinIO health checks pass."
requirements-completed: ["DATA-01", "DATA-02", "DATA-03", "DATA-04", "DATA-05", "DATA-06", "DATA-07"]
duration: "in-session"
completed: 2026-06-17
---

# Phase 2 Plan 09: Validation And Smoke Summary

Plan 02-09 finalized Phase 2 validation, local smoke, environment examples, developer docs, code review, live browser UAT, and verification reporting.

## Tasks Completed

| Task | Result | Evidence |
|------|--------|----------|
| Smoke and validation scripts | Complete | `pnpm validate` passes through Corepack; `pnpm smoke:local` runs service health, Alembic, and durable data smoke. |
| Env examples and guards | Complete | Root/API/worker env comments match Phase 2 local mode; env guard passes with no real secrets. |
| Developer docs | Complete | README and development guide document Alembic, workspace/job/idempotency UAT, validation, smoke, and deferred scope. |
| Final verification report | Complete | `02-VERIFICATION.md` records command evidence, Docker cleanup, browser UAT, requirement coverage, and residual scope. |
| Code review | Complete | `02-REVIEW.md` reports clean quick review for Phase 2 source changes. |

## Verification

| Command | Result |
|---------|--------|
| `node scripts/check-host-prereqs.test.mjs` | Passed. |
| `node scripts/check-env-examples.mjs` | Passed. |
| Docs token check for `Alembic`, `workspace`, `idempotency`, `pnpm validate`, `pnpm smoke:local` | Passed. |
| `cd services/api && uv run ruff check .` | Passed. |
| `cd services/api && uv --no-cache run mypy src` | Passed; `11 source files`. |
| `corepack pnpm contracts:check` | Passed; contract artifacts current. |
| `corepack pnpm lint` | Passed. |
| `corepack pnpm typecheck` | Passed. |
| `corepack pnpm test` | Passed; web `15`, core `21`, API `23`, worker `11`. |
| `corepack pnpm validate` | Passed; Phase 2 aggregate validation passed. |
| `corepack pnpm infra:up` | Passed; PostgreSQL, Redis, and MinIO containers started. |
| `corepack pnpm smoke:local` | Passed; service checks, Alembic, and durable data smoke passed. |
| `corepack pnpm infra:down` | Passed; Compose cleanup completed. |
| Live API-backed browser UAT | Passed; refresh preserved workspace/job state. |

## Deviations from Plan

**[Rule 1 - Toolchain] Align validation with NVM/Corepack/uv-managed runtime**
- Found during: `pnpm validate`.
- Issue: Validation scripts still assumed bare `pnpm`, bare `python`, and old Node `24.15.0`.
- Fix: Updated `.node-version` to `22.15.0`; host prereq checks now resolve Corepack from the active Node install and verify uv-managed Python `3.13.13`.
- Verification: `node scripts/check-host-prereqs.mjs` passed inside `corepack pnpm validate`.

**[Rule 1 - Contract generation] Contract checker must not call bare pnpm**
- Found during: `pnpm validate`.
- Issue: `scripts/check-contracts.mjs` could fail inside aggregate validation when bare `pnpm` was not on PATH.
- Fix: Contract checker now invokes Corepack pnpm directly.
- Verification: `corepack pnpm contracts:check` and `corepack pnpm validate` passed.

**[Rule 2 - Smoke scope] Object storage smoke is bounded to service health plus artifact metadata**
- Rationale: The repo does not include an S3 SDK yet, and adding one just for smoke would widen the dependency surface.
- Implementation: `pnpm smoke:local` validates MinIO health, runs Alembic, and performs a PostgreSQL durable data round trip for workspace/message/job/event/artifact metadata.

## Self-Check: PASSED

Phase 2 can be verified from root commands, Docker-backed smoke exercises the durable data path, docs/env examples match implementation, and `02-VERIFICATION.md` covers DATA-01 through DATA-07.

## Next

Ready to start Phase 3 planning: first text-to-2D generation slice.
