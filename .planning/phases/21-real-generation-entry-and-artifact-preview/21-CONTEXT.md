# Phase 21: Real Generation Entry And Artifact Preview - Context

**Gathered:** 2026-06-22
**Status:** Ready for planning
**Source:** `$gsd-progress --next` fallback from `.planning/STATE.md`; milestone source is `carAgent_CODE_REVIEW.md`.

<domain>
## Phase Boundary

Phase 21 closes the user-visible first generation loop in the existing workbench. The user must be able to create or resume a workspace, save the active structured brief, explicitly submit a generation job, watch the active job refresh while it is queued or running, and view the actual generated image in the 2D preview panel.

This phase does not introduce the full object-storage unification, job outbox, short worker transactions, parser/compositor work, or hosted security hardening from later v4 phases.
</domain>

<decisions>
## Implementation Decisions

### Workbench Generation Entry

- Add an explicit `生成概念` action near the parameter save controls in the existing workbench.
- The action must save dirty brief parameters before submitting a generation job.
- The action must reuse `buildGenerationSubmissionPayload()` and `submitGenerationJob()` rather than creating a separate proof route or hidden generation path.
- The submitted job should use `requested_by: "web-workbench"` and a fresh idempotency key.

### Active Job Refresh

- The workbench must refresh queued or running jobs automatically every 1-2 seconds.
- Refresh must reload jobs and the selected/latest job state: events, artifacts, versions, exports, and feedback.
- Terminal statuses must stop polling.

### Artifact Content

- `ArtifactResponse` must expose `content_url: string | null`.
- The first implementation of `content_url` is an API streaming route, not a presigned URL.
- The content route is `GET /workspaces/{workspace_id}/artifacts/{artifact_id}/content`.
- The route must be workspace-scoped and return 404 when the artifact is missing or belongs to a different workspace.

### 2D Preview

- The 2D preview must render the actual generated artifact image with a real `<img>`.
- PreviewSpec overlays remain layered above the image when a PreviewSpec exists.
- If a selected artifact has image bytes but no PreviewSpec, the panel must still show the image.
- Resuming an existing workspace must load the latest job state so the latest artifact image is visible.

### the agent's Discretion

- Button disabled/loading text, exact cache writes, and test fixture names are implementation details, as long as the user-facing loop and API contracts above are satisfied.
</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone Scope

- `.planning/ROADMAP.md` - Phase 21 goal and success criteria.
- `.planning/REQUIREMENTS.md` - GENC-01 through GENC-04.
- `.planning/STATE.md` - current v4 milestone state and next command.

### Frontend Workbench

- `apps/web/src/components/workbench/workbench-app.tsx` - workbench state, brief save, generation submission, polling, resume flow.
- `apps/web/src/components/workbench/parameter-panel.tsx` - parameter save controls and generation action placement.
- `apps/web/src/components/workbench/preview-panel.tsx` - selected artifact/version rendering and PreviewSpec overlay canvas.
- `apps/web/src/lib/api/generation.ts` - generation brief/job API helpers and submission payload builder.
- `apps/web/src/app/page.test.tsx` - workbench integration tests.

### API And Contracts

- `services/api/src/caragent_api/routes/jobs.py` - artifact listing and job/artifact routes.
- `services/api/src/caragent_api/schemas.py` - `ArtifactResponse`.
- `services/core/src/caragent_core/storage.py` - object storage protocol used by artifact content.
- `services/api/tests/test_jobs.py` - job/artifact API tests.
- `packages/contracts/openapi/openapi.json` and `packages/contracts/src/generated/client.ts` - generated API contracts.
</canonical_refs>

<specifics>
## Specific Ideas

- Keep the action label as `生成概念`.
- Polling cadence should be 1500 ms or another value within the 1-2 second window.
- Use `publicEnv.apiBaseUrl` to resolve relative `content_url` values on the web.
- The image alt text should identify the 2D concept preview.
</specifics>

<deferred>
## Deferred Ideas

- Phase 22 owns shared storage factory defaults and S3/MinIO parity.
- Phase 23 owns dispatch outbox, state version, and worker short transactions.
- Phase 24 owns real 3D screenshot capture validation and parameter clearing.
- Phase 25 owns BriefParser and TemplateCompositor.
- Phase 26 owns authorization dependencies, upload/download hardening, Redis quota, and structured telemetry.
</deferred>

---

*Phase: 21-real-generation-entry-and-artifact-preview*
*Context gathered: 2026-06-22 via `$gsd-progress --next`*
