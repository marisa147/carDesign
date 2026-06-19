---
phase: 14-v2-mvp-hardening-docs-smoke-and-uat
plan: "03"
subsystem: hosted-smoke-runbook
tags: [release, hosted-provider, smoke, docs, cost-guard]
requires:
  - phase: 14-v2-mvp-hardening-docs-smoke-and-uat
    plan: "01"
    provides: release baseline validation
provides:
  - Manual hosted-provider smoke runbook
  - Secret-safe and cost-guarded one-job hosted smoke checklist
  - Explicit hosted smoke skip posture
affects: [phase-14, release-smoke, hosted-provider-docs]
tech-stack:
  added: []
  patterns:
    - Keep hosted provider smoke manual-only unless real credentials and operator cost approval are available.
    - Treat skipped hosted smoke as acceptable local release evidence only when the skip reason is explicit.
key-files:
  created:
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-HOSTED-SMOKE-RUNBOOK.md
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-03-SUMMARY.md
  modified:
    - docs/development.md
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-VALIDATION.md
    - .planning/STATE.md
key-decisions:
  - "Phase 14 hosted-provider release smoke remains manual-only, credentialed, cost-guarded, one-job limited, and reversible; no live hosted quality/account/pricing/moderation readiness is claimed without evidence."
requirements-progress: ["V2-REL-03", "V2-REL-05"]
requirements-completed: []
duration: 8 min
completed: 2026-06-19
---

# Phase 14 Plan 03 Summary

**Hosted-provider smoke runbook is ready**

## Performance

- **Duration:** 8 min
- **Started:** 2026-06-19T10:52:00Z
- **Completed:** 2026-06-19T11:00:00Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Created the Phase 14 hosted-provider smoke runbook.
- Documented prerequisites for real BFL credentials, account/model access, current pricing/moderation/credit checks, and operator cost approval.
- Limited live smoke to one hosted concept-preview generation or child iteration.
- Added explicit evidence fields for job, model-run, version, artifact, provider/model, quota guards, estimated/actual cost, failures, fallback, operations status, and screenshots/logs.
- Added acceptable skip reasons and reversal steps for disabling hosted flags and returning to local deterministic mode.
- Linked the runbook from `docs/development.md`.
- Marked the 14-03 validation row green for completed manual release documentation.

## Verification

- `rg -n "manual-only|cost approval|AI_PROVIDER_CALLS_ENABLED|AI_HOSTED_DAILY_CALL_LIMIT|AI_MAX_ESTIMATED_COST_PER_JOB|disable hosted|14-HOSTED-SMOKE-RUNBOOK|cost-guarded" ...` - passed.
- `git diff --check` - passed.

## Deviations from Plan

### Hosted provider execution

**1. Live hosted call was not run**
- **Found during:** Task 1.
- **Issue:** No real BFL credential or operator cost approval was provided in this agent session.
- **Fix:** Recorded the skip posture in the runbook evidence table and kept live hosted success unclaimed.
- **Verification:** Documentation token checks passed.
- **Committed in:** this docs commit.

## Issues Encountered

- None.

## Next Phase Readiness

Ready for 14-04 browser UAT across V2 workbench flows.

---
*Phase: 14-v2-mvp-hardening-docs-smoke-and-uat*
*Completed: 2026-06-19*
