# Phase 27: View Truthfulness And Current Preview Repair - Context

**Gathered:** 2026-06-23
**Status:** Ready for planning
**Source:** v5 milestone requirement-completion discussion

<domain>
## Phase Boundary

Phase 27 fixes the current misleading preview/view behavior before deeper GR86/BRZ template work begins. The existing side/front/rear/top controls must reflect template capabilities instead of implying that generic side-view templates support all four views.

This phase does not create the GR86/BRZ package, import third-party templates, or implement sectioned GPT generation. It prepares the current UI and contracts so future multi-view templates can be represented truthfully.
</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- Keep the side/front/rear/top controls visible in the workbench.
- If a selected template or generated version does not provide a view, selecting that view must show `模板未提供该视图`.
- Do not synthesize fake front/rear/top previews from a side-only template.
- The selected template/version should expose available and missing views in a way that both preview UI and export warnings can consume.
- Existing side-only generic template behavior must remain usable for generation and review.

### the agent's Discretion
- The exact TypeScript shape for view capability metadata may be derived from the existing template and PreviewSpec contracts.
- The implementation may disable unavailable view buttons or keep them selectable with an empty-state panel, as long as the state is explicit and testable.
- Backend changes are optional if the frontend can derive view capability from existing API payloads; add backend fields only if the current payload cannot represent the state cleanly.
</decisions>

<canonical_refs>
## Canonical References

### Planning
- `.planning/ROADMAP.md` — Phase 27 goal and success criteria.
- `.planning/REQUIREMENTS.md` — VIEW-01 and VIEW-02 requirements.
- `.planning/PROJECT.md` — v5 scope boundaries and product decisions.

### Code Areas To Inspect
- `apps/web` — Workbench preview controls and 2D preview rendering.
- `packages` — generated API/client types used by the frontend.
- `services/core/src/caragent_core/generation/templates.py` — template registry/capability source if view metadata exists there.
- `services/api` — template catalog or artifact/version response fields if UI needs server-provided capabilities.
</canonical_refs>

<specifics>
## Specific Ideas

- The visible empty-state copy must include the exact text `模板未提供该视图`.
- Existing side-only templates should report side as available and front/rear/top as missing.
- A future GR86/BRZ template should be able to report all four views as available without UI changes.
- Tests should cover at least one side-only template and one multi-view fixture or mocked capability payload.
</specifics>

<deferred>
## Deferred Ideas

- GR86/BRZ maintained package implementation moves to Phase 28.
- Template management/import UI moves to Phase 29.
- Section-first workspace and flat panels move to Phase 31.
</deferred>

---

*Phase: 27-view-truthfulness-and-current-preview-repair*
*Context gathered: 2026-06-23 via milestone Q&A*
