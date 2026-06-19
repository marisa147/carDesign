---
phase: 15
status: passed
verified_at: "2026-06-19T13:55:00Z"
requirements:
  total: 5
  passed: 5
  gaps: 0
human_verification:
  required: false
---

# Phase 15 Verification

## Result

Phase 15 passed. Template source governance and compatibility are implemented, tested, documented, and reflected in generated contracts.

## Requirement Evidence

| Requirement | Evidence | Status |
|-------------|----------|--------|
| V3-TEMPLATE-01 | `template_source_policy_table()` plus `docs/template-governance.md` source policy table. | Passed |
| V3-TEMPLATE-02 | `TemplateSourceMetadata`, `VehicleTemplateRecord`, `TemplateRegistry.register()`, and audit tests. | Passed |
| V3-TEMPLATE-03 | Registry validation rejects prohibited sources, missing licensed evidence, and non-reusable license states. | Passed |
| V3-TEMPLATE-04 | `SUPPORTED_TEMPLATE_ID` remains `generic-side-coupe`; `generic_coupe_side_v1` alias resolves without warning; brief/prompt/PreviewSpec carry new metadata. | Passed |
| V3-TEMPLATE-05 | `audit_vehicle_templates()` and `TemplateAuditItem` expose readiness, source, license, missing files, and blocking issues. | Passed |

## Automated Checks

| Command | Result |
|---------|--------|
| `uv run pytest tests/test_generation_briefs.py tests/test_prompt_plans.py -q` in `services/core` | Passed |
| `uv run pytest -q` in `services/core` | Passed |
| `uv run ruff check .` in `services/core` | Passed |
| `uv run mypy src` in `services/core` | Passed with approved elevation |
| `uv run pytest tests/test_generation.py tests/test_jobs.py -q` in `services/api` | Passed |
| `uv run pytest tests/test_generation_tasks.py tests/test_image_providers.py -q` in `services/worker` | Passed |
| `corepack pnpm --filter @caragent/contracts check` | Passed with approved elevation |
| `corepack pnpm --filter @caragent/contracts typecheck` | Passed |
| `corepack pnpm --filter @caragent/web typecheck` | Passed |
| `corepack pnpm --filter @caragent/web lint` | Passed |
| `corepack pnpm --filter @caragent/web test -- src/lib/api/generation.test.ts src/app/page.test.tsx` | Passed with approved elevation |

## Notes

- `contracts check` must run elevated in this Codex sandbox because the script otherwise falls back to a minimal OpenAPI client.
- Web Vitest must run elevated in this Codex sandbox because esbuild startup hits `spawn EPERM`.
- The phase keeps print-ready production claims out of scope.
