# Phase 25 Verification

## TDD Evidence

The Phase 25 tests were written and run before implementation. Initial RED failures were:

- `cd services/core && uv run pytest -q tests/test_generation_briefs.py` failed because `BriefDraft` was not exported.
- `cd services/worker && uv run pytest -q tests/test_image_providers.py` failed because `TemplateCompositionRequest` was not exported.

## Automated Verification

Passed:

- `cd services/core && uv run pytest -q tests/test_generation_briefs.py`
- `cd services/worker && uv run pytest -q tests/test_image_providers.py`
- `cd services/core && uv run ruff check src tests/test_generation_briefs.py --fix`
- `cd services/worker && uv run ruff check src tests/test_image_providers.py --fix`
- `cd services/core && uv run mypy src`
- `cd services/worker && uv run mypy src`
- `cd services/core && uv run pytest -q`
- `cd services/worker && uv run pytest -q`
- `corepack pnpm validate`

## Requirement Evidence

| Requirement | Evidence |
|-------------|----------|
| AGNT-01 | `BriefDraft`, `BriefParserInput`, `BriefParser`, deterministic fallback, strict structured parser, and feature-flag selection are covered by core tests; parser output does not write DB. |
| AGNT-02 | `PillowTemplateCompositor` loads package `base`, `body_mask`, `window_mask`, `wheel_mask`, `handle_mask`, and `panel_lines`; local provider metadata records those slots. |
| AGNT-03 | Worker pixel test compares output against base plus panel lines under protected masks and asserts no decoration changes protected window, wheel, or handle pixels. |

## Notes

`corepack pnpm validate` passed. The run still prints known non-fatal test-environment warnings: jsdom canvas `getContext()` is unavailable without the optional canvas package, and API pytest emits intermittent aiosqlite thread warnings after event-loop shutdown.

## Manual UAT

No browser UAT was run in Phase 25. The change is backend/core rendering behavior and is covered by deterministic pixel and provider regression tests.