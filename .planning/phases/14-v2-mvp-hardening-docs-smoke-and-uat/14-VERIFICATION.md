---
phase: 14-v2-mvp-hardening-docs-smoke-and-uat
artifact: verification
status: passed
created: 2026-06-19
updated: 2026-06-19
requirements: [V2-REL-01, V2-REL-02, V2-REL-03, V2-REL-04, V2-REL-05]
---

# Phase 14 Verification - V2 MVP Hardening, Docs, Smoke, And UAT

## Verdict

Passed on 2026-06-19.

Phase 14 closes the V2 MVP release-hardening pass with fresh aggregate validation, contract drift checks, V1 compatibility, migration safety, Docker-backed local smoke evidence, hosted-provider manual smoke runbook, desktop/mobile Browser UAT evidence, feature flag documentation, release notes, and traceability updates. V2 MVP remains concept-only and not print-ready.

## Requirement Evidence

| Requirement | Evidence | Result |
|-------------|----------|--------|
| V2-REL-01 | Final `corepack pnpm validate` passed in an elevated host run after the default sandbox hit host-prerequisite `EPERM` limits. Web lint/typecheck/test, core/API/worker ruff/mypy/pytest, env checks, contract check, and contracts typecheck passed. | Pass |
| V2-REL-02 | `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-DOCKER-SMOKE.md` records Docker availability, `corepack pnpm infra:up`, `corepack pnpm smoke:local`, hosted-disabled `corepack pnpm smoke:worker -- --dry-run`, and cleanup. Live worker smoke was attempted but is not counted as passed. | Pass |
| V2-REL-03 | `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-HOSTED-SMOKE-RUNBOOK.md` records manual-only hosted smoke prerequisites, quota/rate/cost guards, one-job cap, evidence schema, and reversal steps. No live hosted success is claimed without real credentials and cost approval. | Pass |
| V2-REL-04 | `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-HUMAN-UAT.md` records desktop/mobile Browser UAT with screenshots and metrics for hosted guard visibility, targeted edit controls/comparison, reference warnings, lightweight 3D labels, enhanced ZIP preview/history, and no horizontal overflow. | Pass |
| V2-REL-05 | `14-FEATURE-FLAGS.md`, `14-DOCS-CHECK.md`, `README.md`, `docs/development.md`, and `14-RELEASE-NOTES.md` explain V2 feature flags, provider config, quota behavior, reference usage, 3D limits, handoff boundaries, hosted smoke limits, and deferred production scope. | Pass |

## Final Automated Checks

| Command | Result | Notes |
|---------|--------|-------|
| `corepack pnpm validate` | pass | Elevated host run passed. Web: 9 files / 75 tests. Core: ruff, mypy, 58 pytest tests. API: ruff, mypy, 79 pytest tests. Worker: ruff, mypy, 78 pytest tests. Contracts check and contracts typecheck passed. |
| `corepack pnpm contracts:check` | pass | A default sandbox run first failed because contract generation was blocked/fallback-based. Manual regenerate produced no committed diff; final elevated `contracts:check` reported `Contract artifacts are current.` |
| `corepack pnpm compat:v1` | pass | V1 compatibility check passed: 22 routes, 10 schemas, and 21 client surfaces verified. |
| `corepack pnpm migration:safety` | pass | Alembic head `f2d60f906fc6`; 1 migration; V1 ledger tables verified. |
| `corepack pnpm smoke:worker -- --dry-run` | pass | Worker queue smoke dry run passed and printed real live-smoke prerequisites. No hosted provider calls were made. |
| Docs token check | pass | `rg -n "V2_|feature flag|quota|reference|3D|handoff|concept-only|not print-ready|Docker smoke|hosted-provider smoke" README.md docs/development.md .planning/REQUIREMENTS.md .planning/ROADMAP.md .planning/STATE.md .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat` returned expected coverage. |
| `git diff --check` | pass | Whitespace check passed. Git printed an existing CRLF/LF warning for `packages/contracts/openapi/openapi.json`; no working-tree diff remained. |

## Supporting Artifacts

| Artifact | Purpose |
|----------|---------|
| `14-BASELINE-VALIDATION.md` | Plan 01 aggregate baseline evidence. |
| `14-DOCKER-SMOKE.md` | Plan 02 Docker local smoke and hosted-disabled worker dry-run evidence. |
| `14-HOSTED-SMOKE-RUNBOOK.md` | Plan 03 manual hosted-provider smoke checklist, evidence schema, and reversal steps. |
| `14-HUMAN-UAT.md` | Plan 04 desktop/mobile browser screenshots, fixture ids, and DOM metrics. |
| `14-FEATURE-FLAGS.md` | Plan 05 V2 service/public flags, provider variables, quota guards, smoke overrides, and rollback. |
| `14-DOCS-CHECK.md` | Plan 05 docs token and secret-safety check. |
| `14-RELEASE-NOTES.md` | Final V2 MVP release notes and deferred scope. |
| `14-MILESTONE-NOTES.md` | Final milestone closure notes and evidence map. |

## Known Warnings And Limits

- Default sandbox validation can fail due Windows child-process, Corepack, uv, or Python `EPERM` limits. Final evidence uses elevated host runs for commands affected by those host boundaries.
- Web tests log the expected JSDOM `HTMLCanvasElement.getContext()` warning. Browser UAT supplies real UI evidence.
- Worker tests emitted an existing aiosqlite event-loop-close thread warning while still passing.
- Live `corepack pnpm smoke:worker` without `--dry-run` was attempted during Plan 02 but is not counted as passed. The required Docker-backed local smoke and worker dry-run evidence passed.
- Hosted-provider smoke remains manual-only. No real BFL credential, paid call, output quality, account, pricing, moderation, mask/reference-image support, or commercial readiness is claimed.
- V2 MVP remains concept-only and not print-ready. It does not prove production wrap output, verified scale/bleed/color/DPI, production UV mapping, auth, billing, marketplace/community flows, quotes/orders/payments, installer workflows, or production deployment.

## Completion Criteria

- [x] V2-REL-01..05 have evidence.
- [x] Final validation command set passed or environment-specific blockers are recorded honestly.
- [x] Docker-backed local smoke and hosted-disabled worker dry-run evidence exists.
- [x] Hosted-provider manual smoke checklist exists and avoids false live-provider claims.
- [x] Desktop/mobile Browser UAT evidence exists.
- [x] Feature flag, docs, release notes, and milestone notes exist.
- [x] REQUIREMENTS, ROADMAP, VALIDATION, and STATE traceability are updated.

---
*Verified: 2026-06-19*
