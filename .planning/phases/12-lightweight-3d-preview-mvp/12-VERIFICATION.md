---
phase: 12-lightweight-3d-preview-mvp
artifact: verification
status: passed
created: 2026-06-19
updated: 2026-06-19
requirements: [V2-3D-01, V2-3D-02, V2-3D-03, V2-3D-04, V2-3D-05]
---

# Phase 12 Verification - Lightweight 3D Preview MVP

## Verdict

Passed on 2026-06-19.

Phase 12 delivers a concept-only lightweight 3D preview path with typed Preview3DSpec contracts, one registered shell fixture, a client-only Three.js viewer, camera controls, version-linked screenshot artifacts, persistent non-production/UV warning metadata, 2D fallback behavior, docs, aggregate validation, and desktop/mobile browser evidence.

## Must-Have Verification

| Requirement | Evidence | Result |
|-------------|----------|--------|
| V2-3D-01 | `generic-side-coupe-lightweight-v1` compatibility tests and PreviewSpec fixture coverage in web/core checks. | Pass |
| V2-3D-02 | Workbench `3D 预览` tab opens for selected generated versions in web tests and browser UAT. | Pass |
| V2-3D-03 | Rotate, zoom, reset, screenshot, keyboard labels, and non-production labels are covered by web tests and browser UAT. | Pass |
| V2-3D-04 | API screenshot tests, contracts, and metadata warnings cover Preview3DSpec, camera presets, screenshot artifacts, and warning ids. | Pass |
| V2-3D-05 | Unsupported template fallback is covered by web tests and documented UAT; 2D preview remains available. | Pass |

## Automated Checks

| Command | Result | Notes |
|---------|--------|-------|
| `cd services/core && uv run pytest -q tests/test_models.py tests/test_generation_jobs.py` | pass | 15 tests. |
| `cd services/api && uv run pytest -q tests/test_jobs.py tests/test_generation.py` | pass | 39 tests; existing aiosqlite event-loop-close warnings observed. |
| `corepack pnpm --filter @caragent/web lint` | pass | ESLint passed. |
| `corepack pnpm --filter @caragent/web typecheck` | pass | `tsc --noEmit` passed. |
| `corepack pnpm --filter @caragent/web test` | pass | 9 files / 71 tests, after fixing overly broad 12-07 assertions. JSDOM logs expected canvas `getContext` warning. |
| `corepack pnpm smoke:worker -- --dry-run` | pass | Worker queue command wiring passed; no live queue/provider call. |
| `corepack pnpm validate` | pass | Elevated run passed all host prereqs, env examples, web lint/typecheck/test, core/API/worker ruff/mypy/pytest, contracts check, and contracts typecheck. |

## Contract Checks

`corepack pnpm contracts:check` initially failed in the default sandbox because the script could not run normal generation and used a deterministic fallback that temporarily made generated artifacts stale. The real contract path was restored and verified with:

```powershell
services\api\.venv\Scripts\python.exe -c "import json; from caragent_api.main import create_app; schema=create_app().openapi(); print(json.dumps(schema, indent=2, sort_keys=True))" > packages\contracts\openapi\openapi.json
corepack pnpm --filter @caragent/contracts generate
corepack pnpm --filter @caragent/contracts typecheck
```

The final elevated `corepack pnpm validate` then reported `Contract artifacts are current.`

## Browser UAT

Human/browser UAT is recorded in `.planning/phases/12-lightweight-3d-preview-mvp/12-HUMAN-UAT.md`.

| Viewport | Evidence | Result |
|----------|----------|--------|
| Desktop 1440x900 | `.planning/phases/12-lightweight-3d-preview-mvp/evidence/12-07-desktop-3d.png` | Pass |
| Mobile 390x844, device scale 2 | `.planning/phases/12-lightweight-3d-preview-mvp/evidence/12-07-mobile-3d.png` | Pass |

Screenshot-crop statistics confirm nonblank 3D surfaces:

- Desktop crop `(430, 257, 974, 563)`: 290 unique colors, 32,627 non-background pixels.
- Mobile crop `(100, 284, 679, 795)`: 339 unique colors, 52,130 non-background pixels.

## Known Warnings

- JSDOM logs `HTMLCanvasElement.getContext()` as not implemented during web tests. Browser UAT provides the real WebGL/canvas visual evidence.
- API focused tests emit existing aiosqlite thread-close warnings while still passing.
- Live `pnpm smoke:worker` without `--dry-run` remains a host-prepared smoke path requiring Docker infrastructure, migrated API database, running API, and running worker.

## Completion Criteria

- [x] V2-3D-01..05 have implementation and evidence.
- [x] Phase 12 verification and UAT artifacts exist.
- [x] Docs state lightweight 3D is concept-only and not production UV proof.
- [x] ROADMAP, REQUIREMENTS, and STATE can advance to Phase 13 after this verification.

---
*Phase: 12-lightweight-3d-preview-mvp*
*Verified: 2026-06-19*
