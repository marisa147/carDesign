# Phase 19 UI Spec: Production Readiness Preflight

## Surface

The Workbench export panel gains a compact preflight section for the selected version. It stays inside the existing export/hand-off workflow.

## Requirements

- Show concept-only status for the selected version.
- Let the user run preflight when a generated version exists.
- Display blocker/missing evidence counts and the main missing evidence list.
- Keep print-ready production export controls disabled.
- Enhanced ZIP preview should show that preflight and template validation files are included.

## Copy Boundaries

- Use "概念预检", "非生产文件", and "缺少生产证据" language.
- Do not use "生产就绪", "print-ready", or equivalent success wording unless explicitly negated.

