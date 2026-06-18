---
phase: 11-reference-guided-generation-mvp
status: checklist-ready
created: 2026-06-18
external_calls_default: false
hosted_reference_smoke: optional_manual
---

# Phase 11 Human UAT Checklist

Use this checklist after local infrastructure, migrations, API, worker, and web are running. It covers reference role assignment, rights/source gates, provider warnings, local generation, child iteration reuse, export trace, and optional hosted reference smoke. Manual hosted smoke is optional and must not run without credentials, cost approval, quota guards, and verified provider reference-image support.

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

## Provider-Off Reference UAT

| Step | Expected Result | Status |
|------|-----------------|--------|
| Open or create a workspace and upload at least two reference images. | Assets appear in the asset panel with upload kind, filename, rights/source controls, and role controls. | Not run by agent |
| Leave one asset without confirmed rights/source. | It shows a rights warning and cannot be enabled as generation-eligible. | Not run by agent |
| Confirm rights/source metadata for another asset. | The asset shows `权利已确认` and `可用于生成`. | Not run by agent |
| Assign roles from the six-role set: `角色`, `风格`, `车辆`, `Logo`, `配色`, `仅灵感`. | Role labels remain visible and controls are keyboard reachable. | Not run by agent |
| Save parameters. | The brief persists structured `reference_usage` plus legacy `reference_asset_ids` compatibility data. | Not run by agent |
| Refresh provider status with default/provider-off settings. | Local deterministic mode remains available; hosted blocked reasons are safe and contain no secrets or Windows paths. | Not run by agent |
| Select or inspect BFL when unsupported reference roles are present. | The UI shows `引用受限` / `供应商不支持` before submission. | Not run by agent |
| Submit a local deterministic generation. | Job/version/artifact/model-run trace records reference usage, included/omitted ids, warning count, roles, and rights snapshot metadata. | Not run by agent |
| Select the generated version and open comparison/history. | Compact reference trace row shows included count, role count, omitted count, warning count, and unsupported roles when present. | Not run by agent |
| Submit a child iteration from the selected version. | The request reuses current brief reference usage unless the user changed it; the parent remains immutable. | Not run by agent |
| Create a concept export for the selected version. | Export manifest/source data includes reference trace and still says `概念预览，不是生产印刷文件。` | Not run by agent |
| Repeat at desktop and mobile widths. | No horizontal document scroll, incoherent overlap, or hidden critical reference controls. | Not run by agent |

## Rights And Provider Guardrail UAT

| Step | Expected Result | Status |
|------|-----------------|--------|
| Attempt generation with an enabled reference whose rights are missing. | API/worker rejects or omits the reference before provider execution with a safe rights/source message. | Not run by agent |
| Use provider capability metadata where reference image input is unsupported. | Unsupported roles are warnings or fail-closed configuration errors; they are not silently sent to a hosted provider. | Not run by agent |
| Inspect progress/event diagnostics after a blocked reference request. | Reference warning fields are visible without raw payloads, binary data, credentials, or local paths. | Not run by agent |

## Optional Hosted Reference Smoke

Run this only with explicit operator approval, real credentials in ignored service env files, small quota/rate/cost guards, and verified provider/model support for reference-image inputs. If any prerequisite is missing, skip and record the reason.

```powershell
# services/api/.env and services/worker/.env, never committed
V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=true
V2_REFERENCE_GUIDANCE_ENABLED=true
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
| Confirm the provider/model explicitly supports the tested reference role and content type. | Capability support is verified before any paid request. | Skipped by agent |
| Submit exactly one small hosted reference-guided concept job. | Job records provider, model, cost, reference usage, warning count, rights snapshot, version id, and artifact id. | Skipped by agent |
| Inspect generated-version trace and export manifest. | Reference assets/roles and rights snapshot evidence are durable and visible in compact form. | Skipped by agent |
| Disable hosted flags and remove active credentials. | Local deterministic mode remains available. | Skipped by agent |

## Agent Run Status

- Automated focused regression: passed.
- Provider-off worker smoke dry run: passed.
- Aggregate validation: passed.
- Browser UAT: checklist only; live browser/services were not started in this agent run.
- Hosted reference smoke: skipped because it requires real credentials, cost approval, and verified provider reference-image support.
