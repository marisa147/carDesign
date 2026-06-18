---
phase: 09-hosted-provider-rollout-mvp
artifact: verification
created: 2026-06-18T09:33:14Z
mode: provider-off-default
status: passed
external_provider_calls: false
---

# Phase 9 Verification Evidence

Phase 9 verification was run in provider-off mode. No hosted provider credentials were required, no `AI_PROVIDER_BFL_API_KEY` value was used, and no paid external provider call was intentionally made.

## Summary

| Check | Command | Result | Evidence |
|-------|---------|--------|----------|
| API provider/preflight focused tests | `cd services/api && uv run pytest -q tests/test_config.py tests/test_operations.py tests/test_generation.py tests/test_jobs.py` | PASS | 39 passed |
| Worker provider/routing focused tests | `cd services/worker && uv run pytest -q tests/test_config.py tests/test_image_providers.py tests/test_generation_tasks.py` | PASS | 49 passed |
| Web provider selector/diagnostics tests | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/api/generation.test.ts src/lib/api/operations.test.ts` | PASS | 3 files, 31 tests passed |
| Contract drift check | `corepack pnpm contracts:check` | PASS | Contract artifacts are current |
| Provider-off worker smoke wiring | `corepack pnpm smoke:worker -- --dry-run` | PASS | Dry run printed live smoke prerequisites and made no queue/provider call |
| Aggregate validation | `corepack pnpm validate` | PASS | Web lint/type/test, core/API/worker ruff/mypy/pytest, contracts typecheck/check passed |
| Docs token check | `Select-String -Path README.md,docs/development.md -Pattern "Phase 9","hosted provider","provider-off","provider-on","BFL","quota","cost"` | PASS | Required hosted rollout terms present |

## Aggregate Validation Details

`corepack pnpm validate` passed at 2026-06-18T09:33:14Z.

Observed aggregate evidence:

- Host prerequisites check: PASS.
- Env example safety check: PASS.
- Web lint: PASS.
- Web typecheck: PASS.
- Web tests: PASS, 9 files / 51 tests.
- Core ruff: PASS.
- Core mypy: PASS, 17 source files.
- Core pytest: PASS, 38 tests.
- API ruff: PASS.
- API mypy: PASS, 15 source files.
- API pytest: PASS, 57 tests.
- Worker ruff: PASS.
- Worker mypy: PASS, 10 source files.
- Worker pytest: PASS, 58 tests.
- Contracts check: PASS.
- Contracts typecheck: PASS.

Non-blocking warning:

- API pytest emitted an aiosqlite thread-close warning in `tests/test_jobs.py::test_feedback_and_concept_export_can_be_created_through_api`. The command exited 0 and this warning matches a previously observed test-environment cleanup warning, not a hosted provider failure.

## Requirement Evidence

| Requirement | Evidence |
|-------------|----------|
| V2-PROVIDER-01 | API/worker config tests, env example checks, operations capability status tests, contracts check, and docs runbook cover configurable provider credentials/model/capability/timeouts/retry/fallback/quota. |
| V2-PROVIDER-02 | API preflight tests, worker repeated preflight tests, and web selector tests prove hosted intent is submitted only when enabled and allowed. |
| V2-PROVIDER-03 | Worker generation task tests and API job/operations tests prove provider/model/parameters/cost/fallback/failure traces are durable and redacted. |
| V2-PROVIDER-04 | BFL adapter tests, worker failure classification tests, API operations tests, and web diagnostics tests prove provider failures are visible without secrets. |
| V2-PROVIDER-05 | Provider-off tests, local deterministic worker tests, web local selector tests, and smoke dry-run prove local deterministic remains the free default path. |

## Provider-Off Safety

- Default env examples keep `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=false`, `AI_PROVIDER_CALLS_ENABLED=false`, and `AI_PROVIDER_DEFAULT=disabled`.
- Focused tests and aggregate validation did not require hosted credentials.
- `corepack pnpm smoke:worker -- --dry-run` did not enqueue work, call Redis/Celery, or contact a hosted provider.
- Live `pnpm smoke:worker` and browser UAT require running Docker/API/worker/web services and are documented separately.

## Provider-On Manual Status

Live BFL provider-on smoke was not executed in this agent run because no user-approved real BFL credential and cost-spend approval were provided. This is recorded as a manual verification skip, not as hosted output success. The manual provider-on checklist is documented in `docs/development.md` and `.planning/phases/09-hosted-provider-rollout-mvp/09-HUMAN-UAT.md`.

## Sign-Off

- [x] All Phase 9 plans have focused tests or documented host prerequisite gates.
- [x] No default validation path makes external provider calls.
- [x] Contract artifacts are current.
- [x] Local deterministic provider remains green without hosted credentials.
- [x] Provider-on smoke is documented, explicit, cheap, reversible, and marked skipped when credentials/cost approval are absent.
