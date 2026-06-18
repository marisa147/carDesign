---
phase: 07-operations-and-provider-strategy
plan: "03"
subsystem: worker-failure-classification
tags: [worker, failures, operations, metadata, provider]

requires:
  - phase: "07-01"
    provides: core failure categories and metadata transition support
  - phase: "07-02"
    provides: operations API recent failure surface
provides:
  - worker failure category classifier
  - structured terminal failure metadata
  - provider/configuration/timeout/rights/storage classification tests
  - operations API fallback tests for legacy failures
affects:
  - phase-07-04-cancellation
  - phase-07-05-retry-fallback
  - phase-07-07-workbench-operations-ui

tech-stack:
  patterns:
    - worker tracks the current pipeline stage and provider/model before failure
    - all terminal worker failures write `operations` metadata through core job transitions
    - operations API treats missing legacy metadata as `unknown`

key-files:
  modified:
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/worker/tests/test_generation_tasks.py
    - services/api/tests/test_operations.py

key-decisions:
  - "Provider timeout/configuration/provider errors are classified before the generic provider base class."
  - "Rights failures are mapped from `PermissionError` to `validation_rights`."
  - "Storage failures are identified by the `storage_put` stage or `OSError`."
  - "Failure metadata includes `error`, `failure_category`, `stage`, `provider`, `model`, and `worker_version`."

patterns-established:
  - "Tests assert job metadata, final event metadata, model-run error, and secret redaction together."
  - "Recent failure API tests cover both classified current failures and legacy unknown failures."

requirements-completed:
  - OPS-02 partial
  - OPS-04 partial

duration: 25 min
completed: 2026-06-18
---

# Phase 7 Plan 03: Failure Classification Summary

**Worker failures are now classified and written as structured operational metadata.**

## Accomplishments

- Added failing worker tests for provider, timeout, provider configuration, rights, and storage failures.
- Added a worker failure classifier mapping exceptions/stages to `FailureCategory`.
- Added worker stage tracking for job start, brief load, prompt planning, rights check, provider generation, storage write, and version writes.
- Added terminal failure metadata with category, stage, provider, model, worker version, and sanitized error.
- Preserved secret redaction across `latest_error`, model-run error, job metadata, and event metadata.
- Extended operations API tests to prove legacy failed jobs without metadata fall back to `unknown` and that categorized failures remain sorted newest first.

## Verification

- RED: `uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py -k "failure or timeout or rights or storage"` in `services/worker` failed as expected because operations metadata was missing.
- GREEN: same worker focused command passed, 6 tests.
- `uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py` in `services/worker` passed, 15 tests.
- `uv run ruff check .` in `services/worker` passed.
- `uv run mypy src` in `services/worker` passed after a small metadata type annotation fix and escalation for the Windows `uv` cache permission issue.
- `uv run pytest -q tests/test_operations.py` in `services/api` passed, 6 tests.
- `uv run pytest -q tests/test_operations.py tests/test_openapi_export.py` in `services/api` passed, 9 tests.
- `uv run ruff check .` in `services/api` passed.
- `uv run mypy src` in `services/api` passed with escalation for the Windows `uv` cache permission issue.

## Deviations from Plan

- Classification was implemented in the worker task module, not provider base, because the worker has the stage context needed to distinguish storage and rights failures.
- No API schema or contract regeneration was needed in this plan; operations response schemas were already present from 07-02.

## Next Plan Readiness

Ready for `07-04`: job cancellation and queue revoke handoff.
