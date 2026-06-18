---
phase: 09-hosted-provider-rollout-mvp
plan: "02"
subsystem: worker-provider-adapter
tags: [hosted-provider, bfl, flux2, polling, cost, redaction]

requires:
  - phase: 09-hosted-provider-rollout-mvp
    provides: provider capability map and default-off hosted guard configuration from 09-01
provides:
  - BFL adapter aligned to official x-key auth and FLUX.2 preview submission flow
  - Returned polling_url handling, bounded polling, result download, and provider cost propagation
  - Sanitized provider exceptions carrying normalized provider_status and HTTP status metadata
affects:
  - phase-09-hosted-provider
  - provider-trace-persistence
  - hosted-failure-mapping

tech-stack:
  added: []
  patterns:
    - hosted providers download external result URLs inside the worker before project storage
    - provider exceptions can carry machine-readable provider_status without exposing raw payloads
    - BFL request shape stays inside the ImageProvider boundary

key-files:
  created:
    - .planning/phases/09-hosted-provider-rollout-mvp/09-02-SUMMARY.md
  modified:
    - services/worker/tests/test_image_providers.py
    - services/worker/src/caragent_worker/providers/base.py
    - services/worker/src/caragent_worker/providers/bfl.py
    - services/worker/src/caragent_worker/config.py
    - .env.example
    - services/worker/.env.example

key-decisions:
  - "Use BFL `x-key` auth and `/v1/flux-2-pro-preview` as the default submit path for Phase 9."
  - "Download BFL `result.sample` bytes in the worker and avoid returning signed delivery URLs through provider metadata."
  - "Leave hosted actual_cost null when the provider does not return cost instead of fabricating zero-cost hosted runs."
  - "Keep V2-PROVIDER-03 pending in the main requirement table until 09-04 persists durable trace surfaces."

patterns-established:
  - "BflSubmitInfo captures request_id, polling_url, cost, and safe submit metadata before polling."
  - "ImageProviderError supports optional `provider_status` and `status_code` for downstream classification."
  - "BFL moderation, rate, credit, and HTTP statuses are normalized for later worker/API failure mapping."

requirements-completed:
  - V2-PROVIDER-01
  - V2-PROVIDER-03
  - V2-PROVIDER-05

duration: 5 min
completed: 2026-06-18
---

# Phase 9 Plan 02: BFL Hosted Provider Adapter Summary

**Official-doc BFL FLUX.2 adapter flow with x-key auth, provider polling URL, result-byte download, cost propagation, and sanitized status errors**

## Performance

- **Duration:** 5 min
- **Started:** 2026-06-18T08:33:15Z
- **Completed:** 2026-06-18T08:37:55Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- Added deterministic httpx MockTransport tests for the documented BFL submit, polling, result download, cost, moderation, timeout, and secret-redaction behavior.
- Updated the BFL adapter to use `x-key`, `/v1/flux-2-pro-preview`, returned `polling_url`, bounded polling, and provider-supplied cost.
- Ensured signed BFL delivery URLs are downloaded inside the worker and excluded from returned provider metadata.
- Extended provider exceptions with normalized `provider_status` and `status_code` fields for upcoming trace persistence and failure classification.
- Updated root and worker env examples so manual BFL smoke settings match the FLUX.2 preview endpoint.

## Task Commits

1. **Task 1: Write BFL adapter contract tests from official docs** - `0d318c6` (test)
2. **Task 2: Implement documented submit, polling, download, and cost behavior** - `9d01919` (feat)
3. **Task 3: Normalize BFL provider statuses and sanitized errors** - `9d01919` (feat)

## Files Created/Modified

- `services/worker/tests/test_image_providers.py` - BFL official-flow tests for x-key auth, polling URL usage, result download, cost, timeout, moderation status, and redaction.
- `services/worker/src/caragent_worker/providers/base.py` - Provider errors now carry optional machine-readable provider status and HTTP status.
- `services/worker/src/caragent_worker/providers/bfl.py` - BFL adapter now follows FLUX.2 preview submit/poll/download semantics and returns safe metadata.
- `services/worker/src/caragent_worker/config.py` - Default BFL submit path now targets `/v1/flux-2-pro-preview`.
- `.env.example` and `services/worker/.env.example` - Manual hosted BFL smoke examples now use the FLUX.2 preview endpoint/model.

## Decisions Made

- BFL provider payload construction stays adapter-local. The worker still consumes the generic `ImageGenerationRequest` contract.
- Provider actual cost is trusted only when returned by the provider; missing cost remains null for later persistence instead of becoming fake zero.
- `provider_status` is available for downstream code, but user/API-facing failure taxonomy remains intentionally deferred to 09-05.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- The red tests first failed against the old adapter because it posted to `/v1/flux-pro` with bearer auth and ignored moderated statuses until timeout.
- `uv run ruff check .` caught one unused import during implementation; it was removed before the green commit.

## Verification

- Red tests failed first:
  - `cd services/worker && uv run pytest -q tests/test_image_providers.py` failed on old BFL path/auth and moderation timeout behavior.
- Green verification passed:
  - `cd services/worker && uv run pytest -q tests/test_image_providers.py`
  - `cd services/worker && uv run ruff check .`
  - `Select-String -Path .env.example,services/worker/.env.example -Pattern "AI_PROVIDER_BFL_SUBMIT_PATH","flux-2-pro-preview"`

## User Setup Required

None - no external service configuration required. Hosted BFL calls remain disabled unless the manual Phase 9 smoke flags, credentials, and guard limits are configured.

## Next Phase Readiness

Ready for `09-03-PLAN.md`: hosted preflight integration can rely on the BFL adapter boundary, FLUX.2 defaults, and normalized provider status fields. Durable provider trace and full failure taxonomy remain intentionally scheduled for `09-04-PLAN.md` and `09-05-PLAN.md`.

## Self-Check: PASSED

- Key files exist: PASS.
- Task acceptance criteria verified: PASS.
- Plan-level verification commands passed: PASS.
- Summary requirements match plan frontmatter: PASS.

---
*Phase: 09-hosted-provider-rollout-mvp*
*Completed: 2026-06-18*
