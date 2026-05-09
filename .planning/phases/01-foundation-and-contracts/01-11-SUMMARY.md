---
phase: 01-foundation-and-contracts
plan: "11"
subsystem: configuration
tags: [pydantic-settings, dotenv, env-guard, provider-config, pytest]
requires:
  - phase: 01-09
    provides: Aggregate validation runner and final Phase 1 development runbook.
  - phase: 01-10
    provides: Root and contracts test command gap closure.
provides:
  - API and worker settings load documented service `.env` files from their service working directories.
  - API and worker settings share the Phase 1 `AI_PROVIDER_*` provider env contract.
  - Env examples, env guard, docs, and config tests agree on provider metadata and key names.
affects: [phase-01-foundation, phase-02-planning, developer-onboarding, provider-configuration]
tech-stack:
  added: []
  patterns:
    - Service-local dotenv loading is configured through `pydantic-settings` `env_file=".env"`.
    - Provider keys are parsed as `SecretStr` configuration only and remain redacted.
    - Env example validation rejects legacy provider key definitions.
key-files:
  created:
    - .planning/phases/01-foundation-and-contracts/01-11-SUMMARY.md
  modified:
    - .env.example
    - services/api/src/caragent_api/config.py
    - services/api/.env.example
    - services/api/tests/test_config.py
    - services/worker/src/caragent_worker/config.py
    - services/worker/.env.example
    - services/worker/tests/test_config.py
    - scripts/check-env-examples.mjs
    - docs/development.md
key-decisions:
  - "Kept provider entries configuration-only; no provider SDKs, validation calls, or network behavior were added."
  - "Kept the literal `AI_PROVIDER_OPENAI_API_KEY=` env contract despite a plan-provided substring verification false positive."
  - "Added worker `populate_by_name=True` alongside explicit aliases so direct field-name construction remains compatible."
patterns-established:
  - "API/worker dotenv tests create a temporary `.env`, change into that directory, and instantiate settings to prove documented service-cwd loading."
  - "Legacy provider names are not accepted as API/worker provider settings and are rejected in committed env examples."
requirements-completed: [FOUND-04]
duration: 28min
completed: 2026-05-09
---

# Phase 1 Plan 11: Service Env And Provider Contract Gap Closure Summary

**Service-local dotenv loading and unified `AI_PROVIDER_*` provider configuration across API, worker, examples, guard, tests, and docs.**

## Performance

- **Duration:** 28 min
- **Started:** 2026-05-09T09:39:00+08:00
- **Completed:** 2026-05-09T10:07:00+08:00
- **Tasks:** 3
- **Files modified:** 9 source files plus this summary

## Accomplishments

- Wired `ApiSettings` and `WorkerSettings` to load `.env` from the service current working directory with UTF-8 encoding.
- Added `AI_PROVIDER_DEFAULT`, `AI_PROVIDER_CALLS_ENABLED`, and aligned provider key fields to API and worker settings.
- Replaced legacy provider names in root/API/worker env examples with `AI_PROVIDER_OPENAI_API_KEY`, `AI_PROVIDER_FAL_API_KEY`, and `AI_PROVIDER_BFL_API_KEY`.
- Updated the env guard and docs so service `.env` behavior and Phase 1 provider boundaries are truthful.

## Task Commits

TDD tasks used RED and GREEN commits:

1. **Task 1 RED: API dotenv/provider tests** - `548fe82` (test)
2. **Task 1 GREEN: API dotenv/provider settings** - `52a3122` (feat)
3. **Task 2 RED: Worker dotenv/provider tests** - `990d618` (test)
4. **Task 2 GREEN: Worker dotenv/provider settings** - `cf900fb` (feat)
5. **Task 3: Env guard, root example, and docs alignment** - `d8781ca` (docs)

## Files Created/Modified

- `services/api/src/caragent_api/config.py` - Added service `.env` loading and provider metadata fields.
- `services/api/tests/test_config.py` - Added dotenv loading, provider metadata, legacy-key non-use, and redaction coverage.
- `services/api/.env.example` - Replaced legacy provider keys with the `AI_PROVIDER_*` contract.
- `services/worker/src/caragent_worker/config.py` - Added service `.env` loading, explicit env aliases, and provider metadata fields.
- `services/worker/tests/test_config.py` - Added dotenv loading, provider metadata, legacy-key non-use, redaction, and Redis validation coverage.
- `services/worker/.env.example` - Replaced legacy provider keys with the `AI_PROVIDER_*` contract.
- `.env.example` - Replaced legacy provider keys with the same `AI_PROVIDER_*` contract.
- `scripts/check-env-examples.mjs` - Required aligned provider keys and rejects legacy provider key definitions.
- `docs/development.md` - Documented service `.env` loading and D-16 provider configuration-only behavior.

## Decisions Made

- Used service-cwd `.env` loading instead of manual export instructions as the primary documented local override path.
- Kept provider calls disabled and unimplemented in Phase 1; settings only parse and redact provider values.
- Treated legacy provider names as unsupported for this Phase 1 contract rather than accepting aliases, matching the plan interface.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added explicit legacy provider-key rejection to the env guard**
- **Found during:** Task 3 (Align env guard, root env example, and docs)
- **Issue:** Removing legacy names from required-key lists would not prevent a future env example from reintroducing `OPENAI_API_KEY`, `STABILITY_API_KEY`, `FAL_API_KEY`, or `REPLICATE_API_TOKEN`.
- **Fix:** Added a legacy provider-key list and guard assertion that fails committed examples containing those definitions.
- **Files modified:** `scripts/check-env-examples.mjs`
- **Verification:** `node scripts/check-env-examples.mjs` passed; anchored static check found no legacy provider key definitions in root/API/worker env examples.
- **Committed in:** `d8781ca`

---

**Total deviations:** 1 auto-fixed (1 missing critical).
**Impact on plan:** The guard addition enforces the planned provider contract and does not add product scope.

## Issues Encountered

- The plan-provided inline Node verification command failed because it checks `text.includes("OPENAI_API_KEY=")`, which is also true for the required `AI_PROVIDER_OPENAI_API_KEY=` line. The literal provider contract was kept, and an anchored equivalent check passed.
- `uv` is not installed or not on `PATH`, so the planned `uv run pytest` commands remain host-blocked.
- `pnpm validate` is still host-blocked before package execution with `EPERM: operation not permitted, lstat 'C:\Users\25858'`.
- Git continues to warn that `C:\Users\25858/.config/git/ignore` is inaccessible; all repository operations used `git -c safe.directory=D:/python/carAgent`.

## Verification

- **PASS:** Task 1 RED failed before implementation with missing `ai_provider_default` and missing `.env` loading.
- **PASS:** `$env:PYTHONPATH='services/api/src'; python -B -m pytest -q -p no:cacheprovider services/api/tests/test_config.py` returned `5 passed`.
- **BLOCKED:** `cd services/api && uv run pytest -q tests/test_config.py` could not run because `uv` is not installed/on `PATH`.
- **PASS:** Task 2 RED failed before implementation with missing `ai_provider_default` and missing `.env` loading.
- **PASS:** `$env:PYTHONPATH='services/worker/src'; python -B -m pytest -q -p no:cacheprovider services/worker/tests/test_config.py` returned `5 passed`.
- **BLOCKED:** `cd services/worker && uv run pytest -q tests/test_config.py` could not run because `uv` is not installed/on `PATH`.
- **PASS:** `node scripts/check-env-examples.mjs` returned `Environment examples are present, local-only, and secret-safe.`
- **FAILED AS WRITTEN:** The plan inline provider-token command false-positive matched `OPENAI_API_KEY=` inside `AI_PROVIDER_OPENAI_API_KEY=`.
- **PASS:** Anchored equivalent provider-token check confirmed root/API/worker examples include all required `AI_PROVIDER_*` keys and no legacy key definitions.
- **PASS:** Static scan found `env_file`, provider metadata, and `AI_PROVIDER_*` keys across settings, examples, guard, and docs.
- **PASS:** Static scan found no provider SDK imports or provider call patterns in modified config files.
- **BLOCKED:** `pnpm validate` failed before package execution with host `EPERM` on `C:\Users\25858`.

## Known Stubs

- `.env.example:37-42`, `services/api/.env.example:18-23`, and `services/worker/.env.example:18-23` intentionally keep provider placeholders blank with calls disabled. This is required by D-16 and does not block FOUND-04.
- `docs/development.md` contains docs-only provider placeholder wording; it does not flow into UI rendering or mock product behavior.
- `scripts/check-env-examples.mjs` intentionally checks for blank provider key values in local mode.

## Threat Flags

None. The new dotenv and provider configuration surfaces are covered by the plan threat model; no new endpoint, auth path, schema boundary, provider SDK, provider call, or browser secret surface was introduced.

## TDD Gate Compliance

- RED commits exist for API and worker tests: `548fe82`, `990d618`.
- GREEN commits exist after the RED commits: `52a3122`, `cf900fb`.

## User Setup Required

No new setup was introduced. To run host-blocked validation end to end, use a shell with `uv`, Node `24.15.0`, and pnpm profile access, then run:

```powershell
cd services/api
uv run pytest -q tests/test_config.py
cd ../worker
uv run pytest -q tests/test_config.py
cd ../..
pnpm validate
```

## Next Phase Readiness

FOUND-04 gaps WR-01 and WR-05 are closed structurally: documented service `.env` files configure API/worker settings, and provider env names align across settings, examples, tests, guard, and docs. Plan 01-12 can focus on truthful health/smoke behavior without carrying the provider/env mismatch.

## Self-Check: PASSED

- Verified all created/modified files listed in this summary exist on disk.
- Verified task commits `548fe82`, `52a3122`, `990d618`, `cf900fb`, and `d8781ca` exist in git history.
- Verified no tracked files were deleted by task commits.
- Verified only this summary plus protected untracked seed files `UI.png` and `init.MD` remain unstaged before the metadata commit.

---
*Phase: 01-foundation-and-contracts*
*Completed: 2026-05-09*
