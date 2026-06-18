---
phase: 06-itasha-and-template-intelligence
plan: "03"
subsystem: api-contracts
tags: [fastapi, openapi, contracts, typescript, generation]

requires:
  - plan: "06-01"
    provides: core Phase 6 brief fields and PreviewSpec payload
provides:
  - Phase 6 generation brief create/update API fields
  - regenerated OpenAPI artifact
  - regenerated TypeScript contracts
  - contract drift verification
affects: [phase-06-04-workbench-ui]

tech-stack:
  patterns:
    - FastAPI request schemas define frontend-visible brief input fields
    - response payload remains `GenerationBriefPayload`
    - generated TypeScript contracts come from OpenAPI, not hand-written shapes

key-files:
  modified:
    - services/api/src/caragent_api/schemas.py
    - services/api/src/caragent_api/routes/generation.py
    - services/api/tests/test_generation.py
    - services/api/tests/test_openapi_export.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts

key-decisions:
  - "Phase 6 fields are added to existing create/update brief routes instead of adding new job routes."
  - "Patch payloads continue to reject empty updates while allowing any editable Phase 6 field."
  - "Generated contracts are refreshed from FastAPI OpenAPI and verified with the drift check."

patterns-established:
  - "OpenAPI tests assert Phase 6 field presence on create request, update request, and response payload schemas."
  - "Frontend must consume Phase 6 types from `@caragent/contracts`."

requirements-completed:
  - QUAL-01
  - QUAL-02
  - QUAL-03
  - QUAL-05

duration: 25 min
completed: 2026-06-18
---

# Phase 6 Plan 03: API Schema And Contract Summary

**The API and generated TypeScript contracts now expose Phase 6 itasha brief fields.**

## Accomplishments

- Added failing API tests for create and patch payloads carrying character focus, supporting graphics, racing/JDM cues, typography intent, color harmony, and overlay logo asset ids.
- Added OpenAPI export assertions that Phase 6 fields exist on create request, update request, and `GenerationBriefPayload` response schemas.
- Added Phase 6 fields to `GenerationBriefCreateRequest` and `GenerationBriefUpdateRequest`.
- Passed Phase 6 create fields through `create_generation_brief_route()` into the core brief factory.
- Regenerated `packages/contracts/openapi/openapi.json` and `packages/contracts/src/generated/client.ts`.
- Verified generated TypeScript contains the new Phase 6 fields.

## Verification

- RED: `uv run pytest -q tests/test_generation.py tests/test_openapi_export.py` in `services/api` failed as expected because create/update schemas did not expose Phase 6 fields.
- GREEN: `uv run pytest -q tests/test_generation.py tests/test_openapi_export.py` in `services/api` passed, 10 tests.
- `uv run ruff check .` in `services/api` passed.
- `uv run mypy src` in `services/api` passed after rerunning with escalation because the first run hit a Windows `uv` cache permission error.
- `uv run python -m caragent_api.scripts.export_openapi --out ../../packages/contracts/openapi/openapi.json` regenerated OpenAPI after an escalated rerun for the same `uv` cache permission issue.
- `corepack pnpm --filter @caragent/contracts generate` regenerated TypeScript contracts.
- `corepack pnpm contracts:check` passed after an escalated rerun because the sandbox blocks nested Node/Corepack process creation inside the check script on Windows.
- `rg` confirmed Phase 6 fields are present in both OpenAPI and generated TypeScript artifacts.

## Deviations from Plan

- No code-scope deviation.
- Contract verification needed an escalated `corepack pnpm contracts:check` run because the sandboxed Node process could not spawn the nested Corepack command and temporarily triggered the script fallback.

## Next Plan Readiness

Ready for `06-04`: workbench itasha controls, overlay/safe-zone toggles, warnings, and PreviewSpec display.
