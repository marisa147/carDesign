---
status: partial
phase: 01-foundation-and-contracts
source: [01-VERIFICATION.md]
started: 2026-05-09T10:43:22+08:00
updated: 2026-05-09T15:39:00+08:00
---

# Phase 1 Human Verification

## Current Test

[testing paused - 3 items blocked by current host/toolchain prerequisites]

## Tests

### 1. Full aggregate validation
expected: With Node 24.15.0, pnpm 11.0.8, Python 3.13.13, and uv available, `pnpm validate` runs env guard, web lint/type/test, API ruff/mypy/pytest, worker ruff/mypy/pytest, contract drift check, and contracts typecheck successfully.
result: blocked
blocked_by: other
reason: "Current host does not meet UAT prerequisites: node is v20.12.0 instead of 24.15.0, python is 3.11.5 instead of 3.13.13, uv is not installed, and pnpm fails before running scripts with EPERM: operation not permitted, lstat 'C:\\Users\\25858'."

### 2. Docker local services smoke
expected: With Docker Desktop or Docker Engine running, `pnpm infra:up`, `pnpm smoke:local`, and `pnpm infra:down` complete; smoke fails if Docker is unavailable or services are unreachable.
result: blocked
blocked_by: server
reason: "Current host cannot run the smoke workflow: docker client is installed, but docker info is denied on npipe:////./pipe/docker_engine and Docker config access is denied; pnpm infra:up and pnpm smoke:local also fail before scripts run with EPERM: operation not permitted, lstat 'C:\\Users\\25858'."

### 3. Live web health shell
expected: The `/` shell loads, the health CTA calls the API, configured local services render as configured/not connected, and API failure shows the inline unavailable alert while the shell remains usable.
result: blocked
blocked_by: server
reason: "Current host cannot start the web app for live/browser verification: root package manager is pnpm@11.0.8 but pnpm and npm both fail before scripts run with EPERM: operation not permitted, lstat 'C:\\Users\\25858'; node_modules is not installed at the root or apps/web."

## Summary

total: 3
passed: 0
issues: 0
pending: 0
skipped: 0
blocked: 3

## Gaps

None recorded yet.
