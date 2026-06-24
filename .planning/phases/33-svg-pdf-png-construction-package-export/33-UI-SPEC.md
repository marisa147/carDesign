# Phase 33 UI Spec: Construction Package Export

## Surface

Workbench export panel.

## Behavior

- Add `施工包` as a first-class export format alongside PNG/JPG/enhanced handoff ZIP.
- When selected, show the disclaimer `SVG/PDF/PNG 准施工包，仍需人工生产校验`.
- Reuse the package readiness rows so users see template/source/reference warnings before export.
- Submit the existing version export request with `format: construction_package_zip`.
- Label successful history rows as `施工包`.

## Copy Boundary

The UI must not imply print-shop certification, PSD/AI availability, final installer approval, or production-ready color/bleed guarantees.
