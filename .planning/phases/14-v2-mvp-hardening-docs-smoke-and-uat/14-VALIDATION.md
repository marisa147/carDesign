---
phase: 14
slug: v2-mvp-hardening-docs-smoke-and-uat
status: planned
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-19
requirements: [V2-REL-01, V2-REL-02, V2-REL-03, V2-REL-04, V2-REL-05]
---

# Phase 14 - Validation Strategy

> Release-readiness validation contract for V2 MVP aggregate checks, Docker smoke, hosted-provider manual smoke, browser UAT, docs, release notes, and final milestone evidence.

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | pnpm scripts, pytest, Vitest, ruff, mypy, eslint, tsc, Docker Compose smoke, browser UAT |
| Config file | `package.json`, service `pyproject.toml`, env examples, `infra/compose.yml` |
| Quick run command | `corepack pnpm validate` |
| Full release command set | `corepack pnpm validate && corepack pnpm contracts:check && corepack pnpm compat:v1 && corepack pnpm migration:safety && corepack pnpm smoke:worker -- --dry-run` |
| External-call default | Disabled; hosted provider smoke is manual-only |
| Docker evidence | `corepack pnpm infra:up`, `corepack pnpm smoke:local`, optional live `corepack pnpm smoke:worker`, `corepack pnpm infra:down` |

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 1 | V2-REL-01 | T-14-01 | Aggregate validation proves source, contracts, tests, typing, and V1 compatibility are green | aggregate | `corepack pnpm validate && corepack pnpm contracts:check && corepack pnpm compat:v1 && corepack pnpm migration:safety && corepack pnpm smoke:worker -- --dry-run` | yes | green |
| 14-02-01 | 02 | 2 | V2-REL-02 | T-14-02 | Docker smoke proves local deterministic infra and hosted-disabled behavior without secrets | docker/smoke | `corepack pnpm infra:up && corepack pnpm smoke:local && corepack pnpm smoke:worker -- --dry-run && corepack pnpm infra:down` | yes | green |
| 14-03-01 | 03 | 2 | V2-REL-03 | T-14-03 | Hosted-provider smoke is manual-only, cost-guarded, reversible, and secret-safe | docs/manual | docs token check plus optional manual evidence | yes | green |
| 14-04-01 | 04 | 3 | V2-REL-04 | T-14-04 | Browser UAT covers desktop/mobile V2 workbench flows without overlap or false production claims | browser | browser screenshots and UAT checklist | yes | green |
| 14-05-01 | 05 | 4 | V2-REL-05 | T-14-05 | Docs explain flags, provider config, quotas, references, 3D limits, and handoff boundaries | docs | `rg -n "V2_|feature flag|quota|reference|3D|handoff|concept-only" README.md docs/development.md .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat` | yes | green |
| 14-06-01 | 06 | 5 | V2-REL-01..05 | T-14-06 | Final evidence closes all V2 release requirements and updates traceability truthfully | release | final validation command set plus docs/UAT evidence | planned | pending |

*Status: pending / green / red / flaky*

## Focused Commands

| Area | Command |
|------|---------|
| Aggregate validation | `corepack pnpm validate` |
| Contract drift | `corepack pnpm contracts:check` |
| V1 compatibility | `corepack pnpm compat:v1` |
| Migration safety | `corepack pnpm migration:safety` |
| Worker dry-run | `corepack pnpm smoke:worker -- --dry-run` |
| Docker local smoke | `corepack pnpm infra:up; corepack pnpm smoke:local; corepack pnpm infra:down` |
| Live worker smoke | `corepack pnpm smoke:worker` after Docker/API/worker are running |
| Docs token check | `rg -n "V2_|feature flag|quota|reference|3D|handoff|concept-only|not print-ready" README.md docs/development.md .planning/REQUIREMENTS.md .planning/ROADMAP.md .planning/STATE.md .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat` |
| Whitespace | `git diff --check` |

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Hosted provider one-job smoke | V2-REL-03 | Requires real credentials, account access, quota/cost approval, and provider availability | Follow the Phase 14 hosted smoke runbook; record job/version/artifact/model-run/cost/failure evidence; disable hosted flags afterward. |
| Cross-flow browser UAT | V2-REL-04 | Confirms dense real workbench layout and release copy across desktop/mobile | Use browser automation or manual browser inspection with screenshots for hosted controls, targeted edits, references, 3D, and handoff ZIP. |
| Docker-backed live worker smoke | V2-REL-02 | Requires Docker daemon and local background API/worker processes | Start infra, migrate API, start API, start worker with Windows-safe solo pool, then run `pnpm smoke:worker`. |

## Validation Sign-Off

- [ ] Aggregate validation passed fresh.
- [ ] Contract drift check passed fresh.
- [ ] V1 compatibility and migration safety passed fresh.
- [ ] Docker-backed smoke passed or blocker is honestly recorded.
- [ ] Hosted-provider manual smoke is documented and either performed with evidence or explicitly skipped with reason.
- [ ] Browser UAT desktop/mobile evidence exists.
- [x] Docs explain V2 flags, provider config, quota behavior, reference usage, 3D limits, and concept-only handoff.
- [ ] Release notes explain V2 flags, provider config, quota behavior, reference usage, 3D limits, and concept-only handoff.
- [ ] Requirements V2-REL-01..05 are marked complete only after evidence exists.
- [ ] `nyquist_compliant: true` set in frontmatter.

**Approval:** pending.
