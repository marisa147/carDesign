---
phase: 14-v2-mvp-hardening-docs-smoke-and-uat
plan: "04"
subsystem: browser-uat
tags: [release, browser, uat, desktop, mobile, evidence]
requires:
  - phase: 14-v2-mvp-hardening-docs-smoke-and-uat
    plan: "01"
    provides: release baseline validation
  - phase: 14-v2-mvp-hardening-docs-smoke-and-uat
    plan: "02"
    provides: docker smoke evidence
  - phase: 14-v2-mvp-hardening-docs-smoke-and-uat
    plan: "03"
    provides: hosted smoke runbook
provides:
  - Desktop V2 browser UAT evidence
  - Mobile V2 browser UAT evidence
  - Hosted guard visual evidence
  - Targeted edit/reference/3D/handoff release screenshots
affects: [phase-14, release-uat, web-workbench]
tech-stack:
  added: []
  patterns:
    - Use provider-off seeded browser fixtures for release UAT when paid hosted credentials are not available.
    - Capture viewport metrics with screenshots so responsive pass/fail is evidence-backed.
key-files:
  created:
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-HUMAN-UAT.md
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-04-SUMMARY.md
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-uat-seed.json
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-browser-metrics.json
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-desktop-2d-zip.png
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-desktop-operations-guard.png
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-desktop-targeted-compare.png
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-desktop-3d.png
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-mobile-2d-zip.png
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-mobile-3d.png
  modified:
    - .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-VALIDATION.md
    - .planning/STATE.md
key-decisions:
  - "Phase 14 browser UAT uses a no-secret provider-off fixture and direct headless Chrome CDP screenshots after the in-app Browser could not write localStorage for seeded workspace restore."
requirements-progress: ["V2-REL-04", "V2-REL-05"]
requirements-completed: []
duration: 35 min
completed: 2026-06-19
---

# Phase 14 Plan 04 Summary

**Desktop and mobile browser UAT passed**

## Performance

- **Duration:** 35 min
- **Started:** 2026-06-19T11:00:00Z
- **Completed:** 2026-06-19T11:35:00Z
- **Tasks:** 4
- **Files modified:** 4 plus evidence files

## Accomplishments

- Started Docker-backed local services and applied Alembic migrations.
- Seeded a no-secret V2 UAT workspace with generated version, targeted child version, references, screenshot artifact, feedback, and enhanced ZIP export evidence.
- Started provider-off API on `127.0.0.1:8140` and web on `127.0.0.1:3140` with V2 public flags enabled.
- Captured desktop and mobile full-page screenshots for 2D/ZIP, 3D, hosted guard, and targeted comparison states.
- Recorded DOM metrics proving no horizontal overflow at desktop or mobile widths.
- Documented UAT limitations honestly: no hosted calls, no real credentials, worker not started for browser UAT, and direct CDP used after in-app Browser localStorage limitation.

## Verification

- API health check - passed.
- Web 200 check - passed.
- Browser screenshots saved under `evidence/` - passed.
- Browser metrics saved in `phase14-browser-metrics.json` - passed.
- `Test-Path .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-HUMAN-UAT.md` - passed.
- `Get-ChildItem .planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence` - passed.
- `git diff --check` - passed.

## Deviations from Plan

### Browser driver

**1. In-app Browser could not restore the seeded workspace**
- **Found during:** Task 2.
- **Issue:** The in-app Browser could inspect the page, but its read-only evaluate scope could not write `localStorage`.
- **Fix:** Used direct headless Chrome CDP on `127.0.0.1:9240`, matching the Phase 12/13 evidence pattern.
- **Verification:** Screenshots and metrics were captured from the same local API/web services.
- **Committed in:** this evidence commit.

### Runtime

**2. Next.js dev startup required escalation**
- **Found during:** Task 1.
- **Issue:** Sandbox execution hit `spawn EPERM` when Next tried to spawn a dev child process.
- **Fix:** Restarted the same Next command with approved escalation.
- **Verification:** Web returned 200 and screenshots loaded from `127.0.0.1:3140`.
- **Committed in:** this evidence commit.

## Issues Encountered

- `provider-status` needed a longer timeout while Celery inspect determined no worker was available. The resulting safe UI state is captured in the operations guard screenshot.

## Next Phase Readiness

Ready for 14-05 documentation/release-note hardening.

---
*Phase: 14-v2-mvp-hardening-docs-smoke-and-uat*
*Completed: 2026-06-19*
