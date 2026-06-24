---
phase: 21
status: passed
automated: passed
human_uat: checklist-ready
created: 2026-06-22
---

# Phase 21 Verification

## Scope

Phase 21 verifies the real generation entrypoint, in-flight job refresh, artifact content URL API route, and 2D preview image rendering.

## Automated Checks

| Command | Result | Notes |
|---------|--------|-------|
| `corepack pnpm --filter @caragent/web test -- page.test.tsx` | passed | 11 test files, 89 tests passed. jsdom printed expected `HTMLCanvasElement.getContext` warnings for 3D tests. |
| `corepack pnpm --filter @caragent/contracts generate` | passed | Orval generation now runs the binary artifact route patch after code generation. |
| `corepack pnpm validate` | passed | Full aggregate validation passed: host prereqs, env examples, web lint/type/test, core/API/worker ruff+mypy+pytest, contracts check, and contracts typecheck. |
| `corepack pnpm --filter @caragent/web typecheck` | passed | `tsc --noEmit` exited 0 after contracts were regenerated. |
| `corepack pnpm --filter @caragent/contracts typecheck` | passed | `tsc --project tsconfig.json --noEmit` exited 0. |
| `corepack pnpm contracts:check` | passed | Output: `Contract artifacts are current.` |
| `uv run pytest -q tests/test_jobs.py -k artifact_content` from `services/api` | passed | 1 API artifact content test passed, including binary OpenAPI response metadata assertions. |
| `uv run ruff check .` from `services/api` | passed | All checks passed. |
| `uv run ruff check .` from `services/core` | passed | All checks passed. |
| `uv run ruff check .` from `services/worker` | passed | All checks passed. |
| `git -c safe.directory=D:/python/carAgent diff --check` | passed with warnings | Only CRLF normalization warnings; no whitespace errors. |

## Environment Notes

- First sandboxed Vitest run failed with `spawn EPERM` while starting esbuild. Elevated rerun passed.
- First root-level API pytest failed with `ModuleNotFoundError: No module named 'caragent_core'`. Running pytest from `services/api` with uv service environment passed.
- First sandboxed `contracts:check` used its fallback generator and temporarily reduced `client.ts` to a health-only client. The canonical export/generate sequence was then run:
  - `uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json` from `services/api`
  - `corepack pnpm --filter @caragent/contracts generate`
  - `corepack pnpm contracts:check`
- Code review found that the artifact content operation could still be parsed as JSON by the generated client. The fixed generation chain now emits `await res.blob()` for successful content responses and `await res.json()` for errors.
- API and Worker tests now isolate their current working directory from local service `.env` files so unit tests are not affected by developer hosted-provider settings.
- Full validate initially exposed a React lint issue in chat hydration, a polling dependency warning, and a core mypy secret-value narrowing issue; all were fixed before the final passing run.

## Requirement Coverage

| Requirement | Evidence |
|-------------|----------|
| GENC-01 | `ParameterPanel` exposes `生成概念`; web test covers explicit generation submission. |
| GENC-02 | `WorkbenchApp` polls queued/running jobs every 1500 ms; web test suite covers progress state. |
| GENC-03 | `PreviewPanel` renders `<img alt="2D concept preview">` from `content_url`; web test asserts resolved URL and PreviewSpec summary. |
| GENC-04 | API artifact listing exposes `content_url`; content route streams bytes, rejects cross-workspace reads, declares binary OpenAPI response media, and the generated client reads success responses as Blob; resume flow loads latest job state. |

## Human UAT

Manual browser UAT was not run in this pass. Checklist saved in `21-HUMAN-UAT.md`.

## Verdict

Automated verification passed. Phase 21 is complete for automated GSD tracking, with manual browser UAT remaining as checklist-ready evidence.
