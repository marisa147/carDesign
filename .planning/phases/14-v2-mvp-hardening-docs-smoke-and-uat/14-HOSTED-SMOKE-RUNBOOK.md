---
phase: 14
plan: "03"
artifact: hosted-smoke-runbook
status: ready
created: 2026-06-19
requirements: [V2-REL-03, V2-REL-05]
---

# Phase 14 Hosted Provider Smoke Runbook

This runbook is the release checklist for a manual hosted-provider smoke. The default V2 release validation remains provider-off, local, and free. A live hosted smoke is optional and must be skipped unless an operator provides real credentials, confirms account readiness, and approves the one-job cost exposure.

## Release Posture

- Manual-only: the agent must not run paid hosted calls without explicit credentials and cost approval.
- One job only: submit exactly one hosted concept-preview generation or child iteration unless an operator deliberately expands the run.
- Secret-safe: put real keys only in ignored service env files or ephemeral shells; never commit, paste, screenshot, or record real credential values.
- Cost-guarded: hosted calls require daily, per-minute, and estimated per-job guards before provider execution.
- Reversible: disable hosted flags, clear active keys, restart API/worker, and confirm local deterministic mode after the smoke.
- Evidence-bound: do not claim hosted output quality, account readiness, pricing readiness, moderation readiness, or production readiness unless the evidence table below is filled from a real run.

## Prerequisites

| Check | Required Evidence |
|-------|-------------------|
| Credential | A real BFL key exists only in ignored `services/api/.env` and `services/worker/.env`, or in scoped local shells. |
| Cost approval | Operator approval exists for one small hosted concept-preview job. |
| Account readiness | BFL account access, model access, credit balance, current pricing, moderation policy, and provider terms are checked on the same day as the smoke. |
| Local runtime | Docker services, migrations, API, worker, and web can run locally. |
| Guards | Daily, per-minute, and per-job estimated cost guards are set to small values. |
| Scope | The request is a concept-preview smoke, not print-ready wrap output, production UV proof, billing, ordering, or commercial-rights approval. |

Skip the live smoke if any prerequisite is missing.

## Ignored Env Setup

Use ignored service env files or scoped shells. Do not put real values in tracked docs, screenshots, terminal transcripts, or planning artifacts.

```powershell
# services/api/.env and services/worker/.env, never committed
V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=true
AI_PROVIDER_DEFAULT=bfl
AI_PROVIDER_MODEL=flux-2-pro-preview
AI_PROVIDER_CALLS_ENABLED=true
AI_HOSTED_DAILY_CALL_LIMIT=1
AI_HOSTED_RATE_LIMIT_PER_MINUTE=1
AI_MAX_ESTIMATED_COST_PER_JOB=0.25
AI_PROVIDER_BFL_API_KEY=replace-with-real-key-in-ignored-env
```

Before starting, verify that the active process environment does not contain stale higher quota or cost values.

## One-Job Smoke Steps

1. Start local infrastructure with `corepack pnpm infra:up`.
2. Run API migrations and start the API from a shell that loads the ignored API env file.
3. Start the worker from a shell that loads the ignored worker env file.
4. Start the web app and open the workbench.
5. Refresh operations status and confirm `BFL 托管` is enabled.
6. Confirm the UI shows small hosted daily/rate/cost guard values and does not show raw keys, bearer tokens, local paths, or vendor payloads.
7. Select `BFL 托管`.
8. Submit exactly one concept-preview generation or child iteration.
9. Wait for a succeeded hosted output or a classified hosted failure.
10. Fill the evidence table below from durable job, model-run, version, artifact, and operations records.
11. Run the reversal steps before leaving the environment.

## Evidence To Capture

| Field | Value |
|-------|-------|
| Run timestamp | Not run in this agent session. |
| Operator | Not run in this agent session. |
| Skip reason, if skipped | No real BFL credential or operator cost approval was provided in this agent session. |
| Workspace id |  |
| Brief id |  |
| Job id |  |
| Job status |  |
| Model run id |  |
| Model run status |  |
| Version id |  |
| Generated artifact id |  |
| Provider | `bfl` |
| Model | `flux-2-pro-preview` |
| Estimated cost |  |
| Actual cost, if returned |  |
| Daily guard | `AI_HOSTED_DAILY_CALL_LIMIT=1` |
| Rate guard | `AI_HOSTED_RATE_LIMIT_PER_MINUTE=1` |
| Per-job cost guard | `AI_MAX_ESTIMATED_COST_PER_JOB=0.25` |
| Failure kind, if any |  |
| Provider status, if any |  |
| Fallback path |  |
| Operations status evidence |  |
| Screenshot or log evidence path |  |

## Acceptable Skip Reasons

- No real provider credential is available.
- No operator cost approval exists.
- BFL account access, model access, credit status, pricing, moderation, or terms could not be checked that day.
- Required quota/rate/cost guards are absent or too broad.
- Docker, API, worker, web, database, Redis, or object storage is unavailable.
- The requested smoke would exceed one small concept-preview job.

A skipped live smoke is acceptable local release evidence only when the skip reason is explicit. It is not proof of live hosted output quality, provider account readiness, commercial terms, or moderation readiness.

## Failure Categories To Record

Record safe categories and statuses only. Do not record raw provider payloads if they contain secrets, account details, or unsupported personal data.

| Category | Record |
|----------|--------|
| `missing_credentials` | Which capability was disabled, without printing the secret name value. |
| `quota_or_cost_guard` | Which guard blocked execution and the configured safe value. |
| `provider_validation` | Safe validation status or provider status code, if available. |
| `provider_moderation` | Safe moderation category/status, if available. |
| `provider_credit` | Credit or billing status label, without account identifiers. |
| `provider_rate_limit` | Rate-limit classification and retry eligibility. |
| `provider_timeout` | Timeout stage and configured timeout value. |
| `storage_or_persistence` | Durable record or object-storage failure stage. |
| `fallback_used` | Whether local fallback ran and which artifact/version it created. |

## Reversal Steps

1. Set `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=false`.
2. Set `AI_PROVIDER_CALLS_ENABLED=false`.
3. Set `AI_PROVIDER_DEFAULT=disabled` or the documented local default.
4. Remove the active `AI_PROVIDER_BFL_API_KEY` value from ignored env files or ephemeral shells.
5. Restart API and worker processes.
6. Refresh operations status and confirm `BFL 托管` is blocked or disabled.
7. Submit or inspect local deterministic mode only; confirm it remains available without hosted credentials.
8. Remove accidental key echoes from terminal history, local notes, screenshots, and logs before sharing evidence.

## Non-Goals

This smoke does not prove production deployment readiness, print-ready wrap output, verified scale/bleed/color/DPI, production UV accuracy, marketplace flows, billing, ordering, installer workflows, commercial licensing, moderation guarantees, or long-term hosted provider availability.
