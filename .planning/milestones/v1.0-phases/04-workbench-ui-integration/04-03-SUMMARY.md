---
phase: 04-workbench-ui-integration
plan: "03"
subsystem: web-workbench-chat
tags: [nextjs, react, chat, tanstack-query, brief]

requires:
  - plan: "04-01"
    provides: typed workspace/generation API wrappers and query keys
  - plan: "04-02"
    provides: workbench shell with chat region
provides:
  - GPT-style chat panel
  - durable workspace message creation from chat submit
  - structured generation brief creation with source_message_id
  - API-backed workspace/message/brief resume flow
affects: [phase-04-parameters, phase-04-progress-preview-history]

tech-stack:
  patterns:
    - `ChatPanel` is presentational and receives durable state from `WorkbenchApp`
    - `WorkbenchApp` owns workspace/message/brief orchestration and query cache updates
    - browser storage stores only safe resume identifiers: workspace id and latest brief id

key-files:
  created:
    - apps/web/src/components/workbench/chat-panel.tsx
  modified:
    - apps/web/src/components/workbench/workbench-app.tsx
    - apps/web/src/app/page.test.tsx

key-decisions:
  - "Chat submit creates a workspace only when needed, then creates a user message and a generation brief."
  - "Chat submit does not submit a generation job; generation remains an explicit downstream action."
  - "System feedback is deterministic copy: `结构化 brief 已保存`, not simulated streaming AI behavior."
  - "Refresh/resume refetches workspace messages and briefs from API routes instead of storing chat payloads in localStorage."

patterns-established:
  - "Workbench resume keys use `caragent.workbench.workspaceId` and `caragent.workbench.briefId`."
  - "Phase 4 UI tests assert route-level request bodies for workbench workflows."

requirements-completed:
  - UI-01
  - UI-02
  - UI-04

duration: 20 min
completed: 2026-06-17
---

# Phase 4 Plan 03: Chat-to-Brief Summary

**The workbench chat panel now persists user prompts as durable messages and creates structured generation briefs.**

## Accomplishments

- Added `ChatPanel` with message rendering, composer, pending state, error state, and deterministic system feedback.
- Wired `WorkbenchApp` to create a workspace on first chat submit, then create a durable user message and generation brief.
- Stored only `workspaceId` and latest `briefId` in localStorage for safe resume.
- Added remount/resume behavior that refetches workspace, messages, and briefs through the typed API wrappers.
- Updated page tests to prove chat submit request order, payload shape, no implicit generation job submit, and API-backed resume.

## Deviations from Plan

- None. The plan explicitly keeps generation job submission out of chat submit.

## Issues Encountered

- The first sandboxed Vitest run failed with the known Windows `spawn EPERM` esbuild issue; the same command passed through the approved escalated path.
- Typecheck caught test fixture drift: `GenerationBriefPayload.character_theme` and `style` require strings.
- The current TS lib target does not include `Array.prototype.toSorted`, so resume brief sorting uses a copied array plus `sort`.
- ESLint's React hooks rule flagged synchronous loading-state updates inside an effect; the loading transition now runs after the effect body.

## Verification

- RED: `corepack pnpm --filter @caragent/web test -- page.test.tsx` failed because the workbench did not render persisted chat messages or `结构化 brief 已保存`.
- GREEN: `corepack pnpm --filter @caragent/web test -- page.test.tsx` passed, 6 files / 22 tests.
- `corepack pnpm --filter @caragent/web typecheck` passed.
- `corepack pnpm --filter @caragent/web lint` passed.

## Next Plan Readiness

Ready for `04-04`: the current brief is now available in `WorkbenchApp` and can be surfaced in the structured parameter panel.
