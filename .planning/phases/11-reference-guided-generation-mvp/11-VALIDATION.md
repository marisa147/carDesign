---
phase: 11
slug: reference-guided-generation-mvp
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-18
---

# Phase 11 - Validation Strategy

> Per-phase validation contract for reference roles, rights/source gates, provider capability filtering, trace persistence, workbench UX, and documentation.

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
- **After provider capability changes:** Run API operations/generation tests and worker config/provider tests.
- **After prompt/reference planner changes:** Run core prompt/generation tests.
- **After web role assignment changes:** Run focused workbench Vitest files.
- **Before completion:** Run `corepack pnpm contracts:check`, `corepack pnpm smoke:worker -- --dry-run`, and `corepack pnpm validate`.
- **Manual hosted reference smoke:** Only with explicit real credentials, small quota/cost guards, and operator approval.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | V2-REF-01, V2-REF-02, V2-REF-03, V2-REF-05 | T-11-01 | Reference roles, rights snapshots, and provider capability fields are typed and contract-generated | schema/contract | `cd services/core && uv run pytest -q tests/test_models.py tests/test_prompt_plans.py && cd ../api && uv run pytest -q tests/test_generation.py tests/test_operations.py && cd ../.. && corepack pnpm contracts:check` | existing | green |
| 11-02-01 | 02 | 1 | V2-REF-01, V2-REF-02, V2-REF-04 | T-11-02 | UI role controls cannot silently mark rights-missing assets as generation-eligible | web/unit | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/api/generation.test.ts src/lib/api/assets.test.ts` | existing | green |
| 11-03-01 | 03 | 2 | V2-REF-03, V2-REF-04, V2-REF-05 | T-11-03 | Prompt planner filters unsupported roles into warnings and records included/omitted references | core/api | `cd services/core && uv run pytest -q tests/test_prompt_plans.py tests/test_generation_jobs.py && cd ../api && uv run pytest -q tests/test_generation.py` | existing | green |
| 11-04-01 | 04 | 2 | V2-REF-02, V2-REF-03, V2-REF-04 | T-11-04 | Worker repeats rights/provider reference preflight before any hosted call | worker/unit | `cd services/worker && uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py tests/test_config.py` | existing | green |
| 11-05-01 | 05 | 3 | V2-REF-05 | T-11-05 | Model-run, artifact, version, job, and export metadata carry the same reference usage snapshot | worker/api/web | `cd services/worker && uv run pytest -q tests/test_generation_tasks.py && cd ../api && uv run pytest -q tests/test_jobs.py tests/test_generation.py && cd ../.. && corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/api/iteration.test.ts` | existing | green |
| 11-06-01 | 06 | 4 | V2-REF-01..05 | T-11-06 | Workbench shows reference warnings and preserves reference usage across generation and child iterations | web/unit | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/workbench/store.test.ts src/lib/api/generation.test.ts src/lib/api/iteration.test.ts` | existing | green |
| 11-07-01 | 07 | 5 | V2-REF-01..05 | T-11-07 | Phase evidence distinguishes provider-off automated validation from manual hosted reference smoke | aggregate/manual | `corepack pnpm contracts:check && corepack pnpm smoke:worker -- --dry-run && corepack pnpm validate` | yes | green |

*Status: pending / green / red / flaky*

## Focused Commands

| Area | Command |
|------|---------|
| Core reference schema/prompt | `cd services/core && uv run pytest -q tests/test_models.py tests/test_prompt_plans.py tests/test_generation_jobs.py` |
| API reference/provider gates | `cd services/api && uv run pytest -q tests/test_generation.py tests/test_jobs.py tests/test_operations.py` |
| Worker reference routing | `cd services/worker && uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py tests/test_config.py` |
| Web reference workbench | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/workbench/store.test.ts src/lib/api/generation.test.ts src/lib/api/assets.test.ts src/lib/api/iteration.test.ts` |
| Contracts | `corepack pnpm contracts:check` |
| Provider-off smoke | `corepack pnpm smoke:worker -- --dry-run` |
| Full local validation | `corepack pnpm validate` |

## Wave 0 Requirements

Existing infrastructure covers Phase 11. Each plan should add focused red tests before implementation where behavior is new.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Browser reference-role UAT | V2-REF-01, V2-REF-02, V2-REF-04 | Requires visual inspection of role controls, rights state, and provider warnings | Start local services. Upload two images, confirm rights/source for one, assign multiple roles, switch provider, and verify eligibility/warning copy before submit. |
| Hosted reference provider smoke | V2-REF-03, V2-REF-05 | Requires real hosted credentials, provider support confirmation, and may cost money | Set hosted credentials plus low quota/rate/cost guards. Confirm capability map supports the tested role. Submit one small reference-guided job. Confirm provider/model/cost/reference metadata, then disable hosted flags. |
| Export trace inspection | V2-REF-05 | Requires selecting a generated version through browser flow | Export a concept record and inspect manifest for reference usage snapshot and concept-only disclaimer. |

## Validation Sign-Off

- [x] All plans have focused automated verification or documented manual-only gates.
- [x] No default validation path makes external provider calls.
- [x] Contract changes are reflected in generated OpenAPI/TypeScript client.
- [x] Rights/source snapshots are stored without binary image data or secrets.
- [x] Unsupported reference roles are visible as warnings or validation errors.
- [x] Browser UAT covers role assignment, rights eligibility, provider warnings, generation, child iteration reuse, and export trace.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** passed; see `11-VERIFICATION.md` and `11-HUMAN-UAT.md`.
