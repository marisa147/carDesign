---
phase: 10
slug: targeted-regeneration-and-masked-editing-mvp
status: ready
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-18
---

# Phase 10 - Validation Strategy

> Per-phase validation contract for targeted edits, masks, recomposition, provider capability checks, comparison UI, and documentation.

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
- **After schema changes:** Run `corepack pnpm contracts:check`.
- **After worker routing changes:** Run focused worker generation tests and API job tests.
- **After web selection/comparison changes:** Run focused workbench Vitest files.
- **Before completion:** Run `corepack pnpm contracts:check`, `corepack pnpm smoke:worker -- --dry-run`, and `corepack pnpm validate`.
- **Manual hosted masked smoke:** Only with explicit real credentials, small quota/cost guards, and operator approval.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 10-01-01 | 01 | 1 | V2-EDIT-02 | T-10-01 | Edit intent, region, mask, prompt delta, and provider parameters are typed and durable without exposing secrets | schema/contract | `cd services/api && uv run pytest -q tests/test_generation.py tests/test_jobs.py && cd ../core && uv run pytest -q tests/test_models.py tests/test_generation_jobs.py && cd ../.. && corepack pnpm contracts:check` | existing | pending |
| 10-02-01 | 02 | 1 | V2-EDIT-01 | T-10-02 | UI selection only submits valid version-scoped region/layer targets and previews masks clearly | web/unit | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/workbench/store.test.ts` | existing | pending |
| 10-03-01 | 03 | 2 | V2-EDIT-03 | T-10-03 | Deterministic recomposition changes only allowed layer fields and never calls hosted providers | worker/unit | `cd services/worker && uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py` | existing | pending |
| 10-04-01 | 04 | 2 | V2-EDIT-04 | T-10-04 | Mask-aware provider calls are blocked unless provider/model capability and hosted guards allow them | api/worker | `cd services/api && uv run pytest -q tests/test_generation.py tests/test_operations.py && cd ../worker && uv run pytest -q tests/test_config.py tests/test_generation_tasks.py` | existing | pending |
| 10-05-01 | 05 | 3 | V2-EDIT-02, V2-EDIT-03, V2-EDIT-04 | T-10-05 | Worker creates child versions/artifacts/model-runs with route and parent lineage without mutating parent data | worker/api | `cd services/worker && uv run pytest -q tests/test_generation_tasks.py && cd ../api && uv run pytest -q tests/test_jobs.py tests/test_generation.py` | existing | pending |
| 10-06-01 | 06 | 3 | V2-EDIT-04, V2-EDIT-05 | T-10-06 | Failure categories and retry states preserve original edit intent and sanitize diagnostics | api/web/worker | `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_generation.py && cd ../worker && uv run pytest -q tests/test_generation_tasks.py && cd ../.. && corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/api/iteration.test.ts` | existing | pending |
| 10-07-01 | 07 | 4 | V2-EDIT-05 | T-10-07 | Comparison UI clearly shows parent/child, route type, prompt delta, and changed region without claiming pixel proof | web/unit | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx` | existing | pending |
| 10-08-01 | 08 | 5 | V2-EDIT-01..05 | T-10-08 | Phase evidence covers local-free validation and manual hosted-mask prerequisites | aggregate/manual | `corepack pnpm contracts:check && corepack pnpm smoke:worker -- --dry-run && corepack pnpm validate` | yes | pending |

*Status: pending / green / red / flaky*

## Focused Commands

| Area | Command |
|------|---------|
| API targeted edit schemas/routes | `cd services/api && uv run pytest -q tests/test_generation.py tests/test_jobs.py tests/test_operations.py` |
| Core ledger/schema helpers | `cd services/core && uv run pytest -q tests/test_models.py tests/test_generation_jobs.py tests/test_prompt_plans.py` |
| Worker edit routing | `cd services/worker && uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py tests/test_config.py` |
| Web edit workbench | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/workbench/store.test.ts src/lib/api/iteration.test.ts` |
| Contracts | `corepack pnpm contracts:check` |
| Provider-off smoke | `corepack pnpm smoke:worker -- --dry-run` |
| Full local validation | `corepack pnpm validate` |

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Region/layer edit UAT | V2-EDIT-01, V2-EDIT-05 | Requires browser inspection of selection and comparison | Start local services. Select a generated version, choose a safe zone or overlay layer, preview the mask, submit a recomposition-safe edit, and compare parent/child route metadata. |
| Hosted mask provider smoke | V2-EDIT-04 | Requires real hosted credentials and may cost money | Set explicit hosted credentials and small quota/cost guards. Confirm provider capability supports masks. Submit one tiny masked edit. Confirm provider/model/cost/mask metadata and child version evidence, then disable hosted flags. |
| Failure redaction UAT | V2-EDIT-04, V2-EDIT-05 | Requires inspecting UI plus job events | Trigger unsupported-provider or invalid-mask failure. Confirm user sees a safe category/message and retry preserves edit intent. |

## Validation Sign-Off

- [ ] All plans have focused tests or documented host prerequisite gates.
- [ ] No default validation path makes external provider calls.
- [ ] Contract changes are reflected in generated OpenAPI/TypeScript client.
- [ ] Parent versions/artifacts remain immutable during targeted edits.
- [ ] Recomposition-only route is proven without hosted credentials.
- [ ] Provider mask route is capability-gated and manually smoked when credentials exist.
- [ ] Browser UAT covers selection, mask preview, submission, failure, retry, and comparison.
- [ ] `nyquist_compliant: true` set in frontmatter.

**Approval:** pending
