---
status: checklist-ready
phase: 21-real-generation-entry-and-artifact-preview
source:
  - 21-VERIFICATION.md
started: 2026-06-22
updated: 2026-06-22
---

# Phase 21 Human UAT

## Current Test

Awaiting manual desktop/mobile browser validation against a running local API, Worker, and web app.

## Tests

### 1. Fresh generation from workbench

expected: A user can create a brief, click `生成概念`, see the job enter queued/running state, and see progress refresh without manual reload.
result: pending

### 2. Generated image appears in 2D preview

expected: After job success, the 2D preview renders an image from `content_url` with `alt="2D concept preview"`.
result: pending

### 3. PreviewSpec overlays remain available

expected: When the selected version has PreviewSpec data, `PreviewSpec 摘要` remains visible and overlay/safe-zone toggles still affect layers above the generated image.
result: pending

### 4. Resume shows latest generated artifact

expected: After browser refresh or workspace resume, the latest generated artifact still renders through its stable `content_url`.
result: pending

### 5. Mobile layout remains usable

expected: On a mobile viewport, the generate action, progress state, generated image, and PreviewSpec controls remain visible without horizontal overflow.
result: pending

## Summary

total: 5
passed: 0
issues: 0
pending: 5
skipped: 0
blocked: 0

## Gaps

None recorded yet. Manual UAT is pending.
