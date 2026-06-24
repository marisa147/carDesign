# Phase 25 Context: Parser Boundary And Template Compositor

## Goal

Make the system more Agent-like without letting model output own durable state, and make local concept images come from the governed template package instead of an abstract hand-drawn car.

## Requirements

- AGNT-01: Natural-language brief parsing has a strict `BriefParser` boundary with deterministic fallback and no direct database writes by model output.
- AGNT-02: Local concept generation uses template package base and masks for body, window, wheel, handle, and panel lines.
- AGNT-03: Template compositor output prevents decorative layers from covering windows, wheels, and handles unless an explicit future production workflow allows it.

## Likely Files

- `services/core/src/caragent_core/generation/briefs.py`
- `services/core/src/caragent_core/generation/compositor.py`
- `services/core/src/caragent_core/generation/__init__.py`
- `services/core/tests/test_generation_briefs.py`
- `services/worker/src/caragent_worker/template_compositor.py`
- `services/worker/src/caragent_worker/providers/local.py`
- `services/worker/tests/test_image_providers.py`

## Non-Goals

- Do not add a live LLM call in this phase.
- Do not let parser output write directly to DB.
- Do not claim print-ready artwork, verified UV alignment, or production-safe masking.