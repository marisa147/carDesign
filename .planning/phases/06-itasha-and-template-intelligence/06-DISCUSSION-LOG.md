# Phase 6: Itasha And Template Intelligence - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `06-CONTEXT.md`; this log preserves the alternatives considered.

**Date:** 2026-06-18
**Phase:** 06-itasha-and-template-intelligence
**Mode:** Auto-selected defaults because the user requested autonomous GSD continuation.
**Areas discussed:** Itasha controls, deterministic overlays, warnings, safe zones, preview spec, workbench integration

---

## Itasha Controls

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal explicit fields | Add character focus, supporting graphics, racing/JDM cues, typography intent, and color harmony to the existing brief flow. | x |
| Broad preset library | Add many named presets/templates up front. | |
| Defer controls | Keep current generic style/palette/text fields only. | |

**Auto choice:** Minimal explicit fields.
**Notes:** This satisfies QUAL-01 without opening broad licensed template/library scope.

---

## Deterministic Overlays

| Option | Description | Selected |
|--------|-------------|----------|
| Separate preview layers | Record exact text/logo intent as deterministic overlay/spec data over the concept preview. | x |
| AI-raster only | Keep relying on image generation to render exact text/logo. | |
| Production vector package | Build print-ready layered source output. | |

**Auto choice:** Separate preview layers.
**Notes:** This supports QUAL-02 while keeping production handoff deferred.

---

## Warnings

| Option | Description | Selected |
|--------|-------------|----------|
| Lightweight rule-based warnings | Show durable, concise warnings for resolution, template normalization, text readability, risky zones, and rights uncertainty. | x |
| Blocking quality gates | Prevent most generation/export when any quality risk appears. | |
| No warning layer | Leave risks implicit in prompts and docs. | |

**Auto choice:** Lightweight rule-based warnings.
**Notes:** Rights remains blocking because prior phases already made rights/source confirmation a hard gate.

---

## Safe Zones

| Option | Description | Selected |
|--------|-------------|----------|
| Generic side-coupe zones | Add data-driven concept safe zones for the current supported template/view. | x |
| Broad vehicle template support | Add many vehicle-specific templates now. | |
| No overlay | Keep only textual warnings. | |

**Auto choice:** Generic side-coupe zones.
**Notes:** This satisfies QUAL-04 without expanding template QA beyond v1 scope.

---

## Preview Spec

| Option | Description | Selected |
|--------|-------------|----------|
| Metadata-first PreviewSpec | Store renderer-neutral spec in existing version/artifact/brief JSON fields before adding new core APIs. | x |
| New dedicated preview API surface | Add new routes/models immediately. | |
| Frontend-only spec | Keep preview details in browser state only. | |

**Auto choice:** Metadata-first PreviewSpec.
**Notes:** This satisfies QUAL-05 while preserving existing job/API route shapes.

---

## Workbench Integration

| Option | Description | Selected |
|--------|-------------|----------|
| Extend existing workbench panels | Add controls to parameter/preview/export surfaces. | x |
| New editor mode | Create a separate design editor view. | |
| Marketing/demo page | Build a showcase page for Phase 6 features. | |

**Auto choice:** Extend existing workbench panels.
**Notes:** This preserves the quiet operational surface verified in Phases 4-5.

## the agent's Discretion

- Exact schema field names.
- Exact safe-zone geometry encoding.
- Exact overlay renderer selection.
- Exact warning thresholds.
- Whether concept overlays are preview-only or also baked into local deterministic preview artifacts.

## Deferred Ideas

- Accurate production wrap templates and print preflight.
- True 3D UV preview.
- Mask/inpainting and advanced provider controls.
- Broad licensed template/asset libraries.
