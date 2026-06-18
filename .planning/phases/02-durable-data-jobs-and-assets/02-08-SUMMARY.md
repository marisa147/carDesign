---
phase: 02-durable-data-jobs-and-assets
plan: "08"
subsystem: "minimal web durable refresh proof"
tags: ["web", "contracts", "workspace", "jobs", "refresh", "uat"]
requires:
  - ".planning/phases/02-durable-data-jobs-and-assets/02-08-PLAN.md"
  - ".planning/phases/02-durable-data-jobs-and-assets/02-06-SUMMARY.md"
  - ".planning/phases/02-durable-data-jobs-and-assets/02-07-SUMMARY.md"
provides:
  - "Minimal Phase 2 durable workspace/job proof panel in the web shell"
  - "Workspace and job refetch behavior after remount/refresh using generated contract wrappers"
  - "Browser-local storage limited to workspace ID and client idempotency key"
  - "Human UAT checklist for real API-backed refresh proof"
key-files:
  created:
    - ".planning/phases/02-durable-data-jobs-and-assets/02-HUMAN-UAT.md"
  modified:
    - "apps/web/src/app/page.tsx"
    - "apps/web/src/app/page.test.tsx"
key-decisions:
  - "Phase 2 web proof intentionally remains a compact status panel, not the full Phase 4 chat/upload/preview/export workbench."
  - "The browser stores only the durable workspace ID and idempotency key; canonical messages, jobs, and events are fetched again from API wrappers."
  - "Automated tests mock the backend through generated wrapper URLs, while live API-backed refresh verification is documented as human UAT."
requirements-completed: ["DATA-01", "DATA-05", "DATA-06"]
duration: "in-session"
completed: 2026-06-17
---

# Phase 2 Plan 08: Web Refresh Proof Summary

Plan 02-08 added the minimal frontend proof that durable workspace/job state can be created, resumed, and refetched through generated Phase 2 API contracts without expanding into the later full workbench.

## Tasks Completed

| Task | Result | Evidence |
|------|--------|----------|
| Durable proof tests first | Complete | Tests failed RED before the Phase 2 panel existed, then passed after implementation. |
| Workspace/job status panel | Complete | Web shell can create a workspace proof, create an idempotent simulated job, show message/job/event counts, and refresh canonical state. |
| Refresh/remount behavior | Complete | Tests preload local storage, remount the page, and assert workspace/messages/jobs/events are fetched again from generated wrapper URLs. |
| Human UAT checklist | Complete | `02-HUMAN-UAT.md` documents real API-backed create workspace, create job, browser refresh, and repeat idempotent job checks. |
| Visual smoke | Complete | Local Next shell rendered in the browser with the Phase 2 panel visible and no runtime error. |

## Verification

| Command | Result |
|---------|--------|
| `corepack pnpm --filter @caragent/web test -- src/app/page.test.tsx` | Passed during implementation; page and wrapper tests ran with `15 passed`. |
| `corepack pnpm --filter @caragent/web typecheck` | Passed. |
| `corepack pnpm --filter @caragent/web lint` | Passed. |
| `corepack pnpm --filter @caragent/web test` | Passed with escalated sandbox permissions due Vitest/esbuild process spawning; `3 files passed`, `15 tests passed`. |
| Browser smoke at `http://127.0.0.1:3000/` | Passed; title was `痛车设计 Agent`, Phase 2 controls were visible, and no Next runtime error was present. |

## Deviations from Plan

**[Rule 1 - Runtime Sandbox] Vitest and Next dev server need process spawning**
- Found during: web verification and browser smoke.
- Issue: Vitest and Next dev server hit `spawn EPERM` under the sandbox when esbuild/Next attempted to start child processes.
- Fix: Reran the affected commands with approved escalated execution. No code change was needed for this environment issue.
- Verification: Web tests passed and the local Next dev server rendered the page in the browser.

**[Rule 2 - Visual Fit] Prevent status badge wrapping in foundation cards**
- Found during: browser screenshot.
- Issue: A narrow status badge could wrap Chinese status text vertically in the existing foundation card grid.
- Fix: Added non-wrapping, non-shrinking badge styling in the page card header.
- Verification: Browser screenshot after reload showed the status badges fitting horizontally.

## Not Run

Full live API-backed UAT was documented but not completed in this plan because the browser smoke was limited to the frontend dev server. The checklist is ready for `02-09` phase smoke with API, worker, and Docker services running together.

`pnpm validate` was not used as 02-08 completion evidence because `.node-version` currently requires Node `24.15.0`, while this session is intentionally running under NVM Node `22.15.0` per the user instruction.

## Self-Check: PASSED

The web shell now proves Phase 2 durable workspace/job refresh behavior through generated contract wrappers, keeps only minimal identifiers in browser storage, and leaves the full chat/upload/preview/export workbench deferred to later phases.

## Next

Ready for `02-09-PLAN.md`: Phase 2 smoke, docs, env guards, aggregate validation, and verification report.
