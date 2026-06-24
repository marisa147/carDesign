---
phase: 27
plan: 27-01
subsystem: web-preview
tags:
  - view-truthfulness
  - workbench
key-files:
  - apps/web/src/components/workbench/preview-panel.tsx
  - apps/web/src/app/page.test.tsx
metrics:
  requirements: 2
  tests_targeted: 2
---

# Phase 27 Summary: View Truthfulness And Current Preview Repair

## Completed

- Added frontend view capability resolution from `PreviewSpec.template.view` and future `template.supported_views` metadata.
- Kept the four workbench controls (`侧面`, `前视`, `后视`, `俯视`) visible.
- Side-only templates now report `侧面` as available and `前视/后视/俯视` as unavailable.
- Selecting an unavailable view renders the explicit empty state `模板未提供该视图` instead of reusing the side-view preview.
- Added a visible availability summary: `可用视图：侧面 · 未提供：前视、后视、俯视`.
- Updated the focused page test expectations for side-only template view switching.

## Requirements

| Requirement | Status | Evidence |
|-------------|--------|----------|
| VIEW-01 | Complete | Unavailable views render `模板未提供该视图`; overlay/image controls are hidden for unavailable view state. |
| VIEW-02 | Complete | Button area displays available and missing view summary derived from template capability. |

## Verification

- Passed: `apps\web\node_modules\.bin\tsc.CMD --noEmit -p apps\web\tsconfig.json`
- Blocked: `node_modules\.bin\vitest.CMD --run src/app/page.test.tsx` from `apps/web` failed before collecting tests with Node 20 + jsdom/CSS dependency `ERR_REQUIRE_ESM`.
- Blocked first attempt: root pnpm/Corepack path failed with `EPERM`/dynamic-import shim issues before test execution.

## Notes

- This phase intentionally does not create the GR86/BRZ package; Phase 28 owns real vehicle package schema/assets.
- Existing real artifact image rendering is preserved.
