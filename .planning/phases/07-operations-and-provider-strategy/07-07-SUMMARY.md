---
phase: 07-operations-and-provider-strategy
plan: "07"
subsystem: workbench-operations-ui-docs-smoke-uat
tags: [web, operations, cancel, smoke, docs, uat]

requires:
  - phase: "07-01"
    provides: operational metadata contract
  - phase: "07-02"
    provides: operations API
  - phase: "07-03"
    provides: structured failure classification
  - phase: "07-04"
    provides: cancellation API and queue revoke
  - phase: "07-05"
    provides: provider routing retry fallback
  - phase: "07-06"
    provides: hosted quota rate preflight
provides:
  - workbench operations client
  - workbench cancel client
  - compact progress panel operations status
  - queued/running cancel control
  - structured failure metadata rendering
  - worker queue smoke script
  - Phase 7 docs and verification artifacts
  - Browser UAT evidence
affects:
  - milestone-v1-closure

tech-stack:
  patterns:
    - generated OpenAPI URL helpers are used by web wrappers
    - operations status stays in progress panel instead of a separate admin dashboard
    - UI renders structured metadata and sanitizes raw diagnostic text
    - live queue smoke submits through API and verifies durable worker output

key-files:
  modified:
    - apps/web/src/lib/api/operations.ts
    - apps/web/src/lib/api/operations.test.ts
    - apps/web/src/lib/api/jobs.ts
    - apps/web/src/lib/api/jobs.test.ts
    - apps/web/src/components/workbench/progress-panel.tsx
    - apps/web/src/components/workbench/workbench-app.tsx
    - apps/web/src/app/page.test.tsx
    - scripts/smoke-worker-queue.mjs
    - package.json
    - README.md
    - docs/development.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md
    - .planning/STATE.md
  added:
    - .planning/phases/07-operations-and-provider-strategy/07-VERIFICATION.md
    - .planning/phases/07-operations-and-provider-strategy/07-HUMAN-UAT.md
    - .planning/phases/07-operations-and-provider-strategy/07-07-SUMMARY.md

key-decisions:
  - "Workbench operations visibility remains compact inside the existing progress panel."
  - "Cancel is exposed only for queued/running jobs and hidden for succeeded, failed, and canceled jobs."
  - "Failure metadata is rendered from structured category/stage/provider fields, while raw diagnostics are sanitized."
  - "Worker queue smoke has a dry-run mode for command validation and a real mode for live local evidence."
  - "Hosted provider production readiness remains out of scope even though routing and guardrails are now implemented."

requirements-completed:
  - OPS-01
  - OPS-02
  - OPS-03
  - OPS-04
  - OPS-05
  - OPS-06

duration: 55 min
completed: 2026-06-18
---

# Phase 7 Plan 07: Workbench Operations UI, Docs, Smoke, And UAT Closure

Phase 7 is complete. The workbench now exposes the operational state created by the earlier Phase 7 plans, and local operators have documented smoke commands to verify the full queue path.

## Accomplishments

- Added web operations API wrapper for `/operations/provider-status`.
- Added web cancel wrapper for `POST /jobs/{job_id}/cancel`.
- Added progress panel operations status for provider, worker, queue, and hosted guard state.
- Added cancel control for queued/running jobs and terminal `已取消` rendering.
- Added structured failure metadata display for failure category, stage, and provider.
- Added raw diagnostic text sanitization for secret-like tokens and Windows paths.
- Added `scripts/smoke-worker-queue.mjs` and `pnpm smoke:worker`.
- Documented Windows-safe worker startup with `--pool=solo --concurrency=1`.
- Documented provider opt-in, bounded fallback/retry, cancellation, quota/rate/cost guards, and hosted-provider caveats.
- Created Phase 7 verification and Browser UAT artifacts.
- Marked OPS-01 through OPS-06 complete.

## Verification

- RED/GREEN web API wrapper tests for operations and cancel clients.
- RED/GREEN workbench page tests for operations status, cancel behavior, and failure metadata.
- `corepack pnpm --filter @caragent/web test` passed, 45 tests.
- `corepack pnpm --filter @caragent/web lint` passed.
- `corepack pnpm --filter @caragent/web typecheck` passed.
- `corepack pnpm contracts:check` passed.
- API focused Phase 7 tests passed, 29 tests.
- Worker focused Phase 7 tests passed, 37 tests.
- Core job tests passed, 10 tests.
- API/worker/core ruff and mypy passed.
- `corepack pnpm smoke:worker -- --dry-run` passed.
- `corepack pnpm validate` passed.
- `corepack pnpm infra:up` passed.
- `corepack pnpm smoke:local` passed.
- `corepack pnpm smoke:worker` passed with live job `5f938edf-3daf-40ce-aa99-966ef20f6c70`.
- Browser UAT passed for operations status, cancellation, failed metadata, desktop layout, mobile layout, and console error checks.

## Deviations from Plan

- The workbench does not fetch operations status during initial resume; it fetches on explicit refresh. This keeps resume traffic stable and matches the compact operator workflow.
- The cancel UAT used a generic queued durable job probe so the worker could not consume it before the UI click. The same cancel API and progress-panel behavior apply to generation jobs.
- No new admin page was added. Operations status stays in the existing workbench progress panel.

## Milestone Readiness

Phase 7 is ready for milestone audit/closure. Remaining deferred items are v2+ scope: production-ready wrap packages, true UV/3D preview, hosted provider production rollout, auth/billing, marketplace/community, and deployment hardening.
