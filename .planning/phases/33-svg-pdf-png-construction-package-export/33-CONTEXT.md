# Phase 33 Context: SVG/PDF/PNG Construction Package Export

## Goal

Produce a quasi-construction export package from the selected design version without claiming print-shop certification.

## Requirements

- PACK-01: Export a package containing layered SVG, PDF, PNG/source preview, manifest, template/version trace, scale/safety evidence, and warning evidence.
- PACK-02: SVG output uses stable layer ids: base, body, window, wheel, handle, panel_lines, and artwork_sections.
- PACK-03: PDF and PNG/source outputs preserve visible review evidence and concept-vs-construction warnings.

## Constraints

- Keep the package concept/quasi-construction only; do not add PSD/AI or installer-certified claims.
- Reuse the existing version-scoped export route and immutable artifact/export ledger.
- Store package bytes in configured object storage and keep the API manifest traceable.
