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

## Cross-Milestone Trends

| Milestone | Strong Pattern | Revisit |
|-----------|----------------|---------|
| v1.0 | Durable state + deterministic provider + contract checks gave stable E2E progress | Nyquist artifact consistency and hosted provider readiness |
