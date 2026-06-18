# Phase 4 Verification: Workbench UI Integration

**Date:** 2026-06-17
**Status:** Passed

## Automated Checks

| Check | Command | Result | Evidence |
|-------|---------|--------|----------|
| Docs token check | `node -e "const fs=require('fs'); const d=fs.readFileSync('docs/development.md','utf8'); for (const t of ['Phase 4','workbench','chat','parameters','asset','2D preview','future gates']) if (!d.includes(t)) throw new Error('missing docs token '+t)"` | Passed | Exit 0. |
| Web lint | `corepack pnpm --filter @caragent/web lint` | Passed | `eslint . --max-warnings=0`, exit 0. |
| Web typecheck | `corepack pnpm --filter @caragent/web typecheck` | Passed | `tsc --noEmit`, exit 0. |
| Web tests | `corepack pnpm --filter @caragent/web test` | Passed | 6 test files passed, 31 tests passed. Phase 4 tests cover workbench shell, chat-to-brief, parameter edits, asset rights, 2D preview, and history switching. |
| Web production build | `corepack pnpm --filter @caragent/web build` | Passed | Next.js 16.2.6 compiled and generated static routes `/` and `/_not-found`. |
| Contract drift | `corepack pnpm contracts:check` | Passed | `Contract artifacts are current.` |
| Root aggregate validation | `corepack pnpm validate` | Passed | Web lint/typecheck/test, core/API/worker ruff/mypy/pytest, contracts check, and contracts typecheck all passed. |
| Docker smoke | `corepack pnpm infra:up`; `corepack pnpm smoke:local` | Passed | PostgreSQL, Redis, MinIO, Phase 2 durable data smoke, and Phase 3 local deterministic generation smoke passed. |

## Browser UAT Summary

Browser UAT ran against `http://127.0.0.1:3000/` with the FastAPI dev server on `127.0.0.1:8000` and local PostgreSQL/Redis/MinIO running through Docker Compose.

| Viewport | Result | Evidence |
|----------|--------|----------|
| Desktop default, 1280x720 | Passed | Chat input visible in the initial viewport; chat, 2D preview, progress, history, parameters, assets, and future gates present; no horizontal scroll; no overlapping checked regions; future gate buttons disabled. |
| Mobile, 390x844 | Passed | Single-column layout; chat input visible in the initial viewport; all workbench regions present in document order; no horizontal scroll; no overlapping checked regions; future gate buttons disabled. |

## Requirement Evidence

| Requirement | Status | Evidence |
|-------------|--------|----------|
| UI-01 | Passed | `page.test.tsx` verifies chat submission creates workspace/message/brief. Browser UAT confirms chat panel and input are visible at desktop and mobile widths. |
| UI-02 | Passed | `page.test.tsx` verifies structured parameter edits call the brief update path without submitting generation. Browser UAT confirms parameter panel is present. |
| UI-03 | Passed | `page.test.tsx` verifies upload, rights confirmation, and confirmed reference selection. Browser UAT confirms asset controls are present and upload action is gated before workspace/asset readiness. |
| UI-04 | Passed | `page.test.tsx` verifies distinct job states/events through workbench fixtures. Browser UAT confirms progress panel is present with queued/running/succeeded/failed copy and disabled refresh before a job exists. |
| UI-05 | Passed | `page.test.tsx` and store tests verify 2D preview controls, local zoom bounds, selected view, and version/artifact switching. Browser UAT confirms preview controls are visible and non-overlapping. |
| UI-06 | Passed | `page.test.tsx` verifies history selection changes preview context without losing surrounding workbench state. Browser UAT confirms history region is present. |
| UI-07 | Passed | `page.test.tsx` and Browser UAT confirm true 3D, production export, and marketplace gates are disabled/deferred. |

## Residual Scope

The following remain intentionally deferred and are not Phase 4 gaps: production-ready wrap export, true UV-mapped 3D preview, marketplace/community workflows, auth, billing, quotas, hosted provider operations, and production deployment.
