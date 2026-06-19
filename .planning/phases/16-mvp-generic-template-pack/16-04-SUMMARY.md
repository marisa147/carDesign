---
phase: 16
plan: 4
status: completed
requirements:
  - V3-PACK-05
  - V3-PACK-06
---

# Summary 16.04: Template-Aware Brief And Prompt Coverage

## Completed

- `create_generation_brief()` now preserves selected MVP template ids instead of collapsing all requests to the legacy id.
- Prompt plans and PreviewSpec payloads retain selected template id, label, view, source metadata, readiness, warnings, and safe zones.
- Core tests cover all five MVP ids and the legacy `generic-side-coupe` alias.
- API and worker tests were updated to expect canonical coupe output for unsupported/default requests.

## Evidence

- `services/core/tests/test_generation_briefs.py`
- `services/core/tests/test_prompt_plans.py`
- `services/api/tests/test_generation.py`
- `services/worker/tests/test_generation_tasks.py`
