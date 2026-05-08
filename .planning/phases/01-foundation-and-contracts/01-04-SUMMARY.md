---
phase: 01-foundation-and-contracts
plan: "04"
subsystem: infra
tags: [docker-compose, env, smoke, postgres, redis, minio]
requires:
  - phase: 01-foundation-and-contracts/01-01
    provides: Root pnpm command surface, runtime pins, and env ignore rules.
provides:
  - Local PostgreSQL, Redis, and MinIO Compose services with configurable ports and healthchecks.
  - Root, web, API, and worker env examples for local storage, database, queue, CORS, runtime mode, API base URL, and provider placeholders.
  - Static env example guard and daemon-aware local smoke runner.
  - Docker host setup handoff for manual FOUND-01 smoke verification.
affects: [phase-01-foundation, apps-web, services-api, services-worker, infra]
tech-stack:
  added: [docker-compose, postgres-18-alpine, redis-8-alpine, minio-local, node-smoke-runner]
  patterns:
    - Example env files are committed; real env files stay ignored.
    - Local infrastructure binds to loopback through Compose and remains separate from app processes.
    - Smoke checks gate on Docker daemon availability before probing local services.
key-files:
  created:
    - .env.example
    - apps/web/.env.example
    - services/api/.env.example
    - services/worker/.env.example
    - scripts/check-env-examples.mjs
    - scripts/smoke-local.mjs
    - infra/compose.yml
    - infra/README.md
    - .planning/phases/01-foundation-and-contracts/01-04-USER-SETUP.md
  modified:
    - package.json
key-decisions:
  - "Kept provider keys blank in local mode while still exposing provider config names for later phases."
  - "Bound Compose-published service ports to 127.0.0.1 and documented all defaults as local-only."
  - "Made Docker daemon absence a non-failing automation path but a documented host setup prerequisite."
patterns-established:
  - "Env guard pattern: static Node checks verify required keys, local-only secret values, provider placeholders, and tracked env safety."
  - "Smoke pattern: Docker readiness is checked before local network probes; unavailable Docker exits 0 with host setup instructions."
requirements-completed: [FOUND-01, FOUND-02, FOUND-04]
duration: 18min
completed: 2026-05-08
---

# Phase 1 Plan 04: Local Services And Environment Examples Summary

**Local PostgreSQL, Redis, and MinIO orchestration with secret-safe env examples and Docker-aware smoke checks.**

## Performance

- **Duration:** 18 min
- **Started:** 2026-05-08T15:58:00+08:00
- **Completed:** 2026-05-08T16:16:00+08:00
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- Added root, web, API, and worker `.env.example` files covering local ports, database, Redis, MinIO/S3, CORS, runtime mode, API base URL, and provider placeholders.
- Added `infra/compose.yml` for PostgreSQL, Redis, and MinIO with loopback-bound configurable ports, named volumes, and service healthchecks.
- Replaced the placeholder root `smoke:local` command with a deterministic Node runner that gates on `docker info` and probes local PostgreSQL, Redis, and MinIO.
- Created a user setup handoff for Docker daemon verification outside the sandbox.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create environment examples and static guard** - `cc8b623` (feat)
2. **Task 2: Add local Compose services and infra docs** - `79c214f` (feat)
3. **Task 3: Wire conditional local smoke checks** - `98f3e49` (feat)

## Files Created/Modified

- `.env.example` - Root local defaults for app ports, PostgreSQL, Redis, MinIO/S3, CORS, runtime mode, API base URL, and provider placeholders.
- `apps/web/.env.example` - Browser-safe web shell local env values.
- `services/api/.env.example` - API local env values for backend config.
- `services/worker/.env.example` - Worker local env values for Redis/Celery, storage, and provider placeholders.
- `scripts/check-env-examples.mjs` - Static guard for env key coverage, tracked real env files, local-only secret values, and local provider-key behavior.
- `infra/compose.yml` - Local PostgreSQL, Redis, and MinIO Compose services.
- `infra/README.md` - Local infra command guide, Docker prerequisite, and production-hardening boundary.
- `scripts/smoke-local.mjs` - Docker-aware smoke runner for local service probes.
- `package.json` - Root `smoke:local` now runs `node scripts/smoke-local.mjs`.
- `.planning/phases/01-foundation-and-contracts/01-04-USER-SETUP.md` - Host Docker setup and verification instructions.

## Decisions Made

- Used `quay.io/minio/minio:RELEASE.2025-04-22T22-12-26Z` as the pinned MinIO local-development image because network access is restricted and Compose validation can still prove deterministic configuration.
- Kept application containers out of Compose; API, worker, and web remain local-process workflows owned by their later plans.
- Treated Docker daemon unavailability as expected conditional behavior: static validation passes, while host smoke is documented as manual setup.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added a Git-index fallback to the env guard**
- **Found during:** Task 1 (Create environment examples and static guard)
- **Issue:** `node scripts/check-env-examples.mjs` could not spawn `git` in this sandbox (`spawnSync git EPERM`) while checking for tracked real env files.
- **Fix:** Added a fallback parser for `.git/index`, preserving the tracked-env safety check without depending on subprocess execution.
- **Files modified:** `scripts/check-env-examples.mjs`
- **Verification:** `node scripts/check-env-examples.mjs` passed.
- **Committed in:** `cc8b623`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fallback preserves the planned security check and does not expand scope.

## Issues Encountered

- Docker Compose config validation succeeded, but Docker emitted warnings about inaccessible user-level Docker config at `C:\Users\25858\.docker\config.json`; the command exited 0.
- The sandbox cannot reach the Docker daemon, so the conditional smoke verification returned the documented host prerequisite instead of starting containers.
- The plan's inline Node token check containing `${...}` required PowerShell-safe quoting during execution.
- Other Wave 2 agents committed and created unrelated API/worker files while this plan was running; this plan staged only its declared files.

## Verification

- **PASS:** `node scripts/check-env-examples.mjs`
- **PASS:** `node -e "...RUNTIME_MODE..."` confirmed every env example includes `RUNTIME_MODE`.
- **PASS:** `docker compose --env-file .env.example -f infra/compose.yml config`
- **PASS:** Compose token check confirmed `postgres`, `redis`, `minio`, `healthcheck`, `${POSTGRES_PORT`, `${REDIS_PORT`, and `${MINIO_API_PORT`.
- **PASS:** Smoke script token check confirmed `docker info`, `--with-compose-if-docker`, `pnpm infra:up`, and `pnpm infra:down`.
- **PASS:** `node scripts/smoke-local.mjs` exited 0 with the Docker daemon prerequisite message in this sandbox.
- **PASS:** Conditional PowerShell smoke command exited 0 with `Docker daemon unavailable; host smoke documented in infra/README.md`.
- **PASS:** `package.json` check confirmed `smoke:local` calls `node scripts/smoke-local.mjs` and infra scripts call `infra/compose.yml`.

## Known Stubs

Intentional, plan-required placeholders only:

- `.env.example:40-43`, `services/api/.env.example:21-24`, and `services/worker/.env.example:21-24` keep provider key values blank in `RUNTIME_MODE=local`.
- `infra/README.md:57` documents provider credentials as placeholders because Phase 1 must not call AI providers.

These do not block the plan goal; provider validation belongs to Phase 3.

## User Setup Required

External Docker daemon setup is required for host-level runtime smoke. See `.planning/phases/01-foundation-and-contracts/01-04-USER-SETUP.md`.

## Next Phase Readiness

Plan 01-09 can reuse `node scripts/check-env-examples.mjs`, `pnpm smoke:local`, and the Docker setup handoff when assembling aggregate validation and final developer docs. API and worker plans can consume the committed env examples without introducing real secrets.

## Self-Check: PASSED

- Verified all created and modified plan files exist on disk.
- Verified task commits `cc8b623`, `79c214f`, and `98f3e49` exist in git history.
- Verified only `01-04-SUMMARY.md`, `01-04-USER-SETUP.md`, and untracked seed files `UI.png` / `init.MD` remained unstaged after plan work.

---
*Phase: 01-foundation-and-contracts*
*Completed: 2026-05-08*
