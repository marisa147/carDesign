---
phase: 01-foundation-and-contracts
plan: "01"
subsystem: foundation
tags: [monorepo, pnpm, uv, docker-compose, developer-docs]
requires: []
provides:
  - Root pnpm workspace and stable command surface for later Phase 1 plans.
  - Repo-visible Node, Python, and package-manager runtime pins.
  - Secret-safe ignore rules and text/binary normalization.
  - README and developer command index for the foundation stack.
affects: [phase-01-foundation, apps-web, services-api, services-worker, packages-contracts, infra]
tech-stack:
  added: [pnpm-workspace, uv-command-delegation, docker-compose-command-delegation]
  patterns:
    - Thin root scripts delegate to owning package or service commands.
    - Python services stay outside the pnpm workspace and are reached through uv.
    - Real env files are ignored while .env.example files remain trackable.
key-files:
  created:
    - package.json
    - pnpm-workspace.yaml
    - .node-version
    - .python-version
    - .gitignore
    - .gitattributes
    - README.md
    - docs/development.md
  modified: []
key-decisions:
  - "Reserved the Phase 1 root command names before downstream package and service scaffolds exist."
  - "Kept Python services uv-managed instead of adding services/* to the pnpm workspace."
  - "Documented local-only infrastructure defaults and deferred product workflows explicitly."
patterns-established:
  - "Root command contract: package.json scripts are stable wrappers around web, API, worker, infra, and contracts owners."
  - "Secret handling: ignore real env and key material, but keep example env files eligible for source control."
requirements-completed: [FOUND-01, FOUND-02]
duration: 4min
completed: 2026-05-08
---

# Phase 1 Plan 01: Repo Tooling And Root Commands Summary

**Root pnpm command surface with runtime pins, secret-safe ignore rules, and a developer command inventory.**

## Performance

- **Duration:** 4 min
- **Started:** 2026-05-08T07:59:23Z
- **Completed:** 2026-05-08T08:03:56Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Created the root `package.json` command surface for web, API, worker, infra, contracts, validation, and local smoke checks.
- Added `pnpm-workspace.yaml` with only `apps/*` and `packages/*`, leaving Python services uv-managed.
- Added runtime pins, ignore rules for real env/secret files, and text/binary normalization.
- Added a README entry point and `docs/development.md` with the required command inventory and Phase 1 boundaries.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create root workspace and command surface** - `a61117b` (feat)
2. **Task 2: Pin runtimes and protect local-only files** - `e7703ea` (chore)
3. **Task 3: Add foundation README and developer command index** - `abe04e3` (docs)

## Files Created/Modified

- `package.json` - Root package-manager pin and command wrappers.
- `pnpm-workspace.yaml` - pnpm workspace membership for `apps/*` and `packages/*`.
- `.node-version` - Node 24.15.0 runtime pin.
- `.python-version` - Python 3.13.13 runtime pin.
- `.gitignore` - Local env, secret, cache, dependency, build, log, and temporary output ignores.
- `.gitattributes` - Text normalization and image binary handling.
- `README.md` - Project entry point and Phase 1 foundation command list.
- `docs/development.md` - Developer prerequisites, repository layout, commands, local services, contracts, validation, security notes, and troubleshooting.

## Decisions Made

- Followed the plan's root command vocabulary exactly so later plans can wire implementations without renaming commands.
- Kept `services/api` and `services/worker` out of `pnpm-workspace.yaml` because they are Python projects managed through `uv`.
- Treated Docker Compose commands and example credentials as local-development only in docs.

## Verification

All task-level automated checks were run after implementation:

- **PASS:** `node -e "...required scripts and packageManager..."` confirmed all required root scripts and `pnpm@11.0.8`.
- **PASS:** `node -e "...workspace membership..."` confirmed `apps/*` and `packages/*`, and rejected `services/*`.
- **PASS:** `node -e "...runtime pins and gitignore tokens..."` confirmed Node 24.15.0, Python 3.13.13, and required ignore tokens.
- **PASS:** `git -c safe.directory=D:/python/carAgent check-ignore .env .env.local apps/web/.env.local services/api/.env services/worker/.env` confirmed real env paths are ignored.
- **PASS:** `.env.example` check confirmed example env files are not ignored.
- **PASS:** `node -e "...developer docs tokens..."` confirmed README project name, required guide sections, and command inventory.
- **PASS:** Stub marker scan across created files returned no matches after docs wording cleanup.
- **PASS:** `git -c safe.directory=D:/python/carAgent status --short` showed only untracked seed files `UI.png` and `init.MD` outside committed plan work.

Full `pnpm validate` was not run in this plan because Plan 01-01 only reserves root command names; the target web, contracts, API, worker, and infra implementations are created by later Phase 1 plans.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Git commands emitted warnings about inaccessible user-level git ignore config at `C:\Users\25858/.config/git/ignore`; the repository-scoped commands still exited successfully.
- The summary stub scan initially matched a docs-only use of the word "placeholder"; the sentence was reworded and Task 3 was amended before finalization.

## Known Stubs

None. The root scripts intentionally reserve command names for later Phase 1 plans; this is the declared output of Plan 01-01, not an incomplete product workflow.

## User Setup Required

No separate user setup file was created for this plan. Runtime prerequisites are documented in `docs/development.md`: Node.js 24.15.0, pnpm 11.0.8, Python 3.13.13, uv, and Docker Compose.

## Next Phase Readiness

Ready for Plan 01-02. The API plan can now rely on root `dev:api`, `lint`, `typecheck`, `test`, `smoke:local`, and `validate` command names being present.

## Self-Check: PASSED

- Verified all created files exist on disk.
- Verified task commits `a61117b`, `e7703ea`, and `abe04e3` exist in git history.
- Verified only the summary plus untracked seed files `UI.png` and `init.MD` remained unstaged before the metadata commit.

---
*Phase: 01-foundation-and-contracts*
*Completed: 2026-05-08*
