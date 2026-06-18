---
phase: 04-workbench-ui-integration
plan: "05"
subsystem: web-workbench-assets
tags: [nextjs, react, assets, rights, references]

requires:
  - plan: "04-01"
    provides: asset API wrapper and query keys
  - plan: "04-04"
    provides: parameter panel save flow
provides:
  - asset upload UI
  - asset list and metadata display
  - rights/source update UI
  - missing-rights generation-use gating
  - confirmed asset reference integration with parameters
affects: [phase-04-generation-submit, phase-04-preview-history]

tech-stack:
  patterns:
    - `AssetPanel` owns local upload/right-edit drafts
    - `WorkbenchApp` owns canonical assets and selected reference ids
    - `ParameterPanel` receives selected references and saves them through the brief update route

key-files:
  created:
    - apps/web/src/components/workbench/asset-panel.tsx
  modified:
    - apps/web/src/components/workbench/workbench-app.tsx
    - apps/web/src/components/workbench/parameter-panel.tsx
    - apps/web/src/app/page.test.tsx

key-decisions:
  - "Workspace resume now loads assets alongside workspace, messages, and briefs."
  - "Missing-rights assets remain visible but their `用于生成` checkbox is disabled."
  - "Confirming rights sends `rights_status: confirmed` plus source/notes through the asset rights API."
  - "Selected confirmed asset ids are surfaced as `引用素材 ID` and saved through `reference_asset_ids`."

patterns-established:
  - "Multipart upload tests assert FormData contents and no manual content-type header."
  - "Asset and brief caches are updated from mutation responses to keep the workbench responsive."

requirements-completed:
  - UI-03
  - UI-02

duration: 30 min
completed: 2026-06-17
---

# Phase 4 Plan 05: Asset Panel Summary

**The workbench now supports rights-aware reference asset upload and selection.**

## Accomplishments

- Added `AssetPanel` with visible file upload, kind selection, asset metadata rows, rights/source fields, and error states.
- Wired asset resume/listing into `WorkbenchApp` so assets load with canonical workspace state.
- Implemented upload through `uploadWorkspaceAsset` using multipart `FormData`.
- Implemented rights confirmation through `updateAssetRights`.
- Blocked missing-rights assets from generation reference selection while still listing them clearly.
- Connected confirmed asset selection to `ParameterPanel` via `reference_asset_ids`.
- Added tests for upload route/body, missing-rights gating, rights update payloads, reference selection, and parameter save payloads.

## Deviations from Plan

- Asset list refresh is currently driven by mutation responses plus query cache updates rather than an additional post-mutation GET. This keeps the UI canonical for the returned asset rows without adding extra network calls in the tests.

## Issues Encountered

- `Badge` has no `success` variant in the local UI primitive, so confirmed rights use the existing `primary` variant.
- Existing resume tests needed an asset-list mock because assets are now part of the canonical resume state.

## Verification

- RED: `corepack pnpm --filter @caragent/web test -- page.test.tsx` failed because the asset panel and asset resume call did not exist.
- GREEN: `corepack pnpm --filter @caragent/web test -- page.test.tsx` passed, 6 files / 25 tests.
- `corepack pnpm --filter @caragent/web typecheck` passed.
- `corepack pnpm --filter @caragent/web lint` passed.

## Next Plan Readiness

Ready for `04-06`: assets and references are now part of the workbench state, so progress, preview, and history can focus on job/artifact/version state.
