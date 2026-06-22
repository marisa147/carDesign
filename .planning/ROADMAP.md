# Roadmap: 痛车设计生成 Agent

## Milestones

- ✅ **v1.0 MVP** — Phases 1-7 shipped on 2026-06-18. Archive: `.planning/milestones/v1.0-ROADMAP.md`.
- ✅ **v2.0 V2 MVP** — Phases 8-14 shipped on 2026-06-19. Archive: `.planning/milestones/v2.0-ROADMAP.md`.
- ✅ **v3.0 Template Library And Production Readiness** — Phases 15-20 shipped on 2026-06-20. Archive: `.planning/milestones/v3.0-ROADMAP.md`.
- ◆ **v4.0 Real Generation Closure And Reliability** — Phases 21-26 active from 2026-06-22.

## Current Planning State

v4.0 is initialized from `C:/Users/25858/Downloads/carAgent_CODE_REVIEW.md` and focuses on making the existing concept workflow reliable and truthful before adding more product breadth.

**Next up:** Phase 21 implementation: real generation entrypoint and 2D artifact image preview.

## Active Phase Plan

| Phase | Name | Goal | Requirements | Success Criteria |
|-------|------|------|--------------|------------------|
| 21 | Real Generation Entry And Artifact Preview | Users can generate from the active brief and see the real produced image. | GENC-01..04 | Generate button submits a job; active jobs poll; artifact content URL exists; 2D preview renders real image plus overlays. |
| 22 | Shared Object Storage | API and Worker share one storage contract and settings. | STOR-01..04 | API/Worker use factory; local metadata preserved; content route enforces workspace; storage contract tests pass. |
| 23 | Dispatch And Worker Reliability | Job dispatch and execution state become race-safe and visible. | RELY-01..05 | Outbox records dispatch; enqueue happens after commit; worker claim is conditional; progress commits during provider calls. |
| 24 | Preview And Parameter Correctness | Preview captures and brief patches stop reporting false success. | PREV-01..03 | 3D capture uses real canvas bytes; API validates magic/dimensions; UI can clear strings/lists/references. |
| 25 | Parser Boundary And Template Compositor | Agent understanding and image composition have reliable ownership boundaries. | AGNT-01..03 | BriefParser protocol exists; deterministic fallback remains; local generation uses template masks and compositor pixel tests. |
| 26 | Security And Operations Hardening | Workspace access, inputs, quotas, and telemetry are safe enough for the next product layer. | HARD-01..04 | Ownership checks derive server user; upload/download validation hardened; hosted quota reserves atomically; trace IDs and queue metrics visible. |

## Phase Details

### Phase 21: Real Generation Entry And Artifact Preview

Goal: Close the user-visible generation loop in the workbench.

Success criteria:
1. Workbench shows an explicit `生成概念` action near saved brief parameters.
2. The action saves the current brief, submits `submitGenerationJob`, and stores the returned job in query/cache state.
3. Queued/running jobs poll job, events, artifacts, and versions every 1-2 seconds until terminal.
4. `ArtifactResponse.content_url` points to a workspace-scoped API content route.
5. 2D preview renders `<img>` using `content_url`, with PreviewSpec overlays remaining available.

### Phase 22: Shared Object Storage

Goal: Remove the API/Worker storage split and make artifact reads deterministic.

Success criteria:
1. Storage settings are shared or mirrored by API and Worker without hardcoded `.cache/object-storage` or `.caragent-generated` roots.
2. Local file storage writes sidecar metadata or equivalent content-type preservation.
3. Storage protocol supports `put_object`, `get_object`, `head_object`, and `delete_object`.
4. Artifact content streaming works for generated images and rejects wrong-workspace access.

### Phase 23: Dispatch And Worker Reliability

Goal: Remove commit/enqueue races and long transaction behavior.

Success criteria:
1. `job_dispatch_outbox` exists with pending/dispatched/failed metadata.
2. Generation, iteration, and retry routes write job plus outbox in one transaction.
3. A dispatcher sends Celery tasks after commit and marks outbox dispatched idempotently.
4. Worker claims queued jobs with a conditional update and state version.
5. Worker commits running, progress, failure, success, model run, artifact, and version records in short units of work.

### Phase 24: Preview And Parameter Correctness

Goal: Fix two small but high-trust workflow lies.

Success criteria:
1. The 3D viewer exposes real canvas capture to the panel.
2. Screenshot upload payload dimensions match decoded image dimensions server-side.
3. Parameter patch construction treats empty strings and empty arrays as intentional changes.
4. Clearing all reference assignments persists empty `reference_asset_ids` and `reference_usage`.

### Phase 25: Parser Boundary And Template Compositor

Goal: Make the system more like an Agent without letting model output own durable state.

Success criteria:
1. `BriefParser` and `BriefDraft` exist in core generation contracts.
2. Deterministic fallback parser preserves current brief behavior.
3. LLM parser is feature-flagged and returns strict structured output only.
4. Template compositor loads package base/masks/panel lines and produces a generated PNG.
5. Pixel tests prove windows, wheels, and handles are protected by masks.

### Phase 26: Security And Operations Hardening

Goal: Prepare the reliable loop for real users and future production upgrades.

Success criteria:
1. Workspace resources enforce ownership through server-derived user identity.
2. Upload and provider-download validators check bytes, type, dimensions, and URL safety.
3. Hosted provider quota/rate checks are atomic and record reserve/settle evidence.
4. Logs/events/status include request/job/model-run trace identifiers and queue timing metrics.

## Progress

| Milestone | Phases | Requirements | Status | Completed |
|-----------|--------|--------------|--------|-----------|
| v1.0 MVP | 1-7 | 42/42 | Complete | 2026-06-18 |
| v2.0 V2 MVP | 8-14 | 34/34 | Complete | 2026-06-19 |
| v3.0 Template Library And Production Readiness | 15-20 | 31/31 | Complete | 2026-06-20 |
| v4.0 Real Generation Closure And Reliability | 21-26 | 0/23 | Active | — |

## Deferred Future Directions

- Full print-ready PSD/AI/PDF handoff with verified scale, bleed, color profile, DPI, and installer notes.
- Verified vehicle-specific UV mapping and broad licensed template library coverage.
- Marketplace, template store, public gallery, payment, quoting, ordering, installer network, and collaboration workflows.
- Fully automated copyright/licensing verification.
- Fully consistent multi-view generation across side/front/rear/hood with guaranteed physical alignment.
- Hosted provider production rollout claims after current model quality, pricing, moderation, account status, quota behavior, and commercial terms are re-verified.

---
*Last updated: 2026-06-22 after v4.0 roadmap initialization*