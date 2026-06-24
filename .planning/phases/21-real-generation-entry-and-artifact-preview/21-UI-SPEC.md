# Phase 21 UI Spec: Real Generation Entry And Artifact Preview

## Surface

The existing workbench remains the first screen. Phase 21 changes the parameter panel, job progress state, and 2D preview area only. Do not add a landing page, marketing copy, or a separate proof page.

## Layout Contract

- Place `生成概念` in the same action row as `保存参数`, after the save action.
- Keep the action row compact and scannable in the right-side parameter panel.
- The preview panel keeps its current 2D/3D mode switch and version history layout.
- The 2D image must fit within the existing preview frame using `object-contain`; it must not crop generated content.
- PreviewSpec overlay controls remain near the PreviewSpec summary and canvas.

## Interaction Contract

- `生成概念` is disabled when no brief exists, when a save is in progress, when generation submission is in progress, or while the workbench is loading.
- If parameters are dirty, clicking `生成概念` first saves the dirty fields and then submits the generation job.
- Queued and running jobs refresh automatically; terminal states stop automatic polling.
- A submitted job appears immediately in job/progress state before worker completion.
- API submission failures show an actionable inline error in the parameter panel.

## 2D Preview Contract

- When the selected artifact has `content_url`, render an `<img>` with alt text `2D concept preview`.
- If a selected version has PreviewSpec data, render the generated image as the canvas background and keep overlay/safe-zone/edit-mask layers above it.
- If no PreviewSpec exists, still render the generated image in a bordered preview frame.
- If no artifact exists, keep the existing empty state explaining that generation is required.

## Copy Contract

- Primary action label: `生成概念`.
- Save action label remains `保存参数`.
- Empty preview copy must not claim print-ready or UV-accurate output.
- Error copy should mention checking the local API and Worker, not provider internals.

## Accessibility Contract

- Buttons expose stable text or `aria-label`.
- The generated image has a non-empty `alt`.
- Toggle buttons preserve `aria-pressed`.
- Polling must not force focus changes or scroll jumps.

## States To Cover

- No brief: save/generate disabled.
- Dirty brief: generate saves first, then submits.
- Clean brief: generate submits directly.
- Queued/running job: progress refreshes every 1-2 seconds.
- Succeeded job: latest artifact image appears.
- Failed submit: parameter panel shows error.
- Resumed workspace: latest artifact image appears from `content_url`.
