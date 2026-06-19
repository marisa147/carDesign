---
phase: 17
plan: 3
status: completed
requirements:
  - V3-CATALOG-04
  - V3-CATALOG-05
---

# Summary 17.03: Brief Template Update And Persistence

## Completed

- Added `vehicle_template_id` and `view` to `GenerationBriefUpdateRequest`.
- Recomputed brief payloads through `create_generation_brief()` when template id or view changes.
- Preserved fallback warnings for unsupported template/view selections.
- Added selected template metadata to generation job and iteration job metadata.
- Added API tests for template-changing brief patches and job metadata.

## Evidence

- `services/api/src/caragent_api/schemas.py`
- `services/api/src/caragent_api/routes/generation.py`
- `services/api/tests/test_generation.py`
