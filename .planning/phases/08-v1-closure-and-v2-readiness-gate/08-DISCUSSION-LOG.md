# Phase 8: V1 Closure And V2 Readiness Gate - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-18
**Phase:** 08-v1-closure-and-v2-readiness-gate
**Mode:** auto
**Areas discussed:** Baseline And Release Evidence, Default-Off V2 Flags, Contract Compatibility, Migration Safety, Validation And Smoke, Hosted Provider Boundary

## Baseline And Release Evidence

| Option | Description | Selected |
|--------|-------------|----------|
| Use v1.0 archive as source of truth | Anchor Phase 8 to the archived roadmap, requirements, audit, phase artifacts, README, and runbook. | yes |
| Re-discover v1.0 from code only | Spend the phase re-auditing code without using archived evidence. | |
| Skip baseline marker | Continue V2 without explicitly naming the release baseline. | |

**Auto choice:** Use v1.0 archive as source of truth.
**Rationale:** Phase 8 is a readiness gate after a completed milestone; the archived GSD evidence is the strongest baseline and avoids re-litigating shipped scope.

## Default-Off V2 Flags

| Option | Description | Selected |
|--------|-------------|----------|
| Default-off inert scaffolding | Add flags/settings that keep V2 behavior disabled until owning phases implement and verify it. | yes |
| Enable partial V2 behavior now | Start wiring behavior before the owning phase exists. | |
| Defer all flag work | Leave Phase 9+ to invent flag patterns independently. | |

**Auto choice:** Default-off inert scaffolding.
**Rationale:** This matches the roadmap requirement and protects local deterministic V1 behavior.

## Contract Compatibility

| Option | Description | Selected |
|--------|-------------|----------|
| Extend existing contracts | Prove v1 records stay readable and use OpenAPI/TypeScript drift checks for changes. | yes |
| Replace contracts for V2 | Redesign contract surfaces before compatibility proof. | |
| Manual inspection only | Rely on docs without contract checks. | |

**Auto choice:** Extend existing contracts.
**Rationale:** PROJECT.md and V2 roadmap both require schema extension, not replacement.

## Migration Safety

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit no-op migration proof | Document and verify whether schema migration is unnecessary or safe. | yes |
| Assume no migration | Skip proof because Phase 8 is mostly planning/flags. | |
| Push migration review later | Let the first V2 feature handle compatibility risk. | |

**Auto choice:** Explicit no-op migration proof.
**Rationale:** Phase 8's purpose is to remove this uncertainty before feature work begins.

## Validation And Smoke

| Option | Description | Selected |
|--------|-------------|----------|
| Root commands plus focused checks | Use `pnpm validate`, contracts, smoke, and documented focused commands as the validation vocabulary. | yes |
| Create a new validation runner first | Build a new aggregate layer before inventorying existing commands. | |
| Docs-only readiness | Skip executable gates and only write a report. | |

**Auto choice:** Root commands plus focused checks.
**Rationale:** Root scripts and docs already define the working V1 validation vocabulary.

## Hosted Provider Boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Document and guard only | Keep hosted calls disabled by default; document manual prerequisites for later. | yes |
| Enable hosted by default | Promote hosted behavior during readiness. | |
| Ignore hosted provider details | Leave provider risks untracked until Phase 9. | |

**Auto choice:** Document and guard only.
**Rationale:** Hosted provider rollout is Phase 9 scope; Phase 8 should only prepare safe gates.

## the agent's Discretion

- Exact flag names may be chosen during planning if they follow existing typed config and env-example patterns.
- Exact readiness report structure may be chosen during planning.
- Planner may add focused config/contract tests where existing tests do not prove the readiness gate.

## Deferred Ideas

- Real hosted provider generation and manual hosted smoke execution — Phase 9.
- Targeted region/layer editing and mask assets — Phase 10.
- Reference role assignment and provider-specific reference guidance — Phase 11.
- Lightweight 3D preview shell and screenshots — Phase 12.
- Enhanced concept handoff ZIP package — Phase 13.
