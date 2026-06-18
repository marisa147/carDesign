---
phase: 09
slug: hosted-provider-rollout-mvp
status: ready
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-18
---

# Phase 09 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest, Vitest, ruff, mypy, eslint, tsc, custom Node contract/smoke scripts |
| **Config file** | `package.json`, service `pyproject.toml`, `apps/web/package.json` |
| **Quick run command** | `corepack pnpm contracts:check` |
| **Full suite command** | `corepack pnpm validate` |
| **External-call default** | Disabled; default validation must not call hosted providers |
| **Estimated runtime** | ~120-600 seconds depending on host prerequisites |

## Sampling Rate

- **After every task commit:** Run the focused command listed in that task.
- **After every plan wave:** Run `corepack pnpm contracts:check` plus API/worker/web focused tests touched by that wave.
- **Before hosted smoke:** Confirm the operator intentionally set hosted credentials and small quota/cost guard values.
- **Before completion:** `corepack pnpm validate` must be green, and provider-off smoke/UAT plus manual provider-on instructions must be recorded.
- **Max feedback latency:** 10 minutes for full local validation on a prepared host.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | V2-PROVIDER-01, V2-PROVIDER-05 | T-09-01 | Capability map exposes only browser-safe metadata and keeps local default available | config/unit | `cd services/api && uv run pytest -q tests/test_config.py tests/test_operations.py && cd ../worker && uv run pytest -q tests/test_config.py` | existing | pending |
| 09-02-01 | 02 | 1 | V2-PROVIDER-01, V2-PROVIDER-03, V2-PROVIDER-05 | T-09-02 | BFL adapter uses safe headers, returned polling URL, downloaded results, and sanitized errors | provider/unit | `cd services/worker && uv run pytest -q tests/test_image_providers.py` | existing | pending |
| 09-03-01 | 03 | 2 | V2-PROVIDER-01, V2-PROVIDER-02, V2-PROVIDER-05 | T-09-03 | Hosted jobs are blocked unless all gates pass; worker repeats authoritative preflight | api/worker | `cd services/api && uv run pytest -q tests/test_generation.py tests/test_operations.py && cd ../worker && uv run pytest -q tests/test_generation_tasks.py` | existing | pending |
| 09-04-01 | 04 | 2 | V2-PROVIDER-03, V2-PROVIDER-04 | T-09-04 | Provider trace, cost, fallback, and errors are durable and redacted | worker/api | `cd services/worker && uv run pytest -q tests/test_generation_tasks.py && cd ../api && uv run pytest -q tests/test_jobs.py tests/test_operations.py` | existing | pending |
| 09-05-01 | 05 | 3 | V2-PROVIDER-02, V2-PROVIDER-04 | T-09-05 | Moderation/rate/credit/provider validation failures become user-safe categories | worker/api | `cd services/worker && uv run pytest -q tests/test_image_providers.py tests/test_generation_tasks.py && cd ../api && uv run pytest -q tests/test_jobs.py tests/test_operations.py` | existing | pending |
| 09-06-01 | 06 | 3 | V2-PROVIDER-02, V2-PROVIDER-04, V2-PROVIDER-05 | T-09-06 | Workbench selector sends safe provider intent and hides secrets/raw diagnostics | web/contract | `corepack pnpm --filter @caragent/web test -- --run src/app/page.test.tsx src/lib/api/generation.test.ts src/lib/api/operations.test.ts` | existing | pending |
| 09-07-01 | 07 | 4 | V2-PROVIDER-01..05 | T-09-07 | Provider-off automated validation stays free; provider-on smoke is explicit and documented | aggregate/manual | `corepack pnpm contracts:check && corepack pnpm validate` | yes | pending |

*Status: pending / green / red / flaky*

## Wave 0 Requirements

- No new test framework is required.
- If capability map helpers are added, add unit tests before wiring them into routes or worker tasks.
- If OpenAPI schemas change, regenerate/check contracts before web implementation.
- If BFL official docs drift again, update `09-RESEARCH.md` before changing adapter assumptions.

## Focused Commands

| Area | Command |
|------|---------|
| API provider/preflight | `cd services/api && uv run pytest -q tests/test_config.py tests/test_operations.py tests/test_generation.py tests/test_jobs.py` |
| Worker provider/routing | `cd services/worker && uv run pytest -q tests/test_config.py tests/test_image_providers.py tests/test_generation_tasks.py` |
| Web workbench | `corepack pnpm --filter @caragent/web test -- --run src/app/page.test.tsx src/lib/api/generation.test.ts src/lib/api/operations.test.ts` |
| Contracts | `corepack pnpm contracts:check` |
| Full local validation | `corepack pnpm validate` |
| Provider-off smoke | `corepack pnpm smoke:worker -- --dry-run` plus local deterministic smoke when host services are running |

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Provider-off workbench UAT | V2-PROVIDER-05 | Requires running web/API/worker and visual inspection | Start local services with hosted flags disabled. Confirm local deterministic generation still works, provider controls show local/default-off state, and no hosted credentials are required. |
| Provider-on BFL smoke | V2-PROVIDER-01..04 | Requires real BFL credentials and may cost money | Set explicit BFL credentials, enable V2 hosted rollout and provider calls, configure low quota/rate/cost guards, submit one small hosted generation, confirm stored artifact/model run/job events/operations status, then disable hosted flags. |
| Failure redaction UAT | V2-PROVIDER-04 | Requires inspecting UI and logs together | Trigger a mocked or low-risk provider failure. Confirm workbench and operations status show safe category/message without secrets. |

## Validation Sign-Off

- [ ] All plans have focused tests or documented host prerequisite gates.
- [ ] No default validation path makes external provider calls.
- [ ] Contract changes are reflected in generated OpenAPI/TypeScript client.
- [ ] Local deterministic provider remains green without hosted credentials.
- [ ] Provider-on smoke is documented, explicit, cheap, and reversible.
- [ ] `nyquist_compliant: true` set in frontmatter.

**Approval:** pending
