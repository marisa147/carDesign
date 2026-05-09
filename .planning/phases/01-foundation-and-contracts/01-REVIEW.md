---
status: issues_found
phase: 01-foundation-and-contracts
reviewed: 2026-05-09T02:27:02Z
depth: standard
files_reviewed: 19
files_reviewed_list:
  - .env.example
  - apps/web/src/app/page.test.tsx
  - apps/web/src/app/page.tsx
  - apps/web/src/lib/api/health.ts
  - docs/development.md
  - infra/README.md
  - packages/contracts/openapi/openapi.json
  - packages/contracts/package.json
  - packages/contracts/src/generated/client.ts
  - scripts/check-env-examples.mjs
  - scripts/smoke-local.mjs
  - services/api/.env.example
  - services/api/src/caragent_api/config.py
  - services/api/src/caragent_api/main.py
  - services/api/tests/test_config.py
  - services/api/tests/test_health.py
  - services/worker/.env.example
  - services/worker/src/caragent_worker/config.py
  - services/worker/tests/test_config.py
findings:
  critical: 0
  warning: 2
  info: 0
  total: 2
---

# Phase 1: Code Review Report

**Reviewed:** 2026-05-09T02:27:02Z
**Depth:** standard
**Files Reviewed:** 19
**Status:** issues_found

## Summary

Reviewed the Phase 1 gap-closure source/config/docs files and read the verification plus 01-10/01-11/01-12 summaries as context. The previous structural gaps are mostly closed: the contracts test script exists, service `.env` loading and `AI_PROVIDER_*` names are aligned, health contracts include `configured`, and Docker-unavailable smoke now fails by default.

No critical security issues were found. Two warning-level correctness gaps remain around avoiding false-positive health status.

## Warnings

### WR-01: Failed Health Re-Check Leaves Stale Connected Cards

**File:** `apps/web/src/app/page.tsx:111`

**Issue:** `handleHealthCheck` sets `hasError` on fetch failure but leaves the previous `health` state untouched. If a user gets a successful health result, then the API or services go down and they click `检查堆栈健康` again, the alert appears while the status cards/footer can still show stale connected/configured data from the prior success.

**Fix:** Reset the health cards to an explicit unavailable/error state in the `catch` path, and add a regression test that succeeds once, fails once, and verifies the API/local-service cards no longer claim success.

```tsx
    } catch {
      setHealth({
        ...initialHealth,
        apiBaseUrl: health.apiBaseUrl,
        cards: initialHealth.cards.map((card) =>
          card.id === "api"
            ? {
                ...card,
                detail: "API 健康检查失败，请确认本地服务已启动。",
                state: "unavailable",
                statusLabel: "未连接",
              }
            : card,
        ),
      });
      setHasError(true);
    } finally {
```

### WR-02: PostgreSQL Smoke Check Only Verifies A TCP Listener

**File:** `scripts/smoke-local.mjs:17`

**Issue:** The PostgreSQL smoke step delegates to `checkTcp`, whose success condition is only a completed socket connection. That can pass when any process is listening on the configured port, or when PostgreSQL accepts TCP before it is actually ready for database use. The smoke script is the live local-services gate, so this can still produce false-positive PostgreSQL success.

**Fix:** Make the PostgreSQL check protocol-aware. Since the script already requires Docker by default and the stack is Compose-owned, reuse the container health command or `pg_isready` through Compose instead of a raw TCP connect.

```js
{
  name: "PostgreSQL",
  run: () => checkPostgresReady(),
}

function checkPostgresReady() {
  const result = runCommand(
    "docker compose --env-file .env.example -f infra/compose.yml exec -T postgres pg_isready -U caragent -d caragent",
    { stdio: "pipe" },
  );

  if (!result.ok) {
    throw new Error("pg_isready did not report PostgreSQL ready");
  }
}
```

## Residual Risks / Test Gaps

- Passed here: `node scripts/check-env-examples.mjs`, API config/health tests via ambient Python (`9 passed`), worker config tests via ambient Python (`5 passed`), and static OpenAPI/client health enum alignment.
- `pnpm` remains host-blocked before package execution with `EPERM: operation not permitted, lstat 'C:\Users\25858'`; web tests, contracts typecheck/check, and `pnpm validate` still need a host run.
- `uv` is not installed/on `PATH`, so service checks through the documented `uv run ...` path remain host-blocked.
- Docker daemon access is unavailable in this sandbox. `node scripts/smoke-local.mjs` now exits 1 by default, and `--allow-docker-unavailable` exits 0 while stating checks were not performed; live `pnpm infra:up`, `pnpm smoke:local`, `pnpm infra:down` still need a Docker-enabled host.
- `packages/contracts/src/generated/client.ts` remains a deterministic fallback artifact; run `pnpm contracts:check` on an unblocked host to confirm no generator drift.

---

_Reviewed: 2026-05-09T02:27:02Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
