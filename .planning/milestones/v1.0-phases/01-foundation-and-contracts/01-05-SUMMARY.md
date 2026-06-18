---
phase: 01-foundation-and-contracts
plan: "05"
subsystem: contracts
tags: [openapi, orval, typescript, react-query, contracts]
requires:
  - phase: 01-02
    provides: FastAPI app, typed health endpoint, and deterministic OpenAPI export CLI.
provides:
  - Dedicated @caragent/contracts package boundary under packages/contracts.
  - Orval configuration for OpenAPI-first React Query client generation.
  - Stable package entrypoint for generated client consumption by future web plans.
affects: [phase-01-foundation, apps-web, services-api, plan-01-06]
tech-stack:
  added: [orval, typescript]
  patterns:
    - FastAPI OpenAPI remains the source of truth for frontend API types.
    - Generated TypeScript client is exposed only through @caragent/contracts.
key-files:
  created:
    - packages/contracts/package.json
    - packages/contracts/README.md
    - packages/contracts/tsconfig.json
    - packages/contracts/orval.config.ts
    - packages/contracts/openapi/.gitkeep
    - packages/contracts/src/index.ts
    - packages/contracts/src/generated/.gitkeep
  modified: []
key-decisions:
  - "Kept @caragent/contracts private, ESM-compatible, and limited to generated contract exports."
  - "Used Orval React Query generation from ./openapi/openapi.json to ./src/generated/client.ts."
  - "Pinned TypeScript to 6.0.3 and Orval to 8.8.0 while documenting sandbox registry-check blockers."
patterns-established:
  - "Contract package scripts: generate runs Orval, check delegates to the Plan 01-06 drift checker, lint/typecheck use strict TypeScript."
  - "Contract package public entrypoint: src/index.ts re-exports generated client artifacts after Plan 01-06 generation."
requirements-completed: [FOUND-02, FOUND-03]
duration: 3min
completed: 2026-05-08
---

# Phase 1 Plan 05: Contract Package Scaffold Summary

**OpenAPI-first contract package scaffold with Orval React Query generation wiring and a stable frontend import boundary.**

## Performance

- **Duration:** 3 min
- **Started:** 2026-05-08T08:40:16Z
- **Completed:** 2026-05-08T08:43:37Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Created `@caragent/contracts` as the dedicated frontend/backend contract boundary.
- Added package scripts for generation, future drift checking, TypeScript type checking, and contract linting.
- Added Orval config that reads `./openapi/openapi.json` and writes one React Query client target at `./src/generated/client.ts`.
- Added artifact directories and a stable `src/index.ts` entrypoint without hand-maintained backend type copies.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create contracts package metadata and scripts** - `670bfb2` (feat)
2. **Task 2: Add Orval config and stable exports** - `2bfb154` (feat)

## Files Created/Modified

- `packages/contracts/package.json` - Private ESM package metadata, export map, scripts, and pinned Orval/TypeScript dev dependencies.
- `packages/contracts/README.md` - Contract boundary documentation and no-manual-type-copy rule.
- `packages/contracts/tsconfig.json` - Strict TypeScript config for generated contracts.
- `packages/contracts/orval.config.ts` - Orval `defineConfig` using OpenAPI input and React Query client output.
- `packages/contracts/openapi/.gitkeep` - Placeholder to keep the future OpenAPI artifact directory committed.
- `packages/contracts/src/index.ts` - Stable package entrypoint for the generated client.
- `packages/contracts/src/generated/.gitkeep` - Placeholder to keep the future generated-client directory committed.

## Decisions Made

- Used `type: "module"` in the package to align with Orval v8's ESM direction and the root workspace's modern Node target.
- Kept `lint` as a strict TypeScript gate because this plan adds no ESLint dependency to the contracts package.
- Left `openapi/openapi.json` and `src/generated/client.ts` ungenerated because Plan 01-06 explicitly owns those artifacts.

## Verification

- **PASS:** `node -e "const p=require('./packages/contracts/package.json'); ..."` verified package name and scripts `generate`, `check`, `typecheck`, and `lint`.
- **PASS:** `node -e "const fs=require('fs'); const cfg=fs.readFileSync('packages/contracts/orval.config.ts','utf8'); ..."` verified `defineConfig`, `openapi/openapi.json`, `src/generated/client.ts`, and `react-query`.
- **PASS:** File-existence check found all seven planned contract scaffold files.
- **PASS:** Scoped scan found no hand-maintained TypeScript model declarations, backend internal imports, or concrete secret/env key exports under `packages/contracts`.
- **PASS:** Artifact check confirmed this plan did not create `packages/contracts/openapi/openapi.json` or `packages/contracts/src/generated/client.ts`.
- **PASS:** Stub scan found no `TODO`, `FIXME`, placeholder text, or empty-value stub patterns in `packages/contracts`.
- **BLOCKED:** `pnpm view orval version` and `pnpm view typescript version` failed before registry access with `EPERM: operation not permitted, lstat 'C:\Users\25858'`.
- **BLOCKED:** `Invoke-RestMethod https://registry.npmjs.org/orval/latest` and `Invoke-RestMethod https://registry.npmjs.org/typescript/latest` failed with SSL connection errors in this sandbox.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Shell-based npm registry checks are blocked in this workspace by Node/pnpm user-profile permissions and PowerShell SSL failures. No lockfile was created. The deterministic manifest pins are `orval@8.8.0` and `typescript@6.0.3`; re-run `pnpm view orval version` and `pnpm view typescript version` on a host with working package-manager access before dependency install.
- A parallel Wave 3 agent created untracked `apps/web` files during this run. They were left unstaged and untouched.
- Git continued to warn that `C:\Users\25858/.config/git/ignore` is inaccessible. Repository-scoped `git -c safe.directory=D:/python/carAgent ...` commands still succeeded.

## Known Stubs

None. The `.gitkeep` files and the generated-client re-export are intentional scaffold points for Plan 01-06 and do not block this plan's contract-package goal.

## User Setup Required

None for this plan. Package installation and generated contract artifacts are deferred to downstream validation once pnpm access is available.

## Next Phase Readiness

Ready for Plan 01-06. The next plan can export FastAPI OpenAPI JSON into `packages/contracts/openapi/openapi.json`, run Orval, create `packages/contracts/src/generated/client.ts`, and implement `scripts/check-contracts.mjs`.

## Self-Check: PASSED

- Verified all created files and the summary exist on disk.
- Verified task commits `670bfb2` and `2bfb154` exist in git history.
- Verified the only unstaged plan file before metadata commit was `01-05-SUMMARY.md`; protected seed files `UI.png` and `init.MD` remained untouched.

---
*Phase: 01-foundation-and-contracts*
*Completed: 2026-05-08*
