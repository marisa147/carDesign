---
phase: 17
plan: 4
status: completed
requirements:
  - V3-CATALOG-01
  - V3-CATALOG-02
  - V3-CATALOG-04
---

# Summary 17.04: Frontend Catalog API Client And State

## Completed

- Regenerated OpenAPI and TypeScript contracts after the API catalog changes.
- Added a typed frontend template API wrapper for list/detail and thumbnail URL helpers.
- Added a template query key and persisted selected template id in Workbench state.
- Loaded catalog-ready templates during Workbench resume and cached them in TanStack Query.
- Included selected template id/view in new chat brief creation.

## Evidence

- `packages/contracts/openapi/openapi.json`
- `packages/contracts/src/generated/client.ts`
- `apps/web/src/lib/api/templates.ts`
- `apps/web/src/lib/api/templates.test.ts`
- `apps/web/src/lib/workbench/query-keys.ts`
- `apps/web/src/lib/workbench/store.ts`
- `apps/web/src/components/workbench/workbench-app.tsx`
