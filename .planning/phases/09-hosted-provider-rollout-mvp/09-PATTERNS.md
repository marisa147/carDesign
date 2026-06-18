---
phase: 09-hosted-provider-rollout-mvp
status: ready
created: 2026-06-18
---

# Phase 9 Pattern Map

This file points execution agents at the local code patterns that should be reused during Phase 9. It is not a replacement for reading the files named in each plan.

## Provider Boundary

| Pattern | File | Reuse Guidance |
|---------|------|----------------|
| Normalized provider request/result | `services/worker/src/caragent_worker/providers/base.py` | Extend fields only when needed; keep provider-specific payloads in adapter metadata, not in the generic protocol unless shared. |
| Local deterministic provider | `services/worker/src/caragent_worker/providers/local.py` | Preserve as default provider, free smoke path, and hosted fallback route. |
| Provider selection | `services/worker/src/caragent_worker/providers/__init__.py` | Keep aliases centralized; do not instantiate vendor clients in task code. |
| BFL scaffold | `services/worker/src/caragent_worker/providers/bfl.py` | Update against official docs instead of spreading BFL logic elsewhere. |

## Durable Ledger

| Pattern | File | Reuse Guidance |
|---------|------|----------------|
| Job/model/artifact/version models | `services/core/src/caragent_core/models.py` | Prefer existing `GenerationJob`, `ModelRun`, `Artifact`, and `DesignVersion` fields before adding schema. |
| Job service helpers | `services/core/src/caragent_core/services/jobs.py` | Persist status, events, model-run updates, artifact metadata, and sanitized errors through existing helpers. |
| Failure categories | `services/core/src/caragent_core/enums.py` | Add categories only where provider behavior needs a distinct user/operator meaning. |
| Worker generation pipeline | `services/worker/src/caragent_worker/tasks/jobs.py` | Keep preflight, provider execution, fallback, and persistence ordered around durable job state. |

## API And Contracts

| Pattern | File | Reuse Guidance |
|---------|------|----------------|
| Submission schemas | `services/api/src/caragent_api/schemas.py` | Add provider intent as typed optional fields; regenerate contracts after changes. |
| Generation route | `services/api/src/caragent_api/routes/generation.py` | API preflight belongs here or in a helper called here; do not enqueue obviously blocked hosted jobs. |
| Operations route | `services/api/src/caragent_api/routes/operations.py` | Expose safe provider capability/guard/blocked metadata and recent sanitized failures. |
| Contract artifacts | `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/client.ts` | Must be regenerated/checked after schema changes. |

## Web Workbench

| Pattern | File | Reuse Guidance |
|---------|------|----------------|
| Workbench composition | `apps/web/src/components/workbench/workbench-app.tsx` | Provider selection should feed the existing generation submit path, not create a parallel submit flow. |
| Progress and operations UI | `apps/web/src/components/workbench/progress-panel.tsx` | Reuse existing diagnostics sanitization and operations status rendering. |
| Parameter area | `apps/web/src/components/workbench/parameter-panel.tsx` | Likely placement for provider selector or mode affordance. Keep it compact. |
| API wrappers | `apps/web/src/lib/api/generation.ts`, `apps/web/src/lib/api/operations.ts` | Keep generated contract types as source of truth. |

## Test Patterns

| Area | Existing Tests |
|------|----------------|
| API config/operations/generation/jobs | `services/api/tests/test_config.py`, `test_operations.py`, `test_generation.py`, `test_jobs.py` |
| Worker providers/generation | `services/worker/tests/test_image_providers.py`, `test_generation_tasks.py`, `test_config.py` |
| Web workbench/API wrappers | `apps/web/src/app/page.test.tsx`, `apps/web/src/lib/api/generation.test.ts`, `apps/web/src/lib/api/operations.test.ts` |

## Anti-Patterns

- Do not call BFL or any hosted provider directly from API or web code.
- Do not let browser-visible JSON include API keys, bearer tokens, database URLs, Redis URLs, S3 secrets, or raw provider payloads.
- Do not record fake actual hosted cost. Use provider response cost/trusted calculation or leave actual cost null.
- Do not silently fall back from hosted to local without durable trace metadata.
- Do not make default validation depend on hosted credentials or paid external calls.
