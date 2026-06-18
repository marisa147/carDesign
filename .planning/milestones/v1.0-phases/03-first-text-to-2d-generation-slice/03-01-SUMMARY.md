---
phase: 03-first-text-to-2d-generation-slice
plan: "01"
subsystem: core-generation-briefs
status: complete
completed: 2026-06-17
requirements: ["GEN-01", "GEN-02", "GEN-03"]
key-files:
  - "services/core/pyproject.toml"
  - "services/core/src/caragent_core/generation/__init__.py"
  - "services/core/src/caragent_core/generation/briefs.py"
  - "services/core/src/caragent_core/generation/templates.py"
  - "services/core/tests/test_generation_briefs.py"
---

# Plan 03-01 Summary: Typed Briefs And Template Catalog

## What Changed

- Added `caragent_core.generation` as the shared Phase 3 generation package.
- Added a typed `GenerationBriefPayload` Pydantic model and deterministic `create_generation_brief` helper.
- Added a minimal supported vehicle-template resolver with one explicit template/view: `generic-side-coupe` / `side`.
- Added tests proving natural-language input is preserved, optional fields default safely, unsupported template/view values are normalized with warnings, empty input is rejected, and payloads round-trip as JSON-safe data.
- Added `pydantic>=2.13,<3` to `services/core` and refreshed the core lock data through `uv run`.

## Verification

| Command | Result |
|---------|--------|
| `uv run pytest -q tests/test_generation_briefs.py` | Passed: 5 tests. |
| `uv run ruff check .` | Passed. |
| `uv --no-cache run mypy src` | Passed with escalation: no issues in 15 source files. |
| `uv run pytest -q tests/test_generation_briefs.py tests/test_assets.py tests/test_jobs.py` | Passed: 13 tests. |
| `uv run pytest -q` | Passed: 26 tests. |

## Notes

- The first RED run correctly failed on missing `caragent_core.generation`.
- A parallel uv/mypy attempt hit a Windows `.venv` lock/cache permission issue; rerunning mypy as a single escalated command passed.
- This plan does not call providers, enqueue workers, or touch API/web code. Those remain later Phase 3 plans.

## Self-Check

PASSED. The plan's must-have truths are covered:

- Natural-language generation input becomes typed, reusable structured brief data.
- One supported template/view is explicit and test-covered.
- Unsupported template/view requests produce warnings instead of silent broad support.
