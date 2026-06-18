---
phase: 11
slug: reference-guided-generation-mvp
status: complete
created: 2026-06-18
---

# Phase 11 - Pattern Map

## Core And API Patterns

| New Need | Existing Pattern | Files To Read |
|----------|------------------|---------------|
| Reference role enum/schema | Phase 10 `EditIntent` schema and enum tests | `services/core/src/caragent_core/editing.py`, `services/core/tests/test_models.py` |
| Rights/source validation | Asset service helper with `require_confirmed_rights` | `services/core/src/caragent_core/services/assets.py`, `services/api/src/caragent_api/routes/assets.py` |
| Provider capability fields | Phase 9/10 provider capability map and operations status | `services/core/src/caragent_core/provider_capabilities.py`, `services/api/src/caragent_api/routes/operations.py`, `services/api/tests/test_operations.py` |
| Brief payload extension | Pydantic `GenerationBriefPayload` and API create/update routes | `services/core/src/caragent_core/generation/briefs.py`, `services/api/src/caragent_api/schemas.py`, `services/api/src/caragent_api/routes/generation.py` |
| Prompt payload construction | Prompt plan helper returns text, payload, input artifact IDs | `services/core/src/caragent_core/generation/prompts.py`, `services/core/tests/test_prompt_plans.py` |
| Durable trace metadata | Worker writes model-run, artifact, version, job metadata | `services/worker/src/caragent_worker/tasks/jobs.py`, `services/worker/tests/test_generation_tasks.py` |

## Worker Patterns

| New Need | Existing Pattern | Notes |
|----------|------------------|-------|
| Worker repeats API preflight | `_enforce_provider_mask_preflight` repeats mask capability and artifact checks | Add reference preflight with the same fail-closed posture. |
| Request metadata normalization | `ImageGenerationRequest` and `MaskEditRequest` carry provider-neutral metadata | Add reference usage metadata without provider-specific payload in core request fields. |
| Local deterministic metadata | Local provider writes metadata and preview labels without external calls | Local references can affect metadata/prompt labels but must not claim true image-reference fidelity. |
| Failure classification | `_classify_generation_failure` maps errors to durable categories | Rights errors already use `VALIDATION_RIGHTS`; unsupported references can use provider configuration or a new category if introduced in 11-01. |

## Web Patterns

| New Need | Existing Pattern | Files To Read |
|----------|------------------|---------------|
| Asset row controls | `AssetListItem` keeps local form state and calls parent handlers | `apps/web/src/components/workbench/asset-panel.tsx` |
| Provider warnings | `ProviderSelector` displays blocked reasons and guard labels | `apps/web/src/components/workbench/parameter-panel.tsx`, `apps/web/src/lib/api/operations.ts` |
| Selected reference state | `WorkbenchApp` owns selected reference IDs and passes them to asset/parameter panels | `apps/web/src/components/workbench/workbench-app.tsx` |
| Contract-generated payloads | API clients import generated contract types | `apps/web/src/lib/api/assets.ts`, `apps/web/src/lib/api/generation.ts`, `apps/web/src/lib/api/iteration.ts` |
| Workbench flow tests | Page-level Vitest fixtures cover upload, rights, generation, provider, targeted edits | `apps/web/src/app/page.test.tsx` |

## Planned File Map

| Plan | Main Write Set |
|------|----------------|
| 11-01 | Core reference contracts, provider capabilities, API schemas, core/API tests, generated contracts |
| 11-02 | `asset-panel.tsx`, `workbench-app.tsx`, web fixtures/tests, possibly store/query helpers |
| 11-03 | Core prompt/reference planner helpers and tests, API generation tests |
| 11-04 | Worker request/provider/preflight handling and worker/provider tests |
| 11-05 | Worker persistence metadata, export manifest source trace, API/job tests |
| 11-06 | Web generation UX, warnings, child iteration reuse, page/API tests |
| 11-07 | README, docs, Phase 11 evidence files, ROADMAP, REQUIREMENTS, STATE |

## Codebase Constraints

- Do not scatter provider checks in UI only. Provider support belongs in capability maps and backend/worker validation.
- Do not store binary image data in JSON metadata.
- Do not remove legacy `reference_asset_ids` until structured reference usage is fully adopted.
- Keep external provider calls disabled in default tests.
- Run contract checks after Pydantic schema changes.

## PATTERN MAPPING COMPLETE
