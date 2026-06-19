# Phase 14: V2 MVP Hardening, Docs, Smoke, And UAT - Context

**Gathered:** 2026-06-19
**Status:** Ready for planning
**Source:** Roadmap Phase 14, Phase 8-13 closure artifacts, live validation scripts, and current docs.

<domain>
## Phase Boundary

Phase 14 closes the v2.0 MVP. It should not add new product capability unless validation reveals a blocker that must be fixed to prove the release. The phase is about trustworthy release evidence: clean aggregate validation, Docker-backed local smoke, hosted-provider manual smoke instructions, desktop/mobile browser UAT across V2 flows, feature-flag and operator docs, release notes, and final traceability.

The output is a release-ready V2 MVP evidence package, not production deployment, auth, billing, marketplace, installer workflow, print-ready handoff, or verified UV production tooling.
</domain>

<decisions>
## Locked Decisions

### Validation

- Full aggregate validation must include `corepack pnpm validate`, `corepack pnpm contracts:check`, `corepack pnpm compat:v1`, and `corepack pnpm migration:safety`.
- Provider-off worker smoke must remain runnable without hosted credentials through `corepack pnpm smoke:worker -- --dry-run`.
- Docker-backed smoke should use existing `pnpm infra:up`, `pnpm smoke:local`, and `pnpm infra:down` paths where Docker is available.
- Live worker queue smoke is valid only after Docker services, API migrations, API process, and worker process are running.

### Hosted Provider Safety

- Hosted-provider smoke remains manual-only unless real credentials, explicit cost approval, quota/rate/cost guards, and account/model access are provided.
- Hosted smoke docs must include setup, one-job evidence to record, and reversal steps that disable hosted flags and remove active credentials from ignored env files.
- The release must not imply hosted provider production readiness by default.

### Browser UAT

- Browser UAT must cover desktop and mobile paths for hosted provider controls, targeted edits, references, lightweight 3D preview, and enhanced handoff export.
- UAT may use seeded local data and provider-off fixtures for paid/credentialed flows, but manual-only hosted smoke must be called out separately.
- Screenshots and fixture ids belong under `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/`.

### Documentation

- Docs must explain all V2 feature flags, provider configuration, quota behavior, reference usage, 3D preview limitations, and concept-only handoff boundaries.
- Release notes must state what V2 MVP does and does not guarantee.
- Existing docs should be updated rather than replaced unless a standalone reference is more usable.

### the agent's Discretion

- Decide whether Phase 14 needs small helper scripts for release smoke orchestration after inspecting existing scripts.
- Decide whether browser UAT should reuse seeded fixtures from prior phases or create a new compact Phase 14 fixture.
- Decide final release-note file location, but keep it under `.planning/` unless user-facing docs need a stable public path.
</decisions>

<canonical_refs>
## Canonical References

### Milestone Scope

- `.planning/ROADMAP.md` - Phase 14 success criteria and six plan names.
- `.planning/REQUIREMENTS.md` - V2-REL-01..05 and traceability status.
- `.planning/STATE.md` - current phase position and accumulated decisions.
- `.planning/PROJECT.md` - current milestone scope, target features, constraints, and out-of-scope boundaries.

### Validation And Smoke

- `package.json` - root validation, smoke, contract, compatibility, and migration commands.
- `scripts/validate-all.mjs` - aggregate validation sequence.
- `scripts/check-contracts.mjs` - contract drift guard.
- `scripts/check-v1-compatibility.mjs` - V1 route/schema/client compatibility guard.
- `scripts/check-migration-safety.mjs` - migration head and ledger table guard.
- `scripts/smoke-local.mjs` - Docker-backed PostgreSQL/Redis/MinIO plus data/generation smoke.
- `scripts/smoke-worker-queue.mjs` - provider-off dry-run and live worker queue smoke.
- `.env.example`, `apps/web/.env.example`, `services/api/.env.example`, `services/worker/.env.example` - feature flag and provider config surfaces.

### Prior Phase Evidence

- `.planning/phases/09-hosted-provider-rollout-mvp/09-MILESTONE-NOTES.md` - hosted-provider guardrails and manual smoke posture.
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-MILESTONE-NOTES.md` - targeted edit closure boundaries.
- `.planning/phases/11-reference-guided-generation-mvp/11-MILESTONE-NOTES.md` - reference-role and rights/source evidence.
- `.planning/phases/12-lightweight-3d-preview-mvp/12-HUMAN-UAT.md` - lightweight 3D browser UAT evidence pattern.
- `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-HUMAN-UAT.md` - enhanced handoff browser UAT evidence pattern.

### Docs

- `README.md` - quickstart and phase flow summary.
- `docs/development.md` - detailed developer/operator runbook.
</canonical_refs>

<specifics>
## Specific Ideas

- Phase 14 should produce `14-VERIFICATION.md`, `14-HUMAN-UAT.md`, `14-MILESTONE-NOTES.md`, and release notes.
- Browser UAT should explicitly prove no critical V2 panels lose readability at mobile width.
- Docker smoke should distinguish a real pass from a documented Docker-unavailable blocker.
- The final report should make it easy for a future operator to rerun V2 validation from a clean checkout.
</specifics>

<deferred>
## Deferred Ideas

- Production deployment, authentication, billing, print-ready handoff, production UV verification, marketplace/community flows, quote/order/payment flows, installer workflows, and automated legal licensing checks remain future milestones.
</deferred>

---
*Phase: 14-v2-mvp-hardening-docs-smoke-and-uat*
*Context gathered: 2026-06-19*
