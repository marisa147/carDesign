# Phase 8: V1 Closure And V2 Readiness Gate - Context

**Gathered:** 2026-06-18
**Status:** Ready for planning
**Mode:** auto-selected defaults from `$gsd-progress --next` -> `$gsd-discuss-phase 8 --auto`

<domain>
## Phase Boundary

Phase 8 is a readiness gate for v2.0, not a product-expansion phase. It must prove that the shipped v1.0 baseline is stable, archived, and locally runnable before V2 features are enabled. The phase may add default-off V2 feature flag scaffolding, compatibility checks, no-op migration proof, verification inventory, smoke/UAT checklist, and readiness documentation. It must not enable hosted provider production rollout, targeted editing, reference-guided generation, 3D preview, or enhanced handoff behavior.

</domain>

<decisions>
## Implementation Decisions

### Baseline And Release Evidence

- **D-01:** Treat the existing v1.0 archive as the source of truth for shipped behavior. Phase 8 should inventory and reference `.planning/milestones/v1.0-ROADMAP.md`, `.planning/milestones/v1.0-REQUIREMENTS.md`, `.planning/milestones/v1.0-MILESTONE-AUDIT.md`, `.planning/milestones/v1.0-phases/`, `README.md`, and `docs/development.md`.
- **D-02:** If a release tag or equivalent baseline does not already exist, Phase 8 should create or document the chosen baseline marker before any V2-only behavior is planned as active.
- **D-03:** V1 local-only mode remains the safety anchor. The readiness report must show that the application can still run without hosted provider credentials and without changing V1 user-facing guarantees.

### Default-Off V2 Flags

- **D-04:** Introduce V2 feature flags as inert configuration scaffolding only. Default values must keep hosted generation, targeted editing, reference-guided provider usage, lightweight 3D preview, and enhanced handoff package behavior disabled until their owning phases implement and verify them.
- **D-05:** Feature flags should use the repo's existing config style: root/service `.env.example` documentation, typed API/worker settings where relevant, public web env only for non-secret UI flags, and tests that prove unsafe or missing non-local config is rejected.
- **D-06:** Do not store provider secrets, generated payloads, storage secrets, or database/Redis/S3 URLs in browser-accessible state. Preserve the Phase 4 rule that browser storage is limited to safe resume identifiers.

### Contract Compatibility

- **D-07:** Phase 8 should prove v1 workbench, jobs, artifacts, versions, exports, model runs, and `PreviewSpec` records remain readable before V2 schema extensions are planned.
- **D-08:** Contract drift checks must stay centered on FastAPI/Pydantic OpenAPI -> `packages/contracts` generated TypeScript. `pnpm contracts:check` is the required compatibility gate whenever API schemas or generated clients change.
- **D-09:** New V2 config or schema scaffolding must extend existing contracts rather than replacing v1 ledgers. Existing `workspace`, `asset`, `job`, `artifact`, `version`, `feedback`, `export`, `model_run`, and `PreviewSpec` paths remain canonical.

### Migration Safety

- **D-10:** Phase 8 should include a no-op migration proof or migration-safety review. If no schema migration is needed, that absence must be explicit and verified rather than implicit.
- **D-11:** Any future migration path must keep PostgreSQL/object storage as canonical state and Redis as queue/cache/progress only.
- **D-12:** Backward compatibility takes priority over V2 convenience. If a proposed scaffold would break existing v1 records or smoke paths, defer it to a later phase with a dedicated migration plan.

### Validation And Smoke

- **D-13:** Use root commands as the main validation vocabulary: `pnpm validate`, `pnpm contracts:check`, `pnpm smoke:local`, `pnpm smoke:worker -- --dry-run`, and the documented focused checks for API, worker, web, and contracts.
- **D-14:** Real smoke evidence still requires host prerequisites. Docker-backed `pnpm infra:up`, `pnpm smoke:local`, and non-dry-run `pnpm smoke:worker` are required on a Docker-enabled host; sandbox escape hatches are documentation aids, not completion evidence.
- **D-15:** Browser UAT for Phase 8 should be a readiness checklist rather than a new product flow: confirm V1 workbench still loads, operations status remains visible, and future/V2 gates are disabled or clearly labeled.

### Hosted Provider Boundary

- **D-16:** Hosted provider production readiness remains deferred to Phase 9. Phase 8 may verify existing guardrails and document required inputs, but must not make hosted calls enabled by default.
- **D-17:** Manual hosted smoke belongs in later provider rollout planning unless Phase 8 only documents the checklist. Any actual hosted call must require explicit credentials, explicit quota/cost guards, and a manual operator action outside default local validation.

### the agent's Discretion

- Exact feature flag names, readiness report structure, and no-op migration proof format may be chosen during planning, provided the decisions above are respected.
- Planner may decide whether to make the readiness report one file or split verification inventory, command index, and UAT checklist by plan.
- Planner may add focused tests around config defaults and contract compatibility if the existing suite does not already prove the Phase 8 gate.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### V2 Scope

- `.planning/ROADMAP.md` — Phase 8 goal, requirements, success criteria, plan list, and V2 non-goals.
- `.planning/REQUIREMENTS.md` — V2-READY-01 through V2-READY-04 and full v2.0 traceability.
- `.planning/PROJECT.md` — Current milestone, active requirements, constraints, and key decisions.
- `.planning/STATE.md` — Current session position and carried-forward blockers/concerns.

### V1 Baseline Evidence

- `.planning/MILESTONES.md` — Human-readable v1.0 release summary and next-step note.
- `.planning/milestones/v1.0-MILESTONE-AUDIT.md` — Passed v1.0 audit, known tech debt, and deferred scope.
- `.planning/milestones/v1.0-ROADMAP.md` — Archived v1.0 roadmap and phase coverage.
- `.planning/milestones/v1.0-REQUIREMENTS.md` — Archived v1.0 completed requirements and traceability.
- `.planning/milestones/v1.0-phases/07-operations-and-provider-strategy/07-07-SUMMARY.md` — Latest operations/provider closure evidence and validation list.

### Runbook And Commands

- `README.md` — Repository layout, quickstart, core commands, and phase-specific focused checks.
- `docs/development.md` — Local runbook, host prerequisites, validation/smoke details, provider guardrails, Browser UAT guidance, and troubleshooting.
- `package.json` — Root validation, contract, smoke, infra, and dev command definitions.
- `infra/README.md` — Docker-backed local service boundaries and smoke evidence rules.

### Existing Contracts And Code Anchors

- `.env.example` — Local-only defaults and hosted-provider disabled-by-default environment contract.
- `services/api/src/caragent_api/config.py` — API typed settings and local/non-local config validation.
- `services/worker/src/caragent_worker/config.py` — Worker typed provider settings and guard parsing.
- `services/worker/src/caragent_worker/tasks/jobs.py` — Worker generation task, cancellation checks, provider metadata, and durable output path.
- `services/api/src/caragent_api/routes/operations.py` — Provider/worker/queue operations status API.
- `services/api/src/caragent_api/routes/jobs.py` — Durable job and cancellation API surface.
- `packages/contracts/openapi/openapi.json` — Current generated OpenAPI artifact.
- `packages/contracts/src/generated/client.ts` — Current generated TypeScript client.
- `apps/web/src/components/workbench/progress-panel.tsx` — Operations status/failure/cancel rendering surface.
- `apps/web/src/components/workbench/preview-panel.tsx` — Current `PreviewSpec` reading and 2D preview behavior.
- `scripts/validate-all.mjs` — Aggregate local validation command sequence.
- `scripts/check-contracts.mjs` — Contract drift guard.
- `scripts/smoke-local.mjs` — Local infrastructure/database/generation smoke path.
- `scripts/smoke-worker-queue.mjs` — Live API -> Redis/Celery -> worker smoke path.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets

- Root scripts in `package.json` already provide `pnpm validate`, `pnpm contracts:check`, `pnpm smoke:local`, `pnpm smoke:worker`, `pnpm infra:up`, and dev commands; Phase 8 should organize around these commands rather than inventing a new runner.
- `docs/development.md` already contains the richest runbook for prerequisites, focused checks, smoke, UAT, provider guardrails, and troubleshooting; Phase 8 should update or reference it instead of duplicating large command blocks.
- `.env.example`, `services/api/.env.example`, and `services/worker/.env.example` already express hosted provider disabled-by-default behavior and guard variables.
- Existing tests in `services/api/tests/test_operations.py`, `services/api/tests/test_jobs.py`, `services/worker/tests/test_config.py`, `services/worker/tests/test_image_providers.py`, `services/worker/tests/test_generation_tasks.py`, `apps/web/src/lib/api/operations.test.ts`, and `apps/web/src/lib/api/jobs.test.ts` are likely starting points for Phase 8 readiness assertions.

### Established Patterns

- API/Pydantic OpenAPI is the source of truth for TypeScript contracts; web code consumes generated helpers from `@caragent/contracts`.
- PostgreSQL and object storage are canonical ledgers; Redis is queue/cache/progress only.
- Generated artifacts, versions, exports, and model runs are immutable and linked by durable identifiers.
- Local deterministic generation is the baseline verification path; hosted calls are opt-in and guard-gated.
- Operations status is intentionally compact inside the existing workbench progress panel rather than a separate admin dashboard.
- Concept previews and future gates must keep production-ready wrap and true 3D promises out of v1/v2 scaffolding until verified.

### Integration Points

- Feature flag scaffolding should connect through typed settings and documented env examples before touching UI or worker behavior.
- Contract compatibility checks should use `services/api/src/caragent_api/scripts/export_openapi.py`, `packages/contracts`, and `pnpm contracts:check`.
- Migration safety should inspect Alembic state under `services/api/alembic/versions/` and verify `uv run alembic upgrade head` remains part of smoke.
- Readiness smoke should preserve the current API/worker/web/infra split: Compose starts data services; app processes remain local.

</code_context>

<specifics>
## Specific Ideas

- Phase 8 should produce a crisp readiness report that says what is proven, what is intentionally default-off, and what remains deferred to Phase 9+.
- Treat hosted provider readiness as "documented and guarded" in Phase 8, not "enabled and exercised by default".
- Prefer a boring compatibility gate over clever scaffolding. The value of this phase is confidence before V2 changes begin.

</specifics>

<deferred>
## Deferred Ideas

- Real hosted provider generation and manual hosted smoke execution — Phase 9.
- Targeted region/layer editing and mask assets — Phase 10.
- Reference role assignment and provider-specific reference guidance — Phase 11.
- Lightweight 3D preview shell and screenshots — Phase 12.
- Enhanced concept handoff ZIP package — Phase 13.

</deferred>

---

*Phase: 08-v1-closure-and-v2-readiness-gate*
*Context gathered: 2026-06-18*
