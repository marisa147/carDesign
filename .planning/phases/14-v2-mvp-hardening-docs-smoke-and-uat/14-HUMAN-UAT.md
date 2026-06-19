---
phase: 14-v2-mvp-hardening-docs-smoke-and-uat
artifact: human-uat
status: passed
created: 2026-06-19
updated: 2026-06-19
requirements: [V2-REL-04, V2-REL-05]
---

# Phase 14 Human UAT - V2 MVP Release Workbench

## Current Status

Passed with browser visual evidence on 2026-06-19.

Phase 14 Plan 04 used a seeded provider-off workspace to verify the release-era V2 workbench across desktop and mobile. The UAT covers hosted provider guard visibility, targeted edit controls and comparison evidence, reference role/rights warnings, lightweight 3D preview labels, and enhanced ZIP handoff preview/history. No real secrets or hosted provider calls were used.

## Browser Fixture

| Item | Value |
|------|-------|
| Web app | `http://127.0.0.1:3140` |
| API | `http://127.0.0.1:8140` |
| Browser driver | Headless Chrome CDP on `127.0.0.1:9240` |
| Seed record | `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-uat-seed.json` |
| Metrics record | `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-browser-metrics.json` |
| Workspace | `df3f87de-5dd6-42b9-9fd2-22c25d8ba543` |
| Brief | `e3e46113-3c98-4005-91cb-29daef236ad7` |
| Job | `7463f14e-61a6-49a5-a267-8d7e32b90cc1` |
| Model run | `a7461170-78cf-493a-b22e-072407e2e4dd` |
| Ready version | `4ca171a7-3136-4155-a48e-85ab3063d044` |
| Ready concept artifact | `d34bef89-124c-4334-bad7-eebe1149529a` |
| 3D screenshot artifact | `9c192da5-0899-4ac3-9888-3ff0a7b665ca` |
| Targeted child version | `edbbeb43-5f80-468e-90af-6914fbcd0d9b` |
| Enhanced export | `db429cb3-d557-41dd-bc7b-b10414e423ff` |
| External calls | `false` |

## Browser Visual Evidence

| Viewport | Evidence | Result |
|----------|----------|--------|
| Desktop 1440x900 full-page capture | `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-desktop-2d-zip.png` | Pass. Ready version shows 2D PreviewSpec, selected local edit target, edit mask preview, ZIP mode, handoff package preview/history, reference warnings, and no horizontal overflow. |
| Desktop 1440x900 operations guard capture | `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-desktop-operations-guard.png` | Pass. Operations refresh shows local provider mode, worker/queue unavailable without secrets, and hosted guard text `Guard 托管灰度开关关闭`; BFL remains disabled. |
| Desktop 1440x900 targeted comparison capture | `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-desktop-targeted-compare.png` | Pass. Targeted child comparison shows route `deterministic_recomposition`, target `overlay_layer:text-1`, prompt delta, mask artifact, provider/model, and highlighted changed region metadata. |
| Desktop 1440x900 3D capture | `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-desktop-3d.png` | Pass. Ready version opens `概念 3D 预览`, shows `非生产贴膜参考`, shell `generic-side-coupe-lightweight-v1`, camera controls, source artifact, UV warning, and no fallback. |
| Mobile 390x900, device scale 2, full-page capture | `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-mobile-2d-zip.png` | Pass. Single-column layout keeps 2D controls, ZIP preview/history, reference warnings, asset rights controls, and future gates readable with no horizontal overflow. |
| Mobile 390x900, device scale 2, 3D capture | `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/evidence/phase14-v2-mobile-3d.png` | Pass. Mobile 3D view shows shell, camera controls, non-production/UV labels, reference trace, ZIP history, and no horizontal overflow. |

## DOM Metrics

| View | Client Width | Max Scroll Width | Horizontal Overflow | Key Signals |
|------|--------------|------------------|---------------------|-------------|
| Desktop 2D/ZIP | 1440 | 1440 | false | BFL visible, targeted edit visible, reference warnings visible, ZIP visible, concept-only visible, edit mask visible, handoff history visible |
| Desktop operations guard | 1440 | 1440 | false | hosted guard visible, BFL credential blocker visible, quota guard incomplete visible, worker/queue unavailable visible |
| Desktop 3D | 1440 | 1440 | false | 3D label visible, non-production label visible, shell visible, fallback absent |
| Mobile 2D/ZIP | 390 | 390 | false | BFL visible, targeted edit visible, reference warnings visible, ZIP visible, handoff history visible |
| Mobile 3D | 390 | 390 | false | 3D label visible, non-production label visible, shell visible, reference warnings visible, ZIP history visible |

## Notes And Limitations

- The in-app Browser could inspect the local page but could not write `localStorage` for the seeded workspace restore path, so durable screenshots were captured through a direct headless Chrome CDP driver.
- Next.js dev server startup hit sandbox `spawn EPERM` until the command was rerun with approved escalation. The successful web server log is captured in `phase14-web-run2.log`.
- Worker was not started for this browser UAT. The operations panel therefore records worker/queue as unavailable; Phase 14 Plan 02 already holds Docker-backed local smoke and worker dry-run evidence.
- Hosted provider calls stayed disabled. BFL is visible only as a guarded, unavailable option; no real credential, hosted account, or paid provider output is claimed.
- The fixture uses one missing-rights reference and one confirmed reference so both rights warnings and usable reference trace can be inspected without real customer data.

## Sign-Off

- [x] API health returned ok.
- [x] Web app returned 200.
- [x] Seeded workspace restored by browser.
- [x] Desktop V2 workbench evidence exists.
- [x] Mobile V2 workbench evidence exists.
- [x] Hosted controls show guarded provider-off state without secrets.
- [x] Targeted edit controls and comparison evidence are visible.
- [x] Reference role/rights warnings remain readable.
- [x] Lightweight 3D preview shows non-production and UV-not-verified labels.
- [x] Enhanced ZIP handoff preview/history remains visible and concept-only.
- [x] Desktop and mobile DOM metrics show no horizontal overflow.
