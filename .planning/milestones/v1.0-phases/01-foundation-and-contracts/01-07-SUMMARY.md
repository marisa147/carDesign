---
phase: 01-foundation-and-contracts
plan: "07"
subsystem: ui
tags: [nextjs, react, tailwind, shadcn-ui, vitest, eslint]
requires:
  - phase: 01-foundation-and-contracts
    plan: "01"
    provides: "Root pnpm workspace and @caragent/web command delegation."
provides:
  - "@caragent/web Next.js package with dev/build/lint/typecheck/test scripts."
  - "Strict frontend TypeScript, ESLint, PostCSS, and Vitest configuration."
  - "Official shadcn/ui components.json baseline with neutral base color and CSS variables."
  - "Phase 1 UI-SPEC global Tailwind tokens, root layout, and cn utility."
affects: [phase-01-foundation, apps-web, phase-01-plan-08]
tech-stack:
  added: [Next.js, React, TypeScript, Tailwind CSS, shadcn-ui, lucide-react, TanStack Query, Vitest, Testing Library]
  patterns:
    - "Next.js App Router root layout imports app-level globals directly."
    - "shadcn/ui setup uses CSS variables, neutral base color, lucide icons, and @/ aliases."
    - "Class merging uses the standard clsx plus tailwind-merge cn helper."
key-files:
  created:
    - apps/web/package.json
    - apps/web/tsconfig.json
    - apps/web/postcss.config.mjs
    - apps/web/eslint.config.mjs
    - apps/web/vitest.config.ts
    - apps/web/components.json
    - apps/web/src/app/globals.css
    - apps/web/src/app/layout.tsx
    - apps/web/src/lib/utils.ts
  modified: []
key-decisions:
  - "Used Tailwind CSS v4-style PostCSS setup with no separate tailwind.config file because components.json can point at an empty config path."
  - "Kept Plan 01-07 to scaffold/design-system files only; no page shell, chat, upload, preview, generation, export, auth, provider SDK, or 3D behavior was added."
  - "Pinned explicit package versions without creating a lockfile because registry checks and pnpm execution are blocked in this sandbox."
patterns-established:
  - "Frontend package scripts are local package scripts consumed by root pnpm --filter @caragent/web wrappers."
  - "Phase 1 design tokens live in apps/web/src/app/globals.css and preserve the approved neutral canvas plus single accent color."
requirements-completed: [FOUND-01, FOUND-02]
duration: 4min
completed: 2026-05-08
---

# Phase 1 Plan 07: Web Scaffold And Design System Baseline Summary

**Next.js App Router frontend scaffold with strict TypeScript tooling, Vitest test config, and shadcn/Tailwind design tokens.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-05-08T16:41:00Z
- **Completed:** 2026-05-08T16:44:41Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments

- Created the `@caragent/web` package with deterministic scripts for `dev`, `build`, `lint`, `typecheck`, and `test`.
- Added strict frontend config for TypeScript, ESLint flat config, Tailwind v4 PostCSS, and Vitest with jsdom.
- Added shadcn/ui baseline configuration with neutral base color, CSS variables, lucide icons, and `@/` aliases.
- Added UI-SPEC globals, root `zh-CN` layout metadata, and the standard `cn` helper.

## Package Pins

Workspace registry checks were attempted before lockfile creation with `Invoke-RestMethod https://registry.npmjs.org/<package>/latest`, but every request failed with `The SSL connection could not be established, see inner exception.` No lockfile was created.

Chosen deterministic pins in `apps/web/package.json`:

- Runtime: `next@16.2.6`, `react@19.2.4`, `react-dom@19.2.4`, `@tanstack/react-query@5.87.4`
- Design system: `tailwindcss@4.1.13`, `@tailwindcss/postcss@4.1.13`, `lucide-react@0.468.0`, `clsx@2.1.1`, `tailwind-merge@2.6.0`, `class-variance-authority@0.7.1`
- Tooling: `typescript@6.0.3`, `eslint@10.0.0`, `eslint-config-next@16.2.6`, `vitest@3.2.4`, `jsdom@27.0.0`, `@testing-library/react@16.3.0`, `@testing-library/jest-dom@6.6.3`, `@testing-library/user-event@14.6.1`

## Task Commits

Each task was committed atomically:

1. **Task 1: Scaffold web package and strict tooling** - `3449c29` (feat)
2. **Task 2: Add Tailwind globals, layout, and utilities** - `fe547ed` (feat)

## Files Created/Modified

- `apps/web/package.json` - Web package scripts and explicit frontend dependency pins.
- `apps/web/tsconfig.json` - Strict TypeScript config with App Router-friendly JSX and `@/*` path alias.
- `apps/web/postcss.config.mjs` - Tailwind CSS PostCSS plugin setup.
- `apps/web/eslint.config.mjs` - Next.js/TypeScript ESLint flat config.
- `apps/web/vitest.config.ts` - Vitest jsdom test config with no-test pass behavior for the scaffold phase.
- `apps/web/components.json` - Official shadcn/ui registry configuration with neutral base color and CSS variables.
- `apps/web/src/app/globals.css` - Approved Phase 1 UI tokens, system font, focus ring, and neutral app canvas.
- `apps/web/src/app/layout.tsx` - Root App Router layout with `lang="zh-CN"` and `痛车设计 Agent` metadata.
- `apps/web/src/lib/utils.ts` - Standard `cn` utility using `clsx` and `tailwind-merge`.

## Decisions Made

- Kept this plan below product-shell scope: no `page.tsx`, prompt composer, upload, preview, generation, export, auth, marketplace, provider SDKs, or 3D dependencies were added.
- Used Tailwind v4-style CSS import plus `@theme inline` variables so the design tokens are local to the app and match the approved UI-SPEC.
- Left dependency installation and lockfile generation to a host environment where registry and pnpm access work.

## Verification

- **PASS:** `node -e "...web package name and scripts..."` confirmed `@caragent/web` and required scripts.
- **PASS:** `node -e "...UI tokens..."` confirmed `--radius`, `#F8FAFC`, `#111827`, `#6D5DF6`, and no `gradient`, `radial`, or `conic` CSS.
- **PASS:** `node -e "...components/layout sanity..."` confirmed shadcn neutral base color, CSS variables, global stylesheet import, and `zh-CN` layout language.
- **PASS:** `node -e "...disallowed dependencies..."` confirmed no canvas, 3D, auth, provider, or marketplace dependencies were added.
- **PASS:** Declared artifact existence check found all 9 created files.
- **BLOCKED:** `pnpm --filter @caragent/web typecheck` failed before package script execution with `EPERM: operation not permitted, lstat 'C:\Users\25858'` under Node.js `v20.12.0`.
- **BLOCKED:** `pnpm --filter @caragent/web lint` failed with the same `EPERM: operation not permitted, lstat 'C:\Users\25858'` pnpm/Node sandbox error.

## Deviations from Plan

None - implementation scope matched the plan. Environment limitations are documented under Issues Encountered.

## Issues Encountered

- Official npm registry checks from PowerShell failed for all requested packages with SSL connection errors. Deterministic package pins were still written and no lockfile was created.
- `pnpm` commands cannot run in this sandbox because Node/pnpm attempts to access `C:\Users\25858` and receives `EPERM`. This blocks lint/type-check execution here, not the scaffold source creation.
- The workspace HEAD moved during Wave 3 because Plan 01-05 commits landed in the shared repo. This plan did not stage or modify `packages/contracts`.

## Known Stubs

None. This plan intentionally creates scaffold and design-system baseline files only; the visible web shell and health integration are owned by Plan 01-08.

## User Setup Required

No new external service setup was introduced by this plan. To run the blocked checks on the host, use the pinned root prerequisites from Plan 01-01: Node.js 24.15.0, pnpm 11.0.8, and working npm registry access.

## Next Phase Readiness

Ready for Plan 01-08 once generated contracts from Plan 01-06 are available. The web package, Tailwind/shadcn baseline, root layout, and local utility path are in place for the Phase 1 foundation shell.

## Self-Check: PASSED

- Verified all 9 created files exist on disk.
- Verified task commits `3449c29` and `fe547ed` exist in git history.
- Verified the committed changes did not delete tracked files.
- Verified no plan-owned files remained unstaged after task commits.

---
*Phase: 01-foundation-and-contracts*
*Completed: 2026-05-08*
