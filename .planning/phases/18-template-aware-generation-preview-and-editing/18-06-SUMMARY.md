# Plan 18.06 Summary: Contract Drift And Archived Payload Regression Validation

## Result

Completed. Generated TypeScript contracts remain current, web/core/worker typechecks pass, and legacy PreviewSpec payloads remain compatible.

## Evidence

- `corepack pnpm --filter @caragent/contracts check` passed with real contract generation enabled.
- `corepack pnpm --filter @caragent/contracts typecheck` passed.
- Legacy `generic-side-coupe` fixture still resolves lightweight 3D compatibility.
- Unknown/unsupported PreviewSpec fixtures still render 2D fallback.

## Files

- `apps/web/src/app/page.test.tsx`
- `packages/contracts/openapi/openapi.json` (regenerated, no semantic diff)
- `packages/contracts/src/generated/client.ts` (regenerated, no semantic diff)

