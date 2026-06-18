---
phase: 12
slug: lightweight-3d-preview-mvp
status: planned
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-18
---

# Phase 12 - Validation Strategy

> Per-phase validation contract for Preview3DSpec, shell compatibility, Three.js viewer behavior, screenshot persistence, warnings, fallback states, performance, and documentation.

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | pytest, Vitest, ruff, mypy, eslint, tsc, contract check, browser visual checks |
| Config file | `package.json`, service `pyproject.toml`, `apps/web/package.json` |
| Quick run command | `corepack pnpm contracts:check` |
| Full suite command | `corepack pnpm validate` |
| External-call default | Disabled; no hosted provider calls |
| Visual check | Browser/Playwright screenshot plus canvas-pixel checks after viewer implementation |

## Sampling Rate

- After schema changes: focused core/API tests and `corepack pnpm contracts:check`.
- After viewer changes: focused web Vitest and browser screenshot/canvas-pixel check.
- After screenshot persistence: API tests, generated contracts, and web API wrapper tests.
- Before completion: contracts check, worker dry-run smoke, aggregate validation, and Browser desktop/mobile UAT evidence.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | V2-3D-01, V2-3D-04, V2-3D-05 | T-12-01 | Preview3DSpec and screenshot metadata are typed, versioned, and contract-generated | schema/contract | `cd services/core && uv run pytest -q tests/test_models.py tests/test_generation_jobs.py && cd ../api && uv run pytest -q tests/test_jobs.py tests/test_generation.py && cd ../.. && corepack pnpm contracts:check` | existing | pending |
| 12-02-01 | 02 | 1 | V2-3D-01, V2-3D-05 | T-12-02 | Shell compatibility is explicit and unsupported templates fall back safely | core/web unit | `cd services/core && uv run pytest -q tests/test_generation_jobs.py && cd ../.. && corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx` | existing | pending |
| 12-03-01 | 03 | 2 | V2-3D-02, V2-3D-03, V2-3D-05 | T-12-03 | Viewer lazy-loads client-only and cannot break 2D preview fallback | web/unit | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/workbench/store.test.ts` | existing | pending |
| 12-04-01 | 04 | 2 | V2-3D-01, V2-3D-02, V2-3D-03 | T-12-04 | PreviewSpec overlays map to material/decal plans without production UV claims | web/unit | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx` | existing | pending |
| 12-05-01 | 05 | 3 | V2-3D-03, V2-3D-04 | T-12-05 | Screenshot uploads are bounded, validated, and linked to selected version | api/web/contract | `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_generation.py && cd ../.. && corepack pnpm contracts:check && corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/api/iteration.test.ts` | existing | pending |
| 12-06-01 | 06 | 3 | V2-3D-03, V2-3D-05 | T-12-06 | Non-production labels and fallback warnings are persistent and metadata-backed | web/api | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx && cd services/api && uv run pytest -q tests/test_jobs.py` | existing | pending |
| 12-07-01 | 07 | 4 | V2-3D-02, V2-3D-03, V2-3D-05 | T-12-07 | Browser scene is nonblank, responsive, keyboard-accessible, and cleaned up | browser/web | `corepack pnpm --filter @caragent/web lint && corepack pnpm --filter @caragent/web typecheck` plus Browser/Playwright visual evidence | existing | pending |
| 12-08-01 | 08 | 5 | V2-3D-01..05 | T-12-08 | Phase evidence separates automated checks from manual browser UAT and docs disclaimers | aggregate/docs | `corepack pnpm contracts:check && corepack pnpm smoke:worker -- --dry-run && corepack pnpm validate` | yes | pending |

*Status: pending / green / red / flaky*

## Focused Commands

| Area | Command |
|------|---------|
| Core 3D schema/shell | `cd services/core && uv run pytest -q tests/test_models.py tests/test_generation_jobs.py` |
| API screenshot/contracts | `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_generation.py` |
| Web 3D workbench | `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx src/lib/workbench/store.test.ts src/lib/api/iteration.test.ts` |
| Web static checks | `corepack pnpm --filter @caragent/web lint && corepack pnpm --filter @caragent/web typecheck` |
| Contracts | `corepack pnpm contracts:check` |
| Provider-off smoke | `corepack pnpm smoke:worker -- --dry-run` |
| Full local validation | `corepack pnpm validate` |

## Wave 0 Requirements

Existing infrastructure covers Phase 12, but visual verification must be added during execution because this phase introduces a WebGL/canvas surface.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Browser desktop 3D preview UAT | V2-3D-02, V2-3D-03 | Requires real browser canvas/WebGL inspection | Start local services, select a generated version, open 3D preview, rotate, zoom, reset, capture screenshot, and confirm labels remain visible. |
| Browser mobile 3D preview UAT | V2-3D-02, V2-3D-03, V2-3D-05 | Requires responsive visual inspection | Use mobile viewport, confirm controls wrap, canvas is nonblank, fallback remains readable, and no text overlaps. |
| Incompatible shell fallback | V2-3D-05 | Requires selected version fixture or browser state | Select or seed an unsupported template version and confirm 2D preview remains available with fallback copy. |

## Validation Sign-Off

- [ ] All plans have focused automated verification or documented manual-only gates.
- [ ] No default validation path makes external provider calls.
- [ ] Contract changes are reflected in generated OpenAPI/TypeScript client.
- [ ] Screenshot metadata contains no binary image data, secrets, or raw local paths.
- [ ] Browser visual evidence proves a nonblank 3D canvas on desktop and mobile.
- [ ] Persistent non-production labels are verified in UI and metadata.
- [ ] `nyquist_compliant: true` set in frontmatter.

**Approval:** planned; complete during 12-08.
