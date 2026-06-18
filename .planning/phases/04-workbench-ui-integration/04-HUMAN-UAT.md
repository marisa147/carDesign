# Phase 4 Human UAT: Workbench UI Integration

**Date:** 2026-06-17
**Status:** passed
**Tester:** Codex Browser UAT
**Target:** `http://127.0.0.1:3000/`

## Counts

| Total | Passed | Issues | Pending | Blocked |
|-------|--------|--------|---------|---------|
| 10 | 10 | 0 | 0 | 0 |

## Environment

- Web dev server: `corepack pnpm --filter @caragent/web dev --hostname 127.0.0.1 --port 3000`
- API dev server: `uv run uvicorn caragent_api.main:app --host 127.0.0.1 --port 8000`
- Local services: Docker Compose PostgreSQL, Redis, and MinIO started with `corepack pnpm infra:up`
- Browser viewports checked: default desktop 1280x720, mobile 390x844

## Checks

| ID | Check | Result | Evidence |
|----|-------|--------|----------|
| UAT-01 | Workbench opens as first screen, not a marketing page. | Passed | DOM starts with app banner and workbench main regions. |
| UAT-02 | Chat panel and chat input are visible. | Passed | `对话` region and `设计需求` textbox present; textbox is inside initial viewport on desktop and mobile. |
| UAT-03 | 2D preview region is visible. | Passed | `2D 预览`, empty preview copy, and view buttons `侧面`, `前视`, `后视`, `俯视` present. |
| UAT-04 | Progress/events region is visible. | Passed | `进度` region present with waiting state and queued/running/succeeded/failed explanatory copy. |
| UAT-05 | Version/history region is visible. | Passed | `历史方案` region present with disabled placeholder version buttons before generated versions exist. |
| UAT-06 | Parameter panel is visible. | Passed | `参数` region present with template/view/style fields and disabled save before a brief exists. |
| UAT-07 | Asset panel is visible. | Passed | `素材` region present with upload file control, asset type selector, and disabled upload before workspace readiness. |
| UAT-08 | Future capability gates are disabled/deferred. | Passed | `3D 预览后续开放`, `生产导出后续开放`, and `市场功能后续开放` buttons are disabled. |
| UAT-09 | Desktop layout has no incoherent overlap or horizontal scroll. | Passed | 1280x720 check found `overlaps: []` and `scrollWidth == clientWidth`. |
| UAT-10 | Mobile layout has no incoherent overlap or horizontal scroll. | Passed | 390x844 check found `overlaps: []`, `scrollWidth == clientWidth`, and stacked workbench regions. |

## Notes

Browser UAT focused on the required Phase 4 visibility, responsive layout, and disabled future gates. Interaction coverage for chat-to-brief, parameter updates, asset rights, job state rendering, preview controls, and version switching is covered by automated web tests recorded in `04-VERIFICATION.md`.
