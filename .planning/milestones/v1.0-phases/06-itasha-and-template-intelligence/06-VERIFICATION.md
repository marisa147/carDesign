---
status: passed
phase: 06-itasha-and-template-intelligence
verified: 2026-06-18
source:
  - 06-01-SUMMARY.md
  - 06-02-SUMMARY.md
  - 06-03-SUMMARY.md
  - 06-04-SUMMARY.md
  - 06-05-PLAN.md
requirements:
  - QUAL-01
  - QUAL-02
  - QUAL-03
  - QUAL-04
  - QUAL-05
---

# Phase 6 Verification

Phase 6 passes automated validation, Docker-backed local smoke, and Browser UAT for itasha/template intelligence.

## Automated Evidence

| Command | Result | Evidence |
|---------|--------|----------|
| `node -e "... docs/development.md ..."` | PASS | Required docs tokens present: `Phase 6`, `itasha`, `PreviewSpec`, `safe-zone`, `overlay`, `concept preview`. |
| `cd services/api && uv run pytest -q tests/test_generation.py -k recomputes_quality_warnings` | RED then PASS | New regression first failed because PATCH did not recompute quality warnings, then passed after fix. |
| `cd services/api && uv run pytest -q tests/test_generation.py tests/test_openapi_export.py` | PASS | 11 tests passed after warning-refresh fix. |
| `cd services/core && uv run pytest -q tests/test_generation_briefs.py tests/test_prompt_plans.py` | PASS | 8 tests passed after helper addition. |
| `cd services/api && uv run ruff check .` | PASS | All checks passed. |
| `cd services/api && uv run mypy src` | PASS | No issues found in 14 source files. |
| `cd services/core && uv run ruff check .` | PASS | All checks passed. |
| `cd services/core && uv run mypy src` | PASS | No issues found in 16 source files. |
| `corepack pnpm validate` | PASS | Web lint/typecheck/test passed; 40 web tests passed; core 33 tests passed; API 35 tests passed; worker 25 tests passed; contracts current and typecheck passed. |
| `corepack pnpm smoke:local` | PASS | PostgreSQL, Redis, MinIO, Alembic durable data smoke, and local deterministic generation smoke passed. |
| Post-restart queued generation | PASS | After restarting Celery with `--pool=solo`, queued job `2b022613-938b-409e-8422-d6e70e27fcc5` succeeded with `has_preview_spec: true` and `warning_count: 1`. |
| `06-REVIEW.md` quick local review | PASS | 4 source/test files reviewed; no findings. |

Note: `corepack pnpm validate` completed with exit code 0 and two pre-existing `aiosqlite` thread-close warnings in API tests. They did not fail the suite.

## Browser UAT Evidence

Browser target: `http://127.0.0.1:3000/` with API `http://127.0.0.1:8000`.

UAT workspace/brief:
- workspace: `f4080584-cef6-4067-98d4-7ebfa6204d74`
- brief: `29bb9769-4e3d-46cb-9cde-0dc611b6a956`
- final PreviewSpec job: `176ca7f0-4562-49aa-a4ea-02fbd563cf89`
- final PreviewSpec version: `2a31f477-7e1c-406b-bbaa-4dda941c2a42`

Observed Browser checks:
- Desktop viewport: client `1265 x 900`, `scrollWidth == clientWidth`, console errors `0`, overlap count `0`.
- Mobile viewport: requested `390 x 844`, measured client width `375`, `scrollWidth == clientWidth`, console errors `0`, button overflow `[]`, overlap count `0`.
- Visible UI copy: `痛车设计控制`, `角色焦点`, `辅助图形`, `赛车/JDM 元素`, `字体意图`, `配色协调`, `质量提示`, `PreviewSpec 摘要`, `文字/Logo 图层`, `安全区`, `模板参考区`.
- PreviewSpec summary showed `图层 1`, `安全区 5`, `警告 1`.
- Safe-zone toggle changed `aria-pressed` from `false` to `true` and displayed `door-main` and `rear-quarter`.
- Overlay toggle changed `aria-pressed` from `true` to `false` and back to `true`.
- Concept export remained concept-only and displayed `Concept preview only, not print-ready.` plus PreviewSpec warning summary.

## Requirement Evidence

| Requirement | Status | Evidence |
|-------------|--------|----------|
| QUAL-01 | PASS | API schemas, generated contracts, and workbench parameter panel expose character focus, supporting graphics, racing/JDM cues, typography intent, and color harmony. Browser UAT confirmed all labels visible and editable. |
| QUAL-02 | PASS | Worker persists deterministic overlay metadata and local provider renders text/logo overlay evidence. Browser UAT confirmed `文字/Logo 图层` toggle with `aria-pressed` state and PreviewSpec `图层 1`. |
| QUAL-03 | PASS | Core creates quality/template warnings; API PATCH now recomputes warning data after edits. Browser UAT confirmed `质量提示`, `Text may be hard to read`, and PreviewSpec `警告 1`. |
| QUAL-04 | PASS | Template safe zones are stored in PreviewSpec and rendered by the workbench. Browser UAT confirmed `安全区` toggle, `安全区 5`, `模板参考区`, `door-main`, and `rear-quarter`. |
| QUAL-05 | PASS | Worker stores renderer-neutral `preview_spec` on design version parameters and artifact metadata; export manifest preserves those parameters for later 3D/renderer use without API contract shape changes. |

## Deviations And Fixes

- Found during Browser UAT: updating a brief through `PATCH /generation/briefs/{id}` merged fields without recomputing derived quality warnings. This made `质量提示` stale after editing long text.
- Fix: added `refresh_generation_brief_warnings()` in core and invoked it from the API update route.
- Regression: `test_update_generation_brief_recomputes_quality_warnings` fails before the fix and passes after the fix.
- Runtime note: the existing Celery worker process completed one queued job without `preview_spec`, indicating it had not picked up the latest worker code. The worker was restarted with Windows-compatible Celery `--pool=solo`; a post-restart queued API job then succeeded with `preview_spec` and `warning_count: 1`.

## Sandbox Notes

Some commands required escalated execution on Windows:
- `uv run ...` when the sandbox could not access the uv cache under the user profile.
- `corepack pnpm validate` and nested pnpm commands when sandboxed process spawning caused EPERM-style failures.
- `corepack pnpm smoke:local` when sandboxed execution could not see the Docker daemon.

All such commands were rerun with the established approved escalated patterns and passed.

## Verdict

Phase 6 meets the planned goal: the workbench now provides itasha-specific controls, deterministic overlay metadata, template safe-zone guidance, visible quality warnings, and stored PreviewSpec data for future renderer/3D work while preserving concept-preview boundaries.
