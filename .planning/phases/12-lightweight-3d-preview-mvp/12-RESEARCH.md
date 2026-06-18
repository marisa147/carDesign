---
phase: 12
slug: lightweight-3d-preview-mvp
status: complete
created: 2026-06-18
---

# Phase 12 Research

## Current Repo Evidence

| Area | Finding | Implication |
|------|---------|-------------|
| 3D dependencies | `apps/web/package.json` has no `three`, `@react-three/fiber`, or Playwright dependency. | Viewer work must explicitly add and test any 3D/browser verification dependency. |
| Feature flags | API, worker, and public web env already define `V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED`. | The 3D surface can be independently disabled. |
| Preview source | `PreviewPanel` reads `DesignVersion.parameters.preview_spec` and renders CSS/SVG-like 2D shell, safe zones, and overlay layers. | Phase 12 should extend this data path before introducing new renderer state. |
| Artifacts | `ArtifactKind` includes `preview` and generated image kinds; artifact rows carry `version_id`, dimensions, content type, object key, and metadata. | Screenshot artifacts can reuse the existing ledger, possibly with a new specific kind. |
| Storage | `ObjectStorage` only defines `put_object`. API currently has upload/write behavior but no object read/download route. | 3D texture MVP should not depend on direct object reads unless a controlled API surface is added. |
| Contracts | TypeScript client is generated from FastAPI/Pydantic OpenAPI. | Any screenshot-create endpoint or typed Preview3D response must go through contracts check. |
| Validation | Prior V2 phases use focused pytest/Vitest plus contracts and aggregate validation. | Phase 12 should keep provider-off validation and add browser visual proof. |

## Recommended Architecture

Phase 12 should add a narrow `Preview3DSpec` adapter layer:

1. Read selected version `preview_spec` and selected artifact metadata.
2. Resolve a compatible shell from a small registry.
3. Build `Preview3DSpec` with camera preset, material plan, safe-zone projection metadata, and warnings.
4. Render the spec with a client-only Three.js viewer.
5. Capture screenshots through the viewer canvas and persist them as artifacts linked to the same version.

The core contract stays independent of Three.js. Three.js-specific objects remain in frontend renderer code.

## Preview3DSpec Shape

Candidate stable JSON keys:

- `schema_version: 1`
- `mode: "lightweight_shell"`
- `source`: `workspace_id`, `version_id`, `artifact_id`, `artifact_object_key`, `preview_spec_template_id`, `preview_spec_view`
- `compatibility`: `status`, `shell_id`, `reason`
- `shell`: `id`, `label`, `template_id`, `dimensions`, `material_slots`
- `camera`: `preset_id`, `position`, `target`, `zoom`, `limits`
- `materials`: `decal_strategy`, `source_kind`, `safe_zone_overlays`, `overlay_layers`
- `warnings`: list of `id`, `severity`, `message`
- `created_at` or caller-provided timestamp only where deterministic tests can control it

## Shell Fixture Strategy

Use one first-party fixture:

- `generic-side-coupe-lightweight-v1`
- Compatible with `generic-side-coupe` and side view.
- Simple hull, cabin, wheel, and side-decal plane generated in frontend geometry code.
- Safe zones and overlay layers are projected to the side decal plane using normalized `PreviewSpec.canvas` coordinates.
- The shell metadata lives in core/web helpers, not a hidden binary asset, so tests can inspect it.

This is less realistic than a GLB, but it is controllable, testable, and honest about non-production accuracy.

## Frontend Rendering Strategy

- Add `three` as the minimal runtime dependency.
- Create a client-only viewer component with `useEffect`, a canvas ref, and cleanup of renderer, scene, controls/listeners, and animation frame.
- Use icon buttons for rotate/zoom/reset/capture. Keep text labels short and accessible.
- Expose a deterministic no-WebGL/fallback branch for tests and unsupported browsers.
- Add canvas-pixel checks in browser verification so a nonblank scene is proven instead of only testing DOM labels.

## Screenshot Persistence Strategy

The browser can submit a PNG data URL or blob produced from the canvas. The API should:

- Require the V2 3D feature flag.
- Require a workspace/version relationship.
- Validate PNG/WebP content type and bounded byte size.
- Store bytes through `ObjectStorage.put_object`.
- Create an immutable artifact linked to the version.
- Record `preview_3d_screenshot` metadata with shell id, camera, warning ids, and source artifact id.

## Risks And Mitigations

| Risk | Mitigation |
|------|------------|
| Users read the viewer as production-ready UV proof | Persistent non-production labels in UI and metadata; docs repeat concept-only scope. |
| WebGL scene renders blank in some browsers | Browser screenshot plus canvas-pixel checks; fallback state remains 2D. |
| 3D dependency breaks SSR/tests | Dynamic/client-only loading and testable pure spec helpers. |
| Scope expands into GLB/UV tooling | One shell fixture, no shell upload, no print-ready claims. |
| Screenshot endpoint becomes arbitrary binary upload | Restrict content type, size, workspace/version linkage, and metadata shape. |

## Validation Matrix

| Requirement | Validation |
|-------------|------------|
| V2-3D-01 | Core shell registry tests and Preview3DSpec compatibility tests. |
| V2-3D-02 | Web workbench tests for 3D tab/panel on selected version. |
| V2-3D-03 | Web tests for rotate/zoom/reset/capture controls plus browser canvas proof. |
| V2-3D-04 | API/core tests for screenshot artifact metadata and contracts. |
| V2-3D-05 | Web tests for incompatible template fallback and 2D continuity. |

## RESEARCH COMPLETE
