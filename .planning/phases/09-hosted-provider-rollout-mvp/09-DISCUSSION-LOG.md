# Phase 9: Hosted Provider Rollout MVP - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `09-CONTEXT.md`; this log preserves the auto-selected alternatives.

**Date:** 2026-06-18
**Phase:** 09-hosted-provider-rollout-mvp
**Mode:** auto
**Areas discussed:** Provider choice, enablement gates, per-job routing, capability/cost policy, trace/failure visibility, UI/operations, verification

## Provider Choice

| Option | Description | Selected |
|--------|-------------|----------|
| BFL first | Reuse existing BFL adapter scaffold, env keys, tests, and operations status. | yes |
| Add multiple providers | Expand BFL, OpenAI, and fal together. Higher scope and docs drift risk. | |
| Local-only simulation | Avoid external provider in Phase 9. Would not satisfy hosted rollout. | |

**Auto choice:** BFL first.
**Notes:** This keeps the phase focused on one real provider path while leaving placeholders for future providers.

## Enablement Gates

| Option | Description | Selected |
|--------|-------------|----------|
| Triple-gated hosted calls | Require V2 rollout flag, provider calls enabled, and complete quota/rate/cost guards. | yes |
| Worker-only gate | Let jobs enqueue and fail in worker when provider config is incomplete. | |
| UI-only gate | Trust browser controls to prevent unsafe calls. | |

**Auto choice:** Triple-gated hosted calls.
**Notes:** API should preflight for user feedback; worker remains authoritative before external calls.

## Per-Job Routing

| Option | Description | Selected |
|--------|-------------|----------|
| Persist provider intent per job | Let users select provider/model per generation while preserving config defaults. | yes |
| Process-wide default only | Keep provider choice entirely in worker env. Simpler but weak UI fit. | |
| Browser-only selector | Show a selector without durable provider intent. Misleading and unsafe. | |

**Auto choice:** Persist provider intent per job.
**Notes:** Phase 9 requires a user-visible provider selector, so the choice must become part of the API/job contract.

## Capability And Cost Policy

| Option | Description | Selected |
|--------|-------------|----------|
| Typed capability map | Store provider capabilities, limits, caveats, and estimated cost in config-driven typed metadata. | yes |
| Hardcoded provider constants | Faster, but brittle when provider models/pricing change. | |
| Free-form JSON only | Flexible, but harder to validate and expose safely. | |

**Auto choice:** Typed capability map.
**Notes:** Model names, endpoint details, price estimates, and capability behavior must be re-verified against official provider docs during planning.

## Trace And Failure Visibility

| Option | Description | Selected |
|--------|-------------|----------|
| Extend existing ledger | Use model_runs, job events, job operations metadata, artifacts, and versions for trace/fallback/cost evidence. | yes |
| Add separate provider log table | More explicit but unnecessary unless existing ledger cannot support Phase 9. | |
| Keep provider trace in task result | Not durable enough and invisible to UI/API. | |

**Auto choice:** Extend existing ledger.
**Notes:** Add new failure categories only where needed, especially for provider safety/moderation rejection.

## UI And Operations

| Option | Description | Selected |
|--------|-------------|----------|
| Workbench-integrated selector and status | Add provider controls and warnings to the existing workbench/progress flow. | yes |
| Separate operations dashboard | Larger UX scope than Phase 9 needs. | |
| Hidden env-only provider switch | Satisfies operator config but not user-visible hosted testing. | |

**Auto choice:** Workbench-integrated selector and status.
**Notes:** UI must stay compact and label hosted output as concept preview.

## Verification

| Option | Description | Selected |
|--------|-------------|----------|
| TDD plus provider-off and manual provider-on smoke | Covers safe defaults and real hosted path without spending money in default CI. | yes |
| Only unit tests | Insufficient for provider routing and smoke evidence. | |
| Always run hosted smoke in validation | Unsafe for cost, credentials, and CI repeatability. | |

**Auto choice:** TDD plus provider-off and manual provider-on smoke.
**Notes:** Default validation must not make external calls. Manual hosted smoke requires explicit credentials and guardrails.

## Deferred Ideas

- Targeted masked editing and layer controls remain Phase 10.
- Reference roles and provider-specific reference assets remain Phase 11.
- 3D preview remains Phase 12.
- Enhanced handoff package remains Phase 13.
