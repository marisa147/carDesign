---
phase: 10-targeted-regeneration-and-masked-editing-mvp
status: checklist-ready
created: 2026-06-18
external_calls_default: false
hosted_mask_smoke: optional_manual
---

# Phase 10 Human UAT Checklist

Use this checklist after local infrastructure, migrations, API, worker, and web are running. It covers targeted edit selection, mask preview, deterministic recomposition, provider guardrails, failure/retry behavior, and comparison. Manual hosted mask smoke is optional and must not run without credentials and cost approval.

## Local Setup

```powershell
pnpm infra:up
cd services/api
uv run alembic upgrade head
cd ../..
pnpm dev:api
# second terminal
cd services/worker
uv run celery -A caragent_worker.app worker --loglevel=INFO --pool=solo --concurrency=1
# third terminal
pnpm dev:web
```

## Provider-Off Targeted Edit UAT

| Step | Expected Result | Status |
|------|-----------------|--------|
| Open or create a workspace and generate a local concept preview. | A generated artifact and design version appear in the workbench. | Not run by agent |
| Select the generated version and enable `局部编辑`. | The preview keeps normal version history and shows targeted edit controls. | Not run by agent |
| Toggle `安全区` and choose a safe zone such as `door-main`. | The selected target is visible and bounded inside the 2D preview. | Not run by agent |
| Choose an overlay layer such as `text-1` and toggle mask preview. | A mask preview appears for the selected target without mutating the parent version. | Not run by agent |
| Submit a recomposition-safe change such as moving or changing text. | A child iteration job is created; the parent version remains visible. | Not run by agent |
| After completion, select the child and open comparison. | The comparison panel shows parent, child, `deterministic_recomposition`, target, prompt delta, and metadata-backed changed-region highlight. | Not run by agent |
| Trigger or inspect an invalid target/mask failure. | The progress panel shows a safe failure category, blocked reason, target, and no retry control when metadata says the edit is not retryable. | Not run by agent |
| Trigger or inspect a retryable provider/storage/timeout failure fixture. | Retry preserves the original edit intent and parent/mask metadata. | Not run by agent |
| Repeat at desktop and mobile widths. | No horizontal document scroll, incoherent overlap, or hidden critical controls. | Not run by agent |

## Provider-Mask Guardrail UAT

| Step | Expected Result | Status |
|------|-----------------|--------|
| Keep hosted calls disabled and request provider masked generation. | The API/worker blocks the request with a safe unsupported or configuration failure before provider execution. | Not run by agent |
| Refresh operations status. | Provider capability and blocked reasons are visible without secrets, tokens, or Windows paths. | Not run by agent |
| Inspect job/version/artifact/model-run metadata. | Route, target, prompt delta, parent version, mask artifact, provider intent, and failure category are durable. | Not run by agent |

## Optional Hosted Mask Smoke

Run this only with explicit operator approval, real credentials in ignored service env files, small quota/rate/cost guards, and a verified provider route that supports masks. If any prerequisite is missing, skip and record the reason.

```powershell
# services/api/.env and services/worker/.env, never committed
V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=true
V2_TARGETED_REGENERATION_ENABLED=true
AI_PROVIDER_DEFAULT=bfl
AI_PROVIDER_MODEL=flux-2-pro-preview
AI_PROVIDER_CALLS_ENABLED=true
AI_HOSTED_DAILY_CALL_LIMIT=1
AI_HOSTED_RATE_LIMIT_PER_MINUTE=1
AI_MAX_ESTIMATED_COST_PER_JOB=0.25
AI_PROVIDER_BFL_API_KEY=replace-with-real-key-in-ignored-env
```

| Step | Expected Result | Status |
|------|-----------------|--------|
| Confirm the provider/model explicitly supports mask input for the chosen route. | Mask support is verified before any paid request. | Skipped by agent |
| Submit exactly one small hosted mask edit. | Job records provider, model, cost, target, mask artifact, parent version, child version, and route metadata. | Skipped by agent |
| Inspect comparison UI. | Route displays as provider-generated, not recomposition-only. | Skipped by agent |
| Disable hosted flags and remove active credentials. | Local deterministic mode remains available. | Skipped by agent |

## Agent Run Status

- Automated focused regression: passed.
- Provider-off worker smoke dry run: passed.
- Aggregate validation: passed.
- Browser UAT: checklist only; live browser/services were not started in this agent run.
- Hosted mask smoke: skipped because it requires real credentials, cost approval, and a verified mask-capable hosted route.
