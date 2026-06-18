---
phase: 08-v1-closure-and-v2-readiness-gate
status: baseline-recorded
requirements:
  - V2-READY-01
  - V2-READY-02
created: 2026-06-18
---

# Phase 8 Readiness Baseline

Phase 8 starts V2 from explicit v1.0 evidence. This file is the baseline inventory for V2 readiness work: what shipped, where the archived proof lives, which command surfaces prove the local V1 path still runs, and which capabilities stay deferred.

## Baseline Marker

| Marker | Value |
|--------|-------|
| Release tag | `v1.0` |
| Tag object | `0939ca9` |
| Tagged commit | `f59390e` |
| Commit subject | `chore: archive v1.0 milestone` |
| Audit status | `passed` |
| Audit date | `2026-06-18T06:35:00Z` |

The `v1.0` annotated tag is the release marker. The milestone archive commit `f59390e` is the equivalent immutable baseline commit for V2 readiness checks.

## Archived Evidence

| Evidence | Path | Baseline Use |
|----------|------|--------------|
| Milestone summary | `.planning/MILESTONES.md` | Human-readable v1.0 release summary, metrics, and archive pointers. |
| Milestone audit | `.planning/milestones/v1.0-MILESTONE-AUDIT.md` | Audit verdict, requirement coverage, integration coverage, deferred scope, and known validation debt. |
| Archived roadmap | `.planning/milestones/v1.0-ROADMAP.md` | Original seven-phase roadmap and completion state. |
| Archived requirements | `.planning/milestones/v1.0-REQUIREMENTS.md` | Completed v1 requirement ledger and traceability. |
| Archived phase artifacts | `.planning/milestones/v1.0-phases/` | 54 plan/summary/verification/UAT artifacts from Phases 1 through 7. |
| Final operations closure | `.planning/milestones/v1.0-phases/07-operations-and-provider-strategy/07-07-SUMMARY.md` | Latest provider, operations, smoke, docs, and Browser UAT closure evidence. |
| Root runbook | `README.md` | Quickstart, core commands, focused checks, and phase behavior summary. |
| Development runbook | `docs/development.md` | Host prerequisites, validation commands, smoke instructions, provider guardrails, UAT, and troubleshooting. |

## v1.0 Audit Snapshot

The v1.0 audit passed with no critical gaps:

| Area | Result |
|------|--------|
| Requirements | 42/42 |
| Phases | 7/7 |
| Plans | 54/54 |
| Integration flows | 7/7 |
| End-to-end flows | 7/7 |

The audit records Nyquist validation metadata as partial for some older phases, but that is non-blocking because phase verification files, automated checks, smoke evidence, and Browser UAT artifacts exist.

## Latest Operations Baseline

Phase 7 is the latest shipped runtime baseline before V2. It provides:

- `/operations/provider-status` for provider, worker, queue, and hosted guard status.
- `POST /jobs/{job_id}/cancel` for queued/running job cancellation.
- Structured failure category/stage/provider metadata with diagnostic sanitization.
- Hosted call quota/rate/cost guards.
- `pnpm smoke:worker` dry-run and live queue smoke paths.
- Browser UAT evidence for operations status, cancellation, failed metadata, desktop layout, mobile layout, and console cleanliness.

Hosted provider production readiness remains out of scope for this baseline. V1 only proves guarded opt-in behavior plus local deterministic generation as the default evidence path.

## Readiness Command Index

Run these commands from the repository root unless a command says otherwise.

| Command | Evidence Produced |
|---------|-------------------|
| `pnpm validate` | Aggregate lint, typecheck, unit tests, env guard, and contract drift checks across web, contracts, core, API, and worker. |
| `pnpm contracts:check` | Confirms generated OpenAPI and TypeScript contracts are in sync. |
| `pnpm infra:up` | Starts local PostgreSQL, Redis, and MinIO for live smoke evidence. |
| `pnpm smoke:local` | Verifies Docker-backed local infrastructure, Alembic migration, durable data, and local deterministic generation smoke. |
| `pnpm smoke:worker -- --dry-run` | Verifies worker smoke command wiring without requiring running services. |
| `pnpm smoke:worker` | Live API -> Redis/Celery -> worker -> durable artifact/version smoke. Requires Docker services, migrated API database, API process, and worker process. |

Host-only Browser UAT remains required for visual readiness evidence:

1. Start `pnpm infra:up`, run API migrations, then start `pnpm dev:api`, a Windows-safe worker, and `pnpm dev:web`.
2. Open the workbench.
3. Confirm the V1 workbench loads with chat, parameters, assets, progress, 2D preview, version history, iteration, feedback, concept export, and operations status paths.
4. Confirm future/V2 gates remain disabled, deferred, or clearly labeled.
5. Confirm hosted provider production rollout is not enabled by default.

## Deferred Scope

The following items are explicitly not proven by Phase 8 or the v1.0 baseline:

- Production-ready wrap packages, print preflight, layered source handoff, and installer notes.
- True UV-mapped 3D preview, material simulation, and vehicle-specific production alignment.
- Hosted provider production rollout, provider quality, pricing, moderation, account access, quotas, and commercial-rights readiness.
- Targeted masked editing, reference-guided provider usage, lightweight 3D preview, and enhanced handoff package behavior.
- Auth, billing, marketplace/community, quote/order/payment, installer network, collaboration, deployment hardening, and automated licensing verification.

## Phase 8 Boundary

This baseline allows Phase 8 to add readiness documentation, default-off V2 feature flags, contract compatibility checks, migration-safety proof, and final smoke/UAT checklists. It does not authorize enabling hosted provider calls, targeted editing, reference-guided generation, 3D preview, enhanced handoff, or production handoff behavior by default.
