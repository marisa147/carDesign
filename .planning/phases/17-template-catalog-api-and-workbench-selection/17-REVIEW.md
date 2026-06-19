---
phase: 17
status: clean
depth: standard
files_reviewed: 16
findings:
  critical: 0
  warning: 0
  info: 0
  total: 0
---

# Phase 17 Code Review

## Scope

- `services/api/src/caragent_api/schemas.py`
- `services/api/src/caragent_api/routes/templates.py`
- `services/api/src/caragent_api/routes/generation.py`
- `services/api/src/caragent_api/main.py`
- `services/api/tests/test_templates.py`
- `services/api/tests/test_generation.py`
- `services/api/tests/test_openapi_export.py`
- `packages/contracts/openapi/openapi.json`
- `packages/contracts/src/generated/client.ts`
- `apps/web/src/lib/api/templates.ts`
- `apps/web/src/lib/api/templates.test.ts`
- `apps/web/src/lib/workbench/query-keys.ts`
- `apps/web/src/lib/workbench/store.ts`
- `apps/web/src/components/workbench/parameter-panel.tsx`
- `apps/web/src/components/workbench/workbench-app.tsx`
- `apps/web/src/app/page.test.tsx`

## Findings

No blocking issues found after review.

## Review Notes

- Template catalog endpoints read from the core registry and package resources instead of duplicating template metadata in the API layer.
- Legacy aliases such as `generic-side-coupe` resolve through the same catalog/detail path as canonical ids.
- Workbench template selection is stored through the existing brief contract rather than as disconnected UI-only state.
- Job metadata now carries a compact selected-template trace for generation and iteration submissions.
- Export manifests include template trace only when selected version PreviewSpec metadata contains template context, preserving compatibility with older payloads.

## Residual Risk

Phase 17 intentionally makes templates selectable but does not yet prove generation, targeted editing, or 3D fallback alignment across every template. That remains Phase 18.
