---
phase: 13
slug: enhanced-concept-handoff-package-mvp
status: ready-for-planning
created: 2026-06-19
source: "auto context from ROADMAP/REQUIREMENTS/Phase 12 notes; user requested autonomous continuation"
requirements: [V2-HANDOFF-01, V2-HANDOFF-02, V2-HANDOFF-03, V2-HANDOFF-04, V2-HANDOFF-05]
---

# Phase 13: Enhanced Concept Handoff Package MVP - Context

<domain>
## Phase Boundary

Phase 13 turns the existing concept export record into a richer review package for a selected generated version. The package is still a concept handoff, not a production handoff. It must help a user or reviewer inspect what was generated, what inputs and warnings shaped it, and what cannot be assumed for print production.

This phase must preserve the v2 MVP boundary:

- Export a ZIP package for review.
- Include stable manifest JSON and readable notes.
- Include or reference the selected concept image.
- Include optional Phase 12 3D screenshots when screenshot artifacts exist.
- Include safe-zone/template/warning evidence from PreviewSpec and Preview3DSpec metadata.
- Include prompt/provider trace summary, reference asset manifest, rights/source snapshot, and review notes.
- Block export when required concept image or rights/source metadata is missing; warn when optional metadata such as 3D screenshots is absent.
- Do not claim print-ready scale, bleed, color profile, DPI, production UV accuracy, wrap-shop approval, PSD/AI/PDF source handoff, ordering, quoting, payment, or installer workflow.

</domain>

<decisions>
## Implementation Decisions

### Package Taxonomy

- Use a new explicit format value: `enhanced_concept_handoff_zip`.
- Keep existing `png`/`jpg` concept exports backward compatible.
- Use `schema_version: 1` for the package manifest and all nested package report sections.
- Use an immutable export artifact with `ArtifactKind.EXPORT` and content type `application/zip`.
- The export record continues to link to the selected version; package artifact id points at the ZIP artifact, while manifest source metadata points at the selected concept image artifact.

### Manifest And Notes

- Manifest JSON is the source of truth for package structure.
- Include readable Markdown notes in the ZIP as `handoff-notes.md`.
- Include warning report as both manifest data and `warnings.md`.
- Include reference asset manifest as both manifest data and `references.json`.
- Include prompt/provider trace as both manifest data and `prompt-trace.md`.
- Store only safe metadata in JSON: ids, object keys, content types, dimensions, checksums, prompt summaries, provider/model/cost/status, warning ids/messages, rights/source fields, and selected review notes.
- Never store image bytes, base64, secrets, local filesystem paths, env values, credentials, or raw provider payload secrets in manifest or notes.

### Asset Inclusion

- If object storage can read source bytes, include selected concept image bytes under `images/concept.<ext>`.
- Include optional 3D screenshot bytes under `screenshots/`.
- If a referenced optional artifact cannot be read, keep the package blocked for required concept image and warning-only for optional screenshots.
- Generate a safe-zone overlay report from existing PreviewSpec metadata even if the initial MVP renders it as Markdown/manifest data rather than a new bitmap overlay. If a deterministic overlay bitmap is implemented during execution, include it as `overlays/safe-zone-overlay.png`.

### Rights And Source Guardrails

- Required concept image artifact must belong to the selected version and workspace.
- Reference usage in version parameters must include a rights/source snapshot for every included reference asset id.
- Missing or rejected rights/source metadata blocks enhanced handoff package creation with a user-safe validation error.
- Optional missing metadata produces warnings when it does not undermine package integrity, for example no 3D screenshot artifacts.

### Workbench UX

- The workbench remains the first screen; do not add a landing page.
- Extend the existing export surface instead of creating a disconnected package page.
- Use compact operational controls and icon buttons where possible.
- Show package readiness, blocked reasons, warnings, included files, manifest preview, and export history.
- Keep visible text concise and Chinese-facing for the UI.
- Keep the concept-only disclaimer visible before and after export.

### the agent's Discretion

- The executor may choose the exact internal helper names if tests keep public contracts stable.
- The executor may decide whether package building happens directly in the API route or through a small core service helper. Prefer a core helper if it keeps manifest tests provider-free and easy to exercise.
- The executor may defer a true generated overlay bitmap if manifest/Markdown safe-zone evidence fully satisfies the phase success criteria and tests document the boundary.

</decisions>

<canonical_refs>
## Canonical References

Downstream agents MUST read these before planning or implementing.

### Product Scope

- `.planning/REQUIREMENTS.md` - V2-HANDOFF-01..05 and future production handoff exclusions.
- `.planning/ROADMAP.md` - Phase 13 success criteria, seven plan names, and V2 UAT path.
- `.planning/STATE.md` - recent Phase 11/12 decisions and active blockers.
- `.planning/phases/12-lightweight-3d-preview-mvp/12-MILESTONE-NOTES.md` - how Phase 13 should reuse screenshot artifacts and warning metadata.

### Existing Export And Ledger

- `services/core/src/caragent_core/models.py` - `ExportRecord`, `Artifact`, `DesignVersion`, `ModelRun`, and asset rights fields.
- `services/core/src/caragent_core/services/jobs.py` - `record_export`, `create_artifact`, list helpers, reference trace export merge.
- `services/api/src/caragent_api/routes/jobs.py` - version/artifact/model-run/export routes and 3D screenshot route pattern.
- `services/api/src/caragent_api/schemas.py` - `ExportCreateRequest`, `ExportResponse`, `ArtifactResponse`, and typed 3D screenshot schemas.

### Metadata Sources

- `services/core/src/caragent_core/references.py` - reference usage and rights/source trace metadata keys.
- `services/core/src/caragent_core/preview3d.py` - Preview3D warnings and screenshot metadata.
- `services/core/src/caragent_core/generation/templates.py` - template id, view, safe zones, and canvas metadata.
- `services/worker/src/caragent_worker/tasks/jobs.py` - prompt/model/provider trace and generated artifact metadata patterns.

### Web Surface

- `apps/web/src/components/workbench/export-panel.tsx` - existing export panel and manifest preview.
- `apps/web/src/components/workbench/workbench-app.tsx` - selected version/artifact, export submission, generation state, and history wiring.
- `apps/web/src/lib/api/iteration.ts` - current `createConceptExport` wrapper.
- `apps/web/src/app/page.test.tsx` - workbench fixture and export UX tests.

</canonical_refs>

<specifics>
## Specific Ideas

- Manifest top-level keys should include: `schema_version`, `package_type`, `created_at`, `workspace_id`, `version_id`, `source_artifact`, `package_artifact`, `files`, `template`, `preview_spec`, `preview_3d`, `warnings`, `prompt_trace`, `provider_trace`, `references`, `review_notes`, `disclaimer`.
- Stable package file names should be deterministic enough for tests:
  - `manifest.json`
  - `handoff-notes.md`
  - `warnings.md`
  - `prompt-trace.md`
  - `references.json`
  - `images/concept.<ext>`
  - `screenshots/<artifact-id>.<ext>` when screenshots exist
  - optional `overlays/safe-zone-overlay.png`
- API should return 403 when `V2_ENHANCED_HANDOFF_PACKAGE_ENABLED` is disabled.
- UI should disable/enforce enhanced package action when the browser public flag is off, while still showing existing PNG/JPG concept export behavior.
- Use exact visible UI labels that tests can find: `交接包`, `生成交接包`, `交接包预览`, `概念交接包，仅供评审`, `缺少版权或来源信息`, `ZIP`.

</specifics>

<deferred>
## Deferred Ideas

- Full print-ready PSD/AI/PDF handoff.
- Verified production scale, bleed, color profile, DPI, and installer notes.
- Vehicle-specific production UV package validation.
- Ordering, quoting, payment, marketplace, collaboration, or installer workflow.
- Legal-grade automated copyright/license verification.
- Broad 3D shell library or print-shop approval evidence.

</deferred>

---

*Phase: 13-enhanced-concept-handoff-package-mvp*
*Context gathered: 2026-06-19 via autonomous GSD continuation*
