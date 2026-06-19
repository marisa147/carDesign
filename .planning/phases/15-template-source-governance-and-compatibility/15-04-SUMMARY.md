---
phase: 15
plan: 04
status: complete
subsystem: generation-contracts
tags:
  - compatibility
  - preview-spec
key_files:
  created: []
  modified:
    - services/core/src/caragent_core/generation/templates.py
    - services/core/src/caragent_core/generation/briefs.py
    - services/core/src/caragent_core/generation/prompts.py
    - services/core/tests/test_generation_briefs.py
    - services/core/tests/test_prompt_plans.py
    - apps/web/src/app/page.test.tsx
    - apps/web/src/lib/api/generation.test.ts
metrics:
  tests_added: 2
  requirements_addressed:
    - V3-TEMPLATE-04
---

# Plan 15-04 Summary

## What Changed

- Preserved `SUPPORTED_TEMPLATE_ID = "generic-side-coupe"` for v1/v2 compatibility.
- Added `generic_coupe_side_v1` alias resolution to the legacy coupe template.
- Added `template_source` and `template_readiness` to `GenerationBriefPayload`.
- Added template source/readiness metadata to prompt payloads and `PreviewSpec.template`.
- Updated web fixtures to match the generated contract.

## Verification

- `uv run pytest tests/test_generation_briefs.py tests/test_prompt_plans.py -q` passed.
- `corepack pnpm --filter @caragent/web typecheck` passed.
- Elevated `corepack pnpm --filter @caragent/web test -- src/lib/api/generation.test.ts src/app/page.test.tsx` passed.

## Deviations

None.

## Self-Check

PASSED.
