# Phase 5 Verification: Iteration, Feedback, And Concept Export

**Date:** 2026-06-18
**Status:** Passed

## Automated Checks

| Check | Command | Result | Evidence |
|-------|---------|--------|----------|
| Docs token check | `node -e "const fs=require('fs'); const d=fs.readFileSync('docs/development.md','utf8'); for (const t of ['Phase 5','iteration','feedback','concept export','manifest','not print-ready']) if (!d.includes(t)) throw new Error('missing docs token '+t)"` | Passed | Exit 0. |
| API queue regression | `uv run pytest -q tests/test_queue.py` in `services/api` | Passed | 2 tests passed. Covers Redis transport availability and `caragent.default` queue routing. |
| API full tests | `uv run pytest -q` in `services/api` | Passed | 34 tests passed after Redis queue dependency and routing fixes. |
| Worker dependency regression | `uv run pytest -q tests/test_worker_app.py` in `services/worker` | Passed | 5 tests passed. Covers `asyncpg` availability for PostgreSQL-backed generation tasks. |
| Worker generation tests | `uv run pytest -q tests/test_generation_tasks.py` in `services/worker` | Passed | 4 tests passed. |
| Worker lint/typecheck | `uv run ruff check .`; `uv run mypy src` in `services/worker` | Passed | Ruff passed; mypy passed with 10 source files. |
| Contracts drift | `corepack pnpm contracts:check` | Passed | `Contract artifacts are current.` Run with elevated host permissions because sandboxed Node child processes cannot spawn Corepack reliably on this Windows setup. |
| Root aggregate validation | `corepack pnpm validate` | Passed | Web lint/typecheck/test, core/API/worker ruff/mypy/pytest, contracts check, and contracts typecheck all passed. Web tests: 7 files, 38 tests. Core tests: 32. API tests: 34. Worker tests: 23. |
| Docker smoke | `corepack pnpm smoke:local` | Passed | PostgreSQL, Redis, MinIO, Phase 2 durable data smoke, and Phase 3 local deterministic generation smoke passed. |

## Live End-To-End Evidence

Local services were running with FastAPI on `127.0.0.1:8000`, web on `127.0.0.1:3000`, Celery worker consuming `caragent.default`, and Docker PostgreSQL/Redis/MinIO available.

| Flow | Result | Evidence |
|------|--------|----------|
| Initial generation | Passed | Workspace `f4080584-cef6-4067-98d4-7ebfa6204d74`, brief `f2a4a64d-59f5-4213-95f6-cdca156ad666`, job `8cd7c524-d42a-4231-a82d-6b57a8935f36` reached `succeeded`. |
| Durable feedback | Passed | Created one approved feedback record with rating 5 and comment `Phase 5 browser UAT approval.` |
| Concept export | Passed | Created one PNG export for version `15dad87c-ff90-4258-9b94-74bdc33cda4b`, artifact `65fa38d8-ccda-4f42-8a5e-064aaebf157e`, concept label `client-review`, and manifest disclaimer containing `not print-ready`. |
| Child iteration | Passed | Child job `ecec23ac-1648-4044-8cea-049183636ae1` reached `succeeded`; workspace ended with 2 versions and 2 artifacts. |

## Fixes Found During Verification

| Issue | Root Cause | Fix | Regression Evidence |
|-------|------------|-----|---------------------|
| API generation submit returned 500 when using Redis broker. | `services/api` declared Celery but not the Redis transport dependency. | Added `redis==7.4.0` to `services/api/pyproject.toml` and synced lockfile. | `tests/test_queue.py` imports Redis transport and passes. |
| Jobs stayed queued after API submit. | API `send_task()` used the default Celery queue while the worker consumes `caragent.default`. | Added `GENERATION_QUEUE = "caragent.default"` and pass `queue=GENERATION_QUEUE`. | `test_celery_queue_client_sends_generation_task_to_worker_queue` passes; live generation succeeds. |
| Worker accepted a task but failed with `ModuleNotFoundError: asyncpg`. | Worker package did not declare the PostgreSQL async driver required by `postgresql+asyncpg://` URLs. | Added `asyncpg>=0.30,<1` to `services/worker/pyproject.toml` and synced lockfile. | `test_postgres_async_driver_is_available_for_generation_tasks` passes; live worker generation succeeds. |
| Contract artifacts were stale after API changes. | OpenAPI/client artifacts had not been regenerated after the new generation/iteration/export surface. | Re-exported OpenAPI and regenerated Orval client. | `corepack pnpm contracts:check` passes. |

## Browser UAT Summary

Browser UAT ran against `http://127.0.0.1:3000/` using a UI-created workspace that was then populated through the live API/worker flow above.

| Viewport | Result | Evidence |
|----------|--------|----------|
| Desktop default | Passed | Restored workspace shows 2D preview, completed job status, version history, lineage comparison, feedback history, concept export manifest, export history, concept-preview disclaimer, and disabled future gates. No horizontal overflow, no actual section overlap, no fresh console errors. |
| Mobile, 390x844 | Passed | Same Phase 5 surfaces render in the mobile layout. `scrollWidth == clientWidth`, no actual section overlap, no fresh console errors. |

## Requirement Evidence

| Requirement | Status | Evidence |
|-------------|--------|----------|
| ITER-01 | Passed | API child iteration preserves the parent version and creates a new child version; Browser UAT shows version history with both versions. |
| ITER-02 | Passed | Child iteration request records targeted change text and parameter overrides, then worker creates a child design version. |
| ITER-03 | Passed | Workbench comparison panel renders lineage depth, parent/current version context, and parameter differences. |
| ITER-04 | Passed | API and UI support rating, approval/rejection state, comments, and durable feedback history scoped to the selected version. |
| ITER-05 | Passed | API and UI support selected-version concept export with PNG/JPG controls, manifest preview, and export history. |
| ITER-06 | Passed | UI and export manifest label output as concept preview / not print-ready; Browser UAT found no `production-ready` or `生产就绪` claim. |

## Residual Scope

No Phase 5 gaps remain. Print-ready production export, layered design handoff, true 3D UV preview, marketplace/community, provider operations, quotas, cancellation, and production deployment remain later-phase or v2+ scope.
