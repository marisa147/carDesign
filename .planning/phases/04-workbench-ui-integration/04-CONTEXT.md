# Phase 4: Workbench UI Integration - Context

**Gathered:** 2026-06-17
**Status:** Ready for UI design and planning
**Mode:** Auto-selected defaults from `$gsd-progress --next` because the user requested autonomous GSD continuation.

<domain>
## Phase Boundary

Phase 4 turns the Phase 1-3 proof page into a usable MVP workbench connected to canonical backend state. The user should be able to work in one screen with chat, structured parameters, reference assets, generation progress, 2D preview, version history, and explicit future-feature gates.

This phase does not implement production-ready wrap export, true UV-mapped 3D, marketplace flows, billing, auth, hosted provider operations, rich mask/inpainting controls, or advanced multi-agent orchestration. Those remain later phases or v2+ scope.

</domain>

<decisions>
## Implementation Decisions

### Workbench Layout
- **D-01:** Replace the proof-first landing shell with a dense application workbench as the first screen. No marketing hero or explanatory landing page.
- **D-02:** Use a three-zone desktop layout: left GPT-style chat rail, center 2D preview/progress workspace, right parameter/assets/history rail. On narrower screens, stack the zones with the same interaction order: chat, preview, parameters.
- **D-03:** Keep controls compact and operational. This product is a workbench, not a marketing site; avoid oversized hero typography, nested cards, decorative gradients, and purely illustrative UI.

### Server State And Local UI State
- **D-04:** Treat PostgreSQL/API responses as canonical for workspaces, messages, briefs, assets, jobs, events, artifacts, and versions. Browser storage may keep only resume identifiers and safe UI preferences.
- **D-05:** Use TanStack Query for server-state reads/mutations and invalidation. Do not model durable server data as local-only React state.
- **D-06:** Use a small client-state store for synchronous workbench UI state such as selected tab, selected version, selected view, preview zoom, preview pan, and panel collapse state. Follow the planned stack preference for Zustand if dependency installation is available; otherwise keep the store boundary isolated so Zustand can be added without rewiring API code.

### Chat And Brief Flow
- **D-07:** The chat panel uses durable workspace messages. User submissions create a user message, then create or update a structured generation brief from the message text.
- **D-08:** Assistant/system feedback in Phase 4 can be deterministic UI feedback from existing API/job state, such as "brief parsed", "job queued", "artifact ready", or "generation failed". Do not imply live LLM streaming chat until a later AI orchestration phase exists.
- **D-09:** Follow-up commands should reuse the current workspace and current brief where possible. The first implementation can treat follow-ups as new user messages plus a refreshed brief, not full semantic edit orchestration.

### Parameters And Assets
- **D-10:** The parameter rail exposes the Phase 3 structured brief fields that already exist: vehicle template/view, character/theme, style, palette, text, coverage, reference asset ids, warnings, and canvas dimensions.
- **D-11:** Parameter edits call the existing generation brief update route and then refresh the same canonical state. Edits must not submit generation automatically; the user explicitly starts generation.
- **D-12:** The asset panel connects to Phase 2 upload/list/rights routes. Reference assets must show source/rights status, and assets with missing rights should be visibly blocked from generation use.
- **D-13:** Upload UI should support image/reference/logo/car-photo style use cases as metadata labels, but Phase 4 does not need advanced thumbnail generation beyond what the backend already exposes.

### Progress, Preview, And History
- **D-14:** Generation progress is shown from durable job status plus recent job events. Queued, running, succeeded, failed, and retryable states must be distinct.
- **D-15:** Preview is 2D-first. Show selected generated image artifacts and design versions when present; show a template-aware empty state before generation.
- **D-16:** Preview controls include zoom, pan/reset, thumbnail history, and supported view switching. True 3D rotation is a disabled/experimental gate, not a silently available feature.
- **D-17:** Version history is driven by design version rows and artifact links. Selecting a version changes preview context without destroying chat, parameters, or job history.

### Future-Feature Gates
- **D-18:** True 3D, print-ready export, marketplace/community, payment/order, broad licensed libraries, and production handoff must be visible only as disabled, experimental, or deferred capabilities.
- **D-19:** Disabled controls need short, honest labels. They should not look broken and should not route to empty pages.

### the agent's Discretion
- Exact component decomposition, query key names, polling interval, copy phrasing, icon choices, and responsive breakpoint tuning are implementation details as long as the resulting workbench satisfies UI-01 through UI-07 and remains consistent with the existing design system.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product Scope
- `.planning/ROADMAP.md` - Phase 4 goal, UI-01 through UI-07 success criteria, and later-phase boundaries.
- `.planning/REQUIREMENTS.md` - Pending UI requirements and traceability table.
- `.planning/PROJECT.md` - Product context, seed material references, constraints, and expected user experience.
- `init.MD` - Original module, workflow, UI/UX, and technical stack direction.
- `UI.png` - Visual blueprint for left chat, right preview, parameters, assets, history, and toolbar layout.

### Current Implementation
- `docs/development.md` - Current runbook and explicit Phase 3 boundary.
- `apps/web/src/app/page.tsx` - Existing proof page to evolve or split into workbench components.
- `apps/web/src/app/page.test.tsx` - Existing web test style and fixture coverage.
- `apps/web/src/lib/api/workspaces.ts` - Workspace/message generated-contract wrapper pattern.
- `apps/web/src/lib/api/jobs.ts` - Job/event wrapper pattern.
- `apps/web/src/lib/api/generation.ts` - Generation brief/job/artifact/version wrapper pattern.
- `services/api/src/caragent_api/routes/assets.py` - Upload/list/rights API surface that Phase 4 should expose in the web workbench.

### Library Guidance
- TanStack Query v5 docs - Server state, mutations, and invalidation should manage API-backed state.
- Zustand v5 docs - Local synchronous UI state can use typed stores and optional persistence for safe UI preferences.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `apps/web/src/components/ui/button.tsx`, `card.tsx`, `badge.tsx`, and `alert.tsx` define the current small design-system surface.
- `apps/web/src/lib/api/workspaces.ts`, `jobs.ts`, and `generation.ts` show the wrapper style for generated contract URLs and typed responses.
- `apps/web/src/app/page.test.tsx` already has durable-state and generation fixtures that can seed Phase 4 workbench tests.

### Established Patterns
- Web code is a client-side Next.js screen that currently uses generated `@caragent/contracts` types and plain React state.
- API wrappers accept optional `apiBaseUrl`, `fetch`, and `signal`, which keeps unit tests deterministic.
- Browser storage is currently limited to workspace IDs, job IDs, and idempotency keys. Keep that boundary strict.

### Integration Points
- Add an asset API wrapper for upload/list/get/update-rights routes.
- Add a Query provider and workbench query/mutation hooks around existing API wrappers.
- Split the large proof page into focused workbench components once tests define the target behavior.
- Keep generated contract consumption in `apps/web` only; do not import Python/backend internals into frontend code.

</code_context>

<specifics>
## Specific Ideas

- Use `UI.png` as the visual direction: left chat, central/right preview, tabs for 2D rendering, 3D model, parameter adjustment, and material library, plus a lower history strip.
- Preserve the current local mode status and API base URL visibility, but move them into a compact status area instead of the page being primarily a foundation proof.
- The first useful generation loop should feel like: create/resume workspace -> type prompt in chat -> inspect structured brief -> optionally upload/reference assets -> submit generation -> watch status/events -> inspect generated artifact/version -> select history item.

</specifics>

<deferred>
## Deferred Ideas

- True Three.js / React Three Fiber vehicle preview with UV mapping remains later scope.
- Production export packages and print preflight remain Phase 5+ or v2+ scope.
- Advanced mask/inpainting, multi-view consistency, and ControlNet/IP-Adapter-style controls remain Phase 6+ or v2+ scope.
- Auth, billing, provider operations, quotas, and marketplace/community features remain later scope.

</deferred>

---

*Phase: 04-workbench-ui-integration*
*Context gathered: 2026-06-17*
