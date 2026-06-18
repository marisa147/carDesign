---
phase: 09-hosted-provider-rollout-mvp
plan: "01"
subsystem: provider-config-contracts
tags: [hosted-provider, capability-map, operations, contracts, env]

requires:
  - phase: 08-v1-closure-and-v2-readiness-gate
    provides: default-off V2 flags and local deterministic safety baseline
provides:
  - Browser-safe provider capability map for local deterministic and BFL providers
  - Operations status fields for provider capabilities and hosted guard state
  - Phase 9 hosted-provider env examples and generated API contracts
affects:
  - phase-09-hosted-provider
  - phase-10-targeted-editing
  - phase-11-reference-guidance
  - workbench-provider-selector

tech-stack:
  added: []
  patterns:
    - shared core capability builder feeds API and worker settings
    - operations API exposes credential booleans and blocked reasons, never secrets
    - hosted provider checks require V2 flag, provider calls flag, credential, and quota/rate/cost guards

key-files:
  created:
    - services/core/src/caragent_core/provider_capabilities.py
    - .planning/phases/09-hosted-provider-rollout-mvp/09-01-SUMMARY.md
  modified:
    - services/api/src/caragent_api/config.py
    - services/api/src/caragent_api/routes/operations.py
    - services/api/src/caragent_api/schemas.py
    - services/worker/src/caragent_worker/config.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts
    - scripts/check-contracts.mjs
    - .env.example
    - services/api/.env.example
    - services/worker/.env.example
    - services/api/tests/test_config.py
    - services/api/tests/test_operations.py
    - services/worker/tests/test_config.py

key-decisions:
  - "Expose provider capabilities as browser-safe dictionaries first; no database table is needed for Phase 9 capability metadata."
  - "Treat BFL as callable only when V2 hosted rollout, provider calls, credentials, and all hosted quota/rate/cost guards are configured."
  - "Keep actual secret values out of settings capability maps and operations responses; expose only credential_configured booleans."

patterns-established:
  - "ApiSettings and WorkerSettings both expose `provider_capability_map()` backed by `caragent_core.provider_capabilities`."
  - "Operations provider status includes `capabilities` and `guard_state` while preserving legacy summary fields."
  - "Contract checks may require unsandboxed execution on Windows because the check script spawns local `corepack pnpm generate`."

requirements-completed:
  - V2-PROVIDER-01
  - V2-PROVIDER-05

duration: 19 min
completed: 2026-06-18
---

# Phase 9 Plan 01: Hosted Provider Capability Configuration Summary

**Browser-safe provider capability map with BFL guard metadata, operations exposure, generated contracts, and default-off env examples**

## Performance

- **Duration:** 19 min
- **Started:** 2026-06-18T08:10:48Z
- **Completed:** 2026-06-18T08:29:22Z
- **Tasks:** 4
- **Files modified:** 14

## Accomplishments

- Added a shared `provider_capability_map()` path for API and worker settings, backed by a core capability builder for local deterministic and BFL providers.
- Extended `/operations/provider-status` with safe `capabilities` and `guard_state` metadata for UI selector/preflight work.
- Added focused API/worker tests proving local default safety, hosted BFL blocked reasons, guard metadata, and secret-free response surfaces.
- Updated OpenAPI and generated TypeScript contracts with the new operations fields.
- Documented manual hosted BFL smoke overrides in root/API/worker env examples while keeping all V2 hosted behavior disabled by default.

## Task Commits

1. **Task 1: Add red tests for provider capability defaults and safe operations metadata** - `56e71f7` (test)
2. **Task 2: Implement typed provider capability map** - `dd10b26` (feat)
3. **Task 3: Expose capability and guard status through operations API** - `f02b773` (fix), `57feca6` (chore)
4. **Task 4: Document default-off hosted provider configuration** - `a8847df` (docs)

## Files Created/Modified

- `services/core/src/caragent_core/provider_capabilities.py` - Shared browser-safe capability builder and guard-state formatter.
- `services/api/src/caragent_api/config.py` - API provider model setting and capability map method.
- `services/worker/src/caragent_worker/config.py` - Worker capability map method using server-only credential checks.
- `services/api/src/caragent_api/routes/operations.py` - Provider summary now includes capability list, guard state, active mode, and blocked reasons.
- `services/api/src/caragent_api/schemas.py` - Operations provider schema includes `capabilities` and `guard_state`.
- `packages/contracts/openapi/openapi.json` and `packages/contracts/src/generated/client.ts` - Generated contract artifacts for the operations schema.
- `scripts/check-contracts.mjs` - Windows fallback for locating `corepack` before using deterministic fallback generation.
- `.env.example`, `services/api/.env.example`, `services/worker/.env.example` - Default-off hosted provider guard and manual smoke examples.
- `services/api/tests/test_config.py`, `services/api/tests/test_operations.py`, `services/worker/tests/test_config.py` - Focused capability, guard, and redaction tests.

## Decisions Made

- Capability metadata stays in code/config for Phase 9; there is no database-backed capability registry yet.
- BFL can appear as a supported provider while still blocked. The `enabled` flag and `blocked_reasons` explain whether it is callable.
- `active_mode` remains `local-deterministic` unless BFL is selected and all hosted gates are complete.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Contract check fallback overwrote full Orval client on Windows**

- **Found during:** Task 3 (Expose capability and guard status through operations API)
- **Issue:** `corepack pnpm contracts:check` ran `check-contracts.mjs`; the script could not spawn `corepack` from `dirname(process.execPath)` in this Windows sandbox and fell back to a deterministic health-only client generator, making the generated client look stale and incomplete.
- **Fix:** Updated `scripts/check-contracts.mjs` to use the bundled `corepack.cmd` when it exists and otherwise fall back to `corepack` from PATH. Regenerated the full Orval client and reran contract check with sandbox escalation so the script could spawn local generation.
- **Files modified:** `scripts/check-contracts.mjs`, `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/client.ts`
- **Verification:** `corepack pnpm contracts:check` passed with escalated execution.
- **Committed in:** `f02b773` and `57feca6`

---

**Total deviations:** 1 auto-fixed (1 blocking).
**Impact on plan:** No product-scope expansion. The fix was required to trust contract verification on Windows.

## Issues Encountered

- `uv run python -m caragent_api.scripts.export_openapi` needed sandbox escalation because local `uv` cache access was denied under the managed sandbox.
- `corepack pnpm contracts:check` needed sandbox escalation because the check script spawns local `corepack pnpm generate` via Node child process.

## Verification

- Red tests failed first:
  - `cd services/api && uv run pytest -q tests/test_config.py tests/test_operations.py` failed on missing `provider_capability_map`, `guard_state`, and `capabilities`.
  - `cd services/worker && uv run pytest -q tests/test_config.py` failed on missing `provider_capability_map`.
- Green verification passed:
  - `cd services/api && uv run pytest -q tests/test_config.py tests/test_operations.py`
  - `cd services/worker && uv run pytest -q tests/test_config.py`
  - `cd services/core && uv run ruff check .`
  - `cd services/api && uv run ruff check .`
  - `cd services/worker && uv run ruff check .`
  - `corepack pnpm contracts:check`
  - `Select-String -Path .env.example,services/api/.env.example,services/worker/.env.example -Pattern "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED","AI_PROVIDER_CALLS_ENABLED","BFL","quota","cost"`

## User Setup Required

None - no external service configuration required. Hosted BFL smoke remains documented as manual-only and disabled by default.

## Next Phase Readiness

Ready for `09-02-PLAN.md`: BFL adapter work can consume the capability map, BFL model defaults, guard metadata, and contract-safe operations fields.

## Self-Check: PASSED

- Key files exist: PASS.
- Task acceptance criteria verified: PASS.
- Plan-level verification commands passed: PASS.
- Summary requirements match plan frontmatter: PASS.

---
*Phase: 09-hosted-provider-rollout-mvp*
*Completed: 2026-06-18*
