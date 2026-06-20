# Phase 20 Baseline Validation

**Status:** Passed  
**Date:** 2026-06-20  
**Requirement:** V3-REL-01

## Commands

| Command | Result | Notes |
|---------|--------|-------|
| `corepack pnpm validate` | Passed | Aggregate host prerequisite, env, web, core, API, worker, and contracts validation passed after fixing two web lint warnings. |
| `uv run python -m caragent_core.generation.validate_template_pack` | Passed | Validated all 5 MVP vehicle templates from the internal-original package. |
| `corepack pnpm compat:v1` | Passed | Verified 22 routes, 10 schemas, and 21 client surfaces for archived v1/v2 compatibility. |
| `corepack pnpm migration:safety` | Passed | Verified Alembic head `f2d60f906fc6` and v1 durable ledger tables. |
| `corepack pnpm smoke:worker -- --dry-run` | Passed | Worker smoke command wiring passed without requiring live hosted provider calls. |

## Fixes During Validation

- `apps/web/src/components/workbench/workbench-app.tsx`: the one-shot resume effect now uses `DEFAULT_WORKBENCH_TEMPLATE_ID` as its fallback instead of closing over mutable selected-template state.
- `apps/web/src/components/workbench/parameter-panel.tsx`: the template thumbnail remains a plain `<img>` because catalog thumbnails are API/package assets, not Next image-optimized application media.

## Result

V3 template governance, MVP template pack, catalog selection, template-aware generation/preview/editing, production readiness preflight, enhanced handoff evidence, contracts, and archived payload compatibility are covered by the current validation command surface. No hosted credentials, paid provider calls, or production output claims were required.

