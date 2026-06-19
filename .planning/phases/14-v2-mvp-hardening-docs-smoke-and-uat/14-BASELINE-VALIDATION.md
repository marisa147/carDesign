---
phase: 14-v2-mvp-hardening-docs-smoke-and-uat
artifact: baseline-validation
status: passed
created: 2026-06-19
updated: 2026-06-19
requirements: [V2-REL-01]
---

# Phase 14 Baseline Validation

## Verdict

Passed on 2026-06-19.

This baseline establishes the V2 MVP release hardening starting point. All required aggregate, contract, compatibility, migration, and provider-off worker dry-run checks passed fresh after Phase 14 planning was committed.

## Commands

| Command | Result | Evidence |
|---------|--------|----------|
| `corepack pnpm validate` | pass | Host prereqs and env examples passed; web lint/typecheck/test passed; core/API/worker ruff, mypy, and pytest passed; contracts check and contracts typecheck passed. |
| `corepack pnpm contracts:check` | pass | `Contract artifacts are current.` |
| `corepack pnpm compat:v1` | pass | `V1 compatibility check passed: 22 routes, 10 schemas, and 21 client surfaces verified.` |
| `corepack pnpm migration:safety` | pass | Alembic head `f2d60f906fc6`; 1 migration; V1 ledger tables verified. |
| `corepack pnpm smoke:worker -- --dry-run` | pass | Worker queue smoke dry run passed; real smoke prerequisites printed for live API/worker path. |

## `corepack pnpm validate` Details

- Web: 9 test files / 75 tests passed.
- Core: ruff passed, mypy passed for 21 source files, full pytest passed 58 tests.
- API: ruff passed, mypy passed for 15 source files, full pytest passed 79 tests.
- Worker: ruff passed, mypy passed for 11 source files, full pytest passed 78 tests.
- Contracts: check passed and contracts typecheck passed.

## Known Warnings

- Web tests log the expected JSDOM `HTMLCanvasElement.getContext()` not implemented message. Browser UAT remains the real canvas/UI evidence path.
- Worker tests emitted existing aiosqlite event-loop-close thread warnings while still passing. These warnings did not fail pytest and are tracked as release notes context, not a Phase 14 blocker.
- Elevated host execution was used for `corepack pnpm validate` because Windows sandbox execution can block child-process spawning and uv cache access.

## Follow-Up

- Plan 14-02 still needs Docker-backed local smoke and live worker smoke status.
- Plan 14-03 still needs the manual hosted-provider smoke runbook.
- Plan 14-04 still needs desktop/mobile Browser UAT evidence.

---
*Baseline verified: 2026-06-19*
