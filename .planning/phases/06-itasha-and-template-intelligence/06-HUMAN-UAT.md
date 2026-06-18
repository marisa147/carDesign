---
status: passed
phase: 06-itasha-and-template-intelligence
source:
  - 06-VERIFICATION.md
started: 2026-06-18
updated: 2026-06-18
---

# Phase 6 Human UAT

## Current Test

Browser UAT against local web/API services for Phase 6 itasha controls, PreviewSpec overlays, safe zones, warnings, export boundary, and responsive layout.

## Tests

### 1. Desktop Phase 6 controls
expected: Workbench shows Phase 6 controls and warning copy.
result: passed

Evidence:
- Visible: `痛车设计控制`, `角色焦点`, `辅助图形`, `赛车/JDM 元素`, `字体意图`, `配色协调`, `质量提示`.
- Visible warning: `Text may be hard to read; shorten or enlarge the lettering.`

### 2. Desktop PreviewSpec
expected: Selected generated version shows renderer-neutral PreviewSpec details.
result: passed

Evidence:
- Visible: `PreviewSpec 摘要`, `图层 1`, `安全区 5`, `警告 1`.
- Visible: `文字/Logo 图层`, `安全区`, `模板参考区`.

### 3. Toggle accessibility state
expected: Overlay and safe-zone toggles expose selected state.
result: passed

Evidence:
- Safe-zone toggle changed `aria-pressed` from `false` to `true`.
- Overlay toggle changed `aria-pressed` from `true` to `false` and back to `true`.
- Safe-zone view displayed `door-main` and `rear-quarter`.

### 4. Desktop layout
expected: Desktop has no horizontal document scroll, no visible control overlap, and no app console errors.
result: passed

Evidence:
- Desktop measured client `1265 x 900`.
- `scrollWidth == clientWidth`.
- Interactable overlap count: `0`.
- Browser page console errors: `0`.

### 5. Mobile layout
expected: 390px mobile viewport remains usable without horizontal scroll, button overflow, or control overlap.
result: passed

Evidence:
- Requested viewport `390 x 844`; measured client width `375`.
- `scrollWidth == clientWidth`.
- Button overflow: `[]`.
- Interactable overlap count: `0`.
- Browser page console errors: `0`.

### 6. Concept export boundary
expected: Export remains a concept package and includes PreviewSpec summary data.
result: passed

Evidence:
- Visible: `概念预览，不是生产印刷文件。`
- Export record showed: `Concept preview only, not print-ready.`
- Export UI retained `PreviewSpec 摘要` and `警告 1`.

### 7. Deferred future gates
expected: Future production/3D capabilities remain deferred rather than silently available.
result: passed

Evidence:
- Visible disabled/deferred gate: `生产导出后续开放`.

## Issues Found During UAT

1. PATCH warning refresh
status: resolved

Observed: After editing long text through the API, `warnings` stayed empty because the update route merged fields without recomputing quality warnings.

Fix: Added core `refresh_generation_brief_warnings()` and invoked it from `PATCH /generation/briefs/{id}`. Regression test now covers the behavior.

2. Running worker hot reload
status: resolved

Observed: The long-running Celery worker process generated one succeeded job without `preview_spec`, indicating it was still running old code.

Handling: Browser UAT final data was seeded through the current worker function directly. The old worker was then restarted with Windows-compatible Celery `--pool=solo`, and queued job `2b022613-938b-409e-8422-d6e70e27fcc5` succeeded with `has_preview_spec: true` and `warning_count: 1`. Phase 7 should still add operational visibility around stale workers/restarts.

## Summary

total: 7
passed: 7
issues: 0
pending: 0
skipped: 0
blocked: 0

## Gaps

None.
