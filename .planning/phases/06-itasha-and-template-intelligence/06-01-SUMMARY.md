---
phase: 06-itasha-and-template-intelligence
plan: "01"
subsystem: core-generation-preview-spec
tags: [core, generation, template, preview-spec, warnings]

requires:
  - phase: "06-CONTEXT"
    provides: Phase 6 itasha/template intelligence scope
  - phase: "06-UI-SPEC"
    provides: safe-zone, warning, and PreviewSpec UI contract
provides:
  - typed itasha brief controls
  - deterministic template safe-zone catalog
  - concise quality warnings
  - renderer-neutral PreviewSpec prompt payload
affects: [phase-06-02-worker-preview-spec, phase-06-03-api-contracts]

tech-stack:
  patterns:
    - Pydantic brief payload remains the core generation contract source
    - template safe zones are normalized core data, not browser-only state
    - prompt payload carries PreviewSpec for worker/API/frontend consumers

key-files:
  modified:
    - services/core/src/caragent_core/generation/briefs.py
    - services/core/src/caragent_core/generation/prompts.py
    - services/core/src/caragent_core/generation/templates.py
    - services/core/tests/test_generation_briefs.py
    - services/core/tests/test_prompt_plans.py

key-decisions:
  - "Phase 6 controls default to empty strings/lists to preserve existing brief creation behavior."
  - "The first safe-zone catalog is scoped to `generic-side-coupe` / `side`."
  - "PreviewSpec stores normalized descriptors, asset ids, and warning messages only; it does not store filesystem paths or provider secrets."
  - "Long text receives a concise readability warning before worker/provider execution."

patterns-established:
  - "Core tests specify default compatibility before adding new brief fields."
  - "PreviewSpec assembly is deterministic and derives text/logo overlay layers from the structured brief."

requirements-completed:
  - QUAL-01
  - QUAL-03
  - QUAL-04
  - QUAL-05

duration: 20 min
completed: 2026-06-18
---

# Phase 6 Plan 01: Core Itasha Controls And PreviewSpec Summary

**The core generation contract now produces Phase 6 itasha controls, safe zones, warnings, and PreviewSpec data.**

## Accomplishments

- Added failing core tests for Phase 6 brief defaults, itasha control preservation, safe-zone data, JSON round-tripping, warning copy, and PreviewSpec payload shape.
- Extended `GenerationBriefPayload` and `create_generation_brief()` with character focus, supporting graphics, racing/JDM cues, typography intent, color harmony, and overlay logo asset ids.
- Added deterministic safe-zone data for the supported side-view coupe template, including body, window, and risky wheel-arch zones.
- Added concise quality warnings for long text strings that may be hard to read.
- Added `preview_spec` to prompt payloads with canvas, template, safe zones, overlay layers, warning descriptors, and source asset ids.

## Verification

- RED: `uv run pytest -q tests/test_generation_briefs.py tests/test_prompt_plans.py` in `services/core` failed as expected because Phase 6 fields, safe zones, and PreviewSpec were absent.
- GREEN: `uv run pytest -q tests/test_generation_briefs.py tests/test_prompt_plans.py` in `services/core` passed, 8 tests.
- `uv run ruff check .` in `services/core` passed.
- `uv run mypy src` in `services/core` passed after rerunning with escalation because the first run hit a Windows `uv` cache permission error.

## Deviations from Plan

- No code-scope deviation.
- The first `uv run mypy src` attempt failed before type checking due to local cache permissions, so the same verification command was rerun with approved escalation.

## Next Plan Readiness

Ready for `06-02`: worker/local provider PreviewSpec persistence, deterministic overlays, and rights enforcement.
