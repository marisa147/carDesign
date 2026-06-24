# Phase 21 Patterns

## Workbench Orchestration

Use `WorkbenchApp` as the only stateful orchestrator for this phase:

- Submit jobs through `submitGenerationJob(workspace.id, buildGenerationSubmissionPayload(...))`.
- Store the submitted job in both React state and `workbenchQueryKeys.jobs(workspace.id)`.
- Refresh the latest job with `loadGenerationState(workspace.id, latestJob.id)` so events, artifacts, versions, exports, and feedback stay in sync.
- Use a `useEffect` interval keyed by job id/status; terminal states clear the interval by returning early.

## Parameter Action Row

The parameter panel should not know API details. It receives:

- `onSave(payload)` for dirty brief persistence.
- `onGenerate()` for job submission.
- `isGenerating` and `generationError` for action state and inline error rendering.

This keeps `ParameterPanel` a presentational/controller component while `WorkbenchApp` owns API sequencing.

## Artifact Content

Use a response helper in `services/api/src/caragent_api/routes/jobs.py`:

- Convert `Artifact` to `ArtifactResponse`.
- Set `content_url` to `/workspaces/{workspace_id}/artifacts/{artifact_id}/content`.
- Reuse the helper in all artifact response surfaces that need the URL.

The content route should read bytes with `storage.get_object(artifact.object_key)` and return `artifact.content_type` first, falling back to stored metadata and then `application/octet-stream`.

## Preview Rendering

Resolve artifact image URLs in `preview-panel.tsx`:

1. If `artifact.content_url` is absent, return `null`.
2. If it starts with `http://` or `https://`, use it as-is.
3. Otherwise prefix with `publicEnv.apiBaseUrl`.

Render paths:

- With PreviewSpec: generated image is an absolutely positioned `<img>` beneath overlay layers.
- Without PreviewSpec: render a simple `ConceptImage`.

## Testing Pattern

- Prefer workbench integration tests in `apps/web/src/app/page.test.tsx` for user-visible generation and preview behavior.
- Prefer API route tests in `services/api/tests/test_jobs.py` for content bytes and workspace scoping.
- Always regenerate contracts after schema or route changes and run `pnpm contracts:check`.
