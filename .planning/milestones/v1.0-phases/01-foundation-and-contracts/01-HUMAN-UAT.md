---
status: complete
phase: 01-foundation-and-contracts
source: [01-VERIFICATION.md]
started: 2026-05-09T10:43:22+08:00
updated: 2026-06-17T10:33:21+08:00
---

# Phase 1 Human Verification

## Current Test

[testing complete]

## Tests

### 1. Full aggregate validation
expected: With Node 24.15.0, pnpm 11.0.8, Python 3.13.13, and uv available, `pnpm validate` runs env guard, web lint/type/test, API ruff/mypy/pytest, worker ruff/mypy/pytest, contract drift check, and contracts typecheck successfully.
result: pass
evidence: "Rechecked 2026-06-17T10:18:01+08:00 with Node v24.15.0 from the NVM download cache, pnpm 11.0.8, Python 3.13.13, uv 0.11.12, and `UV_NO_CACHE=1` for this Windows sandbox. `pnpm validate` completed successfully: host prereqs, env guard, web lint/type/test, API ruff/mypy/pytest, worker ruff/mypy/pytest, contract drift check, and contracts typecheck all passed."

### 2. Docker local services smoke
expected: With Docker Desktop or Docker Engine running, `pnpm infra:up`, `pnpm smoke:local`, and `pnpm infra:down` complete; smoke fails if Docker is unavailable or services are unreachable.
result: pass
evidence: "Rechecked 2026-06-17T10:33:21+08:00 after Docker Desktop/Engine was started. `pnpm infra:up` pulled/started PostgreSQL, Redis, and MinIO; `pnpm smoke:local` printed `PostgreSQL check passed.`, `Redis check passed.`, `MinIO check passed.`, and `Local PostgreSQL, Redis, and MinIO smoke checks passed.` `pnpm infra:down` then removed the containers and network, and a follow-up compose `ps -a` showed no remaining containers."

### 3. Live web health shell
expected: The `/` shell loads, the health CTA calls the API, configured local services render as configured/not connected, and API failure shows the inline unavailable alert while the shell remains usable.
result: pass
evidence: "Rechecked 2026-06-17T10:21:00+08:00. Started FastAPI on 127.0.0.1:8000 and Next.js on 127.0.0.1:3000, opened the shell in the in-app browser, clicked `检查堆栈健康`, and observed API connected, Local Services shown as `已配置` with `运行 pnpm smoke:local` copy rather than live connected success. After stopping the API and clicking again, the inline alert `基础服务暂不可用。请确认本地服务已启动，并重新运行健康检查。` appeared and the shell remained usable."

## Summary

total: 3
passed: 3
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

None recorded yet.

## Recheck History

- 2026-05-09T16:46:52+08:00: Installed/activated a workspace-local verification toolchain: Node v24.15.0 from NVM download cache, pnpm 11.0.8, Python 3.13.13, and uv 0.11.12. `pnpm lint`, `pnpm typecheck`, `pnpm --filter @caragent/contracts check`, `pnpm --filter @caragent/contracts test`, API pytest (11 passed), and worker pytest (8 passed) succeeded. At that time, `pnpm test` was not yet runnable at Vitest/esbuild `spawn EPERM`; `pnpm validate` was not yet runnable due to Node child_process prerequisite checks; Docker/live browser UAT still required a host shell outside the sandbox.
- 2026-06-17T10:22:30+08:00: Fixed the Windows/Orval validation issues exposed by non-sandbox execution, then reran `pnpm lint`, `pnpm typecheck`, `pnpm test`, and `pnpm validate` successfully. Live browser health shell passed with API/web processes. Docker smoke was the only remaining item until Docker Desktop/Engine was started.
- 2026-06-17T10:33:21+08:00: After Docker Desktop/Engine was started, `pnpm infra:up`, `pnpm smoke:local`, and `pnpm infra:down` completed successfully. Follow-up `docker compose ... ps -a` showed no remaining containers.
