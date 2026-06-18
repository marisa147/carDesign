# Phase 4: Workbench UI Integration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `04-CONTEXT.md` -- this log preserves the alternatives considered.

**Date:** 2026-06-17
**Phase:** 4 - Workbench UI Integration
**Mode:** Auto-selected defaults because the user requested `$gsd-progress --next` autonomous continuation without confirmation prompts.
**Areas discussed:** Workbench layout, state ownership, chat flow, parameters/assets, progress/preview/history, future-feature gates.

---

## Workbench Layout

| Option | Description | Selected |
|--------|-------------|----------|
| Dense single-screen workbench | Left chat, center preview/progress, right parameters/assets/history using the UI.png direction. | yes |
| Multi-page navigation | Separate pages for chat, assets, preview, and history. | |
| Keep proof-page cards | Continue extending the Phase 1-3 proof page. | |

**Auto choice:** Dense single-screen workbench.
**Notes:** Phase 4 is the point where the product stops being a proof shell and starts behaving like the intended workbench.

---

## State Ownership

| Option | Description | Selected |
|--------|-------------|----------|
| API-backed server state via TanStack Query | Canonical state from backend, mutation invalidation after writes. | yes |
| Browser-local state for everything | Faster to prototype but contradicts durable-state requirements. | |
| Mixed ad hoc React state | Minimal dependency change but easy to blur server/local ownership. | |

**Auto choice:** API-backed server state plus isolated local UI state.
**Notes:** TanStack Query documentation and project conventions both separate server state from local client-only state.

---

## Chat Flow

| Option | Description | Selected |
|--------|-------------|----------|
| Durable workspace messages with deterministic assistant feedback | Fits existing workspace/message/job APIs and avoids implying live LLM chat. | yes |
| Full streaming LLM chat | Product direction later, but not supported by current backend contracts. | |
| Textarea-only brief form | Too small for UI-01 and loses the GPT-style requirement. | |

**Auto choice:** Durable messages plus deterministic assistant/system feedback.
**Notes:** Follow-up commands can create new messages and refresh briefs without full semantic edit orchestration.

---

## Parameters And Assets

| Option | Description | Selected |
|--------|-------------|----------|
| Compact editable rail | Dedicated panel for structured brief fields and reference asset rights/status. | yes |
| Modal-heavy editing | Keeps page simpler but slows repeated workbench use. | |
| Defer uploads | Would miss UI-03 and undercut the workbench goal. | |

**Auto choice:** Compact editable parameter/assets rail.
**Notes:** Asset rights must be visible; missing rights should block generation use.

---

## Progress, Preview, And History

| Option | Description | Selected |
|--------|-------------|----------|
| 2D-first preview workspace | Show generated image artifacts, zoom/pan/reset, view switch, and version thumbnails. | yes |
| True 3D preview now | Attractive, but out of Phase 4 because verified UV/Three.js scope is later. | |
| Metrics-only proof | Existing proof behavior, insufficient for UI-04 through UI-06. | |

**Auto choice:** 2D-first preview with history and event-driven progress.
**Notes:** 3D is visible only as disabled/experimental future capability.

---

## Future-Feature Gates

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit disabled/deferred controls | Honest about true 3D, export, marketplace, and production handoff. | yes |
| Hide future capabilities entirely | Safer but does not satisfy UI-07. | |
| Leave controls active but empty | Misleading and likely to fail UAT. | |

**Auto choice:** Explicit disabled/deferred controls.
**Notes:** Controls should look intentional, not broken.

---

## the agent's Discretion

- Component boundaries, hook names, query key names, polling interval, exact Chinese copy, and responsive breakpoint values.

## Deferred Ideas

- True 3D vehicle preview.
- Print-ready export and production handoff.
- Marketplace/community, auth, billing, quotas, and provider-ops surfaces.
