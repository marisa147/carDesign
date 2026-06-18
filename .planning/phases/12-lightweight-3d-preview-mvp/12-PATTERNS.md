---
phase: 12
slug: lightweight-3d-preview-mvp
status: complete
created: 2026-06-18
---

# Phase 12 Pattern Map

This file points execution agents at local code patterns to reuse during Phase 12. It is not a replacement for reading the files named in each plan.

## Core Contracts And Ledger

| New Need | Existing Pattern | Files To Read |
|----------|------------------|---------------|
| Preview3DSpec schema | Phase 10 `EditIntent` and Phase 11 `ReferenceUsageSnapshot` Pydantic helpers | `services/core/src/caragent_core/editing.py`, `services/core/src/caragent_core/references.py` |
| Artifact kind and metadata | Existing artifact enum and `jobs.create_artifact` validation | `services/core/src/caragent_core/enums.py`, `services/core/src/caragent_core/services/jobs.py` |
| Version-linked metadata | PreviewSpec stored in `DesignVersion.parameters` and artifact metadata | `services/worker/src/caragent_worker/tasks/jobs.py`, `services/api/src/caragent_api/routes/jobs.py` |
| Template compatibility | Current `resolve_vehicle_template` and `supported_safe_zones` | `services/core/src/caragent_core/generation/templates.py` |

## API And Contracts

| New Need | Existing Pattern | Files To Read |
|----------|------------------|---------------|
| Feature flag gate | V2 targeted/reference API guards | `services/api/src/caragent_api/config.py`, `services/api/src/caragent_api/routes/generation.py` |
| Screenshot persistence route | Asset upload writes bytes to object storage and artifact rows link to versions | `services/api/src/caragent_api/routes/assets.py`, `services/core/src/caragent_core/storage.py`, `services/core/src/caragent_core/services/jobs.py` |
| Generated contracts | Prior phase schema regeneration/check flow | `services/api/src/caragent_api/schemas.py`, `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/client.ts` |

## Web Workbench

| New Need | Existing Pattern | Files To Read |
|----------|------------------|---------------|
| Selected version/artifact | `WorkbenchApp` derives selected version and artifact then passes to panels | `apps/web/src/components/workbench/workbench-app.tsx` |
| Preview state | Zustand store keeps preview zoom/mode and resets stale target state | `apps/web/src/lib/workbench/store.ts` |
| 2D PreviewSpec parsing | `PreviewPanel` reads `parameters.preview_spec` and renders safe zones/overlays | `apps/web/src/components/workbench/preview-panel.tsx` |
| API client | Thin generated-client wrappers | `apps/web/src/lib/api/iteration.ts`, `apps/web/src/lib/api/generation.ts` |
| Page tests | Workbench fixtures cover versions, artifacts, selected version, export, references | `apps/web/src/app/page.test.tsx` |

## Planned File Map

| Plan | Main Write Set |
|------|----------------|
| 12-01 | Core Preview3DSpec helpers, artifact kind, API schemas/contracts, core/API tests |
| 12-02 | Shell registry/fixture helpers in core/web, compatibility tests |
| 12-03 | Three.js dependency, 3D panel/viewer scaffold, store mode/camera state, web tests |
| 12-04 | Material/texture mapping helpers, safe-zone/decal projection, viewer updates, web tests |
| 12-05 | Screenshot API route/client, artifact persistence, screenshot UI, API/web tests/contracts |
| 12-06 | Warning metadata, non-production labels, fallback/safe-zone overlays, web/API tests |
| 12-07 | Browser visual/performance/accessibility pass and cleanup |
| 12-08 | Docs, UAT evidence, validation report, ROADMAP/REQUIREMENTS/STATE updates |

## Test Patterns

| Area | Existing Tests |
|------|----------------|
| Core schema/ledger | `services/core/tests/test_models.py`, `test_generation_jobs.py` |
| API routes/contracts | `services/api/tests/test_jobs.py`, `test_generation.py` |
| Web workbench/store | `apps/web/src/app/page.test.tsx`, `apps/web/src/lib/workbench/store.test.ts` |
| API wrappers | `apps/web/src/lib/api/iteration.test.ts`, `apps/web/src/lib/api/generation.test.ts` |

## Anti-Patterns

- Do not make 3D preview imply production-ready UV accuracy.
- Do not store screenshot bytes or generated image bytes inside JSON metadata.
- Do not break 2D preview, generation, targeted edits, references, feedback, or export when 3D is disabled or incompatible.
- Do not load Three.js on the server.
- Do not introduce a broad model library or shell upload workflow in Phase 12.
- Do not depend on hosted provider calls for 3D preview validation.

## PATTERN MAPPING COMPLETE
