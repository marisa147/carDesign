# Phase 5 Human UAT: Iteration, Feedback, And Concept Export

**Date:** 2026-06-18
**Status:** passed
**Tester:** Codex Browser UAT
**Target:** `http://127.0.0.1:3000/`

## Counts

| Total | Passed | Issues | Pending | Blocked |
|-------|--------|--------|---------|---------|
| 12 | 12 | 0 | 0 | 0 |

## Environment

- Web dev server: `corepack pnpm --filter @caragent/web exec next dev --hostname 127.0.0.1 --port 3000`
- API dev server: `uv run uvicorn caragent_api.main:app --reload --host 127.0.0.1 --port 8000`
- Worker: Celery worker consuming `caragent.default`
- Local services: Docker Compose PostgreSQL, Redis, and MinIO
- Browser viewports checked: default desktop, mobile 390x844
- Live UAT workspace: `f4080584-cef6-4067-98d4-7ebfa6204d74`

## Checks

| ID | Check | Result | Evidence |
|----|-------|--------|----------|
| UAT-01 | User can create a workbench session from the chat UI. | Passed | Browser submitted a design request and the UI showed `结构化 brief 已保存`. |
| UAT-02 | Existing version is preserved when generating a child iteration. | Passed | Live API/worker flow ended with 2 versions and 2 artifacts after child job `ecec23ac-1648-4044-8cea-049183636ae1` succeeded. |
| UAT-03 | Targeted iteration request is accepted. | Passed | Child iteration submitted change request `Increase pink side accents while preserving PHASE FIVE door text.` and parameter overrides. |
| UAT-04 | Lineage and comparison UI are visible. | Passed | Browser UAT found `版本对比`, lineage depth, parent/current version copy, and parameter diff rows. |
| UAT-05 | Feedback can be recorded and shown. | Passed | Live feedback record appears in `反馈历史` with rating 5, approval, and comment `Phase 5 browser UAT approval.` |
| UAT-06 | Feedback controls unlock when the user provides feedback input. | Passed | After selecting rating 5, `提交反馈` became enabled. |
| UAT-07 | Concept export manifest is visible for the selected version. | Passed | Browser UAT found `Manifest 预览`, selected version id, artifact id, object key, and format. |
| UAT-08 | Concept export history is visible. | Passed | Browser UAT found `导出历史`, `PNG`, `requested`, and `client-review`. |
| UAT-09 | Concept export controls unlock when a selected version has an artifact. | Passed | `创建概念导出` was enabled with generated version/artifact data loaded. |
| UAT-10 | Output is not represented as production-ready. | Passed | Browser UAT found `概念预览，不是生产印刷文件。` and `not print-ready`, and did not find `production-ready` or `生产就绪`. |
| UAT-11 | Desktop layout has no incoherent overlap or horizontal scroll. | Passed | Default desktop check found `overlaps: []`, no horizontal overflow, and no fresh console errors. |
| UAT-12 | Mobile layout has no incoherent overlap or horizontal scroll. | Passed | 390x844 check found `overlaps: []`, `scrollWidth == clientWidth`, and no fresh console errors. |

## Notes

During UAT, three runtime integration gaps were found and fixed before this artifact was marked passed: API Redis transport dependency, API queue routing to `caragent.default`, and worker `asyncpg` dependency for PostgreSQL generation tasks. The final live UAT and automated checks in `05-VERIFICATION.md` were run after those fixes.
