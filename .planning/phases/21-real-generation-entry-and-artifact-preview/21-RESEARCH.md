# Phase 21 Research: Real Generation Entry And Artifact Preview

## Goal

Answer: what needs to be known to plan Phase 21 well?

## Existing Workbench Flow

- `apps/web/src/components/workbench/workbench-app.tsx` is the orchestration point for workspace resume, chat-created briefs, parameter saves, job list state, generation state, and selected artifact/version state.
- `apps/web/src/lib/api/generation.ts` already exposes the desired boundary: `buildGenerationSubmissionPayload()`, `submitGenerationJob()`, and `loadGenerationState()`.
- `apps/web/src/components/workbench/parameter-panel.tsx` owns the visible parameter controls and is the correct location for an explicit `生成概念` action.
- `apps/web/src/components/workbench/preview-panel.tsx` already owns selected version/artifact rendering, PreviewSpec toggles, and local overlay state.

## Existing API Flow

- `services/api/src/caragent_api/routes/jobs.py` exposes workspace job, event, version, and artifact routes.
- `services/api/src/caragent_api/schemas.py` defines `ArtifactResponse`; extending it is the API source of truth before regenerating contracts.
- Artifact records already store `workspace_id`, `object_key`, `content_type`, `width`, and `height`, which is enough for a workspace-scoped streaming route.
- `services/core/src/caragent_core/storage.py` is the storage boundary that the API should read from for artifact bytes.

## Data Flow To Preserve

1. Chat creates a workspace message and generation brief.
2. Parameter edits patch the active brief.
3. `生成概念` submits a generation job for the active brief.
4. The worker persists job events, artifact rows, and design versions.
5. The workbench polls the durable API state, not Celery result state.
6. The preview panel renders the selected artifact's `content_url`.

## Main Risks

- A generation button that submits stale parameters if dirty state is not saved first.
- Polling only the job row but not events/artifacts/versions, making the UI look stuck after success.
- Returning object keys in API responses without a stable content route.
- Rendering only the synthetic PreviewSpec scaffold instead of the real generated image.
- Showing the latest job after resume but not loading its artifacts and versions.

## Validation Architecture

- Web tests must cover clicking `生成概念`, generation job submission payloads, active polling refresh, and real image rendering from `content_url`.
- API tests must cover `ArtifactResponse.content_url`, correct content type/bytes, and cross-workspace access rejection.
- Contract checks must prove OpenAPI and generated TypeScript clients include `content_url` and the new content path.
- Smoke/UAT should verify a resumed workspace can still show the latest generated image without a hidden proof page.

## Research Complete

The phase is small enough to execute as four plans: frontend generation entry/polling, API content route/contracts, preview/resume image rendering, and focused verification/UAT.
