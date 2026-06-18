---
phase: 09-hosted-provider-rollout-mvp
plan: "06"
subsystem: workbench-provider-selector
tags: [workbench, provider-selection, hosted-warning, quota, cost, diagnostics]

requires:
  - phase: 09-hosted-provider-rollout-mvp
    provides: safe operations provider status, provider intent persistence, and failure diagnostics from 09-03..09-05
provides:
  - Workbench provider selector for local deterministic and BFL hosted modes
  - Browser-safe operations status normalization for provider capability, guard, cost, and recent failures
  - Hosted child-iteration payload intent with provider/model fields only when selected provider is enabled
affects:
  - phase-09-hosted-provider
  - workbench-generation-flow
  - operations-diagnostics

tech-stack:
  added: []
  patterns:
    - normalize provider operations status into a browser-safe view model before rendering
    - keep local deterministic provider as default and fallback browser selection
    - submit provider/model intent only from enabled hosted selector options

key-files:
  created:
    - .planning/phases/09-hosted-provider-rollout-mvp/09-06-SUMMARY.md
  modified:
    - apps/web/src/components/workbench/workbench-app.tsx
    - apps/web/src/components/workbench/parameter-panel.tsx
    - apps/web/src/components/workbench/progress-panel.tsx
    - apps/web/src/lib/api/generation.ts
    - apps/web/src/lib/api/operations.ts
    - apps/web/src/app/page.test.tsx
    - apps/web/src/lib/api/generation.test.ts
    - apps/web/src/lib/api/operations.test.ts
    - apps/web/src/lib/config/public-env.test.ts

key-decisions:
  - "Keep the selector in the existing parameter panel instead of creating a separate provider/admin page."
  - "Treat local deterministic as always available; blocked or unrefreshed hosted state cannot prevent local iteration submit."
  - "Map raw blocked reasons such as API key configuration names into safe user-facing Chinese labels before rendering."
  - "Do not send estimated_cost from the browser; API/worker guardrails remain authoritative."

patterns-established:
  - "`normalizeProviderStatus` is the shared web boundary for safe provider capability, guard, cost, and recent failure display."
  - "`buildProviderIntentPayload` returns no provider fields for local/disabled selections and provider/model fields for enabled hosted selections."
  - "Progress and parameter surfaces reuse sanitized provider diagnostics instead of rendering raw operations strings."

requirements-supported:
  - V2-PROVIDER-02
  - V2-PROVIDER-04
  - V2-PROVIDER-05

duration: 20 min
completed: 2026-06-18
---

# Phase 9 Plan 06: Workbench Provider Selector Summary

**The workbench now exposes local vs. hosted provider choice with safe blocked-state, cost, quota, and failure visibility.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-06-18T09:04:22Z
- **Completed:** 2026-06-18T09:24:14Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- Added red web tests for provider status normalization, local default payloads, enabled hosted payloads, blocked hosted UI state, quota/cost labels, concept-preview labeling, and diagnostic sanitization.
- Added `normalizeProviderStatus` and provider option helpers so browser UI uses safe capability, guard, cost, and recent failure fields.
- Added provider intent payload builders that omit provider/model fields for local or disabled selections and include provider/model only for enabled hosted selections.
- Added a compact provider selector to the workbench parameter panel with local and BFL options, BFL blocked reasons, quota/rate/cost visibility, and concept-preview labeling.
- Wired selected hosted provider intent into child-iteration submit while preserving local deterministic default behavior.
- Updated progress diagnostics to use sanitized provider guard and recent failure summaries.
- Fixed an existing frontend lint naming issue in `public-env.test.ts` so web lint passes cleanly.

## Task Commits

1. **Tasks 1-3: Provider selector tests, API helpers, and workbench UI integration** - `02b12da` (feat)

## Files Created/Modified

- `apps/web/src/lib/api/operations.ts` - Browser-safe provider status view model and diagnostic sanitization.
- `apps/web/src/lib/api/generation.ts` - Provider intent payload builders for local/default and hosted selections.
- `apps/web/src/components/workbench/parameter-panel.tsx` - Compact provider selector, hosted blocked reasons, and cost/quota visibility.
- `apps/web/src/components/workbench/workbench-app.tsx` - Provider selection state and hosted child-iteration payload wiring.
- `apps/web/src/components/workbench/progress-panel.tsx` - Sanitized provider guard and recent failure display.
- `apps/web/src/app/page.test.tsx` - Workbench selector, blocked hosted, hosted payload, and diagnostics tests.
- `apps/web/src/lib/api/generation.test.ts` - Provider intent payload tests.
- `apps/web/src/lib/api/operations.test.ts` - Provider status normalization tests.
- `apps/web/src/lib/config/public-env.test.ts` - Lint-safe dynamic import variable name.

## Decisions Made

- Keep selector placement in the parameter panel because provider choice is part of generation/iteration setup.
- Keep BFL cost and quota visible even while local remains selected, so users can see hosted spend boundaries before switching.
- Preserve server-side enforcement: frontend disables obvious blocked hosted choices, but API and worker remain authoritative.
- Sanitize raw operations blocked reasons into user-facing labels before display.

## Deviations from Plan

- Added a small lint-only rename in `public-env.test.ts` after `corepack pnpm --filter @caragent/web lint` surfaced an existing Next rule violation.

## Issues Encountered

- Initial sandboxed Vitest run failed with Windows `spawn EPERM` while starting esbuild; focused Vitest commands passed with escalated execution.
- A first implementation used a React effect to reset disabled provider state; lint rejected synchronous setState in effect, so selection fallback was changed to pure derived state.
- The new hosted test initially clicked version 2 and leaked selected-version state into a later test; it was corrected to use the default selected version.

## Verification

- Red tests failed first:
  - `corepack pnpm --filter @caragent/web test -- --run src/app/page.test.tsx src/lib/api/generation.test.ts src/lib/api/operations.test.ts` failed on missing provider status normalization, payload helpers, and selector UI.
- Green verification passed:
  - `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/api/generation.test.ts src/lib/api/operations.test.ts`
  - `corepack pnpm --filter @caragent/web typecheck`
  - `corepack pnpm --filter @caragent/web lint`

## User Setup Required

None - hosted mode still depends on the existing API/worker feature flags and credentials.

## Next Phase Readiness

Ready for `09-07-PLAN.md`: the workbench now has visible provider selection, blocked hosted feedback, cost/quota labels, and safe diagnostics needed for final Phase 9 smoke/docs/UAT.

## Self-Check: PASSED

- Key files exist: PASS.
- Task acceptance criteria verified: PASS.
- Plan-level verification commands passed: PASS.
- Summary requirements match plan frontmatter: PASS.

---
*Phase: 09-hosted-provider-rollout-mvp*
*Completed: 2026-06-18*
