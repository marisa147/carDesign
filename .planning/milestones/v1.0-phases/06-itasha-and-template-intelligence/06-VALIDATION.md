---
phase: 6
slug: itasha-and-template-intelligence
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-18
---

# Phase 6 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | pytest for core/API/worker; Vitest + Testing Library for web; Orval/TypeScript for contracts |
| Config file | `services/core/pyproject.toml`, `services/api/pyproject.toml`, `services/worker/pyproject.toml`, `apps/web/package.json`, `packages/contracts/package.json` |
| Quick run command | `uv run pytest -q tests/test_generation_briefs.py`; `corepack pnpm --filter @caragent/web test -- --run apps/web/src/app/page.test.tsx` |
| Full suite command | `corepack pnpm validate` |
| Estimated runtime | Targeted tests under 30 seconds each; full validation depends on Docker/Node/Python cache state |

## Sampling Rate

- After every backend task commit: run the targeted pytest file for the touched service plus ruff/mypy before the plan summary.
- After every frontend task commit: run the targeted Vitest file plus web lint/typecheck before the plan summary.
- After every contract change: regenerate OpenAPI/contracts and run `corepack pnpm contracts:check`.
- After every plan wave: run all touched service tests for that wave.
- Before `$gsd-verify-work`: `corepack pnpm validate`, `corepack pnpm smoke:local`, and Browser desktop/mobile UAT must be green.
- Max targeted feedback latency: 30 seconds per focused command.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | QUAL-01, QUAL-03, QUAL-04, QUAL-05 | T-06-01 | Pydantic validates user-controlled fields and normalizes warning data | unit | `uv run pytest -q tests/test_generation_briefs.py tests/test_prompt_plans.py` | yes | pending |
| 06-01-02 | 01 | 1 | QUAL-04, QUAL-05 | T-06-02 | Template normalization does not claim unsupported template support | unit | `uv run pytest -q tests/test_generation_briefs.py tests/test_prompt_plans.py` | yes | pending |
| 06-02-01 | 02 | 2 | QUAL-02, QUAL-05 | T-06-03 | Worker stores renderer-neutral metadata without leaking secrets | unit | `uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py` | yes | pending |
| 06-02-02 | 02 | 2 | QUAL-02, QUAL-03 | T-06-04 | Missing-rights assets remain blocked before provider generation | unit | `uv run pytest -q tests/test_generation_tasks.py` | yes | pending |
| 06-03-01 | 03 | 3 | QUAL-01, QUAL-05 | T-06-05 | API schema exposes only typed/validated fields through OpenAPI | unit/contract | `uv run pytest -q tests/test_generation.py tests/test_openapi_export.py` | yes | pending |
| 06-03-02 | 03 | 3 | QUAL-01, QUAL-05 | T-06-05 | Generated contracts match current OpenAPI | contract | `corepack pnpm contracts:check` | yes | pending |
| 06-04-01 | 04 | 4 | QUAL-01, QUAL-03 | T-06-06 | UI renders user text as React text, not raw HTML | unit | `corepack pnpm --filter @caragent/web test -- --run apps/web/src/app/page.test.tsx` | yes | pending |
| 06-04-02 | 04 | 4 | QUAL-02, QUAL-04 | T-06-07 | Overlay controls stay bounded in preview and expose selected state | unit | `corepack pnpm --filter @caragent/web test -- --run apps/web/src/app/page.test.tsx` | yes | pending |
| 06-05-01 | 05 | 5 | QUAL-05 | T-06-08 | Export manifest preserves concept-only disclaimer and redacts sensitive values | unit | `corepack pnpm --filter @caragent/web test -- --run apps/web/src/app/page.test.tsx` | yes | pending |
| 06-05-02 | 05 | 5 | QUAL-01..QUAL-05 | T-06-09 | End-to-end smoke proves durable preview-spec path remains runnable | smoke/browser | `corepack pnpm validate`; `corepack pnpm smoke:local` | yes | pending |

## Wave 0 Requirements

Existing infrastructure covers all phase requirements:

- `services/core/tests/test_generation_briefs.py`
- `services/core/tests/test_prompt_plans.py`
- `services/api/tests/test_generation.py`
- `services/api/tests/test_openapi_export.py`
- `services/worker/tests/test_generation_tasks.py`
- `services/worker/tests/test_image_providers.py`
- `apps/web/src/app/page.test.tsx`
- `scripts/validate-all.mjs`
- `scripts/smoke-local.mjs`

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Desktop/mobile overlay layout has no visual overlap or horizontal scroll | QUAL-02, QUAL-04 | Browser rendering and viewport geometry need visual/runtime inspection | Open `http://127.0.0.1:3000`, verify desktop and 390px/320px mobile workbench layouts with Browser viewport checks, console check, and overlap/scrollWidth evaluation |

## Validation Sign-Off

- [x] All tasks have automated verify or existing Wave 0 test infrastructure.
- [x] Sampling continuity: no three consecutive implementation tasks lack automated verify.
- [x] Wave 0 infrastructure exists for all referenced test files.
- [x] No watch-mode flags in planned commands.
- [x] Targeted feedback latency target is below 30 seconds.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** approved 2026-06-18
