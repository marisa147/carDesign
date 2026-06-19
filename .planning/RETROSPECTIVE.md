# Retrospective: 痛车设计生成 Agent

## Milestone: v1.0 — MVP

**Shipped:** 2026-06-18
**Phases:** 7
**Plans:** 54

### What Was Built

v1.0 delivered the first real concept-generation loop: runnable local stack, durable data/job/artifact ledger, local text-to-2D generation, integrated Web workbench, versioned iteration and concept export, itasha/template intelligence, and operations/provider guardrails.

### What Worked

- Building durable state before real generation kept later UI, retry, iteration, and operations work grounded in canonical records.
- OpenAPI-first contracts caught drift between FastAPI/Pydantic and TypeScript clients during each phase.
- The local deterministic provider made E2E generation smoke reliable without hosted credentials or variable model behavior.
- Browser UAT at both desktop and mobile widths caught practical UI issues that unit tests would not cover.
- Explicit future gates prevented v1 from implying production-ready print export, marketplace, auth/billing, or true 3D support.

### What Was Inefficient

- Older phases accumulated partial/missing Nyquist `VALIDATION.md` artifacts even though verification, smoke, and UAT evidence existed elsewhere.
- Toolchain assumptions around bare `pnpm`, Node versions, uv-managed Python, and Docker availability required repeated cleanup.
- A few UAT files report metadata statuses that `audit-open` treats as open despite having 0 pending scenarios.
- Hosted provider readiness stayed intentionally deferred because current model availability, pricing, moderation, and rights constraints need fresh validation.

### Patterns Established

- PostgreSQL job rows and job events are the source of truth; Redis/Celery state is operational support, not canonical product history.
- Artifacts and versions are immutable; iterations create child versions and new artifacts rather than overwriting prior output.
- Workers use provider adapters, not vendor calls scattered through application code.
- Frontend server state belongs in TanStack Query; workbench-local UI state belongs in local component/Zustand-style boundaries.
- Export files must be labeled concept preview until production handoff checks exist.

### Key Lessons

- A deterministic provider is not a placeholder nicety; it is the backbone for repeatable local smoke and CI-friendly generation tests.
- Provider operations should be visible in the user workbench early because generation failures are part of the product experience.
- Itasha-specific controls and warnings make the product more useful than a generic car image prompt tool even before true 3D exists.
- Windows-first local verification needs explicit worker pool settings, Corepack commands, uv-managed Python, and Docker smoke documentation.

### Cost Observations

- Hosted model cost was not measured in v1.0 because non-local generation remains opt-in/deferred.
- The main cost driver was validation breadth: web, API, worker, contracts, Docker smoke, live queue smoke, and Browser UAT.
- Next milestone should decide whether to add provider-cost fixtures or real hosted-provider budget tests before enabling non-local generation.

## Milestone: v2.0 — V2 MVP

**Shipped:** 2026-06-19
**Phases:** 7
**Plans:** 48

### What Was Built

v2.0 upgraded the concept workflow with guarded Hosted Provider rollout, Targeted editing, Reference guidance, lightweight 3D preview, enhanced concept handoff ZIPs, and a Phase 14 release-hardening package with aggregate validation, Docker smoke, Browser UAT, docs, and traceability.

### What Worked

- Keeping V2 flags default-off let each new capability ship behind an explicit server/browser switch without breaking the V1 local path.
- Provider capability metadata and preflight checks kept BFL hosted behavior visible without requiring paid calls for baseline validation.
- Reusing PreviewSpec as the shared contract made targeted edit regions, reference traces, 3D material mapping, and handoff reports align around the same evidence model.
- Browser UAT with seeded local data gave high-signal visual proof for dense workbench flows that unit tests could not fully represent.
- Final Phase 14 release hardening made limitations explicit, especially concept-only 3D and not print-ready handoff boundaries.

### What Was Inefficient

- Windows sandbox limits repeatedly required elevated host runs for Corepack, uv, Python, and Next/Vitest child processes.
- `contracts:check` can produce confusing fallback output when sandbox generation is blocked; manual regenerate plus elevated check was needed to prove no true drift.
- Earlier UAT metadata statuses still show as open in `audit-open` even when later release UAT passed, so milestone close needed explicit acknowledgement.
- Live non-dry-run worker smoke remains operationally finicky on Windows because it needs Docker, migrated API, running API, and solo-pool worker orchestration all at once.

### Patterns Established

- V2 rollout flags should be documented with both server-authoritative and browser-public behavior; `NEXT_PUBLIC_V2_*` never grants capability by itself.
- Hosted provider smoke should stay one-job, credentialed, cost-approved, quota-limited, and reversible until production readiness is separately verified.
- Concept-only labels need to appear in tests, docs, UAT screenshots, release notes, and package manifests, not just UI copy.
- Handoff packages are review artifacts: immutable, traceable, sanitized, and rights/source guarded.

### Key Lessons

- V2 capability growth is manageable when each slice preserves local deterministic validation and explicit deferred production claims.
- Reference usage and handoff exports need rights/source enforcement at both UI and server boundaries.
- 3D preview is useful as an inspection aid, but every artifact and screenshot must avoid implying verified UV or print readiness.
- Milestone close should run `audit-open` before final archive so stale metadata can be acknowledged instead of rediscovered later.

### Cost Observations

- No hosted model spend was incurred; live provider smoke remains manual-only.
- Validation cost grew mostly through browser UAT and aggregate test breadth, not provider usage.
- Future milestones should budget explicit hosted-provider smoke if output quality, pricing, moderation, or commercial terms become release criteria.

## Cross-Milestone Trends

| Milestone | Strong Pattern | Revisit |
|-----------|----------------|---------|
| v1.0 | Durable state + deterministic provider + contract checks gave stable E2E progress | Nyquist artifact consistency and hosted provider readiness |
| v2.0 | Feature-flagged V2 slices + local deterministic validation + browser UAT kept scope controlled | Sandbox/elevated validation ergonomics, stale UAT metadata, live worker smoke orchestration |
