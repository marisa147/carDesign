---
phase: 21
slug: real-generation-entry-and-artifact-preview
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-22
---

# Phase 21 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | Vitest, pytest, TypeScript |
| Config file | `apps/web/vitest.config.ts`, service `pyproject.toml`, package scripts |
| Quick run command | `corepack pnpm --filter @caragent/web test -- page.test.tsx` |
| Full suite command | `corepack pnpm contracts:check`; `uv run pytest -q services/api/tests/test_jobs.py`; `corepack pnpm --filter @caragent/web test` |
| Estimated runtime | 60-180 seconds |

## Sampling Rate

- After every frontend task: run the focused web test that covers the changed behavior.
- After every API/contract task: run the focused API test plus contracts check.
- After the verification plan: run all Phase 21 focused commands and record any skipped aggregate command honestly.
- Max feedback latency: under 3 minutes for focused checks.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 21.01.01 | 01 | 1 | GENC-01 | T-21-01 | Generation only submits from an active workspace/brief | web integration | `corepack pnpm --filter @caragent/web test -- page.test.tsx` | yes | pending |
| 21.01.02 | 01 | 1 | GENC-02 | T-21-02 | Polling stops for terminal jobs | web integration | `corepack pnpm --filter @caragent/web test -- page.test.tsx` | yes | pending |
| 21.02.01 | 02 | 1 | GENC-04 | T-21-03 | Workspace-scoped content route rejects cross-workspace access | pytest | `uv run pytest -q services/api/tests/test_jobs.py -k artifact_content` | yes | pending |
| 21.02.02 | 02 | 1 | GENC-04 | T-21-04 | Content type comes from artifact/storage metadata | pytest | `uv run pytest -q services/api/tests/test_jobs.py -k artifact_content` | yes | pending |
| 21.03.01 | 03 | 2 | GENC-03 | T-21-05 | Preview image URL resolves through API base URL | web integration | `corepack pnpm --filter @caragent/web test -- page.test.tsx` | yes | pending |
| 21.04.01 | 04 | 3 | GENC-01..04 | - | N/A | aggregate | `corepack pnpm contracts:check`; `corepack pnpm --filter @caragent/web typecheck`; `uv run ruff check .` | yes | pending |

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Browser UAT desktop/mobile image visibility | GENC-03, GENC-04 | Requires running local app/API/worker and inspecting actual browser layout | Submit a local generation, wait for success, refresh/resume workspace, confirm the same generated image is visible with overlays and no horizontal overflow. |

## Validation Sign-Off

- [x] All tasks have automated verify commands or existing test infrastructure.
- [x] Sampling continuity: no 3 consecutive tasks without automated verify.
- [x] Wave 0 covers all missing references.
- [x] No watch-mode flags.
- [x] Feedback latency target is under 3 minutes for focused checks.
- [ ] Phase execution summary records actual command output.

**Approval:** pending execution
