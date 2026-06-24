# Phase 30 UI Spec: Construction Brief And Smart Q&A

## Chat Panel

- Show a compact requirement-completion panel when a brief exists.
- Display required core fields: vehicle template, character/theme, main color, wrap range, and text/logo.
- Ask the first missing required field as the visible next question.
- If the user's prompt mentions GPT supplement/autocomplete intent, show that GPT may fill reasonable style, composition, palette, and section details.
- Add `清除对话` beside `新建对话`; clearing removes local messages/draft while preserving saved workspace/brief state.

## Right Panel

- Display construction-order groups above editable fields:
  - 车型
  - 范围
  - 设计
  - 素材
  - 导出
  - 风险
- Missing required fields should be visible as `待补充`.
- Construction/auth/delivery risks should be warnings, not hard blockers.
- Existing `保存参数`, `生成概念`, `新建概念`, and `作废当前` remain the primary save/discard controls.

## Interaction Rules

- Sending a prompt still saves a draft brief immediately.
- The assistant summary must not say the brief is complete when required fields are missing.
- New conversation resets workspace-local session state.
- Clear conversation keeps the saved brief visible and does not delete persisted workspace records.
