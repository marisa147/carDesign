---
phase: 17
plan: 1
status: completed
requirements:
  - V3-CATALOG-02
  - V3-CATALOG-05
---

# Summary 17.01: Template Catalog API Schemas And Endpoints

## Completed

- Added typed API schemas for catalog list items, detail responses, and safe-zone summaries.
- Added `GET /templates` with optional `view` and `catalog_eligible` filters.
- Added `GET /templates/{template_id}` with canonical id and legacy alias resolution.
- Returned stable 404 messages for unknown templates without leaking internal paths.
- Covered catalog list, detail, filtering, alias, and OpenAPI export shape in tests.

## Evidence

- `services/api/src/caragent_api/schemas.py`
- `services/api/src/caragent_api/routes/templates.py`
- `services/api/src/caragent_api/main.py`
- `services/api/tests/test_templates.py`
- `services/api/tests/test_openapi_export.py`
