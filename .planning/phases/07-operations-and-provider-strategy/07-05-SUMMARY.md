---
phase: 07-operations-and-provider-strategy
plan: "05"
subsystem: provider-retry-fallback
tags: [worker, provider, retry, fallback, operations]

requires:
  - phase: "07-03"
    provides: failure classification and retry eligibility categories
  - phase: "07-04"
    provides: cancellation guards that attempt orchestration must respect
provides:
  - bounded provider attempt settings
  - provider-name routing validation
  - transient provider retry loop
  - visible local fallback after hosted provider failure
  - per-attempt model-run records
affects:
  - phase-07-06-quota-rate-limit
  - phase-07-07-workbench-operations-ui

tech-stack:
  patterns:
    - one `ModelRun` row is created per provider attempt
    - retry eligibility is based on classified provider/timeout categories only
    - fallback metadata is persisted into artifact metadata, version parameters, and job operations metadata

key-files:
  modified:
    - .env.example
    - docs/development.md
    - services/worker/.env.example
    - services/worker/src/caragent_worker/config.py
    - services/worker/src/caragent_worker/providers/__init__.py
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/worker/tests/test_config.py
    - services/worker/tests/test_image_providers.py
    - services/worker/tests/test_generation_tasks.py

key-decisions:
  - "Local deterministic generation remains the safe default with `AI_GENERATION_MAX_ATTEMPTS=1` and fallback disabled."
  - "Unsupported hosted provider names fail fast when hosted calls are enabled instead of silently falling back to local."
  - "Only `provider` and `timeout` categories are retry/fallback eligible."
  - "Provider configuration, rights/validation, storage, unknown, and canceled categories do not retry."
  - "v1 supports only local deterministic fallback, even though BFL remains the only hosted adapter."

patterns-established:
  - "Provider routing accepts explicit provider names for primary and fallback execution."
  - "Fallback is represented as a successful local attempt plus a preserved failed hosted model run."
  - "Success operations metadata can carry provider attempt information, not only failure details."

requirements-completed:
  - OPS-03 partial
  - OPS-02 partial
  - OPS-04 partial

duration: 45 min
completed: 2026-06-18
---

# Phase 7 Plan 05: Provider Retry And Fallback Summary

**Provider routing, retries, and fallback are now config-driven, bounded, and visible in durable records.**

## Accomplishments

- Added worker settings for `AI_GENERATION_MAX_ATTEMPTS`, `AI_PROVIDER_FALLBACK_ENABLED`, and `AI_PROVIDER_FALLBACK_NAME`.
- Added fallback-name validation and documented the new env values in root/worker examples and development docs.
- Refactored provider selection to support explicit provider names and fail fast for unsupported hosted providers.
- Added one-model-run-per-attempt orchestration in generation workers.
- Added retry behavior for transient provider and timeout categories only.
- Added local deterministic fallback after eligible hosted provider failures when fallback is explicitly enabled.
- Persisted fallback and attempt metadata into model runs, generated artifact metadata, design version parameters, and successful job operations metadata.
- Preserved cancellation guards so canceled jobs still stop before provider/storage/success side effects.

## Verification

- RED: `uv run pytest -q tests/test_config.py tests/test_image_providers.py -k "provider or fallback or attempts"` in `services/worker` failed because settings and explicit provider routing did not exist.
- GREEN: same settings/provider focused command passed, 15 tests.
- RED: `uv run pytest -q tests/test_generation_tasks.py -k "falls_back or retries"` in `services/worker` failed because provider failures stopped the job immediately.
- GREEN: `uv run pytest -q tests/test_generation_tasks.py -k "falls_back or retries or provider_configuration_failure or rights"` passed, 6 tests.
- `uv run pytest -q tests/test_config.py tests/test_image_providers.py tests/test_generation_tasks.py` in `services/worker` passed, 32 tests.
- `uv run ruff check .` in `services/worker` passed.
- `uv run mypy src` in `services/worker` passed with escalation for the Windows `uv` cache permission issue.
- `corepack pnpm exec node scripts/check-env-examples.mjs` passed.

## Deviations from Plan

- Fallback target support is intentionally narrower than the setting name suggests: v1 validates fallback to local deterministic only.
- Retry/fallback changes did not require API schema or generated TypeScript contract updates because the durable visibility is stored in existing metadata fields.
- Rights-failure no-retry coverage was added by increasing the rights test attempt count rather than adding a duplicate rights-only test.

## Next Plan Readiness

Ready for `07-06`: hosted-call quota and rate-limit preflight.
