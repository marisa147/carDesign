# Phase 32 Summary: GPT Sectioned Generation Pipeline

## Status

Complete.

## Delivered

- `build_prompt_plan()` now creates a `section_design_plan` for the selected template.
- The plan includes overall direction, template id/label/view, and one section prompt per template section.
- GR86/BRZ section prompts carry section id, label, related views, normalized bounds, real size, and section-scoped prompt instructions.
- Worker metadata now records `section_design` summary across model run parameters, artifact metadata, version parameters, job operations, and final event metadata.
- Targeted section regeneration metadata can mark `regeneration.target_section_id` when the edit target matches a planned section id.
- Focused tests cover GR86/BRZ section prompt planning and durable worker section trace persistence.

## Verification

Passed:

- `cd services/core && uv run pytest -q tests/test_prompt_plans.py`
- `cd services/core && uv run ruff check src tests/test_prompt_plans.py`
- `cd services/core && uv run mypy src`
- `cd services/worker && uv run pytest -q tests/test_generation_tasks.py -k section_design`
- `cd services/worker && uv run ruff check src tests/test_generation_tasks.py`
- `cd services/worker && uv run mypy src`

## Requirements Closed

- GPTD-01: GPT/provider prompt planning now includes an overall design direction from brief and template context.
- GPTD-02: The design direction is split into section-level prompts tied to GR86/BRZ template sections.
- GPTD-03: Section regeneration target metadata is preserved when targeted edit scope matches a section id.
- GPTD-04: Prompt, model, section ids, template id, provider, and model-run trace are durable across worker records.

## Next

Phase 33 SVG/PDF/PNG Construction Package Export.
