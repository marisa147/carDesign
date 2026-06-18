# Phase 6: Itasha And Template Intelligence - Context

**Gathered:** 2026-06-18
**Status:** Ready for UI design and planning
**Mode:** Auto-selected defaults from `$gsd-progress --next` because the user requested autonomous GSD continuation.

<domain>
## Phase Boundary

Phase 6 adds itasha-specific controls and template-aware quality signals on top of the verified Phase 5 workbench. Users should be able to choose domain-oriented design intent, see deterministic text/logo overlay support where possible, get lightweight warnings, view basic safe-zone/panel overlays for the supported template, and inspect stored preview-spec data that can later feed a true 3D renderer.

This phase does not implement broad vehicle-template libraries, production print preflight, layered PSD/AI/PDF handoff, true UV-mapped 3D, automatic mask/inpainting, LoRA training, marketplace/community flows, or provider operations. The output remains a concept preview unless a later phase explicitly implements production validation.

</domain>

<decisions>
## Implementation Decisions

### Itasha Controls
- **D-01:** Add a small, explicit set of itasha-oriented fields rather than a broad preset library: character focus, supporting graphics, racing/JDM cues, typography intent, and color harmony.
- **D-02:** These controls should extend the existing structured brief/parameter workflow and prompt payload. They should not create a new wizard, landing page, or separate editor.
- **D-03:** Defaults should preserve the current local deterministic path: if a user does nothing, existing Phase 3-5 generation still works.

### Deterministic Text And Logo Overlays
- **D-04:** Treat exact text/logo rendering as deterministic preview layers where possible, not as a claim that the AI raster generated perfect text.
- **D-05:** Phase 6 should record overlay intent/spec separately from the base generated artifact. A planner may bake a preview composite artifact only if it remains labeled as concept preview.
- **D-06:** Uploaded logos must continue to respect asset rights/source status. Missing-rights assets stay blocked from generation/overlay use.

### Warnings And Quality Signals
- **D-07:** Add lightweight rule-based warnings for low resolution, unsupported or normalized template/view, unreadable text risk, face/text near risky vehicle zones, and uncertain/missing rights metadata.
- **D-08:** Warnings are visible and durable, but mostly non-blocking. Rights violations remain blocking because Phase 2 already made rights/source confirmation a hard gate.
- **D-09:** Warning copy should be concise and operational, not a tutorial. It should tell the user what is risky and what to adjust.

### Template And Safe-Zone Scope
- **D-10:** Keep Phase 6 to the current supported `generic-side-coupe` / `side` template first.
- **D-11:** Safe-zone overlays should be data-driven rectangles/polygons for broad panel zones such as door, hood/roof-equivalent side surface, wheel arches, windows, and risky trim edges. They are concept guidance, not installer-accurate templates.
- **D-12:** Unsupported templates/views should keep normalizing to the supported template/view with warnings instead of pretending broad template support exists.

### PreviewSpec Contract
- **D-13:** Store renderer-neutral preview-spec data in existing version parameters, artifact metadata, or brief payload fields before adding new core job APIs.
- **D-14:** The preview spec should include canvas size, template id/view, safe-zone data, overlay layer descriptors, warning ids/messages, and source artifact/version references.
- **D-15:** The preview spec must be readable through existing API responses so frontend and future 3D work can consume it without changing the core design/job route shape.

### Workbench Integration
- **D-16:** Integrate Phase 6 into the existing workbench: parameter panel for controls, preview panel for overlay/safe-zone toggles, and comparison/export surfaces for manifest/spec visibility.
- **D-17:** Maintain the quiet operational layout from Phases 4-5. No nested cards, hero surfaces, or marketing copy.
- **D-18:** Mobile must remain single-column with no horizontal document scroll at 390px and ideally 320px.

### the agent's Discretion
- Exact field names, storage location among existing JSON fields, safe-zone geometry format, whether overlays render via HTML/SVG/canvas/Konva/PIL, and exact warning thresholds are implementation details for research/planning as long as QUAL-01 through QUAL-05 are satisfied and evidence is recorded.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product Scope
- `.planning/ROADMAP.md` - Phase 6 goal, QUAL-01 through QUAL-05 success criteria, and later phase boundaries.
- `.planning/REQUIREMENTS.md` - Quality/itasha requirements and v2 production/3D deferrals.
- `.planning/PROJECT.md` - Product context, seed references, constraints, and expected user experience.
- `init.MD` - Original module, workflow, UI/UX, risk, and 2D/3D preview direction.
- `UI.png` - Visual blueprint for the workbench, preview, parameter, material, and export surfaces.

### Prior Phase Decisions
- `.planning/phases/05-iteration-feedback-and-concept-export/05-CONTEXT.md` - Phase 5 selected-version, concept-preview, export, and non-production decisions.
- `.planning/phases/05-iteration-feedback-and-concept-export/05-UI-SPEC.md` - Current workbench UI contract for iteration, feedback, comparison, export, and future gates.
- `.planning/phases/05-iteration-feedback-and-concept-export/05-VERIFICATION.md` - Verified live API/worker/browser behavior that Phase 6 must preserve.
- `.planning/phases/04-workbench-ui-integration/04-CONTEXT.md` - Workbench state, layout, canonical backend state, and future-gate decisions.
- `.planning/phases/04-workbench-ui-integration/04-UI-SPEC.md` - Existing visual/layout contract for the base workbench.

### Current Implementation
- `services/core/src/caragent_core/generation/briefs.py` - Structured brief payload fields and warning list.
- `services/core/src/caragent_core/generation/templates.py` - Current supported template/view, canvas size, and normalization warnings.
- `services/core/src/caragent_core/generation/prompts.py` - Prompt payload and prompt text construction from brief fields.
- `services/worker/src/caragent_worker/providers/local.py` - Deterministic local rendering path and PIL-based concept preview generation.
- `services/worker/src/caragent_worker/tasks/jobs.py` - Worker creation of design versions/artifacts and Phase 5 iteration metadata handling.
- `services/api/src/caragent_api/schemas.py` - Existing OpenAPI response/request schema surface for brief, version, artifact, and metadata-bearing records.
- `apps/web/src/components/workbench/parameter-panel.tsx` - Existing parameter editor and warning rendering.
- `apps/web/src/components/workbench/preview-panel.tsx` - Existing 2D preview, version selection, zoom, and view controls.
- `apps/web/src/components/workbench/export-panel.tsx` - Existing concept manifest preview and not-print-ready boundary.
- `apps/web/src/components/workbench/workbench-app.tsx` - Existing workbench composition and canonical state loading.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `GenerationBriefPayload` already includes `style`, `palette`, `text`, `coverage`, `reference_asset_ids`, `warnings`, `vehicle_template_id`, `view`, and canvas dimensions. Phase 6 can extend this schema for itasha-specific controls and preview-spec data.
- `resolve_vehicle_template()` already normalizes unsupported templates/views and emits warnings. Phase 6 can evolve this into data-backed safe-zone/template metadata.
- `build_prompt_plan()` already preserves prompt payload JSON. Phase 6 can add itasha control values, overlay intent, warnings, and preview-spec references there.
- `LocalDeterministicImageProvider` already uses PIL and prompt payload metadata. It is a practical place to prototype deterministic concept-preview overlays without hosted provider calls.
- `ParameterPanel` already edits structured fields and renders warnings. It can host the first itasha controls without changing the workbench shell.
- `PreviewPanel` already owns selected version/artifact context, zoom, and view controls. It can host overlay and safe-zone toggles.

### Established Patterns
- Backend-owned durable state is canonical; frontend local state handles only selected version/view/zoom and transient form controls.
- OpenAPI generated contracts are the frontend/backend boundary.
- Future production/3D/business capabilities are visibly deferred rather than silently implied.
- Browser UAT must check desktop and mobile layouts for no horizontal overflow and no fresh console errors.

### Integration Points
- Extend generation brief schemas and API create/update payloads for itasha controls and preview-spec metadata.
- Add template/safe-zone data to the core generation/template module and expose it through prompt/version/artifact metadata.
- Add rule-based warning generation to the brief/template/prompt path and render warnings in parameter/preview surfaces.
- Add deterministic overlay rendering to the preview surface and optionally to local deterministic worker output as concept-preview composition.
- Refresh OpenAPI/contracts and update frontend wrappers/tests after schema changes.

</code_context>

<specifics>
## Specific Ideas

- Add compact controls labeled for character focus, supporting graphics, racing/JDM cues, typography intent, and color harmony.
- Add preview toggles for `安全区` and `文字/Logo 图层` near the existing preview controls.
- Show warnings as short chips or rows near parameters/preview, reusing warning colors already present in the design system.
- Represent safe zones as concept guidance for the generic side coupe: doors/body side, windows, wheel arches, trim/risky edge zones.
- Preserve export copy: overlays/specs can appear in the manifest, but output is still a concept preview and not print-ready.

</specifics>

<deferred>
## Deferred Ideas

- Accurate vehicle-specific wrap templates, UV maps, production scale/bleed/DPI, layered source packages, and installer proofing remain v2+ production handoff scope.
- True Three.js/React Three Fiber 3D preview and UV material assignment remain future scope after the renderer-neutral preview spec stabilizes.
- Mask/inpainting, ControlNet/IP-Adapter, LoRA training, multi-view consistency, and provider orchestration remain advanced generation scope.
- Broad licensed vehicle-template/character-asset libraries, marketplace/community, and commercial quote/order/payment flows remain later scope.

</deferred>

---

*Phase: 06-itasha-and-template-intelligence*
*Context gathered: 2026-06-18*
