---
phase: 5
slug: iteration-feedback-and-concept-export
status: complete
created: 2026-06-17
sources:
  - .planning/phases/05-iteration-feedback-and-concept-export/05-CONTEXT.md
  - .planning/phases/05-iteration-feedback-and-concept-export/05-UI-SPEC.md
  - services/core/src/caragent_core/services/jobs.py
  - services/api/src/caragent_api/routes/jobs.py
  - services/api/src/caragent_api/schemas.py
  - services/worker/src/caragent_worker/tasks/jobs.py
  - apps/web/src/components/workbench/workbench-app.tsx
  - apps/web/src/components/workbench/preview-panel.tsx
  - apps/web/src/lib/api/generation.ts
---

# Phase 5 Research: Iteration, Feedback, And Concept Export

## Summary

Phase 5 can build on existing durable ledger primitives rather than introducing new storage concepts. The core package already supports version lineage, feedback records, export records, artifact links, and workspace-scoped list queries. The main missing work is to expose creation/submission APIs, refresh generated TypeScript contracts, add frontend wrappers, extend the workbench UI, and teach the worker to create child design versions when a generation job carries parent-version metadata.

## Current State

### Durable Core

- `create_design_version` already accepts `parent_version_id` and increments `lineage_depth`.
- `record_feedback` already validates rating 1-5 and approval states from `FeedbackApprovalState`.
- `record_export` already records format, status, artifact id, concept label, and manifest JSON.
- `list_workspace_versions`, `list_workspace_feedback`, and `list_workspace_exports` already exist.

### API

- Existing `jobs.py` routes list jobs/events/versions/artifacts/model-runs/feedback/exports.
- Missing routes for Phase 5:
  - Create feedback for a selected version.
  - Create concept export for a selected version.
  - Submit child iteration generation from a selected parent version.
- `schemas.py` has response models but no create request schemas for feedback/export/iteration.

### Worker

- The generation task already creates a generated design version and artifact.
- It should pass `parent_version_id` from durable job metadata into `create_design_version` when present.
- Local deterministic generation can remain the baseline for child iterations; no hosted provider keys are needed.

### Frontend

- `WorkbenchApp` currently loads workspace/messages/briefs/assets/jobs and latest generation state.
- `PreviewPanel` already receives artifacts/versions and handles selected version id locally.
- `workbench/store.ts` already has selected version, view, zoom, and pan.
- Missing frontend work:
  - API wrappers/query keys for feedback, exports, and iteration submit.
  - Extended generation state or workbench state that includes feedback/exports.
  - Iteration controls, lineage/comparison, feedback form/history, concept export panel/history.

## Recommended API Shape

Keep Phase 5 routes workspace/version scoped:

| Capability | Suggested Route | Notes |
|------------|-----------------|-------|
| Create feedback | `POST /workspaces/{workspace_id}/versions/{version_id}/feedback` | Body: rating, approval_state, comment, metadata. |
| Create concept export | `POST /workspaces/{workspace_id}/versions/{version_id}/exports` | Body: format, artifact_id optional, manifest optional. Server adds concept-preview safety fields. |
| Submit child iteration | `POST /workspaces/{workspace_id}/versions/{version_id}/iterations` | Body: brief_id, idempotency_key, requested_by, change_request, parameter_overrides. Creates generation job metadata with parent_version_id. |

Existing list routes can remain as-is for Phase 5.

## Export Strategy

Phase 5 should produce concept-preview export records and manifest metadata, not full file serving. Minimum useful manifest fields:

- `workspace_id`
- `version_id`
- `parent_version_id`
- `brief_id`
- `source_artifact_id`
- `source_artifact_object_key`
- `format`
- `concept_label`
- `parameters`
- `disclaimer`: `Concept preview only. Not print-ready.`
- `created_at`

If object-storage writing is straightforward during implementation, write a manifest JSON artifact and link it from the export record. If not, store the manifest in the export row and record the source artifact id; signed download/file packaging can follow later without changing the user-facing concept-export contract.

## Validation Architecture

### Automated Backend Tests

- Core service tests for child version lineage, feedback validation, and export manifest defaults.
- API route tests for create feedback/export and child iteration submission.
- Worker tests proving child generation jobs create versions with the expected parent/depth.
- Contract drift check after OpenAPI generation.

### Automated Frontend Tests

- API wrapper tests for feedback/export/iteration routes.
- Workbench tests for lineage/comparison display and selected-version preservation.
- Workbench tests for feedback submit/history.
- Workbench tests for export format selection, disclaimer, manifest preview, and disabled production gates.

### Required Commands

- `corepack pnpm --filter @caragent/web test`
- `corepack pnpm --filter @caragent/web lint`
- `corepack pnpm --filter @caragent/web typecheck`
- `corepack pnpm --filter @caragent/web build`
- `corepack pnpm contracts:check`
- `cd services/core && uv run pytest -q tests/test_jobs.py`
- `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_generation.py`
- `cd services/worker && uv run pytest -q tests/test_generation_tasks.py`
- `corepack pnpm validate`
- Browser UAT at desktop and mobile widths.

## Risks And Mitigations

| Risk | Mitigation |
|------|------------|
| Export is mistaken for production-ready wrap output. | Add server manifest disclaimer and UI warning; keep production handoff gates disabled. |
| Child iteration overwrites or obscures parent versions. | Use `parent_version_id`, `lineage_depth`, and immutable artifacts; tests must assert parent remains readable. |
| API route surface duplicates generation submit behavior. | Keep iteration route a thin wrapper that creates a generation job with parent metadata and reuses worker generation. |
| UI grows cluttered after Phase 4. | Add compact panels near preview/history and preserve the existing three-zone layout. |
| Feedback approval conflicts with version status. | Store feedback durably first; update version status only if implementation can do it safely and tests prove it. |
| No signed artifact download route exists. | Phase 5 can record export manifest/source artifact and show export history; signed download can be a later capability if needed. |

## Source Coverage

| Requirement | Research Finding |
|-------------|------------------|
| ITER-01 | `parent_version_id` and `lineage_depth` already support preserved parent/child versions. |
| ITER-02 | Generation brief update and job metadata can capture targeted style/palette/text/composition/coverage changes. |
| ITER-03 | Version parameters plus parent id can power comparison and lineage views. |
| ITER-04 | Feedback table/service/list route exist; create route/UI is missing. |
| ITER-05 | Export table/service/list route exist; create route/UI/manifest is missing. |
| ITER-06 | Existing docs/future gates already establish concept-preview vs production boundary; Phase 5 must make it explicit in export manifest/UI. |

## Recommendation

Plan Phase 5 as seven small plans:

1. Backend schemas/routes for feedback and concept exports.
2. Child iteration generation contract and worker lineage support.
3. Contract refresh and frontend API wrappers/query keys.
4. Workbench lineage, comparison, and child iteration controls.
5. Feedback/approval panel.
6. Concept export panel/history/manifest and deferred production gates.
7. Phase 5 docs, verification, Browser UAT, and requirement closure.
