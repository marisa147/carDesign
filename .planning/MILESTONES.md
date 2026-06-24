# Project Milestones: 痛车设计生成 Agent

## v4.0 Real Generation Closure And Reliability (Implemented: 2026-06-22)

**Delivered:** A reliability-focused closure layer for the concept workflow: explicit generation entry, real artifact image preview, shared API/Worker object storage, durable dispatch outbox, conditional worker claim, short worker transactions, real 3D screenshots, clearable fields, strict parser boundary, template compositor, workspace ownership, safer uploads/downloads, hosted quota reserve/settle, and traceable operations metadata.

**Phases completed:** 21-26

**Key accomplishments:**

- Added the explicit `生成概念` workbench path, active job polling, artifact content URLs, and real image rendering in the 2D preview.
- Unified object storage settings and contract across API and Worker with file metadata preservation and workspace-scoped artifact streaming.
- Added `job_dispatch_outbox`, `generation_jobs.state_version`, after-commit dispatch, conditional worker claim, and committed progress events during provider calls.
- Replaced fake 3D screenshot bytes with real canvas capture and fixed parameter/reference clearing semantics.
- Introduced strict `BriefParser`/`BriefDraft` boundaries and deterministic template-mask composition for local generation.
- Hardened workspace ownership, upload/provider-download validation, hosted quota reserve/settle, and trace metadata.

**Stats:**

- 6 phases, 23/23 v4 requirements complete.
- Current state marks the milestone archive-ready; formal archive/audit can still be run before tagging if needed.

**Verification:**

- Phase validations and aggregate `pnpm validate` were recorded during v4 completion.
- Docker/local smoke evidence was recorded during Phase 26 closure.

**Archives:**

- Formal v4 archive files are still pending if `$gsd-complete-milestone` is run.

**What's next:** v5.0 GR86/BRZ Construction Package Customization has been initialized from user-confirmed requirement-completion discussion; start Phase 27 with `$gsd-plan-phase 27`.

---
## v3.0 Template Library And Production Readiness (Shipped: 2026-06-20)

**Delivered:** A trustworthy template foundation and concept-only production readiness layer: source/license governance, five internal-original MVP templates, catalog selection, template-aware generation/preview/editing, production-readiness preflight, enhanced handoff evidence, and release validation.

**Phases completed:** 15-20 (33 plans total)

**Key accomplishments:**

- Established template source governance with source/license/readiness metadata, prohibited-source blocking, audit output, and legacy `generic-side-coupe` compatibility.
- Added five internal-original generic side-view templates for coupe, sedan, hatchback, SUV, and van with required assets, thumbnails, safe zones, masks, metadata, and a validation command.
- Exposed template catalog list/detail APIs, thumbnail serving, and Workbench selection with source/license/readiness warnings and selected-template persistence.
- Carried selected-template context through local generation, PreviewSpec overlays, targeted edits, reference/provider trace, durable worker records, 3D compatibility/fallback, artifacts, versions, and exports.
- Added concept-only production readiness preflight plus enhanced handoff ZIP evidence for `production-readiness-preflight.json` and `template-validation.json`.
- Closed the release with aggregate validation, template-pack validation, V1 compatibility, migration safety, Docker/local smoke, worker dry-run, desktop/mobile Browser UAT, docs, release notes, and milestone audit.

**Stats:**

- 6 phases, 33 plans, 31/31 v3 requirements complete.
- 7 commits after `v2.0` through the Phase 20 closure commit.
- Milestone diff from `v2.0` to closure: 201 files changed, 10,648 insertions, 199 deletions.
- Current source-plus-test-and-doc scale snapshot: about 35,525 lines across `apps/`, `packages/`, `services/`, `scripts/`, `infra/`, `docs/`, and `README.md`, excluding generated contracts and dependency folders.
- Known deferred items at close: 8 UAT metadata/status items from `audit-open`; Phase 20 UAT passed with 0 pending scenarios (see `.planning/STATE.md` Deferred Items).

**Verification:**

- Final Phase 20 verification passed: aggregate validation, template-pack validation, V1 compatibility, migration safety, worker dry-run, Docker/local smoke, docs, release notes, whitespace check, and milestone audit.
- Browser UAT passed on desktop and mobile for template catalog selection, selected van PreviewSpec evidence, targeted edit controls, 3D fallback, enhanced handoff files, production preflight, concept-only labels, and no horizontal overflow.
- Production readiness preflight remains an evidence-gap report. It does not unlock print-ready PSD/AI/PDF output, verified UV, installer readiness, or real licensed-template production claims.

**Git range:** `v2.0` through `97ac11a chore(20): harden v3 release`.

**Archives:**

- `.planning/milestones/v3.0-ROADMAP.md`
- `.planning/milestones/v3.0-REQUIREMENTS.md`
- `.planning/milestones/v3.0-MILESTONE-AUDIT.md`

**What's next:** start the next milestone with `$gsd-new-milestone` from the next source document or product direction.

---

## v1.0 MVP (Shipped: 2026-06-18)

**Delivered:** End-to-end itasha concept-generation workbench from natural-language brief to structured parameters, asynchronous 2D concept render, preview, iteration, feedback, export, and operations visibility.

**Phases completed:** 1-7 (54 plans total)

**Key accomplishments:**

- Established the runnable monorepo, local Docker services, runtime pins, validation commands, typed FastAPI/OpenAPI contracts, and Next.js workbench foundation.
- Built the durable product ledger for workspaces, messages, structured briefs, uploads, jobs, events, artifacts, versions, model runs, feedback, exports, costs, and lineage.
- Shipped the first text-to-2D generation path through a local deterministic provider and Celery worker, preserving prompt/provider/model-run traceability.
- Integrated the Web workbench: chat, structured parameters, asset rights gating, progress/events, 2D preview controls, variant history, future gates, and responsive Browser UAT coverage.
- Added versioned iteration, feedback, approval/rejection, concept preview export, metadata manifest/history, itasha controls, safe-zone overlays, deterministic text/logo layers, quality warnings, and PreviewSpec persistence.
- Hardened operations with provider/worker/queue health, classified failures, cancellation, provider routing, bounded retry/fallback, hosted quota/rate/cost guards, worker smoke, and diagnostic sanitization.

**Stats:**

- 7 phases, 54 plans, 42/42 v1 requirements complete.
- 268 milestone worktree files created/modified before archive, excluding runtime generated worker artifacts.
- About 112 source files / 17,452 LOC, or 120 source-plus-test files / 19,836 LOC across `apps/`, `packages/`, `services/`, `scripts/`, and `infra/`.
- Known deferred items at close: 5 UAT metadata/status items with 0 pending scenarios (see `.planning/STATE.md` Deferred Items).

**Verification:**

- Milestone audit passed: requirements 42/42, phases 7/7, plans 54/54, integration 7/7, flows 7/7.
- Final validation included web tests/lint/typecheck, API/core/worker ruff/mypy/pytest, contracts check/typecheck, Docker smoke, live worker queue smoke, and Browser desktop/mobile UAT.

**Git range:** initial v1 work snapshot through `v1.0` milestone archive commit.

**Archives:**

- `.planning/milestones/v1.0-ROADMAP.md`
- `.planning/milestones/v1.0-REQUIREMENTS.md`
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md`

**What's next:** v2.0 V2 MVP planning has been initialized from `C:/Users/25858/Downloads/V2_MVP_ROADMAP (1).md`; start Phase 8 with `$gsd-discuss-phase 8` or `$gsd-plan-phase 8`.

---

## v2.0 V2 MVP (Shipped: 2026-06-19)

**Delivered:** A guarded V2 concept-review workflow on top of the v1.0 workbench: hosted provider rollout controls, targeted edits, reference guidance, lightweight 3D preview, enhanced concept handoff ZIPs, and final release hardening evidence.

**Phases completed:** 8-14 (48 plans total)

**Key accomplishments:**

- Established a V2 readiness gate from the archived v1.0 baseline, including compatibility checks, migration safety, and default-off feature flags.
- Added a guarded BFL Hosted Provider path with provider capability metadata, preflight, quota/rate/cost guards, trace/cost/failure diagnostics, workbench provider selector, and provider-off/provider-on runbooks.
- Shipped Targeted editing with selectable PreviewSpec regions/layers, mask preview, deterministic recomposition, provider-mask guardrails, retry-safe failures, and parent/child comparison evidence.
- Added Reference guidance with six roles, rights/source snapshots, provider unsupported-role warnings, durable trace metadata, and child-iteration reference reuse.
- Added lightweight 3D preview with `Preview3DSpec`, one `generic-side-coupe-lightweight-v1` shell, camera controls, screenshot artifacts, fallback states, and persistent concept-only/UV-not-verified labels.
- Added enhanced concept handoff ZIP exports with stable manifests, Markdown reports, prompt/provider traces, reference manifests, immutable package artifacts, Workbench ZIP UX, and rights/source guardrails.
- Closed the release with aggregate validation, contract drift check, V1 compatibility, migration safety, Docker smoke, hosted-provider smoke runbook, Browser UAT, feature flag docs, release notes, and traceability.

**Stats:**

- 7 phases, 48 plans, 34/34 v2 requirements complete.
- 145 commits after `v1.0` through the Phase 14 closure commit.
- Milestone diff from `v1.0` to closure: 409 files changed, 35,969 insertions, 510 deletions.
- Current source-plus-test scale snapshot: about 30,301 lines across `apps/`, `packages/`, `services/`, `scripts/`, and `infra/`, excluding generated contracts and dependency folders.
- Known deferred items at close: 7 UAT metadata/status items from `audit-open`; Phase 8 records 2 pending scenarios, later Phase 14 release UAT passed (see `.planning/STATE.md` Deferred Items).

**Verification:**

- Final Phase 14 verification passed: aggregate validation, contract drift check, V1 compatibility, migration safety, worker dry-run, docs token check, and whitespace check.
- Docker smoke passed for PostgreSQL, Redis, MinIO, Alembic, durable data, and local deterministic generation.
- Browser UAT passed on desktop and mobile for hosted guard visibility, Targeted edits, Reference warnings, 3D preview, enhanced handoff ZIP, and no horizontal overflow.
- Hosted Provider smoke remains manual-only, credentialed, quota/cost guarded, one-job limited, and reversible. No live hosted output quality/account/pricing/moderation readiness is claimed.

**Git range:** `v1.0` through `092cd62 docs(14-06): close v2 mvp milestone`.

**Archives:**

- `.planning/milestones/v2.0-ROADMAP.md`
- `.planning/milestones/v2.0-REQUIREMENTS.md`

**What's next:** start the next milestone with `$gsd-new-milestone`. Fresh requirements should be defined before implementation resumes.

---

