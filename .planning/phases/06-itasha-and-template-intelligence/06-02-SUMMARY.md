---
phase: 06-itasha-and-template-intelligence
plan: "02"
subsystem: worker-provider-preview-spec
tags: [worker, provider, preview-spec, overlays, rights]

requires:
  - plan: "06-01"
    provides: core itasha fields, safe zones, warnings, and PreviewSpec payload
provides:
  - PreviewSpec persistence in generated version parameters
  - PreviewSpec persistence in generated artifact metadata
  - deterministic local text/logo overlay evidence
  - reference and logo asset rights enforcement before generation
affects: [phase-06-03-api-contracts, phase-06-04-workbench-ui]

tech-stack:
  patterns:
    - worker reads PreviewSpec from `PromptPlan.prompt_payload`
    - generated versions/artifacts keep durable PreviewSpec metadata in existing JSON fields
    - local deterministic provider remains no-external-call and returns audit metadata

key-files:
  modified:
    - services/worker/src/caragent_worker/tasks/jobs.py
    - services/worker/src/caragent_worker/providers/local.py
    - services/worker/tests/test_generation_tasks.py
    - services/worker/tests/test_image_providers.py

key-decisions:
  - "Worker combines reference asset ids and overlay logo asset ids before rights checks."
  - "PreviewSpec is duplicated into version parameters and artifact metadata so UI/export consumers can inspect it without provider-specific parsing."
  - "Local provider draws deterministic text/logo overlay evidence but still labels output as a concept preview."

patterns-established:
  - "PreviewSpec summary counts use `overlay_layer_count`, `safe_zone_count`, and `warning_count`."
  - "Logo overlay asset ids follow the same confirmed-rights gate as reference assets."

requirements-completed:
  - QUAL-02
  - QUAL-03
  - QUAL-05

duration: 20 min
completed: 2026-06-18
---

# Phase 6 Plan 02: Worker PreviewSpec Persistence Summary

**Worker generation now persists PreviewSpec metadata and blocks unconfirmed logo overlay assets before provider execution.**

## Accomplishments

- Added failing worker tests for version parameters, artifact metadata, local provider PreviewSpec metadata, deterministic overlay output, and missing logo rights blocking.
- Updated worker generation to extract `preview_spec` from prompt payloads and write it into generated design version parameters.
- Updated artifact metadata to include `preview_spec`, `concept_label`, `overlay_layer_count`, `safe_zone_count`, and `warning_count`.
- Extended worker rights enforcement to combine reference asset ids with PreviewSpec overlay logo asset ids before generation.
- Updated the local deterministic provider to draw text/logo overlay evidence from PreviewSpec safe zones and mirror PreviewSpec summary metadata.

## Verification

- RED: `uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py` in `services/worker` failed as expected for missing PreviewSpec metadata and missing logo rights blocking.
- GREEN: `uv run pytest -q tests/test_generation_tasks.py tests/test_image_providers.py` in `services/worker` passed, 12 tests.
- `uv run ruff check .` in `services/worker` passed.
- `uv run mypy src` in `services/worker` passed after rerunning with escalation because the first run hit a Windows `uv` cache permission error.

## Deviations from Plan

- No code-scope deviation.
- The first `uv run mypy src` attempt failed before type checking due to local cache permissions, so the same verification command was rerun with approved escalation.

## Next Plan Readiness

Ready for `06-03`: API schema, OpenAPI export, and generated TypeScript contracts for Phase 6 fields.
