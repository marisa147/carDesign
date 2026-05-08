---
phase: 01
slug: foundation-and-contracts
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-05-08
---

# Phase 01 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Frontend: Vitest + Testing Library; backend/worker: pytest + pytest-asyncio; contracts: Orval drift check; smoke: scripted local checks |
| **Config file** | Wave 0 creates `apps/web/vitest.config.ts`, `services/api/pyproject.toml`, `services/worker/pyproject.toml`, and `packages/contracts/orval.config.ts` |
| **Quick run command** | `pnpm test && uv run pytest` |
| **Full suite command** | `pnpm validate` |
| **Estimated runtime** | ~120 seconds after dependencies are installed and Docker is ready |

---

## Sampling Rate

- **After every task commit:** Run `pnpm test && uv run pytest` once the relevant Wave 0 test infrastructure exists.
- **After every plan wave:** Run `pnpm validate`.
- **Before `$gsd-verify-work`:** `pnpm validate` must be green.
- **Max feedback latency:** 120 seconds for the normal local validation pass, excluding first dependency install and Docker image pulls.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | FOUND-01, FOUND-02 | T-01-01 / T-01-05 | Root scripts document local app and infra commands without production defaults | config/static | `pnpm validate --help` or `pnpm run validate` once scripts exist | No, W0 creates root scripts | pending |
| 01-02-01 | 02 | 2 | FOUND-02, FOUND-03, FOUND-04 | T-01-01 / T-01-03 / T-01-04 | API settings parse env values, reject unsafe CORS, never log secret values, and export OpenAPI | unit/static/contract | `cd services/api && uv run ruff check . && uv run mypy src && uv run pytest -q` | No, W0 creates API project | pending |
| 01-03-01 | 03 | 2 | FOUND-01, FOUND-02, FOUND-04 | T-01-01 / T-01-02 | Worker imports only worker modules and boots with Redis broker config | unit/static | `cd services/worker && uv run ruff check . && uv run mypy src && uv run pytest -q` | No, W0 creates worker project | pending |
| 01-04-01 | 04 | 2 | FOUND-01, FOUND-02, FOUND-04 | T-01-01 / T-01-05 | Docker Compose exposes local Postgres, Redis, and MinIO with documented local-only defaults and conditional daemon-aware smoke | smoke/config | `docker info` gates `pnpm infra:up && pnpm smoke:local && pnpm infra:down`; static checks still run when daemon unavailable | No, W0 creates Compose/env/smoke files | pending |
| 01-05-01 | 05 | 3 | FOUND-02, FOUND-03 | T-01-02 / T-01-04 | Contract package scaffolds OpenAPI-first generation without hand-maintained frontend types | contract/static | `pnpm --filter @caragent/contracts typecheck` after generation exists | No, W0 creates contracts package | pending |
| 01-06-01 | 06 | 4 | FOUND-02, FOUND-03 | T-01-02 / T-01-04 | Generated OpenAPI and TypeScript artifacts fail validation when stale | contract/unit | `pnpm contracts:generate && pnpm contracts:check` | No, W0 creates generated contract artifacts | pending |
| 01-07-01 | 07 | 3 | FOUND-01, FOUND-02 | T-01-02 / T-01-05 | Web scaffold uses approved shadcn/Tailwind baseline and no backend secret imports | unit/static | `pnpm --filter @caragent/web lint && pnpm --filter @caragent/web typecheck` | No, W0 creates web scaffold | pending |
| 01-08-01 | 08 | 5 | FOUND-01, FOUND-02, FOUND-03, FOUND-04 | T-01-02 / T-01-04 / T-01-05 | Web shell calls generated health client and exposes no provider keys or deferred controls | unit/static | `pnpm --filter @caragent/web lint && pnpm --filter @caragent/web typecheck && pnpm --filter @caragent/web test -- --run` | No, W0 creates shell/tests | pending |
| 01-09-01 | 09 | 6 | FOUND-01, FOUND-02, FOUND-03, FOUND-04 | T-01-01 / T-01-02 / T-01-03 / T-01-04 / T-01-05 | Aggregate validation proves local run, validation, contract drift, configurable env paths, and source coverage | integration | `pnpm validate` | No, W0 creates aggregate docs/scripts | pending |

---

## Threat References

| Threat ID | Threat | Mitigation Required In Plans |
|-----------|--------|------------------------------|
| T-01-01 | Real secrets committed in env/config files | Commit example env files only, ignore real env files, and test placeholders are present. |
| T-01-02 | Browser imports backend internals or reads provider keys | Web imports generated contracts only; provider keys remain backend/worker placeholders and are not used in Phase 1. |
| T-01-03 | Wildcard CORS becomes the default | Typed backend settings parse explicit origins and avoid `"*"` when credentials are enabled. |
| T-01-04 | OpenAPI/client drift hides unsafe API changes | `contracts:check` fails if generated OpenAPI or TypeScript artifacts are stale. |
| T-01-05 | Local infra defaults are mistaken for production-safe deployment | Compose/docs label defaults as local-only and defer production hardening to later phases. |

---

## Wave 0 Requirements

- [ ] `package.json` and `pnpm-workspace.yaml` provide root validation scripts.
- [ ] `.node-version`, `.python-version`, and package manager metadata pin intended runtimes.
- [ ] `apps/web/vitest.config.ts` and minimal shell tests exist.
- [ ] `services/api/pyproject.toml`, API test files, ruff, mypy, and pytest configuration exist.
- [ ] `services/worker/pyproject.toml`, worker import/boot tests, ruff, mypy, and pytest configuration exist.
- [ ] `packages/contracts/orval.config.ts`, generated OpenAPI/client artifacts, and contract generation/check scripts exist.
- [ ] `infra/compose.yml` and conditional `pnpm smoke:local` exist for local service validation.
- [ ] `.env.example` files exist and real env files are ignored.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Host Docker daemon is available | FOUND-01 | Sandbox cannot currently reach the Docker daemon even though Docker CLI exists | Run `docker info` on the host, then run `pnpm infra:up` before `pnpm smoke:local`. |
| Dependency installers are available outside sandbox | FOUND-01, FOUND-02 | Local `uv` is missing and npm/pnpm access is blocked by user-profile permissions in this session | Install/enable `uv`, Node 24 LTS, pnpm 10.x, and Python 3.13 before first dependency sync. |

---

## Validation Sign-Off

- [x] All Phase 1 requirements have automated validation paths.
- [x] Threat refs are mapped to automated or manual validation.
- [x] Wave 0 covers missing test infrastructure.
- [x] No watch-mode flags are part of required validation commands.
- [x] Feedback latency target is less than 120 seconds after setup.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** draft 2026-05-08
