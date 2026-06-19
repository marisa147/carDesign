---
phase: 15
plan: 05
status: complete
subsystem: validation-docs
tags:
  - contracts
  - docs
  - verification
key_files:
  created:
    - docs/template-governance.md
  modified:
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts
metrics:
  docs_added: 1
  requirements_addressed:
    - V3-TEMPLATE-01
    - V3-TEMPLATE-02
    - V3-TEMPLATE-03
    - V3-TEMPLATE-04
    - V3-TEMPLATE-05
---

# Plan 15-05 Summary

## What Changed

- Added `docs/template-governance.md` with source policy, registration, readiness, and non-production boundaries.
- Exported OpenAPI after adding template governance metadata to `GenerationBriefPayload`.
- Regenerated the Orval TypeScript client.
- Ran contract drift, core, API, worker, contracts, and web checks relevant to Phase 15.

## Verification

- Elevated `corepack pnpm --filter @caragent/contracts check` passed.
- `corepack pnpm --filter @caragent/contracts typecheck` passed.
- `uv run pytest -q` passed in `services/core`.
- `uv run pytest tests/test_generation.py tests/test_jobs.py -q` passed in `services/api`.
- `uv run pytest tests/test_generation_tasks.py tests/test_image_providers.py -q` passed in `services/worker`.
- `corepack pnpm --filter @caragent/web typecheck` passed.
- `corepack pnpm --filter @caragent/web lint` passed.

## Deviations

`uv run mypy src` and contract/web Vitest checks required elevated execution because the sandbox could not access the user uv cache or spawn esbuild. The commands passed when rerun with approved elevation.

## Self-Check

PASSED.
