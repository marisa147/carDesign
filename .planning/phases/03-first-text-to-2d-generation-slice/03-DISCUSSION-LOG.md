# Phase 3: First Text-To-2D Generation Slice - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `03-CONTEXT.md`; this log preserves the auto-selected alternatives.

**Date:** 2026-06-17
**Phase:** 03-first-text-to-2d-generation-slice
**Mode:** auto
**Areas discussed:** Brief capture, Template scope, Provider strategy, Async pipeline, Traceability, Artifacts, Rights gate, Failure/retry, Validation

## Brief Capture

| Option | Description | Selected |
|--------|-------------|----------|
| Deterministic typed parser | Keep first structured brief conversion inspectable and testable. | yes |
| AI parser immediately | Adds provider dependency and eval burden before image path is proven. | |
| Freeform JSON only | Too loose for Phase 3 contracts and reuse. | |

**Selected default:** Deterministic typed parser with Pydantic schemas.
**Notes:** Natural language remains the user input source, but the stored brief must be structured enough to review, edit, reuse, and prompt from.

## Template Scope

| Option | Description | Selected |
|--------|-------------|----------|
| One generic 2D side-view template | Best MVP boundary and keeps QA tractable. | yes |
| Multiple templates/views now | Belongs to later template intelligence and workbench phases. | |
| No template concept | Would fail GEN-03 and weaken prompt constraints. | |

**Selected default:** One supported vehicle template and default view with explicit normalization/warnings for unsupported requests.

## Provider Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Adapter interface plus local deterministic provider | Keeps tests/smoke stable and hosted providers swappable. | yes |
| Direct vendor call in worker | Faster initially but creates hard-to-change coupling. | |
| Local-only forever | Cannot satisfy provider-backed MVP intent. | |

**Selected default:** Internal adapters, config-driven provider/model, local deterministic provider for normal validation, hosted provider behind explicit env.
**Notes:** Exact hosted provider/model must be researched against current official docs during planning.

## Async Pipeline

| Option | Description | Selected |
|--------|-------------|----------|
| API creates job, worker performs generation | Preserves Phase 2 durable job model and avoids blocking HTTP. | yes |
| Synchronous FastAPI generation | Simpler but violates architecture and user-visible durability expectations. | |
| Worker-only hidden state | Would regress DATA-05 and DATA-06. | |

**Selected default:** Durable job creation and worker-owned execution with append-only events.

## Traceability

| Option | Description | Selected |
|--------|-------------|----------|
| Store full prompt/model/provider trace | Required for reuse, debugging, and later iteration. | yes |
| Store output only | Not enough for GEN-04 or future iteration. | |
| Store raw vendor payloads/logs | Risks secrets/noise and brittle schemas. | |

**Selected default:** Store exact prompt text, structured prompt payload, provider/model/parameters, input assets, output artifact id, and cost fields where available.

## Artifacts

| Option | Description | Selected |
|--------|-------------|----------|
| Immutable generated image artifact plus design version | Matches Phase 2 ledger and Phase 3 success criteria. | yes |
| Store image bytes only on filesystem | Would bypass object storage and contracts. | |
| Preview/export package now | Belongs to later phases. | |

**Selected default:** Successful jobs create object-storage artifact records and a generated design version.

## Rights Gate

| Option | Description | Selected |
|--------|-------------|----------|
| Require confirmed rights for referenced assets | Keeps Phase 2 rights metadata meaningful. | yes |
| Allow any uploaded asset | Creates avoidable IP/source ambiguity. | |
| Ignore references in Phase 3 | Would undercut prompt usefulness. | |

**Selected default:** Only workspace-owned assets with sufficient rights metadata can be used as generation inputs.

## Failure And Retry

| Option | Description | Selected |
|--------|-------------|----------|
| Durable failed state plus explicit retry | Preserves auditability and user recovery. | yes |
| Overwrite failed job on retry | Loses traceability. | |
| Leave retries to manual re-submit only | Weakens GEN-07. | |

**Selected default:** Failed jobs retain sanitized errors/events; retry creates a new durable attempt from the same brief without overwriting prior records.

## Validation

| Option | Description | Selected |
|--------|-------------|----------|
| Local deterministic end-to-end smoke | Validates Phase 3 without external credentials or spend. | yes |
| Hosted provider smoke required | Too brittle and environment-dependent for baseline validation. | |
| Unit tests only | Insufficient for API/worker/storage integration. | |

**Selected default:** Unit/API/worker/contract validation plus Docker-backed local generation smoke; optional hosted smoke behind explicit flags.

## Deferred Ideas

- Full workbench UI is deferred to Phase 4.
- Iteration/export UX is deferred to Phase 5.
- Itasha/template intelligence is deferred to Phase 6.
- Operations/provider dashboards, quotas, cancellation, fallback/rate-limit controls are deferred to Phase 7.
