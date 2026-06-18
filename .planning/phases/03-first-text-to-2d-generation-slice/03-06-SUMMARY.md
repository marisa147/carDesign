---
phase: 03-first-text-to-2d-generation-slice
plan: "06"
subsystem: contracts-web
tags: [openapi, orval, nextjs, react, generation]

requires:
  - phase: 03-05
    provides: generation API routes and OpenAPI schemas
  - phase: 02-06
    provides: web API wrapper patterns and durable job status endpoints
provides:
  - refreshed TypeScript contract artifacts for Phase 3 generation routes
  - browser-safe generation API wrapper module
  - minimal Phase 3 web proof for creating a structured brief and submitting a 2D generation job
  - API-backed job/event/artifact/version status display in the web shell
affects: [phase-03-smoke, phase-04-workbench-ui]

tech-stack:
  patterns:
    - generated URL helpers wrapped behind small web API clients
    - localStorage remembers durable workspace and generation job ids only
    - Phase 3 UI proof is intentionally separate from the deferred full generation workbench

key-files:
  created:
    - apps/web/src/lib/api/generation.ts
    - apps/web/src/lib/api/generation.test.ts
  modified:
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts
    - apps/web/src/app/page.tsx
    - apps/web/src/app/page.test.tsx

key-decisions:
  - "The browser calls only FastAPI generation routes; provider names, API keys, and secrets are not accepted or sent by the web wrapper."
  - "The homepage exposes a compact Phase 3 concept-generation proof, while the full generation workbench remains labelled as a later-stage region."
  - "Frontend result state is refreshed through durable job, event, artifact, and version endpoints rather than queue result state."

patterns-established:
  - "Web generation calls mirror existing `jobs.ts` and `workspaces.ts` wrappers with generated route helpers plus typed request/response models."
  - "Phase 3 proof stores `caragent.phase3.generationJobId` for refresh after reload, not provider execution details."
  - "Page tests assert generated route usage and that request bodies do not contain provider-secret fields."

requirements-completed: [GEN-01, GEN-02, GEN-05, GEN-06, GEN-07]

duration: 29 min
completed: 2026-06-17
---

# Phase 3 Plan 06: Contracts and Web Proof Summary

**Contracts are current and the web shell can submit a structured Phase 3 brief/generation request through browser-safe API wrappers**

## Performance

- **Duration:** 29 min
- **Started:** 2026-06-17T07:42:00Z
- **Completed:** 2026-06-17T08:11:00Z
- **Tasks:** 4
- **Files modified:** 6

## Accomplishments

- Exported the updated API OpenAPI document and regenerated TypeScript contract artifacts.
- Added `apps/web/src/lib/api/generation.ts` with create/update brief, submit/retry generation, and durable state loading wrappers.
- Added wrapper tests covering generated route helper usage, error handling, and browser request bodies without provider secrets.
- Extended the homepage with a compact Phase 3 concept-generation proof: natural-language brief, create concept task, refresh status, and durable job/artifact/version metrics.
- Kept future full workbench regions disabled by renaming the deferred nav target to `生成工作台`.

## Task Commits

No task commits were created during this inline run because the workspace already contains broad uncommitted GSD Phase 1/2/3 changes. The completed files are listed below and verified by the commands in this summary.

## Files Created/Modified

- `apps/web/src/lib/api/generation.ts` - Browser-safe generation API wrapper module.
- `apps/web/src/lib/api/generation.test.ts` - Wrapper contract and no-provider-secret tests.
- `apps/web/src/app/page.tsx` - Minimal Phase 3 concept-generation proof in the existing shell.
- `apps/web/src/app/page.test.tsx` - Homepage tests for Phase 3 proof behavior and deferred workbench boundaries.
- `packages/contracts/openapi/openapi.json` - Exported OpenAPI source for generated contracts.
- `packages/contracts/src/generated/client.ts` - Orval-generated TypeScript routes and schemas.

## Decisions Made

- Phase 3 web proof submits fixed safe prompt metadata alongside the user brief; provider/model details stay behind the API/worker boundary.
- The proof displays counts and statuses from durable records rather than pretending to be the final visual preview workbench.
- Refresh uses the stored generation job id and rehydrates job/event/artifact/version state from API endpoints.

## Deviations from Plan

- Browser plugin navigation loaded the page title, but DOM/screenshot calls timed out in the plugin runtime. Headless Chrome/Edge screenshot paths were also unreliable in this Windows permission environment, so final visual confidence was supplemented with production build and HTTP-rendered HTML checks.

## Issues Encountered

- Vitest/esbuild failed inside the sandbox with `spawn EPERM`; web tests were rerun outside the sandbox.
- `corepack pnpm --filter @caragent/web test -- generation.test.ts` passes the literal `--` through this pnpm/script setup, so it also ran the existing web tests. The target wrapper test file still executed and passed.
- A stale dev server process hit `EPIPE`; it was stopped by exact PID and restarted cleanly on `http://127.0.0.1:3000`.

## Verification

- `uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json` in `services/api` - passed outside sandbox.
- `corepack pnpm contracts:generate` - passed.
- `corepack pnpm contracts:check` - passed, contract artifacts current.
- `corepack pnpm --filter @caragent/web test -- generation.test.ts` - RED failed before wrapper implementation because `@/lib/api/generation` did not exist.
- `corepack pnpm --filter @caragent/web test -- generation.test.ts` - passed after implementation; target wrapper file passed 4 tests.
- `corepack pnpm --filter @caragent/web test -- page.test.tsx generation.test.ts` - passed, 20 tests.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web build` - passed.
- `Invoke-WebRequest http://localhost:3000` - passed after clean dev restart; confirmed `Phase 3 概念生成证明`, `generation-request`, `生成工作台`, and `创建概念任务` are present in served HTML.

## User Setup Required

The frontend dev server is running at `http://127.0.0.1:3000`. Submitting a real generation task requires the API, worker, Redis, PostgreSQL, and object storage services to be running.

## Next Phase Readiness

Ready for `03-07`: contracts and web proof are in place, so final smoke scripts, env guards, docs, verification report, and UAT checklist can cover the end-to-end Phase 3 slice.

---
*Phase: 03-first-text-to-2d-generation-slice*
*Completed: 2026-06-17*
