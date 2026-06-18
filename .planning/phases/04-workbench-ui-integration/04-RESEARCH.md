---
phase: 4
slug: workbench-ui-integration
status: complete
created: 2026-06-17
sources:
  - .planning/phases/04-workbench-ui-integration/04-CONTEXT.md
  - .planning/phases/04-workbench-ui-integration/04-UI-SPEC.md
  - apps/web/src/app/page.tsx
  - apps/web/src/lib/api/workspaces.ts
  - apps/web/src/lib/api/jobs.ts
  - apps/web/src/lib/api/generation.ts
  - services/api/src/caragent_api/routes/workspaces.py
  - services/api/src/caragent_api/routes/assets.py
---

# Phase 4 Research: Workbench UI Integration

## Summary

Phase 4 can be implemented primarily in `apps/web` using existing API surfaces and generated contracts. The backend already exposes durable workspaces, messages, generic design brief listing, generation brief create/update, jobs/events, assets/rights, artifacts, and versions. The main work is to replace the proof page with a typed workbench shell, add missing frontend wrappers/hooks, and render the canonical state through chat, parameter, upload, progress, preview, history, and deferred-feature gates.

## Current State

### Frontend

- `apps/web/src/app/page.tsx` is a single large client component with Phase 1-3 proof panels.
- Existing wrappers:
  - `apps/web/src/lib/api/workspaces.ts` covers create/resume workspace and messages.
  - `apps/web/src/lib/api/jobs.ts` covers jobs and events.
  - `apps/web/src/lib/api/generation.ts` covers generation brief create/update, job submit/retry, and loading job/events/artifacts/versions.
- Existing component primitives are intentionally small: `Button`, `Card`, `Badge`, `Alert`.
- `@tanstack/react-query` is already an app dependency, but not wired into the app yet.
- Zustand is part of the planned stack, but is not currently in `apps/web/package.json` or `pnpm-lock.yaml`.

### Backend And Contracts

- `services/api/src/caragent_api/routes/workspaces.py` already exposes `GET /workspaces/{workspace_id}/briefs` returning durable design briefs. This can support refresh/resume of parameters without adding a new backend route.
- `services/api/src/caragent_api/routes/assets.py` exposes asset upload/list/get/update-rights routes. Contracts include generated URL helpers for these routes.
- `services/api/src/caragent_api/routes/generation.py` owns generation-specific create/update/submit/retry behavior.
- Generated contract types already include `AssetResponse`, `AssetRightsUpdateRequest`, `BodyUploadAssetWorkspacesWorkspaceIdAssetsPost`, `DesignBriefResponse`, `GenerationBriefResponse`, `GenerationJobResponse`, `JobEventResponse`, `ArtifactResponse`, and `DesignVersionResponse`.

## Library Guidance

### TanStack Query

Use Query for server state. The v5 docs emphasize queries for fetches, mutations for writes, and invalidation after mutation success/settlement. This maps directly to workspace/message/brief/asset/job state:

- Query keys should be stable and domain-shaped, for example `["workspace", workspaceId]`, `["messages", workspaceId]`, `["briefs", workspaceId]`, `["assets", workspaceId]`, `["generation-state", workspaceId, jobId]`.
- Mutations should invalidate the affected query keys after success. Returning invalidation promises keeps pending state accurate.
- Do not use Query for local preview zoom, selected version, selected view, or panel state.

### Local UI State

The project convention prefers Zustand for local workbench state. If package installation is feasible, add Zustand and keep a small store for:

- selected workbench tab
- selected version id
- selected 2D view
- preview zoom/pan
- collapsed panel state

If dependency installation is blocked, keep this logic isolated in a single local store module using React state so replacing it with Zustand later is mechanical. Do not mix UI state into API wrappers.

## Implementation Architecture

### Recommended File Boundaries

| File | Responsibility |
|------|----------------|
| `apps/web/src/app/page.tsx` | Thin page entry that renders the workbench app and provider. |
| `apps/web/src/app/page.test.tsx` | Integration-level workbench behavior tests and fixture-driven route assertions. |
| `apps/web/src/components/workbench/workbench-app.tsx` | Primary workbench composition, resume flow, layout zones. |
| `apps/web/src/components/workbench/chat-panel.tsx` | Durable message list, prompt composer, send flow. |
| `apps/web/src/components/workbench/parameter-panel.tsx` | Structured brief edit UI and save/generate controls. |
| `apps/web/src/components/workbench/asset-panel.tsx` | Upload/list/rights UI and reference selection affordance. |
| `apps/web/src/components/workbench/progress-panel.tsx` | Job status, events, refresh/retry states. |
| `apps/web/src/components/workbench/preview-panel.tsx` | 2D preview, zoom/pan/reset, view switch, history thumbnails. |
| `apps/web/src/components/workbench/future-gates.tsx` | Deferred/disabled controls for 3D/export/marketplace/production. |
| `apps/web/src/lib/api/assets.ts` | Asset wrapper matching existing wrapper style. |
| `apps/web/src/lib/api/workbench.ts` | Aggregated load/submit/update helper only if it reduces duplication. |
| `apps/web/src/lib/workbench/query-keys.ts` | Stable query key helpers. |
| `apps/web/src/lib/workbench/store.ts` | Local UI state store boundary. |

### Data Flow

1. On load, read only safe resume ids from browser storage.
2. If no workspace exists, create one from the first chat submission or via an explicit start action.
3. Queries fetch workspace, messages, briefs, assets, jobs, events, artifacts, and versions from the API.
4. Chat submit mutation creates a user message, then creates a generation brief from the message text.
5. Parameter edits call `PATCH /generation/briefs/{brief_id}` and invalidate brief/generation state.
6. Asset upload calls multipart upload, then rights update if provided; missing rights remain visible and blocked.
7. Generation submit uses the current brief id and idempotency key, then refreshes job/events/artifacts/versions.
8. Preview selection is local UI state derived from version/artifact ids.

## Validation Architecture

### Automated Web Tests

Phase 4 tests should start RED against the current proof page and then drive implementation:

- Workbench layout renders chat, preview, parameters, assets, progress, version history, and deferred gates.
- Chat submission creates a workspace if needed, creates a durable user message, creates a generation brief, and shows deterministic assistant/system feedback.
- Parameter edits call `PATCH /generation/briefs/{brief_id}` and update visible structured fields.
- Asset upload uses multipart `FormData`, lists assets, updates rights, and blocks missing-rights assets from being included.
- Job status and events render queued/running/succeeded/failed states distinctly, with retry action only for failed jobs.
- Preview/version selection changes selected version/artifact without losing chat or parameters.
- Future 3D/export/marketplace controls are disabled or labelled deferred.

### Required Commands

- `corepack pnpm --filter @caragent/web test`
- `corepack pnpm --filter @caragent/web lint`
- `corepack pnpm --filter @caragent/web typecheck`
- `corepack pnpm --filter @caragent/web build`
- `corepack pnpm contracts:check` if generated contract usage changes
- Browser verification at `http://127.0.0.1:3000/` on desktop and mobile widths after implementation

## Risks And Mitigations

| Risk | Mitigation |
|------|------------|
| The page component becomes too large. | Split workbench components early after tests lock behavior. |
| Server state and local UI state blur together. | Add query key/store boundaries before feature panels. |
| Asset uploads are hard to test with generated FormData helpers. | Add wrapper tests that inspect `FormData` and route URLs. |
| No direct image download/display URL route exists for object storage. | Phase 4 can display artifact metadata and stable preview placeholders; actual export/download belongs later unless existing public object URLs are added. |
| True 3D is tempting because UI.png shows it. | Use disabled/experimental gates in Phase 4 and leave real Three.js/UV work to later phases. |
| Zustand install may require network. | Prefer adding it when install succeeds; keep state boundary isolated if dependency installation is blocked. |

## Source Coverage

| Requirement | Research Finding |
|-------------|------------------|
| UI-01 | Durable messages exist; chat panel can build on workspace message APIs. |
| UI-02 | Generation brief create/update exists; brief listing exists through generic workspace briefs. |
| UI-03 | Asset upload/list/rights routes exist and are in generated contracts. |
| UI-04 | Jobs/events APIs already expose status and event history. |
| UI-05 | Artifacts/versions exist; preview controls are local UI work. |
| UI-06 | Version rows and artifact links support history switching. |
| UI-07 | Future gates are frontend-only copy/state work for this phase. |

## Recommendation

Plan Phase 4 as seven small plans:

1. API wrappers, Query provider, query keys, and local UI state boundary.
2. Workbench shell layout and future gates.
3. Chat-to-brief flow.
4. Parameter editing.
5. Asset upload/rights panel.
6. Progress, preview, and version history.
7. Phase 4 docs, UAT, Browser verification, and roadmap/state closure.
