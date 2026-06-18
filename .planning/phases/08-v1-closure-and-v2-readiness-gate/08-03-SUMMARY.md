---
phase: 08-v1-closure-and-v2-readiness-gate
plan: "03"
subsystem: contract-compatibility
tags: [openapi, contracts, compatibility, generated-client, preview-spec]

requires:
  - phase: "08-02"
    provides: default-off V2 config flags
provides:
  - root-runnable V1 compatibility check
  - static OpenAPI route/schema assertions
  - generated TypeScript client surface assertions
affects:
  - phase-09-hosted-provider
  - phase-10-targeted-editing
  - phase-11-reference-guidance
  - phase-12-lightweight-3d

tech-stack:
  added: []
  patterns:
    - compatibility checks inspect committed generated artifacts without starting the API
    - compatibility gates supplement contract drift checks instead of replacing them

key-files:
  created:
    - scripts/check-v1-compatibility.mjs
  modified:
    - package.json
    - docs/development.md

key-decisions:
  - "Keep FastAPI/Pydantic OpenAPI as the contract source and add a static V1 surface check before V2 schema expansion."
  - "Run `pnpm compat:v1` alongside, not instead of, `pnpm contracts:check`."

patterns-established:
  - "V2 schema work must preserve V1 route, schema, generated helper, and PreviewSpec-compatible parameter surfaces."

requirements-completed:
  - V2-READY-02
  - V2-READY-03

duration: 5 min
completed: 2026-06-18
---

# Phase 8 Plan 03: V1 Compatibility Gate Summary

**Static V1 compatibility gate for OpenAPI routes, schemas, generated helpers, and PreviewSpec-compatible parameters**

## Performance

- **Duration:** 5 min
- **Started:** 2026-06-18T07:27:00Z
- **Completed:** 2026-06-18T07:31:58Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments

- Added `scripts/check-v1-compatibility.mjs`, a static compatibility gate that checks key v1 workbench, job, artifact, version, feedback/export/iteration, operations, and health surfaces.
- Verified `DesignVersionResponse.parameters` remains an open object so `preview_spec` metadata stays readable by existing clients.
- Added root script `pnpm compat:v1`.
- Documented how `pnpm compat:v1` complements `pnpm contracts:check`.

## Task Commits

1. **Task 1: Specify V1 compatibility checker expectations** - `4293cda` (test)
2. **Task 2: Wire compatibility gate into root scripts and docs** - `6089d63` (docs)

## Files Created/Modified

- `scripts/check-v1-compatibility.mjs` - Static compatibility assertions over OpenAPI and generated TypeScript client.
- `package.json` - Root `compat:v1` script.
- `docs/development.md` - Root command table and Phase 8 readiness command guidance.

## Decisions Made

- The compatibility gate checks committed generated artifacts and does not require network access, provider credentials, or a running API.
- The compatibility gate is intentionally narrower than `contracts:check`: it verifies V1 surface presence, while `contracts:check` verifies generated artifact synchronization.

## Deviations from Plan

None - plan executed exactly as written.

---

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No scope change.

## Issues Encountered

- `corepack pnpm contracts:check` initially hit the script's sandbox fallback path, which generated a health-only fallback client and reported a false stale diff. Root cause: the real Orval generator was blocked in the sandbox, not an API schema change. Running the real generator and `contracts:check` with approved elevated execution restored and verified the generated artifacts.

## Verification

- RED command `node scripts/check-v1-compatibility.mjs` failed because the script did not exist.
- `node scripts/check-v1-compatibility.mjs` passed.
- `corepack pnpm compat:v1` passed.
- `corepack pnpm contracts:check` passed with real Orval generation.
- Generated OpenAPI and TypeScript contract artifacts remained clean after the final check.

## User Setup Required

None - compatibility checks run from committed artifacts and do not need external services.

## Next Phase Readiness

Ready for `08-04-PLAN.md`: migration safety can build on a stable contract gate and default-off V2 flags.

## Self-Check: PASSED

- Key files exist: PASS.
- RED/GREEN discipline followed for the new compatibility command: PASS.
- Task acceptance criteria verified: PASS.
- Plan-level verification commands passed: PASS.
- Summary requirements match plan frontmatter: PASS.

---
*Phase: 08-v1-closure-and-v2-readiness-gate*
*Completed: 2026-06-18*
