---
phase: 33
status: issues_found
reviewed_at: "2026-06-24T00:00:00+08:00"
files_reviewed: 4
findings:
  critical: 0
  warning: 3
  info: 1
  total: 4
---

# Phase 33 Code Review

## Findings

### WR-01: Construction SVG/PDF contents are placeholders, not derived from the selected template or generated design

Severity: Warning

Files:
- `services/api/src/caragent_api/routes/jobs.py:651`
- `services/api/src/caragent_api/routes/jobs.py:673`
- `services/api/src/caragent_api/routes/jobs.py:707`

`_build_construction_package_zip()` writes `construction/layered.svg` and `construction/package.pdf`, but `_construction_svg()` hardcodes a generic 1536x768 coupe silhouette and one cyan rectangle, and `_construction_pdf()` writes only a title string. Neither function consumes `source_bytes`, `preview_spec.safe_zones`, `section_design.sections`, GR86/BRZ template assets, bleed/safety margins, or generated artwork. This means the exported construction package can pass the current test while still being another generic abstract car output, which directly conflicts with PACK-01..03.

### WR-02: Generated PDF is not a valid readable PDF

Severity: Warning

Files:
- `services/api/src/caragent_api/routes/jobs.py:707`
- `services/api/tests/test_jobs.py:885`

The PDF helper returns `%PDF-1.4` plus objects and `%%EOF`, but omits `xref`, `trailer`, and `startxref`. A parser check with bundled `pypdf` fails with `PdfReadError: startxref not found`. The test only asserts that the bytes contain `%PDF-1.4`, so an unreadable PDF is accepted as a successful export.

### WR-03: Manifest omits the construction evidence promised by PACK-01

Severity: Warning

Files:
- `services/api/src/caragent_api/routes/jobs.py:615`
- `services/core/src/caragent_core/generation/prompts.py:249`
- `services/core/src/caragent_core/generation/template_pack/mvp_generic_side_v1/toyota_gr86_brz_v1/template.json:55`

`_construction_package_manifest()` records `safe_zone_count`, a shallow `template` object, `section_design`, source ids, and warnings. It does not include actual safe-zone geometry, forbidden zones, template package version, dimensions, scale, bleed, safe margin, or export config. Those values exist in the template package, but they are not carried into the export manifest, so downstream users cannot audit whether the package matches the vehicle template or construction constraints.

### IN-01: Explicit artifact ids are not constrained to generated images

Severity: Info

Files:
- `services/api/src/caragent_api/routes/jobs.py:824`
- `services/api/src/caragent_api/routes/jobs.py:665`

When `payload.artifact_id` is supplied, `_resolve_handoff_source_artifact()` only checks workspace and version. It returns preview screenshots or export artifacts too, and `_build_construction_package_zip()` then writes those bytes as `preview/source.png`. The current Web path passes a `generated_image`, but API callers and future UI changes can create misleading packages unless the resolver enforces `ArtifactKind.GENERATED_IMAGE` and an image content type.

## Positive Notes

- `record_export()` now preserves caller-provided source artifact ids/object keys, which is the right fix for ZIP-artifact exports.
- The Web path selects a `generated_image` artifact before submitting export requests.
- Focused API/core/worker/web checks passed before this review.

## Recommended Fix Order

1. Replace the hand-written PDF with a real PDF writer or a small validated PDF builder, and add a parser-based test.
2. Generate SVG/PDF contents from `preview_spec`, `section_design.sections`, template scale/export config, and source preview evidence instead of hardcoded geometry.
3. Expand the manifest to include actual safe zones, forbidden zones, template package version, dimensions, scale, bleed, safe margin, and section ids.
4. Reject explicit source artifacts unless `kind == generated_image` and content type/magic are supported.
