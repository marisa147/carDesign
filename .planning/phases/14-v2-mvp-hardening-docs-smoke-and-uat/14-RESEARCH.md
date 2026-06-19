---
phase: 14
slug: v2-mvp-hardening-docs-smoke-and-uat
artifact: research
status: complete
created: 2026-06-19
requirements: [V2-REL-01, V2-REL-02, V2-REL-03, V2-REL-04, V2-REL-05]
---

# Phase 14 Research

## What This Phase Needs To Prove

Phase 14 is a release-readiness phase. The codebase already contains the V2 feature slices, so the plan should spend most effort on evidence quality, repeatability, and honest boundaries.

The release is credible only if a future operator can rerun the documented command set and understand which paths are automated, Docker-backed, browser-observed, or manual-only.

## Existing Validation Surfaces

| Surface | Current Mechanism | Phase 14 Use |
|---------|-------------------|--------------|
| Aggregate local validation | `corepack pnpm validate` runs host prereqs, env example guard, web lint/type/test, core/API/worker ruff/mypy/pytest, contracts check, and contracts typecheck. | Primary V2-REL-01 evidence. |
| Contract drift | `corepack pnpm contracts:check` delegates to package check and `scripts/check-contracts.mjs`. | Must be explicit in 14-01 and final report. |
| V1 compatibility | `corepack pnpm compat:v1` verifies required V1 OpenAPI routes, schemas, and generated client tokens. | Guards V2 changes from breaking the V1 baseline. |
| Migration safety | `corepack pnpm migration:safety` verifies Alembic head and ledger table presence. | Guards clean-checkout database evolution. |
| Docker local smoke | `corepack pnpm smoke:local` checks Docker, PostgreSQL, Redis, MinIO, Alembic upgrade, Phase 2 data smoke, and Phase 3 generation smoke. | Primary V2-REL-02 evidence when Docker is available. |
| Worker queue smoke | `corepack pnpm smoke:worker -- --dry-run` is provider-off; live mode requires API and worker. | Dry-run is release baseline; live mode can be Docker-backed. |

## Existing V2 Feature Evidence

| V2 Area | Evidence Source | Phase 14 Role |
|---------|-----------------|---------------|
| Hosted provider rollout | Phase 9 docs, tests, provider-off UAT, manual provider-on runbook. | Summarize and provide one safe manual smoke checklist. |
| Targeted edits | Phase 10 verification/UAT/docs. | Include in cross-flow Browser UAT and docs reference. |
| Reference guidance | Phase 11 verification/UAT/docs. | Include rights/source and provider unsupported-role checks in UAT/docs. |
| Lightweight 3D | Phase 12 verification/UAT/screenshots. | Include 3D tab/screenshot/fallback labels in cross-flow UAT. |
| Enhanced handoff ZIP | Phase 13 verification/UAT/screenshots. | Include ZIP success and blocked rights/source evidence in cross-flow UAT. |

## Validation Architecture

Phase 14 should create a layered release gate:

1. **Static/aggregate gate**: `validate`, `contracts:check`, `compat:v1`, `migration:safety`, and dry-run worker smoke.
2. **Docker gate**: `infra:up`, `smoke:local`, and optionally live `smoke:worker` with API/worker running.
3. **Manual hosted gate**: documented but skipped unless credentials and cost approval are present.
4. **Browser UAT gate**: desktop/mobile screenshots and notes proving the release surface remains usable.
5. **Docs/release gate**: README, development docs, feature-flag reference, release notes, and final verification report align with the actual codebase.

## Risks And Mitigations

| Risk | Mitigation |
|------|------------|
| Release docs overclaim production readiness. | Repeat concept-only, provider opt-in, manual hosted smoke, non-production 3D, and non-print-ready handoff boundaries. |
| Docker unavailable in the agent environment. | Record a blocker only if Docker cannot run; do not treat `--allow-docker-unavailable` as release evidence. |
| Hosted provider smoke accidentally incurs cost. | Manual checklist requires explicit credentials, quota/rate/cost guards, one-job limit, and reversal steps. |
| Browser UAT becomes too broad for a single run. | Use a compact seeded workspace covering representative controls and cite prior phase evidence for deep per-feature behavior. |
| Final release report drifts from committed code. | Run fresh validation immediately before marking V2-REL-01..05 complete. |

## Planning Implications

- Plan 14-01 should be the release baseline and fix blockers discovered by aggregate validation.
- Plan 14-02 should treat Docker-backed smoke as real evidence, not a doc-only checkbox.
- Plan 14-03 should avoid real hosted calls unless explicit external prerequisites exist.
- Plan 14-04 should focus on end-to-end user-facing release confidence across V2 controls.
- Plan 14-05 should make the operator/developer path self-contained.
- Plan 14-06 should be the final sign-off and traceability update.

---
*Research complete: 2026-06-19*
