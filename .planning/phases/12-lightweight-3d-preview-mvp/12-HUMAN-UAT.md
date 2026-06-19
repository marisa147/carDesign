---
phase: 12-lightweight-3d-preview-mvp
artifact: human-uat
status: passed
created: 2026-06-18
updated: 2026-06-19
requirements: [V2-3D-02, V2-3D-03, V2-3D-05]
---

# Phase 12 Human UAT - Lightweight 3D Preview

## Current Status

Passed with browser visual evidence on 2026-06-19.

Phase 12 Plan 07 now has desktop and mobile browser evidence for a nonblank lightweight 3D preview, persistent concept-only labels, accessible camera/screenshot controls, and mobile-safe framing. The original 2026-06-18 browser startup blocker was resolved by restarting local API/web services and using headless Chrome CDP for screenshots after the in-app Browser could inspect the DOM but could not capture screenshots or read WebGL pixels in this run.

## Automated Evidence

| Check | Result | Notes |
|-------|--------|-------|
| `corepack pnpm --filter @caragent/web typecheck` | pass | Re-run after mobile canvas framing fix. |
| `corepack pnpm --filter @caragent/web lint` | pass | Re-run after mobile canvas framing fix. |
| `git diff --check` | pass | No whitespace errors before commit. |

## Browser Fixture

| Item | Value |
|------|-------|
| Web app | `http://127.0.0.1:3000` |
| API | `http://127.0.0.1:8000` |
| Browser driver | Headless Chrome CDP on `127.0.0.1:9223` |
| Workspace | `c1dcd152-e8df-4fe1-973f-50adc3b36e93` |
| Brief | `bf3c22fe-e39c-435b-8c92-66c375e4a255` |
| Generated job | `46a54d7f-2ee2-4c83-b2b0-446d29823b53` |
| Generated version | `9169d366-6909-46dd-9256-fb2eb121c615` |
| Generated artifact | `dd85fff9-ad63-4a3b-8024-b2778f98ef98` |

## Browser Visual Evidence

| Viewport | Evidence | Result |
|----------|----------|--------|
| Desktop 1440x900 | `.planning/phases/12-lightweight-3d-preview-mvp/evidence/12-07-desktop-3d.png` | Pass. 3D tab is active, vehicle shell is visible, controls fit in one wrapped row, `概念 3D 预览` and `非生产贴膜参考` remain visible, and no overlap/horizontal overflow is present. |
| Mobile 390x844, device scale 2 | `.planning/phases/12-lightweight-3d-preview-mvp/evidence/12-07-mobile-3d.png` | Pass. 3D tab is active, vehicle shell is fully framed inside the canvas, controls wrap into multiple rows without overlap, 2D preview remains available, and warning/source text stays readable. |

## Canvas / Nonblank Evidence

Screenshot crop statistics were collected from the visible 3D surface after browser capture:

| Viewport | Crop | Unique colors | Dominant background | Non-background pixels | Result |
|----------|------|---------------|---------------------|-----------------------|--------|
| Desktop | `(430, 257, 974, 563)` from 1440x900 screenshot | 290 | 80.40% | 32,627 | Pass |
| Mobile | `(100, 284, 679, 795)` from 780x1688 screenshot | 339 | 82.38% | 52,130 | Pass |

The in-app Browser DOM inspection also confirmed the accessible region `概念 3D 预览，非生产贴膜参考`, image label `概念 3D 预览，非生产贴膜参考，版本 1`, camera controls, shell id `generic-side-coupe-lightweight-v1`, camera preset `front-left-default`, UV warning text, and safe-zone/overlay chips. Direct WebGL `readPixels` returned zeroed samples in this environment, so the durable evidence uses browser screenshot crops.

## Test Runner Limitation

| Command | Result |
|---------|--------|
| `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx` | Failed on Windows/pnpm workspace binary resolution: `vitest` not recognized. |
| `corepack pnpm exec vitest --run src/app/page.test.tsx` from `apps/web` | Failed on Windows/pnpm local binary resolution: `vitest` not recognized. |
| `corepack pnpm --filter @caragent/web test` | Reached package script but failed while loading `vitest.config.ts` with esbuild `Error: spawn EPERM`. |

Vitest should be rerun outside the current Codex sandbox when local child-process spawning is available. The plan's required browser evidence, typecheck, lint, and visual nonblank checks passed.

## Sign-Off

- [x] Automated 12-07 typecheck passed.
- [x] Automated 12-07 lint passed.
- [x] 3D panel accessibility hardening committed.
- [x] Desktop browser screenshot collected.
- [x] Mobile browser screenshot collected.
- [x] Canvas-pixel/nonblank evidence collected.
- [x] 12-07 summary created after browser evidence is available.
