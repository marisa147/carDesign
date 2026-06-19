---
phase: 13
slug: enhanced-concept-handoff-package-mvp
status: complete
created: 2026-06-19
---

# Phase 13 Pattern Map

This file points execution agents at local code patterns to reuse during Phase 13. It is not a replacement for reading the files named in each plan.

## Core Package And Ledger

| New Need | Existing Pattern | Files To Read |
|----------|------------------|---------------|
| Handoff manifest Pydantic helpers | Phase 10 `EditIntent`, Phase 11 `ReferenceUsageSnapshot`, Phase 12 `Preview3DSpec` | `services/core/src/caragent_core/editing.py`, `services/core/src/caragent_core/references.py`, `services/core/src/caragent_core/preview3d.py` |
| Export artifact rows | `jobs.create_artifact` plus existing `ArtifactKind.EXPORT` | `services/core/src/caragent_core/enums.py`, `services/core/src/caragent_core/services/jobs.py` |
| Export record manifest merge | `jobs.record_export` concept export manifest and reference trace merge | `services/core/src/caragent_core/services/jobs.py`, `services/core/tests/test_jobs.py` |
| Storage reads | `InMemoryObjectStorage` and `FileObjectStorage.put_object` | `services/core/src/caragent_core/storage.py`, `services/core/tests/test_assets.py` |

## API And Contracts

| New Need | Existing Pattern | Files To Read |
|----------|------------------|---------------|
| Feature flag gate | 3D screenshot route checks `v2_lightweight_3d_preview_enabled` | `services/api/src/caragent_api/routes/jobs.py`, `services/api/src/caragent_api/config.py` |
| Version-scoped export route | Existing `POST /workspaces/{workspace_id}/versions/{version_id}/exports` | `services/api/src/caragent_api/routes/jobs.py`, `services/api/tests/test_jobs.py` |
| Generated contracts | Prior OpenAPI/Orval workflow | `services/api/src/caragent_api/schemas.py`, `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/client.ts` |
| Object storage fixture | API tests set `app.state.object_storage = InMemoryObjectStorage()` for uploads | `services/api/tests/test_assets.py`, `services/api/tests/test_jobs.py` |

## Web Workbench

| New Need | Existing Pattern | Files To Read |
|----------|------------------|---------------|
| Selected version/artifact export | `WorkbenchApp.submitSelectedExport` | `apps/web/src/components/workbench/workbench-app.tsx` |
| Export panel UI | Current `ExportPanel` mode, manifest preview, and history rows | `apps/web/src/components/workbench/export-panel.tsx` |
| API wrapper | `createConceptExport` thin wrapper around generated route URL | `apps/web/src/lib/api/iteration.ts`, `apps/web/src/lib/api/iteration.test.ts` |
| Feature flag | `publicEnv.v2EnhancedHandoffPackageEnabled` | `apps/web/src/lib/config/public-env.ts`, `apps/web/src/lib/config/public-env.test.ts` |
| Page tests | Export fixture, reference fixture, 3D screenshot fixture, selected version workflow | `apps/web/src/app/page.test.tsx` |

## Planned File Map

| Plan | Main Write Set |
|------|----------------|
| 13-01 | `handoff.py`, storage read API, package schema tests, enum/format constants |
| 13-02 | warning/safe-zone/report rendering helpers and tests |
| 13-03 | ZIP package builder, storage reads/writes, package artifact creation, tests |
| 13-04 | API route feature gate, export ledger integration, OpenAPI/contracts, API tests |
| 13-05 | web API wrapper/export panel/workbench wiring/page tests |
| 13-06 | rights/source guardrails in core/API/web and failure-state tests |
| 13-07 | docs, smoke, contracts, aggregate validation, browser UAT evidence |

## Test Patterns

| Area | Existing Tests |
|------|----------------|
| Core schema/ledger | `services/core/tests/test_models.py`, `services/core/tests/test_jobs.py`, `services/core/tests/test_generation_jobs.py` |
| API routes/contracts | `services/api/tests/test_jobs.py`, `services/api/tests/test_config.py`, `services/api/tests/test_openapi_export.py` |
| Web workbench | `apps/web/src/app/page.test.tsx`, `apps/web/src/lib/api/iteration.test.ts`, `apps/web/src/lib/api/generation.test.ts` |
| Validation scripts | `corepack pnpm contracts:check`, `corepack pnpm validate`, `corepack pnpm smoke:worker -- --dry-run` |

## Anti-Patterns

- Do not create production handoff claims.
- Do not store binary bytes, base64 images, local paths, API keys, secrets, or raw provider credentials in manifest JSON.
- Do not overwrite prior export rows or package artifacts.
- Do not make ZIP export depend on hosted provider calls.
- Do not block PNG/JPG concept export solely because ZIP handoff package guardrails fail.
- Do not add a new standalone marketing page for package export.

## PATTERN MAPPING COMPLETE
