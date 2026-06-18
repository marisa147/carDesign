---
phase: 10-targeted-regeneration-and-masked-editing-mvp
status: ready
created: 2026-06-18
---

# Phase 10 Pattern Map

This file points execution agents at local code patterns to reuse during Phase 10. It is not a replacement for reading the files named in each plan.

## Durable Ledger

| Pattern | File | Reuse Guidance |
|---------|------|----------------|
| Parent/child design lineage | `services/core/src/caragent_core/models.py` | Reuse `DesignVersion.parent_version_id`; never overwrite parent versions for targeted edits. |
| Job metadata | `services/core/src/caragent_core/models.py`, `services/core/src/caragent_core/services/jobs.py` | Store request-time edit intent, prompt delta, selected region/layer, route, and provider intent in typed metadata. |
| Artifact metadata | `services/core/src/caragent_core/models.py` | Store mask artifact provenance, dimensions, selected target, and changed-region metadata. |
| Model-run trace | `services/core/src/caragent_core/services/jobs.py` | Record recomposition/provider route, mask inputs, provider/model/cost, and sanitized errors. |
| Failure categories | `services/core/src/caragent_core/enums.py` | Add only categories with distinct user/operator actions. |

## Generation And Provider Boundary

| Pattern | File | Reuse Guidance |
|---------|------|----------------|
| Iteration context | `services/worker/src/caragent_worker/tasks/jobs.py` | Extend existing child-iteration metadata rather than creating unrelated task state. |
| Prompt plan payload | `services/core/src/caragent_core/generation/prompts.py` | Preserve PreviewSpec and add edit metadata in parameters/prompt payload where provider route needs it. |
| Normalized image request | `services/worker/src/caragent_worker/providers/base.py` | Extend with optional mask/edit fields only if shared by provider adapters. |
| Local PreviewSpec rendering | `services/worker/src/caragent_worker/providers/local.py` | Reuse drawing/metadata patterns for deterministic recomposition or move common helpers out carefully. |
| Provider capability status | `services/core/src/caragent_core/provider_capabilities.py`, `services/api/src/caragent_api/routes/operations.py` | Gate mask-aware generation by typed capability metadata, not UI hardcoding. |

## API And Contracts

| Pattern | File | Reuse Guidance |
|---------|------|----------------|
| Generation schemas | `services/api/src/caragent_api/schemas.py` | Add typed edit intent, region, mask, and prompt-delta schemas; regenerate contracts. |
| Iteration route | `services/api/src/caragent_api/routes/generation.py` | Keep targeted edits version-scoped through the child iteration route unless a separate route is necessary. |
| Jobs route | `services/api/src/caragent_api/routes/jobs.py` | Expose enough version/job/model/artifact metadata for comparison and retry. |
| Contract artifacts | `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/client.ts` | Must be regenerated/checked after schema changes. |

## Web Workbench

| Pattern | File | Reuse Guidance |
|---------|------|----------------|
| Workbench UI state | `apps/web/src/lib/workbench/store.ts` | Add selected edit target, mask visibility, and comparison mode to existing store. |
| PreviewSpec parsing/rendering | `apps/web/src/components/workbench/preview-panel.tsx` | Use parsed safe zones and overlay layers for selectable targets and changed-region highlight. |
| Existing iteration form | `apps/web/src/components/workbench/workbench-app.tsx` | Submit targeted edit payload through existing child iteration flow. |
| Provider selector | `apps/web/src/components/workbench/parameter-panel.tsx` | Keep provider route visibility compact and concept-preview scoped. |
| API wrappers | `apps/web/src/lib/api/iteration.ts`, `apps/web/src/lib/api/generation.ts` | Keep generated contract types as source of truth. |

## Test Patterns

| Area | Existing Tests |
|------|----------------|
| API generation/jobs/operations | `services/api/tests/test_generation.py`, `test_jobs.py`, `test_operations.py` |
| Core ledger/generation | `services/core/tests/test_models.py`, `test_generation_jobs.py`, `test_prompt_plans.py` |
| Worker providers/generation | `services/worker/tests/test_generation_tasks.py`, `test_image_providers.py`, `test_config.py` |
| Web workbench/API wrappers | `apps/web/src/app/page.test.tsx`, `apps/web/src/lib/workbench/store.test.ts`, `apps/web/src/lib/api/iteration.test.ts` |

## Anti-Patterns

- Do not overwrite parent version parameters, parent artifacts, or parent generated images during targeted edits.
- Do not silently fall back from masked provider generation to full regeneration.
- Do not route mask provider payloads directly from browser code.
- Do not spend hosted provider quota during default tests or local validation.
- Do not expose secrets, raw provider payloads, or bearer tokens in edit failure diagnostics.
- Do not claim mask precision, 3D accuracy, or print readiness from Phase 10 outputs.
