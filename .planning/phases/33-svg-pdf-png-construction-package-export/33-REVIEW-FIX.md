---
phase: 33
status: all_fixed
fixed_at: "2026-06-24T00:00:00+08:00"
findings_in_scope: 4
fixed: 4
skipped: 0
iteration: 1
---

# Phase 33 Review Fix Report

## Fixed Findings

### WR-01: Construction SVG/PDF placeholders

Fixed.

- `construction/layered.svg` now renders section rectangles from `construction_evidence.sections`, safe zones from `construction_evidence.safe_zones`, forbidden zones from `construction_evidence.forbidden_zones`, and carries `data-source-artifact-id` for the packaged source image.
- `construction/package.pdf` now includes template, source artifact, section ids, bleed, safe margin, and warning text.
- Package generation now validates the source is a generated PNG concept image before writing the package.

### WR-02: Invalid PDF bytes

Fixed.

- Replaced the previous header-only PDF bytes with a minimal valid PDF builder that writes object offsets, xref table, trailer, and startxref.
- Added regression assertions that `startxref` points at the xref table.
- Verified with bundled `pypdf` that the generated PDF parses as one page.

### WR-03: Missing construction evidence in manifest

Fixed.

- Manifest now includes `construction_evidence` with template id/label/view/version, canvas, dimensions, scale, export config, safe zones, forbidden zones, section ids, and section payloads.
- Evidence is resolved from the selected template id/view via `resolve_vehicle_template()` and falls back to version `preview_spec` where appropriate.

### IN-01: Explicit artifact ids not constrained to generated images

Fixed.

- `_resolve_handoff_source_artifact()` now rejects explicit source artifacts unless `kind == generated_image`.
- Construction package generation also requires PNG content type and PNG magic bytes.
- Added regression coverage for trying to export a construction package from a `preview_3d_screenshot` artifact.

## Additional Fix

- Restored `ArtifactResponse.content_url` in the API schema so `_artifact_response()` output is not dropped by Pydantic serialization.

## Verification

Passed:

- `cd services/api && uv run pytest -q tests/test_jobs.py -k construction_package`
- `cd services/api && uv run pytest -q tests/test_jobs.py -k "construction_package or enhanced_handoff_export or concept_exports_can_be_created"`
- `cd services/api && uv run pytest -q tests/test_jobs.py`
- `cd services/api && uv run pytest -q tests/test_openapi_export.py`
- `cd services/api && uv run ruff check src tests/test_jobs.py`
- `cd services/api && uv run mypy src`
- `packages\contracts\node_modules\.bin\tsc.CMD --project packages\contracts\tsconfig.json --noEmit`
- `apps\web\node_modules\.bin\tsc.CMD --noEmit -p apps\web\tsconfig.json`
- Bundled `pypdf` parsed generated construction PDF as 1 page.
