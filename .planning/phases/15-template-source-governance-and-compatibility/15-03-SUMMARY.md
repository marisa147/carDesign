---
phase: 15
plan: 03
status: complete
subsystem: core-generation
tags:
  - source-blocking
  - licensing
key_files:
  created: []
  modified:
    - services/core/src/caragent_core/generation/templates.py
    - services/core/tests/test_generation_briefs.py
metrics:
  tests_added: 2
  requirements_addressed:
    - V3-TEMPLATE-03
---

# Plan 15-03 Summary

## What Changed

- Registration rejects `third_party_reference_only` and `web_crawled_image` source types.
- Registration rejects licensed records without evidence.
- Registration rejects blocked, missing, or reference-only license states.
- Tests assert rejected records do not appear in registry audit output.

## Verification

- `uv run pytest tests/test_generation_briefs.py -q` passed as part of focused core checks.

## Deviations

None.

## Self-Check

PASSED.
