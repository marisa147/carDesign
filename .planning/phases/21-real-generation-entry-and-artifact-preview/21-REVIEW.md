---
phase: 21-real-generation-entry-and-artifact-preview
status: clean
reviewed: 2026-06-22
files_reviewed: 16
findings_open: 0
findings_fixed_during_review: 4
---

# Phase 21 Code Review

## Verdict

Clean after review fix.

## Fixed During Review

### Binary artifact content route was documented as binary but generated client parsed JSON

- **Severity:** High
- **Files:** `services/api/src/caragent_api/routes/jobs.py`, `services/api/tests/test_jobs.py`, `packages/contracts/src/generated/client.ts`, `scripts/patch-contract-binary-routes.mjs`
- **Issue:** The artifact content endpoint returned image bytes correctly at runtime, but the OpenAPI declaration did not explicitly advertise binary image media types. After adding binary media types, Orval generated `Blob` response types but still emitted a fetch implementation that called `res.text()` and `JSON.parse(body)`, which would break any direct use of the generated client for real image content.
- **Fix:** The route now declares binary response content for `application/octet-stream`, `image/png`, and `image/webp`; the API test asserts that `application/json` is not advertised for the 200 response; contracts generation now runs a deterministic post-generation patch that makes the artifact content operation return `await res.blob()` on successful responses and `await res.json()` on error responses.


## Fixed During Validation

### Aggregate validate was not reproducible with local service `.env` files

- **Severity:** Medium
- **Files:** `services/api/tests/conftest.py`, `services/worker/tests/conftest.py`
- **Issue:** `services/api/.env` and `services/worker/.env` can hold local hosted-provider smoke settings. Unit tests that expected local deterministic defaults were reading those files during `pnpm validate`.
- **Fix:** API and Worker tests now run from per-test temporary directories. Worker tests also clear the cached settings before and after each test.

### Web lint flagged hydration-gated chat submit state

- **Severity:** Medium
- **File:** `apps/web/src/components/workbench/chat-panel.tsx`
- **Issue:** React lint rejected synchronous `setState` inside an effect used only to detect hydration.
- **Fix:** The component now uses `useSyncExternalStore` with server/client snapshots for the hydration gate.

### Core mypy could not narrow optional secret values

- **Severity:** Low
- **File:** `services/core/src/caragent_core/storage.py`
- **Issue:** `StorageSettings.from_object()` called `get_secret_value()` through an optional dynamic attribute, which mypy treated as possibly `None`.
- **Fix:** Added a runtime-checkable `SecretValue` protocol and explicit string normalization.

## Verification

- `corepack pnpm validate`
- `corepack pnpm --filter @caragent/contracts generate`
- `corepack pnpm contracts:check`
- `corepack pnpm --filter @caragent/contracts typecheck`
- `corepack pnpm --filter @caragent/web typecheck`
- `corepack pnpm --filter @caragent/web test -- page.test.tsx`
- `uv run pytest -q tests/test_jobs.py -k artifact_content` from `services/api`
- `uv run ruff check .` from `services/api`
- `uv run ruff check .` from `services/core`
- `uv run ruff check .` from `services/worker`

## Open Questions

None.
