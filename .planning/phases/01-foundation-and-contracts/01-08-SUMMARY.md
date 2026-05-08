---
phase: 01-foundation-and-contracts
plan: "08"
subsystem: web
tags: [nextjs, react, contracts, health-check, testing-library, foundation-shell]
requires:
  - phase: 01-foundation-and-contracts
    plan: "06"
    provides: "Generated OpenAPI and TypeScript health client artifacts."
  - phase: 01-foundation-and-contracts
    plan: "07"
    provides: "Next.js web scaffold, Tailwind/shadcn baseline, and Vitest config."
provides:
  - "Phase 1 foundation shell at `/` with readiness cards and disabled future regions."
  - "Browser public env wrapper limited to NEXT_PUBLIC_API_BASE_URL."
  - "Generated-contract health wrapper using @caragent/contracts."
  - "Testing Library coverage for shell copy, disabled regions, health URL usage, and status mapping."
affects: [phase-01-foundation, apps-web, packages-contracts]
tech-stack:
  added: []
  patterns:
    - "Web code consumes API health through @caragent/contracts, not backend internals."
    - "Future workbench regions are visible but disabled with aria-disabled and 后续阶段开放 copy."
    - "Vitest resolves the same @/ source alias used by the Next.js app."
key-files:
  created:
    - apps/web/src/lib/config/public-env.ts
    - apps/web/src/lib/api/health.ts
    - apps/web/src/app/page.tsx
    - apps/web/src/app/page.test.tsx
    - apps/web/src/components/ui/button.tsx
    - apps/web/src/components/ui/badge.tsx
    - apps/web/src/components/ui/card.tsx
    - apps/web/src/components/ui/alert.tsx
    - apps/web/src/test/setup.ts
  modified:
    - apps/web/package.json
    - apps/web/vitest.config.ts
key-decisions:
  - "Used generated export healthHealthGet from @caragent/contracts as the health client operation name."
  - "Kept the shell client-side so the health CTA can run without adding new routes or server actions."
  - "Added only the allowed local shadcn-style primitives: button, badge, card, and alert."
requirements-completed: [FOUND-01, FOUND-02, FOUND-03, FOUND-04]
duration: 13min
completed: 2026-05-08
---

# Phase 1 Plan 08: Web Shell Health Integration And Tests Summary

**Foundation workbench shell with generated-contract health integration and UI boundary tests.**

## Performance

- **Duration:** 13 min
- **Started:** 2026-05-08T16:56:38+08:00
- **Completed:** 2026-05-08T17:09:24+08:00
- **Tasks:** 3
- **Files modified:** 11

## Accomplishments

- Added `@caragent/contracts` as a workspace dependency for the web package.
- Created `public-env.ts` so browser code reads only `NEXT_PUBLIC_API_BASE_URL`, defaulting to `http://localhost:8000`.
- Created `checkStackHealth` and `mapHealthResponse` around generated contract export `healthHealthGet`.
- Built the `/` Phase 1 shell with top bar, left rail, five readiness cards, footer status strip, and disabled future workbench regions.
- Added Testing Library coverage for required copy, loading state, disabled future regions, forbidden product controls, contract URL usage, and health response mapping.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement public env and generated-contract health wrapper** - `0c2d131` (feat)
2. **Task 2: Build root foundation shell** - `cd790f1` (feat)
3. **Task 3: Add shell tests and frontend verification** - `ab55b70` (test)

## Files Created/Modified

- `apps/web/package.json` - Added `@caragent/contracts` workspace dependency.
- `apps/web/src/lib/config/public-env.ts` - Browser-safe public API base URL reader.
- `apps/web/src/lib/api/health.ts` - Generated-contract health wrapper and five-card status mapping.
- `apps/web/src/app/page.tsx` - Phase 1 foundation shell.
- `apps/web/src/components/ui/button.tsx` - Local allowed button primitive.
- `apps/web/src/components/ui/badge.tsx` - Local allowed badge primitive.
- `apps/web/src/components/ui/card.tsx` - Local allowed card primitive.
- `apps/web/src/components/ui/alert.tsx` - Local allowed alert primitive.
- `apps/web/src/app/page.test.tsx` - UI contract and boundary tests.
- `apps/web/src/test/setup.ts` - Testing Library jest-dom setup import.
- `apps/web/vitest.config.ts` - Vitest `@/` alias resolution for app imports.

## Decisions Made

- Used `healthHealthGet` because that is the exact generated health operation exported by `packages/contracts/src/generated/client.ts`.
- Kept footer runtime display fixed to local shell state until the health response updates it, avoiding any non-public browser env reads.
- Used Chinese disabled-region labels for deferred workbench areas so the UI remains honest without adding functional prompt, upload, generation, preview, or export controls.

## Verification

- **PASS:** `node -e "...@caragent/contracts workspace dependency..."`.
- **PASS:** `rg "@caragent/contracts" apps/web/src/lib/api/health.ts`.
- **PASS:** Backend/secret leak scan for `AI_PROVIDER_`, `S3_SECRET_ACCESS_KEY`, `DATABASE_URL`, `REDIS_URL`, `services/api`, and `caragent_api`.
- **PASS:** Static UI copy check for `痛车设计 Agent`, `检查堆栈健康`, `正在检查服务...`, `工作台基础已就绪`, and `后续阶段开放`.
- **PASS:** Static component inventory check found only allowed `button`, `badge`, `card`, and `alert` primitives.
- **PASS:** Static test artifact check found required Testing Library assertions and contract health URL/mapping coverage.
- **PASS:** Product/security term scan excluding TypeScript syntax found no `chat`, `upload`, `generate`, `Three`, `canvas`, provider, database, or secret env matches.
- **INSPECTED:** Full plan scan including `export` matched only normal TypeScript `export` declarations.
- **BLOCKED:** `pnpm --filter @caragent/web lint` failed before package execution with `EPERM: operation not permitted, lstat 'C:\Users\25858'`.
- **BLOCKED:** `pnpm --filter @caragent/web typecheck` failed before package execution with the same Node/pnpm profile `EPERM`.
- **BLOCKED:** `pnpm --filter @caragent/web test -- --run` failed before package execution with the same Node/pnpm profile `EPERM`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added Vitest source alias wiring**
- **Found during:** Task 3
- **Issue:** The app source imports `@/...` paths, but `apps/web/vitest.config.ts` did not define a Vite/Vitest alias. Host test execution would be unable to resolve the page and component imports.
- **Fix:** Added `resolve.alias` for `@` to `apps/web/src`.
- **Files modified:** `apps/web/vitest.config.ts`
- **Commit:** `ab55b70`

## Issues Encountered

- `pnpm` remains unusable in this sandbox because Node fails on `C:\Users\25858` profile access before package scripts run.
- Git still warns that `C:\Users\25858/.config/git/ignore` is inaccessible; all git commands used `git -c safe.directory=D:/python/carAgent`.

## Known Stubs

None. Stub scan only matched `options: CheckStackHealthOptions = {}` in `apps/web/src/lib/api/health.ts`, which is an optional-argument default and does not flow empty UI data.

## Threat Flags

None. The browser-to-API health call, public env boundary, and disabled future-region user-expectation boundary are covered by the plan threat model (`T-01-02H`, `T-01-04H`, `T-01-05H`).

## User Setup Required

Run these on a host where Node/pnpm can access the user profile and dependencies are installed:

```powershell
pnpm --filter @caragent/web lint
pnpm --filter @caragent/web typecheck
pnpm --filter @caragent/web test -- --run
```

## Self-Check: PASSED

- Verified created files exist on disk.
- Verified task commits `0c2d131`, `cd790f1`, and `ab55b70` exist in git history.
- Verified no tracked files were deleted by task commits.
- Verified protected untracked seed files `UI.png` and `init.MD` remain untouched.

---
*Phase: 01-foundation-and-contracts*
*Completed: 2026-05-08*
