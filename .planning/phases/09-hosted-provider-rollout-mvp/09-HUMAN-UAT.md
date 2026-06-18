---
phase: 09-hosted-provider-rollout-mvp
artifact: human-uat
created: 2026-06-18T09:33:14Z
status: partial
provider_off_status: documented-and-automated-pass
provider_on_status: skipped-no-credential-cost-approval
---

# Phase 9 Human UAT

This artifact records the Phase 9 human-facing UAT contract. Automated provider-off checks passed in this run; live browser/provider-on checks require host processes and, for BFL, real credentials plus cost approval.

## Provider-Off UAT

Status: **PASS for automated workbench coverage; host browser checklist documented.**

Evidence already run:

- Web workbench tests passed for local/default provider selection, blocked BFL state, safe diagnostics, concept-preview labeling, and hosted payload shape only after selecting enabled BFL.
- API and worker tests passed without hosted credentials.
- `corepack pnpm smoke:worker -- --dry-run` passed and made no external call.
- `corepack pnpm validate` passed in provider-off mode.

Host browser checklist for a human run:

1. Start local infrastructure with `pnpm infra:up`.
2. Run API migrations with `cd services/api && uv run alembic upgrade head`.
3. Start API, worker, and web in separate terminals.
4. Open the workbench and refresh operations status.
5. Confirm `本地概念` is selectable without credentials.
6. Confirm `BFL 托管` is disabled when rollout/calls/credentials/guards are missing.
7. Confirm blocked reasons are safe labels such as `BFL 凭据未配置`.
8. Confirm no API keys, bearer tokens, secrets, or Windows paths are visible in the workbench or operations UI.
9. Submit a local deterministic generation or child iteration and confirm output remains a concept preview.

## Provider-On BFL UAT

Status: **SKIPPED in this run.**

Skip reason:

- No real BFL credential was provided to this agent session.
- No explicit approval to spend hosted provider credits was provided.
- The project must not claim live hosted output quality, account readiness, pricing behavior, or moderation behavior without a real one-job smoke.

Manual prerequisites before running:

1. Confirm BFL account access, credit balance, pricing, moderation policy, and model access.
2. Put real credentials only in ignored `services/api/.env` and `services/worker/.env` files.
3. Set `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=true`.
4. Set `AI_PROVIDER_CALLS_ENABLED=true`.
5. Set `AI_PROVIDER_DEFAULT=bfl`.
6. Set `AI_PROVIDER_MODEL=flux-2-pro-preview`.
7. Set low guards such as `AI_HOSTED_DAILY_CALL_LIMIT=1`, `AI_HOSTED_RATE_LIMIT_PER_MINUTE=1`, and `AI_MAX_ESTIMATED_COST_PER_JOB=0.25`.
8. Restart API and worker so they load the ignored env files.

Manual provider-on evidence to record:

- Workspace id.
- Job id.
- Model run id if available.
- Version id.
- Artifact id.
- Provider and model.
- Estimated cost and actual cost if available.
- Whether fallback ran.
- Operations status and any provider failure kind/status.
- Confirmation that diagnostics contain no credentials, tokens, secrets, or local paths.
- Confirmation that hosted flags and credentials were disabled after the smoke.

## UAT Verdict

- Provider-off local deterministic behavior: **supported by automated workbench/API/worker validation and ready for host browser confirmation**.
- Provider-on live BFL behavior: **not run; explicitly skipped due missing credential/cost approval**.
- No production-readiness claim is made for hosted image quality, pricing, moderation, account availability, commercial terms, print readiness, true 3D, auth, billing, marketplace, or deployment.
