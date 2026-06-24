# Phase 25 Summary: Parser Boundary And Template Compositor

## Completed

- Added strict core `BriefDraft`, `BriefParserInput`, `BriefParser`, `DeterministicBriefParser`, `StructuredBriefParser`, and `select_brief_parser()` boundaries.
- Refactored `create_generation_brief()` through `BriefDraft` and added `create_generation_brief_from_draft()` so parser output remains a draft-only contract before persistence.
- Added core `TemplateCompositor` protocol with `TemplateCompositionRequest` and `TemplateCompositionResult` dataclasses, keeping Pillow out of core.
- Implemented worker `PillowTemplateCompositor` that loads template package `base`, `body_mask`, `window_mask`, `wheel_mask`, `handle_mask`, and `panel_lines` assets.
- Replaced the local deterministic provider's abstract hand-drawn car renderer with template-package composition.
- Routed deterministic recomposition through the same local provider render path, preserving existing recomposition behavior while changing the underlying renderer.
- Added compositor metadata to local provider outputs so generated artifacts/model runs can trace the template compositor and loaded asset slots.

## Tests Added

- Core tests for deterministic parser draft output, feature-flagged LLM parser selection fallback, and strict structured parser rejection of extra fields.
- Worker pixel test proving decorations do not alter protected `window_mask`, `wheel_mask`, or `handle_mask` regions compared with structural base plus panel lines.
- Worker provider test proving local deterministic generation records template compositor metadata.

## Files Touched

- `services/core/src/caragent_core/generation/briefs.py`
- `services/core/src/caragent_core/generation/compositor.py`
- `services/core/src/caragent_core/generation/__init__.py`
- `services/core/tests/test_generation_briefs.py`
- `services/worker/src/caragent_worker/template_compositor.py`
- `services/worker/src/caragent_worker/providers/local.py`
- `services/worker/tests/test_image_providers.py`

## Notes

Phase 25 intentionally does not add a live LLM provider. The structured parser hook validates strict `BriefDraft` output and stays behind `select_brief_parser(llm_enabled=...)`, leaving durable DB writes in the existing API/service layer.