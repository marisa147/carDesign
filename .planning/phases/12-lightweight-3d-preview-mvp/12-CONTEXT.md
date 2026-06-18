---
phase: 12
slug: lightweight-3d-preview-mvp
status: ready-for-execution
source: roadmap-auto-context
created: 2026-06-18
requirements: [V2-3D-01, V2-3D-02, V2-3D-03, V2-3D-04, V2-3D-05]
depends_on: [11-reference-guided-generation-mvp]
---

# Phase 12 - Lightweight 3D Preview MVP Context

**Gathered:** 2026-06-18
**Status:** Planned and ready for execution
**Source:** ROADMAP Phase 12, REQUIREMENTS V2-3D-01..05, Phase 10/11 handoff notes, and current code inspection.

<domain>
## Phase Boundary

Phase 12 delivers a lightweight browser 3D preview path for selected concept versions. The preview consumes existing `PreviewSpec`, selected generated artifact metadata, and a single registered shell fixture. It must stay explicitly concept-only and non-production.

This phase does not deliver verified vehicle-specific UV mapping, print-ready texture placement, production wrap templates, multi-vehicle shell coverage, or a physically accurate 3D export.
</domain>

<decisions>
## Implementation Decisions

### 3D Rendering Scope

- Use Three.js for browser 3D rendering. Add the dependency only when the frontend viewer plan executes.
- Keep the primary 3D scene unframed inside the workbench preview surface, not in a decorative nested card.
- Use a single lightweight shell fixture linked to the existing `generic-side-coupe` template.
- Prefer a simple mesh/decal-plane shell and PreviewSpec-driven material plan over a GLB/UV production pipeline.
- Lazy-load the viewer so workbench shell, 2D preview, and tests remain stable when 3D is disabled.

### Preview3DSpec Contract

- Add a versioned `Preview3DSpec` JSON contract with `schema_version: 1`.
- Link every spec to `workspace_id`, `version_id`, source artifact id/object key, source `PreviewSpec` template id/view, shell id, compatibility status, camera preset, material mapping, and warnings.
- Store 3D preview metadata in existing version/artifact metadata surfaces. Add a specific screenshot artifact kind only if it clarifies downstream export and tests.
- Do not store binary image data inside JSON metadata.

### Compatibility And Fallback

- Compatibility is explicit. A selected version is compatible only if its `PreviewSpec.template.id` maps to a registered shell.
- If no compatible shell exists, the UI keeps the 2D preview available and shows a concise fallback state.
- 3D preview failure must not block generation, targeted edits, reference usage, feedback, or concept export.

### Screenshot Persistence

- Screenshot capture is a user action from the 3D viewer.
- Persist screenshots as immutable artifacts linked to the selected version and current camera/material warning metadata.
- Use existing object storage and artifact ledger patterns. Browser-submitted screenshot bytes must be validated by API before storage.

### Warning Posture

- Every 3D preview surface must show persistent non-production labeling.
- Metadata must carry warning identifiers such as `non_production_preview`, `uv_not_verified`, and `single_shell_fixture`.
- Phase 13 can include screenshots in handoff packages only as concept screenshots with the same disclaimers.

### Validation Defaults

- Default validation must not require hosted provider calls.
- Browser/Playwright screenshot and canvas-pixel checks are required before Phase 12 closes because the primary deliverable is visual and WebGL/canvas based.
- Automated unit tests should cover contract mapping, fallback, screenshot payload validation, and warning metadata.
</decisions>

<canonical_refs>
## Canonical References

Downstream agents MUST read these before implementing Phase 12 plans.

### Planning And Handoff

- `.planning/ROADMAP.md` - Phase 12 goal, success criteria, plan list, data additions, UI additions, and risk register.
- `.planning/REQUIREMENTS.md` - V2-3D-01..05 requirement definitions and traceability.
- `.planning/STATE.md` - current milestone state and prior decisions.
- `.planning/phases/10-targeted-regeneration-and-masked-editing-mvp/10-MILESTONE-NOTES.md` - PreviewSpec targeting, child version lineage, and provider-off validation posture.
- `.planning/phases/11-reference-guided-generation-mvp/11-MILESTONE-NOTES.md` - reference trace handoff and concept-preview boundary.

### Core Contracts And Ledger

- `services/core/src/caragent_core/enums.py` - `ArtifactKind` and status enum patterns.
- `services/core/src/caragent_core/models.py` - `DesignVersion`, `Artifact`, and metadata surfaces.
- `services/core/src/caragent_core/services/jobs.py` - version/artifact/model-run creation and validation helpers.
- `services/core/src/caragent_core/storage.py` - object-key construction and storage write boundary.
- `services/core/src/caragent_core/generation/prompts.py` - current `PreviewSpec` construction.
- `services/core/src/caragent_core/generation/templates.py` - supported template and safe-zone registry.

### API And Contracts

- `services/api/src/caragent_api/config.py` - `V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED`.
- `services/api/src/caragent_api/schemas.py` - generated OpenAPI/Pydantic contract source.
- `services/api/src/caragent_api/routes/jobs.py` - version/artifact/export endpoints.
- `services/api/src/caragent_api/routes/generation.py` - selected version lineage and generation metadata patterns.
- `packages/contracts/openapi/openapi.json` - generated OpenAPI artifact.
- `packages/contracts/src/generated/client.ts` - generated TypeScript client.

### Web Workbench

- `apps/web/src/lib/config/public-env.ts` - public V2 3D feature flag.
- `apps/web/src/lib/workbench/store.ts` - preview transform and selected version state.
- `apps/web/src/components/workbench/preview-panel.tsx` - current 2D PreviewSpec parsing/rendering.
- `apps/web/src/components/workbench/workbench-app.tsx` - selected version/artifact wiring.
- `apps/web/src/app/page.test.tsx` - workbench flow fixtures and assertions.

### Existing Tests

- `services/core/tests/test_models.py`
- `services/core/tests/test_generation_jobs.py`
- `services/api/tests/test_jobs.py`
- `services/api/tests/test_generation.py`
- `apps/web/src/app/page.test.tsx`
- `apps/web/src/lib/workbench/store.test.ts`
</canonical_refs>

<specifics>
## Specific Ideas

- Add `caragent_core.preview3d` with Pydantic helpers such as `Preview3DSpec`, `Preview3DShell`, `Preview3DCameraPreset`, `Preview3DMaterialPlan`, `Preview3DWarning`, and `Preview3DScreenshotMetadata`.
- Use deterministic ids: `generic-side-coupe-lightweight-v1`, `front-left-default`, `side-decal-plane`.
- Expose readable metadata keys: `preview_3d`, `preview_3d_shell_id`, `preview_3d_warning_count`, `preview_3d_screenshot`, `camera_preset`, `non_production`.
- Add web helpers under `apps/web/src/lib/preview3d/` and components under `apps/web/src/components/workbench/`.
- Keep 2D and 3D controls stable when switching selected versions.
</specifics>

<deferred>
## Deferred Ideas

- Verified UV unwraps, production texture coordinates, GLB upload pipeline, shell authoring UI, and multi-template vehicle coverage are future work.
- Real generated raster image serving can be added if needed for richer texture mapping, but Phase 12 must still work from PreviewSpec and artifact metadata.
- Handoff package inclusion of 3D screenshots is implemented in Phase 13; Phase 12 only creates durable screenshot artifacts and metadata.
</deferred>

---

*Phase: 12-lightweight-3d-preview-mvp*
*Context gathered: 2026-06-18 via roadmap-auto-context*
