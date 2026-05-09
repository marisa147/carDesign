---
status: partial
phase: 01-foundation-and-contracts
source: [01-VERIFICATION.md]
started: 2026-05-09T10:43:22+08:00
updated: 2026-05-09T10:43:22+08:00
---

# Phase 1 Human Verification

## Current Test

awaiting human testing

## Tests

### 1. Full aggregate validation
expected: With Node 24.15.0, pnpm 11.0.8, Python 3.13.13, and uv available, `pnpm validate` runs env guard, web lint/type/test, API ruff/mypy/pytest, worker ruff/mypy/pytest, contract drift check, and contracts typecheck successfully.
result: pending

### 2. Docker local services smoke
expected: With Docker Desktop or Docker Engine running, `pnpm infra:up`, `pnpm smoke:local`, and `pnpm infra:down` complete; smoke fails if Docker is unavailable or services are unreachable.
result: pending

### 3. Live web health shell
expected: The `/` shell loads, the health CTA calls the API, configured local services render as configured/not connected, and API failure shows the inline unavailable alert while the shell remains usable.
result: pending

## Summary

total: 3
passed: 0
issues: 0
pending: 3
skipped: 0
blocked: 0

## Gaps

None recorded yet.
