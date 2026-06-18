# Phase 5: Iteration, Feedback, And Concept Export - Context

**Gathered:** 2026-06-17
**Status:** Ready for UI design and planning
**Mode:** Auto-selected defaults from `$gsd-progress --next` because the user requested autonomous GSD continuation.

<domain>
## Phase Boundary

Phase 5 completes the v1 concept loop after the Phase 4 workbench: users can create child iterations from an existing generated design version, see lineage and parameter differences, record feedback/approval/rejection/commentary, and export a selected concept as a clearly labeled concept preview package.

This phase does not implement production-ready wrap shop handoff, layered PSD/AI/PDF packages, print preflight, true UV-mapped 3D, auth, billing, marketplace/community publishing, provider operations, quotas, or advanced mask/inpainting workflows. Exports must be honest concept-preview outputs, not production claims.

</domain>

<decisions>
## Implementation Decisions

### Iteration Model
- **D-01:** Treat `design_versions` as the source of truth for variant lineage. Child iterations use `parent_version_id` and `lineage_depth`, not browser-only history.
- **D-02:** A regeneration or targeted change creates a new generation job tied to the current workspace/brief and records the selected parent version in durable job metadata. The original version remains immutable.
- **D-03:** Phase 5 targeted changes are structured request text and supported brief parameter edits. Rich masks, inpainting, layer-specific edits, and ControlNet/IP-Adapter controls remain later scope.

### Version Comparison
- **D-04:** The UI should compare parent and child using available structured parameters, titles, summaries, status, lineage depth, artifact object keys, and prompt/model metadata where available.
- **D-05:** If exact visual diffing is not available, present a truthful metadata/parameter comparison instead of implying pixel-level image comparison.

### Feedback And Approval
- **D-06:** Feedback records are durable API-backed records with rating, approval state, comment, and version id.
- **D-07:** Approval/rejection in the UI should be lightweight and reversible through additional feedback records or status updates; it must not delete versions or artifacts.
- **D-08:** Feedback should preserve the selected version context so users can comment/rate without losing chat, parameters, progress, preview, or history.

### Concept Export
- **D-09:** Phase 5 export creates a concept-preview export record for a selected version in `png` or `jpg/jpeg` format plus a JSON manifest that includes version id, workspace id, brief id, source artifact id/object key, concept label, parameters, and "not print-ready" wording.
- **D-10:** Export output may reference/copy the selected generated image artifact; it must not claim scale, bleed, DPI, layer separation, vector text/logo, or wrap-shop readiness.
- **D-11:** Export state is canonical in PostgreSQL/object storage metadata. The web UI can show export history and manifest details even before a signed download route exists.

### Workbench Integration
- **D-12:** Extend the existing Phase 4 workbench rather than replacing it. Iteration, feedback, and export controls should live near the preview/history surface and preserve the dense operational layout.
- **D-13:** Keep TanStack Query for feedback/export/version reads and mutations; keep Zustand for local selected version/view/zoom/panel state only.
- **D-14:** Browser storage remains limited to safe resume ids and local UI preferences. Do not store export payloads, feedback comments, image bytes, provider secrets, or durable version data in local storage.

### the agent's Discretion
- Exact endpoint names, component decomposition, copy phrasing, manifest schema field ordering, idempotency-key construction, and whether feedback is a new record or a status-update wrapper are implementation details as long as ITER-01 through ITER-06 are satisfied and evidence is recorded.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product Scope
- `.planning/ROADMAP.md` - Phase 5 goal, ITER-01 through ITER-06 success criteria, and later phase boundaries.
- `.planning/REQUIREMENTS.md` - ITER requirements and traceability table.
- `.planning/PROJECT.md` - Product context, seed material references, constraints, and expected user experience.
- `init.MD` - Original module, workflow, UI/UX, and export direction.
- `UI.png` - Visual blueprint for preview/history, parameter adjustment, and export/share controls.

### Prior Phase Contracts
- `.planning/phases/04-workbench-ui-integration/04-CONTEXT.md` - Workbench state, layout, canonical backend state, and future-gate decisions.
- `.planning/phases/04-workbench-ui-integration/04-UI-SPEC.md` - Current visual/layout contract.
- `.planning/phases/04-workbench-ui-integration/04-VERIFICATION.md` - Phase 4 verification evidence and supported UI behavior.

### Current Implementation
- `services/core/src/caragent_core/services/jobs.py` - Existing version lineage, feedback, and export service primitives.
- `services/api/src/caragent_api/routes/jobs.py` - Current job/version/artifact/feedback/export list routes.
- `services/api/src/caragent_api/schemas.py` - Current response schemas and missing create request schemas.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Generation task that creates versions/artifacts and needs parent-version metadata support.
- `apps/web/src/components/workbench/workbench-app.tsx` - Existing workbench composition and canonical state loading.
- `apps/web/src/components/workbench/preview-panel.tsx` - Existing version selection and 2D preview surface.
- `apps/web/src/lib/api/generation.ts` - Existing generated-contract wrapper style for job/artifact/version state.
- `apps/web/src/app/page.test.tsx` - Existing workbench integration test style and fixtures.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `services/core/src/caragent_core/services/jobs.py` already has `create_design_version(parent_version_id=...)`, `record_feedback`, `record_export`, `list_workspace_feedback`, and `list_workspace_exports`.
- `services/api/src/caragent_api/routes/jobs.py` already exposes list routes for versions, artifacts, feedback, and exports.
- `packages/contracts/src/generated/client.ts` already contains response types and generated list helpers for feedback/exports.
- `apps/web/src/components/workbench/preview-panel.tsx` already selects versions locally and can host iteration/export controls.
- `apps/web/src/lib/workbench/store.ts` already stores selected version id, view, zoom, and pan.

### Established Patterns
- API wrappers accept optional `apiBaseUrl`, `fetch`, and `signal`.
- Workbench tests stub generated-contract URLs and assert exact request bodies.
- Canonical server state is refetched through API wrappers; local state only controls synchronous UI selection.
- Existing docs and UAT distinguish concept preview from production-ready wrap output.

### Integration Points
- Add create request schemas/routes for feedback and concept export.
- Add an iteration submission route that creates a child generation job with parent version metadata and idempotency.
- Update worker generation task to pass `parent_version_id` into `create_design_version` when job metadata provides it.
- Refresh OpenAPI/contracts after backend route changes and add frontend wrappers for feedback/export/iteration.
- Extend workbench preview/history with lineage, feedback, export, and comparison controls.

</code_context>

<specifics>
## Specific Ideas

- Add a compact "迭代" control near the selected version: change request textarea, regenerate button, and parent/child lineage label.
- Add a "反馈" panel with 1-5 rating, approve/reject buttons, and comment box.
- Add a "概念导出" panel that offers PNG/JPG concept export and shows manifest metadata including "concept preview, not print-ready".
- Show parent/child comparison as metadata and parameter deltas first; avoid fake visual diffing until image processing exists.

</specifics>

<deferred>
## Deferred Ideas

- Pixel-level visual diff, mask/inpainting, local layer editing, and deterministic text/logo overlays remain Phase 6+ scope.
- Print preflight, layered production packages, PDF/PSD/AI-style handoff, bleed/DPI/color workflow, and installer notes remain v2+ production handoff scope.
- Signed download URLs, CDN delivery, auth-bound private artifacts, quotas, marketplace publishing, and payment/order flows remain later phases.

</deferred>

---

*Phase: 05-iteration-feedback-and-concept-export*
*Context gathered: 2026-06-17*
