---
phase: 12
slug: lightweight-3d-preview-mvp
status: complete
created: 2026-06-18
surface: workbench
requirements: [V2-3D-01, V2-3D-02, V2-3D-03, V2-3D-04, V2-3D-05]
---

# Phase 12 - UI Design Contract

## Product Surface

Phase 12 extends the existing AI workbench preview area. It must not introduce a landing page, hero section, marketing copy, or separate showcase page. The first screen remains the dense operational workbench.

## User Goals

- Open a 3D preview for the currently selected generated version.
- Rotate, zoom, reset the camera, and capture a screenshot.
- Understand that the preview is concept-only and not production UV proof.
- See a clear 2D fallback when the selected version has no compatible shell.
- Return to the 2D PreviewSpec preview without losing selected version state.

## Layout Contract

### Preview Mode Switch

- Add a compact 2D/3D mode switch inside the existing preview panel.
- Use buttons or tabs consistent with the current workbench controls.
- Do not hide existing version history, zoom/reset controls, safe-zone controls, comparison controls, or 2D fallback.

### 3D Viewer

- The 3D canvas is the primary content of the 3D mode and should fill the available preview surface.
- Do not put the canvas inside nested decorative cards. A simple bordered operational surface is acceptable if it matches the existing preview panel.
- Keep a stable minimum height on desktop and mobile so loading text, unsupported states, and canvas controls do not shift the surrounding layout.
- The selected version title/summary and source artifact metadata can remain compact above or below the viewer.

### Controls

Use icon buttons where possible:

- Rotate left/right: rotate icons or arrow icons.
- Zoom in/out: plus/minus icons.
- Reset camera: reset/rotate icon.
- Capture screenshot: camera icon.

Controls must have accessible labels. Visible text should be concise and only used where the action is unclear.

### Persistent Labels

Every 3D mode state must show:

- `概念 3D 预览`
- `非生产贴膜参考`

The label must remain visible after camera changes, screenshot capture, and selected version changes.

### Fallback State

When no compatible shell exists:

- Keep 2D preview available.
- Show a short fallback message: `当前模板暂无 3D 壳体，继续使用 2D 预览。`
- Do not disable generation, iteration, feedback, or export controls because of 3D incompatibility.

## Interaction Contract

- Switching 2D/3D mode preserves selected version.
- Selecting a different version re-evaluates 3D compatibility and resets stale screenshot status.
- Reset camera returns to the named default preset.
- Screenshot capture creates visible success/error feedback that does not permanently clutter the UI.
- If WebGL/canvas setup fails, the viewer shows fallback text and leaves 2D available.

## Visual Contract

- Keep panel-scale typography. No hero-scale type inside the workbench.
- Use existing semantic colors and avoid one-note palette changes.
- The viewer should read as an operational inspection tool, not a decorative product render.
- Avoid gradients, bokeh, ornamental blobs, and marketing-style imagery.
- Text must not overlap with controls, canvas, labels, or version history on desktop or mobile.

## Accessibility Contract

- Mode switch must expose selected state.
- Camera and capture controls must be keyboard reachable.
- The canvas container needs an accessible label describing selected version and concept-only status.
- Non-production warning must be readable without relying on color.
- Fallback state should be available to screen readers.
- Respect reduced motion where practical by pausing idle animation or keeping it subtle.

## Responsive Contract

- Desktop: viewer controls may sit in a compact row above or below the canvas.
- Mobile: controls wrap into multiple rows without horizontal scroll.
- Canvas keeps a useful aspect ratio and does not overflow the viewport width.

## Empty, Loading, And Error States

- No selected version: preserve current empty 2D preview state.
- Loading shell/spec: show compact loading state in the 3D surface.
- Incompatible shell: show fallback message and 2D path.
- Capture error: show inline destructive status with a retry action.
- Screenshot saved: show artifact-linked confirmation and auto-clear if existing surrounding UX supports it.

## Test Hooks And Verifiable Text

Automated tests should be able to find:

- `概念 3D 预览`
- `非生产贴膜参考`
- `当前模板暂无 3D 壳体，继续使用 2D 预览。`
- `重置相机`
- `截图`
- Submitted or returned metadata containing `preview_3d`.

## UI-SPEC COMPLETE
