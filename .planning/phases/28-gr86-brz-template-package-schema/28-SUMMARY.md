---
phase: 28
plan: 28-01
subsystem: template-registry
tags:
  - gr86-brz
  - template-schema
  - vehicle-package
key-files:
  - services/core/src/caragent_core/generation/templates.py
  - services/core/src/caragent_core/generation/validate_template_pack.py
  - services/core/src/caragent_core/generation/template_pack/mvp_generic_side_v1/toyota_gr86_brz_v1/
  - services/api/src/caragent_api/routes/templates.py
  - services/api/src/caragent_api/schemas.py
  - packages/contracts/openapi/openapi.json
  - packages/contracts/src/generated/client.ts
metrics:
  requirements: 4
  templates_validated: 6
---

# Phase 28 Summary: GR86/BRZ Template Package Schema

## Completed

- Extended `VehicleTemplateRecord` with additive deep-template fields: `supported_views`, `view_assets`, `sections`, `forbidden_zones`, `dimensions`, `scale`, `export_config`, and `authorization`.
- Added `toyota_gr86_brz_v1` as the first maintained deep vehicle template package.
- Generated distinct internal schematic PNG assets for `side`, `front`, `rear`, and `top` views plus existing compositor asset slots.
- Added GR86/BRZ sections, safe zones, forbidden zones, real-unit dimensions, scale metadata, export configuration, and authorization metadata.
- Updated template catalog filtering so `view=front|rear|top` returns templates whose `supported_views` include that view.
- Exposed deep construction metadata through template detail API responses and generated contracts.
- Updated validator to keep MVP side-only checks while adding deep vehicle validation for required views and construction metadata.

## Requirements

| Requirement | Status | Evidence |
|-------------|--------|----------|
| TPLG-01 | Complete | `toyota_gr86_brz_v1` is registered and returned by `/templates`. |
| TPLG-02 | Complete | Package exposes `supported_views == [side, front, rear, top]` and has four view PNGs. |
| TPLG-03 | Complete | Detail response includes sections, safe zones, forbidden zones, dimensions, scale, export config, and authorization. |
| TPLG-04 | Complete | Validator checks four views and construction metadata; focused validator/tests pass. |

## Verification

- Passed: `cd services/core && uv run pytest -q tests/test_template_pack.py`
- Passed: `cd services/api && uv run pytest -q tests/test_templates.py`
- Passed: `cd services/core && uv run python -m caragent_core.generation.validate_template_pack`
- Passed: `cd services/core && uv run ruff check src tests/test_template_pack.py`
- Passed: `cd services/api && uv run ruff check src tests/test_templates.py`
- Passed: `cd services/core && uv run mypy src`
- Passed: `cd services/api && uv run mypy src`
- Passed: `cd services/api && uv run pytest -q tests/test_openapi_export.py`
- Passed: `cd packages/contracts && node_modules\.bin\tsc.CMD --project tsconfig.json --noEmit`
- Passed: `apps\web\node_modules\.bin\tsc.CMD --noEmit -p apps\web\tsconfig.json`

## Tooling Notes

- `node scripts/check-contracts.mjs` and `orval` generation are blocked by the local Node/Corepack/orval toolchain (`ERR_VM_DYNAMIC_IMPORT_CALLBACK_MISSING` and Node 20 `styleText` incompatibility). OpenAPI was exported successfully and generated TypeScript response types were manually aligned with the new schema.

## Deferred

- Template package import/management UI remains Phase 29.
- Section-first workspace behavior remains Phase 31.
- SVG/PDF/PNG construction package export remains Phase 33.
