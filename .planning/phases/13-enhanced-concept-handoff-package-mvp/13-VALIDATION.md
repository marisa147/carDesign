---
phase: 13
slug: enhanced-concept-handoff-package-mvp
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-19
---

# Phase 13 - Validation Strategy

> Per-phase validation contract for enhanced concept handoff package schema, manifest stability, ZIP contents, export ledger immutability, rights/source guardrails, web UX, docs, and browser UAT.

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | pytest, Vitest, ruff, mypy, eslint, tsc, contract check, browser UAT |
| Config file | `package.json`, service `pyproject.toml`, `apps/web/package.json` |
| Quick run command | `cd services/core && uv run pytest -q tests/test_jobs.py tests/test_models.py` |
| Full suite command | `corepack pnpm validate` |
| External-call default | Disabled; no hosted provider calls |
| Package inspection | Python `zipfile.ZipFile` tests over generated package bytes |

## Sampling Rate

- After schema/storage changes: core unit tests.
- After package builder changes: core ZIP inspection tests.
- After API changes: API route tests plus contracts check.
- After web changes: focused Vitest export tests and web lint/typecheck.
- Before completion: worker dry-run smoke, aggregate validation, docs review, and browser UAT evidence.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 1 | V2-HANDOFF-01, V2-HANDOFF-03 | T-13-01 | Manifest/package schemas are typed, versioned, and binary/secret-free | core/schema | `cd services/core && uv run pytest -q tests/test_models.py tests/test_jobs.py` | existing | green |
| 13-02-01 | 02 | 1 | V2-HANDOFF-02, V2-HANDOFF-05 | T-13-02 | Safe-zone, warning, prompt/provider, reference, and disclaimer reports are deterministic and sanitized | core/unit | `cd services/core && uv run pytest -q tests/test_jobs.py tests/test_generation_jobs.py` | existing | green |
| 13-03-01 | 03 | 2 | V2-HANDOFF-02, V2-HANDOFF-03 | T-13-03 | ZIP includes stable manifest/notes/reports plus required concept image and optional screenshots | core/package | `cd services/core && uv run pytest -q tests/test_jobs.py` | existing | green |
| 13-04-01 | 04 | 3 | V2-HANDOFF-01, V2-HANDOFF-04 | T-13-04 | API creates immutable package artifact/export records behind feature flag and generated contracts | api/contract | `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_openapi_export.py && cd ../.. && corepack pnpm contracts:check` | existing | green |
| 13-05-01 | 05 | 4 | V2-HANDOFF-01, V2-HANDOFF-03 | T-13-05 | Workbench submits ZIP payload, previews package contents, and updates history safely | web/unit | `corepack pnpm --filter @caragent/web test` | existing | green |
| 13-06-01 | 06 | 5 | V2-HANDOFF-05 | T-13-06 | Missing/rejected rights or source metadata blocks enhanced package export with user-safe error | core/api/web | `cd services/core && uv run pytest -q tests/test_jobs.py && cd ../api && uv run pytest -q tests/test_jobs.py && cd ../.. && corepack pnpm --filter @caragent/web test` | existing | green |
| 13-07-01 | 07 | 6 | V2-HANDOFF-01..05 | T-13-07 | Final evidence proves provider-off validation, docs, contracts, smoke, and browser UAT | aggregate/docs/browser | `corepack pnpm contracts:check && corepack pnpm smoke:worker -- --dry-run && corepack pnpm validate` | yes | green |

*Status: pending / green / red / flaky*

## Focused Commands

| Area | Command |
|------|---------|
| Core handoff schema/package | `cd services/core && uv run pytest -q tests/test_models.py tests/test_jobs.py tests/test_generation_jobs.py` |
| API handoff route/contracts | `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_openapi_export.py` |
| Web export package UX | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/api/iteration.test.ts src/lib/api/generation.test.ts` |
| Web static checks | `corepack pnpm --filter @caragent/web lint && corepack pnpm --filter @caragent/web typecheck` |
| Contracts | `corepack pnpm contracts:check` |
| Provider-off smoke | `corepack pnpm smoke:worker -- --dry-run` |
| Full local validation | `corepack pnpm validate` |

## Wave 0 Requirements

Existing test infrastructure is sufficient. Phase 13 adds ZIP/package byte assertions and browser UAT evidence, but no new third-party package is required for package generation.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Browser desktop enhanced package UAT | V2-HANDOFF-01, V2-HANDOFF-02, V2-HANDOFF-03 | Confirms real workbench layout, disabled states, and history behavior | Start local services with enhanced handoff flag enabled, select a generated version, inspect ZIP package preview, create package, and confirm history shows ZIP/export disclaimer. |
| Browser mobile enhanced package UAT | V2-HANDOFF-01, V2-HANDOFF-05 | Confirms no overflow or overlapping text in dense export panel | Use mobile viewport and confirm readiness rows wrap, blocked/warning text fits, and primary controls remain reachable. |
| Rights/source blocked state | V2-HANDOFF-05 | Requires browser state with missing rights reference | Select or seed a version with included reference usage missing rights/source snapshot and confirm ZIP action is blocked while PNG/JPG concept export remains available if applicable. |

## Validation Sign-Off

- [x] All plans have focused automated verification or documented manual-only gates.
- [x] No default validation path makes external provider calls.
- [x] Contract changes are reflected in generated OpenAPI/TypeScript client.
- [x] Package manifest and notes contain no binary data, base64, secrets, API keys, or local paths.
- [x] ZIP includes stable `manifest.json` and `handoff-notes.md`.
- [x] Export records and package artifacts are immutable and version-linked.
- [x] Rights/source guardrails are verified in core/API/web tests.
- [x] Browser UAT evidence proves desktop/mobile package UX.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** passed, 2026-06-19. See `13-VERIFICATION.md` and `13-HUMAN-UAT.md`.
