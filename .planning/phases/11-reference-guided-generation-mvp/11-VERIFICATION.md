---
phase: 11-reference-guided-generation-mvp
status: passed
created: 2026-06-18
external_calls_default: false
hosted_reference_smoke: skipped_manual
---

# Phase 11 Verification Report

Phase 11 closed with local/provider-off automated validation. No command in the default validation path required hosted credentials or made paid provider calls.

## Summary

| Check | Result | Notes |
|-------|--------|-------|
| Core reference schema/prompt tests | Passed | Covers roles, structured reference usage, legacy id bridge, provider warning planning, and generation-job metadata. |
| API generation/jobs/operations tests | Passed | Covers rights/provider gates, job/export trace, operations capability metadata, and browser-safe provider status. |
| Worker generation/provider/config tests | Passed | Covers rights gates, provider request reference metadata, local prompt-only trace, BFL fail-closed behavior, and config flags. |
| Web workbench tests | Passed | Covers role assignment, rights eligibility, unsupported provider warnings, progress diagnostics, comparison trace, and child iteration reuse. |
| Contracts check | Passed | `Contract artifacts are current.` |
| Provider-off worker smoke dry run | Passed | Dry-run only; no live API/worker/provider calls. |
| Aggregate validation | Passed | Full root validation passed after type/contract/test fixes. |
| Hosted reference smoke | Skipped | Manual-only; no real credentials or cost approval were provided. |
| Browser UAT | Checklist ready | Live browser/services were not started by the agent run. |

## Focused Regression Evidence

```powershell
cd services/core
uv run pytest -q tests/test_models.py tests/test_prompt_plans.py tests/test_generation_jobs.py
```

Result: passed, 16 tests.

```powershell
cd services/api
uv run pytest -q tests/test_generation.py tests/test_jobs.py tests/test_operations.py
```

Result: passed, 43 tests.

```powershell
cd services/worker
uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py tests/test_config.py
```

Result: passed, 69 tests.

```powershell
cd apps/web
./node_modules/.bin/vitest.CMD --run src/app/page.test.tsx src/lib/workbench/store.test.ts src/lib/api/generation.test.ts src/lib/api/assets.test.ts src/lib/api/iteration.test.ts
```

Result: passed with sandbox escalation, 53 tests.

```powershell
corepack pnpm contracts:check
```

Result: passed with sandbox escalation. Running the check inside the sandbox can fall back to a minimal deterministic client and should not be used as final evidence on this Windows setup.

## Provider-Off Smoke And Aggregate Evidence

```powershell
corepack pnpm smoke:worker -- --dry-run
```

Result: passed. Output summary: `Worker queue smoke dry run passed.`

```powershell
corepack pnpm validate
```

Result: passed with sandbox escalation.

Aggregate validation covered:

- Host prerequisite and env-example checks.
- Web lint, typecheck, and full web tests: 9 files, 64 tests.
- Core ruff, mypy, and full pytest: 45 tests.
- API ruff, mypy, and full pytest: 69 tests.
- Worker ruff, mypy, and full pytest: 78 tests.
- Contracts check and contracts package typecheck.

Known non-blocking warning:

- API pytest emitted `PytestUnhandledThreadExceptionWarning` from `aiosqlite` worker threads after event-loop closure in targeted iteration tests. Tests passed and the warning is existing async-sqlite teardown noise, not a Phase 11 requirement failure.

## Validation Fixes Made During Closure

- Normalized mixed `ReferenceAssignment`/mapping input in `create_generation_brief()` before constructing `GenerationBriefPayload`, satisfying core/API mypy while preserving API compatibility.
- Updated API provider capability tests to reflect Phase 11 semantics: local deterministic supports prompt-only reference guidance but not reference image inputs; BFL remains unsupported for reference images.
- Converted worker snapshot role strings into `ReferenceRole` before building `ReferenceUsageItem`.

## Requirement Mapping

| Requirement | Evidence |
|-------------|----------|
| V2-REF-01 | Web role assignment tests, role contract tests, and Human UAT checklist. |
| V2-REF-02 | API/worker rights gate tests and workbench eligibility tests. |
| V2-REF-03 | Prompt planner/provider filtering tests, worker provider preflight tests, and capability map tests. |
| V2-REF-04 | Workbench unsupported-role warning tests, progress diagnostics tests, and BFL fail-closed tests. |
| V2-REF-05 | Worker/API durable trace tests, version comparison trace tests, and export manifest trace tests. |

## Manual Hosted Reference Smoke

Skipped in the agent run. It requires all of the following before execution:

- Real hosted provider credentials in ignored service env files.
- Operator cost approval.
- Low daily, rate, and per-job cost guards.
- Verified provider/model support for the intended reference-image route.

The default Phase 11 evidence is provider-off and local.
