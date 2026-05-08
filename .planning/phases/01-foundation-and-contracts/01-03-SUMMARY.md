---
phase: 01-foundation-and-contracts
plan: "03"
subsystem: worker
tags: [celery, redis, pydantic-settings, pytest, ruff, mypy, uv]
requires:
  - phase: 01-01
    provides: Root command surface, runtime pins, and worker command delegation.
provides:
  - Separate uv-managed Celery worker project under services/worker.
  - Typed worker settings for runtime mode, Redis broker URL, and provider key entries.
  - No-op worker health task for boot/import validation without provider or database calls.
  - Tests for settings parsing, secret redaction, Celery app shape, health payload, and API/provider import boundaries.
affects: [phase-01-foundation, services-worker, local-validation, future-generation-workers]
tech-stack:
  added: [celery, redis, pydantic, pydantic-settings, pytest, ruff, mypy, hatchling]
  patterns:
    - Worker settings live in a central pydantic-settings object and are cached through get_settings().
    - Non-local worker runtimes must provide REDIS_URL explicitly instead of inheriting local broker defaults.
    - Worker tasks stay in caragent_worker.tasks and do not import FastAPI/API/provider modules.
key-files:
  created:
    - services/worker/pyproject.toml
    - services/worker/README.md
    - services/worker/src/caragent_worker/__init__.py
    - services/worker/src/caragent_worker/config.py
    - services/worker/src/caragent_worker/app.py
    - services/worker/src/caragent_worker/tasks/__init__.py
    - services/worker/src/caragent_worker/tasks/health.py
    - services/worker/tests/test_config.py
    - services/worker/tests/test_worker_app.py
  modified: []
key-decisions:
  - "Pinned the worker manifest directly instead of creating a lockfile because uv is unavailable in this sandbox."
  - "Required REDIS_URL outside local runtime mode to prevent local broker defaults from leaking into non-local workers."
  - "Kept worker health as a static no-op Celery task with no provider, database, artifact, upload, export, or API imports."
patterns-established:
  - "Worker configuration pattern: WorkerSettings owns environment parsing, SecretStr provider key redaction, and non-local queue validation."
  - "Worker boundary pattern: tests and source scans enforce no caragent_api, FastAPI, or provider SDK imports in services/worker/src."
requirements-completed: [FOUND-01, FOUND-02, FOUND-04]
duration: 21min
completed: 2026-05-08
---

# Phase 1 Plan 03: Worker Foundation Summary

**Celery worker boot path with typed Redis/provider settings, secret redaction tests, and API/provider import boundary checks.**

## Performance

- **Duration:** 21 min
- **Started:** 2026-05-08T08:08:11Z
- **Completed:** 2026-05-08T08:29:01Z
- **Tasks:** 2
- **Files modified:** 9

## Accomplishments

- Created `services/worker` as a separate Python worker project with Celery, Redis, pydantic-settings, ruff, mypy, and pytest manifest entries.
- Implemented `WorkerSettings` with `RUNTIME_MODE`, `REDIS_URL`, and provider key env parsing, using `SecretStr` for redaction.
- Added a Celery app named `caragent_worker` configured from `settings.redis_url`.
- Added a no-op `worker_health` task that returns local status without external calls.
- Added tests for settings behavior, secret redaction, Celery app shape, health payload, and worker/API/provider boundary enforcement.

## Task Commits

TDD tasks used RED and GREEN commits:

1. **Task 1 RED: Worker settings tests** - `6de3f1a` (test)
2. **Task 1 GREEN: Worker settings foundation** - `3715767` (feat)
3. **Task 2 RED: Worker app tests** - `9d38659` (test)
4. **Task 2 GREEN: Celery worker boot path** - `b68c7db` (feat)

## Files Created/Modified

- `services/worker/pyproject.toml` - Worker package manifest, pinned dependencies, and pytest/ruff/mypy configuration.
- `services/worker/README.md` - Local worker commands, config variables, local-only Redis defaults, and Phase 1 scope boundaries.
- `services/worker/src/caragent_worker/__init__.py` - Worker package marker and version.
- `services/worker/src/caragent_worker/config.py` - `WorkerSettings` and cached `get_settings()`.
- `services/worker/src/caragent_worker/app.py` - Celery app object exported as `celery_app`.
- `services/worker/src/caragent_worker/tasks/__init__.py` - Worker task package marker.
- `services/worker/src/caragent_worker/tasks/health.py` - No-op `worker_health` Celery task.
- `services/worker/tests/test_config.py` - Settings parsing, secret redaction, and non-local Redis validation tests.
- `services/worker/tests/test_worker_app.py` - Celery app, health task, and boundary tests.

## Decisions Made

- Used exact dependency pins in `pyproject.toml` and did not create a lockfile because `uv` is not installed in this environment.
- Treated package patch checks as PyPI page checks only; `uv`/resolver validation must be run later on a host with `uv` and network/package-cache access.
- Required explicit `REDIS_URL` for every runtime mode other than `local`.
- Kept the health task purely local: it reports status and does not touch Redis, databases, object storage, provider SDKs, or product job state.

## Verification

- **BLOCKED:** `cd services/worker; uv run ruff check .` - `uv` is not installed in this sandbox.
- **BLOCKED:** `cd services/worker; uv run mypy src` - `uv` is not installed in this sandbox.
- **BLOCKED:** `cd services/worker; uv run pytest -q` - `uv` is not installed in this sandbox.
- **PASS:** `cd services/worker; python -m pytest -q tests/test_config.py` - 3 settings tests passed with the ambient Python packages.
- **BLOCKED:** `cd services/worker; python -m pytest -q` - ambient Python lacks `celery`; the manifest declares it for the intended `uv sync --dev` path.
- **PASS:** plan boundary scan command over `services/worker/src` found no `caragent_api`, provider SDK, or forbidden worker API/provider imports.
- **PASS:** `cd services/worker; python -m compileall -q src tests` completed successfully.
- **PASS:** file/export checks confirmed `celery_app`, `WorkerSettings`, `get_settings`, `settings.redis_url`, `caragent_worker.tasks.health`, and `worker_health` are present.

## Deviations from Plan

None - implementation scope followed the plan exactly. Full `uv run` verification and resolver-backed package validation were blocked by the sandbox environment, not by code changes.

## Issues Encountered

- `uv` is not installed, so the required `uv run ruff`, `uv run mypy`, `uv run pytest`, and resolver-backed dependency checks could not execute.
- Ambient Python has `pytest`, `pydantic`, and `pydantic-settings`, but not `celery`, so only settings tests and static checks could run locally.
- Git continued to warn about inaccessible user-level git ignore config at `C:\Users\25858/.config/git/ignore`; repository-scoped git commands still succeeded.

## Known Stubs

None. The no-op `worker_health` task is the intended Phase 1 boot/import probe, not a product job implementation.

## Threat Flags

None. The new env and worker-to-Redis surfaces are covered by the plan threat model.

## User Setup Required

Install or enable `uv`, then run from `services/worker`:

```powershell
uv sync --dev
uv run ruff check .
uv run mypy src
uv run pytest -q
```

## Next Phase Readiness

Ready for later Phase 1 plans that need the worker command surface. Aggregate validation should re-run the blocked `uv` commands once the worker dependencies are installed.

## Self-Check: PASSED

- Verified all created worker files and the summary exist on disk.
- Verified task commits `6de3f1a`, `3715767`, `9d38659`, and `b68c7db` exist in git history.
- Verified only the summary plus untracked seed files `UI.png` and `init.MD` remained unstaged before the metadata commit.

---
*Phase: 01-foundation-and-contracts*
*Completed: 2026-05-08*
