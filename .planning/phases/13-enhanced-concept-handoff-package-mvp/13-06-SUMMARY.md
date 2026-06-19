---
phase: 13-enhanced-concept-handoff-package-mvp
plan: "06"
subsystem: handoff-guardrails
tags: [handoff, rights, source, api, web]
requires:
  - phase: 13-enhanced-concept-handoff-package-mvp
    plan: "04"
    provides: feature-gated enhanced handoff export API
  - phase: 13-enhanced-concept-handoff-package-mvp
    plan: "05"
    provides: Workbench ZIP handoff export mode
provides:
  - server-authoritative rights/source validation for enhanced handoff packages
  - 422 blocked-export API behavior without package artifact/export row creation
  - Workbench blocked state for missing/rejected reference rights/source metadata
  - warning-only Workbench state for missing 3D screenshots
affects: [phase-13, core-handoff, api-export, web-export]
tech-stack:
  added: []
  patterns:
    - core package builder owns authoritative handoff rights/source validation
    - API reuses existing HandoffPackageBuildError to 422 mapping
    - browser readiness mirrors server rules but is not trusted
key-files:
  created: []
  modified:
    - services/core/src/caragent_core/handoff.py
    - services/core/tests/test_jobs.py
    - services/api/tests/test_jobs.py
    - apps/web/src/components/workbench/export-panel.tsx
    - apps/web/src/app/page.test.tsx
key-decisions:
  - "Validate included reference rights/source at the core ZIP builder entrypoint so all package creation paths share the same guardrail."
  - "Block included references unless `rights_status` is `confirmed` and at least one of `source_label` or `source_url` is present."
  - "Keep missing 3D screenshots warning-only in Workbench readiness and package building."
patterns-established:
  - "Tests cover missing rights snapshot, rejected rights status, and missing source fields for both core and API."
  - "Workbench ZIP mode can show blocked readiness while keeping PNG/JPG controls available."
requirements-completed: ["V2-HANDOFF-05", "V2-HANDOFF-02", "V2-HANDOFF-03"]
duration: 10 min
completed: 2026-06-19
---

# Phase 13 Plan 06 Summary

**Rights/source guardrails and blocked export states for enhanced handoff packages**

## Performance

- **Duration:** 10 min
- **Started:** 2026-06-19T08:10:08Z
- **Completed:** 2026-06-19T08:19:54Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments

- Added core tests for missing rights snapshot, rejected rights status, and missing source metadata blocking enhanced ZIP creation.
- Added API tests proving invalid rights/source metadata returns 422, writes no package object, creates no export row, and creates no package artifact.
- Added web tests for visible `缺少版权或来源信息`, disabled `生成交接包`, preserved PNG/JPG controls, and warning-only missing 3D screenshots.
- Implemented `validate_handoff_rights_source()` in `caragent_core.handoff`.
- Called the guardrail before reading/writing package storage, keeping failed exports side-effect free.
- Extended Workbench package readiness rows from boolean to ready/warning/blocked states.
- Added UI text for `缺少版权或来源信息` and `未包含 3D 截图`.

## Task Commits

1. **Task 1: Add red guardrail tests** - `c747cb1` (feat)
2. **Task 2: Implement core/API rights-source guardrails** - `c747cb1` (feat)
3. **Task 3: Implement workbench blocked and warning states** - `c747cb1` (feat)

## Verification

- `cd services/core && uv run pytest -q tests/test_jobs.py` - passed, 17 tests.
- `cd services/api && uv run pytest -q tests/test_jobs.py` - passed, 18 tests.
- `cd services/core && uv run ruff check .` - passed.
- `cd services/api && uv run ruff check .` - passed.
- `corepack pnpm --filter @caragent/web typecheck` - passed.
- `corepack pnpm --filter @caragent/web lint` - passed.
- `corepack pnpm --filter @caragent/web test src/lib/api/iteration.test.ts src/app/page.test.tsx src/lib/api/generation.test.ts` - passed after escalation, 3 files / 52 tests.

## Deviations from Plan

### Implementation

**1. API route did not need a separate validation branch**
- **Found during:** Task 2
- **Issue:** The API already maps `HandoffPackageBuildError` to HTTP 422.
- **Fix:** Centralized validation in the core ZIP builder before storage reads/writes; API behavior became correct through the existing error boundary.
- **Files modified:** `services/core/src/caragent_core/handoff.py`
- **Verification:** API tests assert 422 plus no export/package side effects.
- **Committed in:** `c747cb1`

### Environment

**1. Vitest needed elevated execution**
- **Found during:** Web verification
- **Issue:** Sandbox execution cannot spawn esbuild for Vitest config loading.
- **Fix:** Reran the same focused web test command with approved escalation.
- **Files modified:** None.
- **Verification:** Elevated targeted Vitest run passed, 52 tests.
- **Committed in:** N/A

---

**Total deviations:** 1 implementation simplification, 1 environment item.
**Impact on plan:** None. Server-authoritative guardrails and visible Workbench failure states are green.

## Issues Encountered

None beyond the known Windows sandbox/esbuild child-process limitation.

## User Setup Required

No new setup beyond the existing enhanced handoff flags:

- `V2_ENHANCED_HANDOFF_PACKAGE_ENABLED=true`
- `NEXT_PUBLIC_V2_ENHANCED_HANDOFF_PACKAGE_ENABLED=true`

## Next Phase Readiness

Ready for 13-07. Phase 13 now has schema, reports, ZIP packaging, API ledger integration, Workbench UX, and rights/source guardrails; the remaining work is final smoke, docs, manifest validation, and Browser UAT evidence.

---
*Phase: 13-enhanced-concept-handoff-package-mvp*
*Completed: 2026-06-19*
