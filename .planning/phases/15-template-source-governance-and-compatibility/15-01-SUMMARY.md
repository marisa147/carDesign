---
phase: 15
plan: 01
status: complete
subsystem: core-generation
tags:
  - template-governance
  - source-policy
key_files:
  created: []
  modified:
    - services/core/src/caragent_core/generation/templates.py
    - services/core/src/caragent_core/generation/__init__.py
    - services/core/tests/test_generation_briefs.py
metrics:
  tests_added: 3
  requirements_addressed:
    - V3-TEMPLATE-01
    - V3-TEMPLATE-05
---

# Plan 15-01 Summary

## What Changed

- Added canonical source policy definitions for all source types named by `MVP_FINAL.md`.
- Added typed source metadata, readiness report, and audit item models.
- Exported the governance helpers through `caragent_core.generation`.
- Added focused coverage for policy-table inspection and readiness metadata.

## Verification

- `uv run pytest tests/test_generation_briefs.py tests/test_prompt_plans.py -q` passed.
- `uv run ruff check .` passed in `services/core`.

## Deviations

None.

## Self-Check

PASSED.
