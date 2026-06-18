---
phase: 08
slug: v1-closure-and-v2-readiness-gate
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-18
---

# Phase 08 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Vitest, pytest, ruff, mypy, eslint, tsc, custom Node smoke scripts |
| **Config file** | `package.json`, service `pyproject.toml`, `apps/web/package.json` |
| **Quick run command** | `corepack pnpm contracts:check` |
| **Full suite command** | `corepack pnpm validate` |
| **Estimated runtime** | ~120-600 seconds depending on host prerequisites |

---

## Sampling Rate

- **After every task commit:** Run the focused command listed in the task.
- **After every plan wave:** Run `corepack pnpm contracts:check` plus the focused tests touched by that wave.
- **Before `$gsd-verify-work`:** `corepack pnpm validate` must be green, and smoke/UAT evidence must be recorded or explicitly blocked by host prerequisites.
- **Max feedback latency:** 10 minutes for full local validation on a prepared host.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | V2-READY-01 | — | N/A | static/doc | `Test-Path .planning/milestones/v1.0-MILESTONE-AUDIT.md` | yes | pending |
| 08-02-01 | 02 | 2 | V2-READY-03, V2-READY-04 | T-08-01 | V2 flags remain disabled by default and secrets are not exposed | config/unit | `cd services/api && uv run pytest -q tests/test_config.py && cd ../worker && uv run pytest -q tests/test_config.py` | existing | pending |
| 08-03-01 | 03 | 3 | V2-READY-02 | T-08-02 | Contract checks do not leak secrets or break existing v1 clients | contract | `corepack pnpm contracts:check` | existing | pending |
| 08-04-01 | 04 | 3 | V2-READY-02 | T-08-03 | Migration path does not corrupt durable ledger state | migration | `cd services/api && uv run alembic upgrade head && uv run alembic current` | existing | pending |
| 08-05-01 | 05 | 4 | V2-READY-01..04 | T-08-04 | Readiness report truthfully documents evidence and blockers | aggregate/manual | `corepack pnpm validate` | yes | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers the phase; no new test framework is required.
- If config flag tests are missing, Plan 08-02 must add focused tests before implementation.
- If compatibility script tests are missing, Plan 08-03 must add command dry-run or contract assertions before implementation.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Browser readiness UAT | V2-READY-01, V2-READY-04 | Requires running web/API/worker and visual inspection | Start local services, open workbench, confirm V1 workflow loads and V2/future gates remain disabled or clearly labeled. |
| Live Docker smoke | V2-READY-02 | Docker daemon may not be available in sandbox | On a Docker-enabled host, run `pnpm infra:up`, `pnpm smoke:local`, `pnpm smoke:worker`, then `pnpm infra:down`. |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or documented host prerequisite gates.
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify.
- [ ] Wave 0 covers all missing references.
- [ ] No watch-mode flags.
- [ ] Feedback latency < 10 minutes on a prepared host.
- [ ] `nyquist_compliant: true` set in frontmatter.

**Approval:** pending
