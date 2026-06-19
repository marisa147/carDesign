---
phase: 17
plan: 5
status: completed
requirements:
  - V3-CATALOG-01
  - V3-CATALOG-03
  - V3-CATALOG-05
---

# Summary 17.05: Workbench Template Selector UX

## Completed

- Added a compact template catalog selector to the parameter panel.
- Rendered thumbnails, labels, view badges, source type, license state, and readiness state.
- Added client-side filtering for the catalog selector.
- Disabled non-catalog-ready options and showed blocking reasons or warnings.
- Persisted template selection through `PATCH /generation/briefs/{brief_id}` when a brief exists.
- Added Workbench regression coverage for browsing, selecting, and request payloads.

## Evidence

- `apps/web/src/components/workbench/parameter-panel.tsx`
- `apps/web/src/components/workbench/workbench-app.tsx`
- `apps/web/src/app/page.test.tsx`
