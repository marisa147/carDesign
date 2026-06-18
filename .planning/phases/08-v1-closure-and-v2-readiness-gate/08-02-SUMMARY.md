---
phase: 08-v1-closure-and-v2-readiness-gate
plan: "02"
subsystem: config-feature-flags
tags: [v2-flags, config, env, api, worker, web]

requires:
  - phase: "08-01"
    provides: V1 baseline and readiness command index
provides:
  - default-off V2 feature flags
  - API and worker typed flag settings
  - browser-safe public V2 capability flags
  - focused config tests
affects:
  - phase-09-hosted-provider
  - phase-10-targeted-editing
  - phase-11-reference-guidance
  - phase-12-lightweight-3d
  - phase-13-handoff

tech-stack:
  added: []
  patterns:
    - server-side V2 capability flags use typed Pydantic settings
    - browser-visible V2 flags use only NEXT_PUBLIC non-secret booleans
    - local deterministic mode accepts empty hosted provider secrets when V2 flags are off

key-files:
  created:
    - apps/web/src/lib/config/public-env.test.ts
  modified:
    - .env.example
    - services/api/.env.example
    - services/worker/.env.example
    - apps/web/.env.example
    - services/api/src/caragent_api/config.py
    - services/worker/src/caragent_worker/config.py
    - services/api/tests/test_config.py
    - services/worker/tests/test_config.py
    - apps/web/src/lib/config/public-env.ts

key-decisions:
  - "Use explicit V2 flag names for hosted provider rollout, targeted regeneration, reference guidance, lightweight 3D preview, and enhanced handoff package."
  - "Expose only NEXT_PUBLIC non-secret capability booleans to browser code."

patterns-established:
  - "V2 capability rollout starts with default-off config fields plus RED/GREEN tests before any behavior changes."

requirements-completed:
  - V2-READY-03
  - V2-READY-04

duration: 6 min
completed: 2026-06-18
---

# Phase 8 Plan 02: Default-Off V2 Flags Summary

**Default-off V2 capability flags in API, worker, web public env, and local-safe env examples**

## Performance

- **Duration:** 6 min
- **Started:** 2026-06-18T07:21:00Z
- **Completed:** 2026-06-18T07:26:59Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments

- Added RED tests proving API, worker, and web public env expected V2 flags and failed before implementation.
- Added default-off typed V2 flags to API and worker settings.
- Added browser-safe `NEXT_PUBLIC_V2_*` capability booleans to web public env.
- Documented all V2 readiness flags in root, API, worker, and web env examples with false defaults.
- Verified local mode still accepts empty hosted provider credentials while V2 and hosted provider calls are disabled.

## Task Commits

1. **Task 1: Specify default-off V2 config behavior** - `57a8b76` (test)
2. **Task 2: Implement typed V2 flag settings and env examples** - `77f552f` (feat)

## Files Created/Modified

- `apps/web/src/lib/config/public-env.test.ts` - Focused test for default-off browser-safe V2 flags and no secret-like values.
- `services/api/tests/test_config.py` - API settings test for default-off V2 flags and empty hosted credentials.
- `services/worker/tests/test_config.py` - Worker settings test for default-off V2 flags and empty hosted credentials.
- `services/api/src/caragent_api/config.py` - API typed V2 flag settings.
- `services/worker/src/caragent_worker/config.py` - Worker typed V2 flag settings.
- `apps/web/src/lib/config/public-env.ts` - Non-secret public V2 capability booleans.
- `.env.example`, `services/api/.env.example`, `services/worker/.env.example`, `apps/web/.env.example` - False/off V2 readiness defaults.

## Decisions Made

- V2 flags are named `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED`, `V2_TARGETED_REGENERATION_ENABLED`, `V2_REFERENCE_GUIDANCE_ENABLED`, `V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED`, and `V2_ENHANCED_HANDOFF_PACKAGE_ENABLED`.
- Browser code receives only matching `NEXT_PUBLIC_V2_*` booleans. Provider keys, URLs, database, Redis, and S3 secrets remain server-side.

## Deviations from Plan

None - plan executed exactly as written.

---

**Total deviations:** 0 auto-fixed.
**Impact on plan:** No scope change.

## Issues Encountered

- Vitest initially hit Windows sandbox `spawn EPERM` while starting esbuild. The focused web test passed when rerun with approved elevated execution.
- `uv run mypy` initially could not open the user uv cache under AppData in the sandbox. API and worker mypy passed when rerun with approved elevated execution.

## Verification

- RED API config test failed because `ApiSettings.v2_hosted_provider_rollout_enabled` was missing.
- RED worker config test failed because `WorkerSettings.v2_hosted_provider_rollout_enabled` was missing.
- RED web public env test failed because `publicEnv.v2HostedProviderRolloutEnabled` was `undefined`.
- `uv run pytest -q tests/test_config.py` passed in `services/api`.
- `uv run pytest -q tests/test_config.py` passed in `services/worker`.
- `corepack pnpm --filter @caragent/web exec vitest --run src/lib/config/public-env.test.ts` passed.
- `uv run ruff check .` passed in `services/api`.
- `uv run ruff check .` passed in `services/worker`.
- `uv run mypy src` passed in `services/api`.
- `uv run mypy src` passed in `services/worker`.
- `corepack pnpm --filter @caragent/web typecheck` passed.
- `node scripts/check-env-examples.mjs` passed.

## User Setup Required

None - all V2 readiness flags default to false and do not require hosted provider credentials.

## Next Phase Readiness

Ready for `08-03-PLAN.md`: compatibility checks can now rely on explicit default-off V2 flags while preserving V1 local-only behavior.

## Self-Check: PASSED

- Key files exist: PASS.
- RED/GREEN test discipline followed: PASS.
- Task acceptance criteria verified: PASS.
- Plan-level verification commands passed: PASS.
- Summary requirements match plan frontmatter: PASS.

---
*Phase: 08-v1-closure-and-v2-readiness-gate*
*Completed: 2026-06-18*
