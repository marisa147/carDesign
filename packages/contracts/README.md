# @caragent/contracts

This package is the shared API contract boundary between the FastAPI control plane and the Next.js workbench.

FastAPI and Pydantic own the source schema. The API exports OpenAPI JSON to `openapi/openapi.json`, then Orval generates the TypeScript client into `src/generated/client.ts`.

Manual TypeScript copies of backend request or response models are not allowed here. If the backend schema changes, regenerate contracts from OpenAPI instead of editing generated types by hand.

## Commands

- `pnpm --filter @caragent/contracts generate` runs Orval against `openapi/openapi.json`.
- `pnpm --filter @caragent/contracts check` delegates to the drift checker created by Plan 01-06.
- `pnpm --filter @caragent/contracts typecheck` type-checks the generated client and package entrypoint after generation exists.
- `pnpm --filter @caragent/contracts lint` currently uses the same strict TypeScript gate as `typecheck`.

Plan 01-05 creates the package scaffold only. Plan 01-06 owns `openapi/openapi.json`, `src/generated/client.ts`, and the contract drift check script.

No environment files, provider keys, backend internals, or runtime secrets belong in this package.
