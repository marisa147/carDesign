---
phase: 11-reference-guided-generation-mvp
plan: "01"
subsystem: reference-contracts
tags: [references, rights, provider-capabilities, openapi, contracts]

requires:
  - phase: 10-targeted-regeneration-and-masked-editing-mvp
    provides: generated contract workflow, provider capability map, and structured generation brief patterns
provides:
  - Typed `ReferenceRole`, `ReferenceAssignment`, `ReferenceRightsSnapshot`, `ReferenceUsageItem`, and `ReferenceUsageSnapshot` contracts
  - Structured `reference_usage` on generation brief create/update payloads while preserving legacy `reference_asset_ids`
  - Browser-safe provider reference capability metadata for local deterministic and BFL providers
  - Current OpenAPI and generated TypeScript contracts for reference usage fields
affects:
  - phase-11-reference-guided-generation
  - workbench-reference-upload
  - prompt-planning-reference-usage
  - worker-reference-snapshotting
  - provider-capability-status

tech-stack:
  added: []
  patterns:
    - shared core Pydantic schemas are imported by API request contracts
    - browser-visible provider capabilities explicitly distinguish prompt guidance from verified image-reference input
    - contract checks may need unsandboxed execution on Windows to avoid fallback client generation

key-files:
  created:
    - services/core/src/caragent_core/references.py
    - .planning/phases/11-reference-guided-generation-mvp/11-01-SUMMARY.md
  modified:
    - services/core/src/caragent_core/enums.py
    - services/core/src/caragent_core/generation/briefs.py
    - services/core/src/caragent_core/provider_capabilities.py
    - services/api/src/caragent_api/schemas.py
    - services/api/src/caragent_api/routes/generation.py
    - services/core/tests/test_models.py
    - services/core/tests/test_prompt_plans.py
    - services/api/tests/test_generation.py
    - services/api/tests/test_operations.py
    - packages/contracts/openapi/openapi.json
    - packages/contracts/src/generated/client.ts

key-decisions:
  - "Use six explicit reference roles: character, style, vehicle, logo, palette, and inspiration."
  - "Keep `reference_asset_ids` as a legacy compatibility field while adding structured `reference_usage` for role-aware flows."
  - "Local deterministic references are prompt-guidance metadata only; BFL reference-image input remains unsupported until adapter support is verified."
  - "Rights/source snapshots carry metadata and schema version only; binary image bytes remain outside the reference contracts."

patterns-established:
  - "`ReferenceAssignment.model_dump(mode=\"json\")` produces string UUIDs and schema version 1."
  - "`GenerationBriefPayload` accepts both `reference_asset_ids` and structured `reference_usage`."
  - "`provider.capabilities[*].reference_input` exposes accepted/supported/prompt-guidance/unsupported roles without credentials."

requirements-completed:
  - V2-REF-01
  - V2-REF-02
  - V2-REF-03
  - V2-REF-05

duration: 41 min
completed: 2026-06-18
---

# Phase 11 Plan 01: Reference Contract Foundation Summary

**Typed reference roles, usage metadata, provider capability visibility, and generated API contracts**

## Performance

- **Duration:** 41 min
- **Completed:** 2026-06-18T22:09:41+08:00
- **Tasks:** 4
- **Files modified:** 11

## Accomplishments

- Added shared core reference contracts with schema-versioned assignment, rights snapshot, usage item, and usage snapshot models.
- Extended generation brief create/update contracts with optional structured `reference_usage`, preserving legacy `reference_asset_ids` behavior.
- Added provider capability metadata for reference handling, making local prompt-guidance support and BFL unverified image-reference support explicit.
- Regenerated OpenAPI and TypeScript contracts so the web app can consume `ReferenceAssignment`, `ReferenceRole`, and `reference_usage`.

## Task Commits

1. **Task 1: Add red tests for reference roles, snapshots, and capability metadata** - `1d844f2` (test)
2. **Tasks 2-4: Add shared reference contracts, provider metadata, API passthrough, and generated contracts** - `496ae61` (feat)

## Files Created/Modified

- `services/core/src/caragent_core/references.py` - Shared Phase 11 reference assignment, rights snapshot, usage item, and usage snapshot schemas.
- `services/core/src/caragent_core/enums.py` - Added `ReferenceRole`.
- `services/core/src/caragent_core/generation/briefs.py` - Added structured `reference_usage` to generation briefs.
- `services/core/src/caragent_core/provider_capabilities.py` - Added `reference_input`, `supports.references`, and `supports.reference_image_inputs`.
- `services/api/src/caragent_api/schemas.py` - Added optional `reference_usage` to generation brief create/update requests.
- `services/api/src/caragent_api/routes/generation.py` - Passes structured reference usage into the core brief builder.
- `services/core/tests/test_models.py` and `services/core/tests/test_prompt_plans.py` - Core schema and brief round-trip coverage.
- `services/api/tests/test_generation.py` and `services/api/tests/test_operations.py` - API round-trip and provider capability coverage.
- `packages/contracts/openapi/openapi.json` and `packages/contracts/src/generated/client.ts` - Generated contract updates.

## Decisions Made

- Reference roles are intentionally narrow and product-facing. Additional roles require enum and contract changes rather than freeform strings.
- `ReferenceRightsSnapshot` stores source/rights metadata and immutable object identifiers, not image bytes.
- `supports.references` means the provider can participate in a reference-guided flow; `supports.reference_image_inputs` means actual reference-image input has been verified.
- Local deterministic uses prompt guidance only, so `reference_input.accepted` remains false while `prompt_guidance_roles` lists all six roles.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Contract check needed unsandboxed execution**
- **Found during:** Task 4 (Extend API schemas and generated contracts)
- **Issue:** `corepack pnpm contracts:check` in the sandbox reported Orval generation as blocked and rewrote `client.ts` with the deterministic health-only fallback.
- **Fix:** Regenerated the real Orval client, exported OpenAPI with elevated `uv` cache access, then reran `corepack pnpm contracts:check` with sandbox escalation.
- **Files modified:** `packages/contracts/openapi/openapi.json`, `packages/contracts/src/generated/client.ts`
- **Verification:** `corepack pnpm contracts:check` reported "Contract artifacts are current."

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** No scope change. Generated contracts are current and the Windows sandbox behavior is documented for future Phase 11 work.

## Issues Encountered

- `uv run python -m caragent_api.scripts.export_openapi` initially failed because the sandbox could not open the user-level `uv` cache. Rerunning with sandbox escalation succeeded.
- `git diff --check` passed, with only a line-ending warning for the generated OpenAPI JSON.

## Verification

- `cd services/core && uv run pytest -q tests/test_models.py tests/test_prompt_plans.py` - passed, 11 tests.
- `cd services/api && uv run pytest -q tests/test_generation.py tests/test_operations.py` - passed, 34 tests.
- `corepack pnpm contracts:check` - passed with unsandboxed execution so real OpenAPI export and Orval generation ran.
- `git diff --check` - passed.

## User Setup Required

None - no provider keys or external service configuration required.

## Next Phase Readiness

Ready for `11-02-PLAN.md`: the web workbench can now capture structured reference assignments against the stable `ReferenceAssignment` contract and provider capability metadata.

---
*Phase: 11-reference-guided-generation-mvp*
*Completed: 2026-06-18*
