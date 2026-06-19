# Plan 18.02 Summary: Template-Aligned PreviewSpec Overlays And Warnings

## Result

Completed. Core prompt planning now chooses text/logo overlay zones from the selected template's safe zones instead of assuming fixed ids blindly.

## Evidence

- `test_prompt_plan_uses_existing_overlay_zones_for_every_mvp_template` checks all MVP templates.
- Workbench PreviewSpec summary now shows template label, id, view, counts, and warning messages from the selected version.
- Van PreviewSpec UI regression verifies template warnings, safe-zone labels, and overlay text.

## Files

- `services/core/src/caragent_core/generation/prompts.py`
- `services/core/tests/test_prompt_plans.py`
- `apps/web/src/components/workbench/preview-panel.tsx`
- `apps/web/src/app/page.test.tsx`

