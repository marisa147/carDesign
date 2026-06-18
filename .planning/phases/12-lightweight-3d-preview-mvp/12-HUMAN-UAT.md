---
phase: 12-lightweight-3d-preview-mvp
artifact: human-uat
status: blocked
created: 2026-06-18
updated: 2026-06-18
requirements: [V2-3D-02, V2-3D-03, V2-3D-05]
---

# Phase 12 Human UAT - Lightweight 3D Preview

## Current Status

Blocked before browser visual evidence.

The 12-07 automated accessibility/static pass is complete, but desktop/mobile browser screenshots and canvas-pixel evidence could not be collected in the current Codex run because local process spawning is blocked and the required elevated retry was rejected by the environment usage limit.

## Automated Pre-Browser Evidence

| Check | Result | Notes |
|-------|--------|-------|
| `corepack pnpm --filter @caragent/web typecheck` | pass | Validated 3D viewer/panel TypeScript changes. |
| `corepack pnpm --filter @caragent/web lint` | pass | Validated 3D viewer/panel/page test lint. |
| `git diff --check` | pass | No whitespace errors before commit. |

## Browser UAT Attempts

| Step | Command / Action | Result |
|------|------------------|--------|
| Port check | `Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue` | No listener found on port 3000. |
| Start Next dev server, first attempt | `corepack pnpm --filter @caragent/web dev -- --hostname 127.0.0.1 --port 3000` via `Start-Process` | Failed because pnpm passed `--hostname` as a project directory argument to Next. |
| Start Next dev server, corrected sandbox attempt | `corepack pnpm dev --hostname 127.0.0.1 --port 3000` from `apps/web` via `Start-Process` | Failed with `Error: spawn EPERM` from Next dev startup. |
| Elevated retry | Same corrected `Start-Process` command with elevated execution | Rejected by environment usage limit before a browser server could start. |

## Test Runner Limitation

| Command | Result |
|---------|--------|
| `corepack pnpm --filter @caragent/web exec vitest --run src/app/page.test.tsx` | Failed on Windows/pnpm workspace binary resolution: `vitest` not recognized. |
| `corepack pnpm exec vitest --run src/app/page.test.tsx` from `apps/web` | Failed on Windows/pnpm local binary resolution: `vitest` not recognized. |
| `corepack pnpm --filter @caragent/web test` | Reached package script but failed while loading `vitest.config.ts` with esbuild `Error: spawn EPERM`. |

## Required Follow-Up

Run these after the Codex usage limit resets or in a local shell that can spawn child processes:

```powershell
cd D:\python\carAgent\apps\web
corepack pnpm dev --hostname 127.0.0.1 --port 3000
```

Then open `http://127.0.0.1:3000` and verify:

- Desktop viewport around 1440x900: 3D mode opens for a generated version, canvas/surface is nonblank, `概念 3D 预览` and `非生产贴膜参考` remain visible, controls wrap cleanly, and screenshot status auto-clears.
- Mobile viewport around 390x844: 3D mode controls wrap without horizontal scroll or overlap, fallback text remains readable, and the 2D preview button remains available.
- Canvas-pixel/nonblank check: sample the 3D surface screenshot and confirm there are multiple non-background colors or a visible canvas placeholder/scene.

## Sign-Off

- [x] Automated 12-07 typecheck passed.
- [x] Automated 12-07 lint passed.
- [x] 3D panel accessibility hardening committed.
- [ ] Desktop browser screenshot collected.
- [ ] Mobile browser screenshot collected.
- [ ] Canvas-pixel/nonblank evidence collected.
- [ ] 12-07 summary created after browser evidence is available.
