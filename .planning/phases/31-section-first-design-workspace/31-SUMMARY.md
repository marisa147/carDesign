# Phase 31 Summary: Section-First Design Workspace

## Status

Complete.

## Delivered

- Workbench now loads selected template detail metadata with sections.
- `ParameterPanel` now includes a `分区工作台` section selector.
- GR86/BRZ template sections now cover door, rear quarter, front fender, hood, roof, trunk, front bumper, rear bumper, and side skirt.
- Selecting a section switches to the section's first related view, turns on targeted edit mode, and sets a normalized rectangle target from section bounds.
- The UI shows related views, flat panel real size, normalized position, and explicit fallback when a template has no sections.
- Core template tests assert the maintained GR86/BRZ section set.

## Verification

Passed:

- `apps\web\node_modules\.bin\tsc.CMD --noEmit -p apps\web\tsconfig.json`
- `cd services/core && uv run pytest -q tests/test_template_pack.py`
- `cd services/core && uv run ruff check src tests/test_template_pack.py`
- `cd services/core && uv run python -m caragent_core.generation.validate_template_pack`

Known local test blocker remains:

- Frontend Vitest/jsdom startup fails before collecting tests with `ERR_REQUIRE_ESM` from the css-color/css-calc dependency chain.

## Requirements Closed

- SECT-01: Users can choose wrap scope by practical vehicle sections.
- SECT-02: Selecting a section exposes related views, normalized position, and flat panel real dimensions when available.
- SECT-03: Selecting a section creates a targeted edit scope from template section geometry.

## Next

Phase 32 GPT Sectioned Generation Pipeline.
