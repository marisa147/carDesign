# Phase 1: Foundation And Contracts - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-05-08
**Phase:** 01-foundation-and-contracts
**Areas discussed:** Repository Shape, Tooling And Runtime Baseline, Local Development Services, API Contract Strategy, Environment And Configuration, Validation And Quality Gates, Minimal UI Shell

---

## Runtime Note

The interactive `AskUserQuestion` UI was unavailable in this Codex Default-mode session. Per the skill adapter fallback, the workflow selected the recommended Phase 1 areas and resolved them with conservative defaults derived from `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/research/SUMMARY.md`, `.planning/research/STACK.md`, and `.planning/research/ARCHITECTURE.md`.

No user-entered freeform corrections were provided during this discuss phase.

---

## Repository Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Monorepo with explicit web/API/worker/contracts/infra boundaries | Matches research and keeps later phases separated while preserving a single workspace. | yes |
| Flat single app scaffold | Simpler initially but would blur frontend, API, worker, and contract ownership. | |
| Full platform tooling such as Turborepo/Nx/Kubernetes | More structure than Phase 1 needs; risks scaffold complexity before app code exists. | |

**Selected choice:** Monorepo with explicit `apps/web`, `services/api`, `services/worker`, `packages/contracts`, and `infra` boundaries.
**Notes:** API and worker may share Python modules but must keep separate entrypoints and avoid importing API routers into worker code.

---

## Tooling And Runtime Baseline

| Option | Description | Selected |
|--------|-------------|----------|
| `pnpm` for frontend and `uv` for Python services | Matches research; keeps JS and Python dependency management explicit and modern. | yes |
| npm/pip only | Familiar but weaker workspace/lockfile ergonomics for this planned stack. | |
| Heavy build orchestrator from day one | Useful later only if the workspace grows enough to need it. | |

**Selected choice:** Use `pnpm` and `uv`, with repo-visible runtime pins where practical.
**Notes:** Exact versions must be verified from official docs during planning before implementation locks them.

---

## Local Development Services

| Option | Description | Selected |
|--------|-------------|----------|
| Docker Compose for infrastructure, app processes local by default | Good balance: reproducible PostgreSQL/Redis/MinIO while preserving fast app iteration. | yes |
| Docker Compose for everything only | More reproducible but slower and more brittle during early scaffold work. | |
| No Compose yet | Would fail Phase 1's local full-stack run requirement. | |

**Selected choice:** Compose owns PostgreSQL, Redis, and MinIO; API/worker can have optional profiles if useful.
**Notes:** Conventional local ports should be used but configurable.

---

## API Contract Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| FastAPI/Pydantic OpenAPI as source of truth with generated TypeScript client | Aligns Python backend with typed frontend and avoids duplicated schemas. | yes |
| Hand-written TypeScript types | Simple at first but type drift is likely once APIs grow. | |
| tRPC or TS-first API contracts | Good for TS-only stacks, but conflicts with Python FastAPI direction. | |

**Selected choice:** FastAPI/Pydantic owns OpenAPI; generated TypeScript client/hooks live under frontend/contracts paths.
**Notes:** Phase 1 should prove generation with minimal endpoints, not design the full product API.

---

## Environment And Configuration

| Option | Description | Selected |
|--------|-------------|----------|
| Typed backend settings plus committed example env files | Gives clear local setup and avoids committing secrets. | yes |
| Hard-coded local config | Fast initially but blocks real deployment and violates Phase 1 configuration requirement. | |
| Full secrets manager integration now | Useful later, too heavy for first scaffold. | |

**Selected choice:** Use typed config and committed example env files with placeholders for DB, Redis, storage, CORS, runtime mode, and provider keys.
**Notes:** Provider keys are placeholders only in Phase 1; real provider calls are deferred.

---

## Validation And Quality Gates

| Option | Description | Selected |
|--------|-------------|----------|
| Local validation commands for frontend/backend/contracts/smoke checks | Directly satisfies Phase 1 and keeps feedback fast. | yes |
| CI-first validation | Useful if easy, but cloud CI setup should not block the local foundation. | |
| Manual run instructions only | Too weak; Phase 1 needs executable validation commands. | |

**Selected choice:** Define root and service-level validation commands for lint, type-check, tests, contract generation/checking, and smoke checks.
**Notes:** Initial tests should be small and foundation-focused.

---

## Minimal UI Shell

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal app shell only | Honors Phase 1 UI hint without stealing Phase 4's workbench scope. | yes |
| No frontend shell | Would undercut the runnable stack and typed contract proof. | |
| Full mocked workbench | Scope creep; chat, preview, upload, history, and feature gates belong to Phase 4. | |

**Selected choice:** Build only the minimal Next.js shell, Tailwind/shadcn baseline, and placeholder regions if useful.
**Notes:** Full GPT-style workbench, 2D preview, and 3D UI are deferred.

---

## the agent's Discretion

- Exact helper script names.
- Whether API and worker share one Python package or start as separate packages.
- Whether to include CI if it is low-friction.
- Exact health endpoint/test names.

## Deferred Ideas

- Real generation, real product tables, full workbench UI, iteration/export, itasha controls, operations dashboards, production handoff, and true 3D preview are deferred to their roadmap phases.
