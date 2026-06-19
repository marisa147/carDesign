---
phase: 14
plan: 05
status: ready
requirements: [V2-REL-05]
---

# Phase 14 - V2 Feature Flags And Release Configuration

This reference is the release-readiness map for V2 MVP flags, hosted-provider configuration, quota guards, manual smoke overrides, and rollback behavior. Defaults are local, provider-off, free, and concept-only.

## Server Flags

| Variable | Default | Read By | Gated Behavior |
|----------|---------|---------|----------------|
| `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED` | `false` | `services/api/src/caragent_api/config.py`, `services/worker/src/caragent_worker/config.py`, `services/core/src/caragent_core/provider_capabilities.py`, worker hosted preflight | Enables the BFL hosted rollout path only when `AI_PROVIDER_CALLS_ENABLED`, credentials, and quota/rate/cost guards are also valid. When disabled, BFL reports blocked reasons and no hosted call is made. |
| `V2_TARGETED_REGENERATION_ENABLED` | `false` | API generation routes and worker targeted edit tasks | Allows provider-masked targeted regeneration routes. Local deterministic recomposition for safe overlay edits remains the baseline path; unsupported provider-mask routes fail closed. |
| `V2_REFERENCE_GUIDANCE_ENABLED` | `false` | API/worker settings, provider capability tests, release env examples | Release switch for structured reference guidance posture. Rights/source gates and provider unsupported-role warnings still protect reference usage. |
| `V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED` | `false` | `services/api/src/caragent_api/routes/jobs.py`, API/worker settings | Allows version-scoped `preview_3d_screenshot` artifact creation. The browser 3D viewer must still display concept-only and UV-not-verified labels. |
| `V2_ENHANCED_HANDOFF_PACKAGE_ENABLED` | `false` | `services/api/src/caragent_api/routes/jobs.py`, API/worker settings | Allows `enhanced_concept_handoff_zip` export creation after server-authoritative rights/source checks. PNG/JPG concept export remains separate. |

## Browser Flags

Browser values are public hints only. They do not grant server capabilities, bypass API/worker validation, or make hosted provider calls safe.

| Variable | Default | Read By | Gated Behavior |
|----------|---------|---------|----------------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | `apps/web/src/lib/config/public-env.ts` | Points the Next.js workbench at the API. |
| `NEXT_PUBLIC_V2_HOSTED_PROVIDER_ROLLOUT_ENABLED` | `false` | `apps/web/src/lib/config/public-env.ts` | Browser-visible release posture for hosted-provider rollout. The API/worker server flags and hosted guards remain authoritative. |
| `NEXT_PUBLIC_V2_TARGETED_REGENERATION_ENABLED` | `false` | `apps/web/src/lib/config/public-env.ts` | Browser-visible release posture for targeted regeneration. API/worker targeted edit gates remain authoritative. |
| `NEXT_PUBLIC_V2_REFERENCE_GUIDANCE_ENABLED` | `false` | `apps/web/src/lib/config/public-env.ts` | Browser-visible release posture for reference guidance. Rights/source and provider capability checks remain authoritative. |
| `NEXT_PUBLIC_V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED` | `false` | `apps/web/src/lib/config/public-env.ts` | Browser-visible release posture for lightweight 3D. Screenshot persistence is still gated by the API server flag. |
| `NEXT_PUBLIC_V2_ENHANCED_HANDOFF_PACKAGE_ENABLED` | `false` | `apps/web/src/lib/config/public-env.ts`, Workbench ZIP mode helper | Shows the enhanced handoff ZIP mode in the workbench. The API server flag and rights/source validation still decide whether package creation succeeds. |

## Provider Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `AI_PROVIDER_DEFAULT` | `disabled` | Selects the provider path. Local release validation keeps this disabled or local deterministic unless running a manual hosted smoke. |
| `AI_PROVIDER_MODEL` | `local-concept-v1` | Records model identity in provider/model trace metadata. Manual BFL smoke uses `flux-2-pro-preview` only after rechecking access and pricing. |
| `AI_PROVIDER_CALLS_ENABLED` | `false` | Hard switch for any non-local provider calls. Missing or false blocks hosted execution before vendor access. |
| `AI_GENERATION_TIMEOUT_SECONDS` | `30` | Hosted/local generation timeout budget. |
| `AI_GENERATION_POLL_INTERVAL_SECONDS` | `1` | Hosted result polling interval. |
| `AI_GENERATION_MAX_POLL_ATTEMPTS` | `30` | Hosted polling attempt cap. |
| `AI_GENERATION_MAX_ATTEMPTS` | `1` | Worker retry attempt cap. |
| `AI_PROVIDER_FALLBACK_ENABLED` | `false` | Keeps fallback explicit; do not silently switch hosted output claims. |
| `AI_PROVIDER_FALLBACK_NAME` | `local-deterministic` | Local deterministic fallback identity when fallback is intentionally enabled. |
| `AI_PROVIDER_BFL_BASE_URL` | `https://api.bfl.ai` | BFL API base for the adapter. |
| `AI_PROVIDER_BFL_SUBMIT_PATH` | `/v1/flux-2-pro-preview` | BFL submit path for the current guarded adapter. |
| `AI_PROVIDER_BFL_RESULT_PATH` | `/v1/get_result` | BFL polling result path. |
| `AI_PROVIDER_OPENAI_API_KEY` | empty | Placeholder only; no OpenAI image adapter is release-enabled in V2 MVP. |
| `AI_PROVIDER_FAL_API_KEY` | empty | Placeholder only; no FAL adapter is release-enabled in V2 MVP. |
| `AI_PROVIDER_BFL_API_KEY` | empty | Ignored-env secret for manual BFL smoke. Never commit real values or expose them in screenshots/logs. |

## Hosted Guard Variables

All hosted-provider smoke runs must configure these values in ignored service env files before any provider call:

| Variable | Local Default | Manual Smoke Value | Required Behavior |
|----------|---------------|--------------------|-------------------|
| `AI_HOSTED_DAILY_CALL_LIMIT` | empty | `1` | Blocks hosted execution unless a daily cap exists. |
| `AI_HOSTED_RATE_LIMIT_PER_MINUTE` | empty | `1` | Blocks hosted execution unless a per-minute cap exists. |
| `AI_MAX_ESTIMATED_COST_PER_JOB` | empty | `0.25` or lower practical cap | Blocks hosted execution unless a per-job cost cap exists. |

Missing quota, rate, or cost guards must surface as safe blocked reasons in operations status or job metadata, not as hidden provider attempts.

## Manual Hosted Smoke Overrides

Use these only for the Phase 14 hosted-provider smoke runbook after operator cost approval, real credential availability, and provider account/model checks:

```dotenv
V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=true
AI_PROVIDER_DEFAULT=bfl
AI_PROVIDER_MODEL=flux-2-pro-preview
AI_PROVIDER_CALLS_ENABLED=true
AI_HOSTED_DAILY_CALL_LIMIT=1
AI_HOSTED_RATE_LIMIT_PER_MINUTE=1
AI_MAX_ESTIMATED_COST_PER_JOB=0.25
AI_PROVIDER_BFL_API_KEY=replace-with-real-key-in-ignored-env
```

Run exactly one concept-preview job, record workspace/job/model-run/version/artifact/cost evidence, then reverse the overrides.

## Reversal

1. Set `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED=false` and `AI_PROVIDER_CALLS_ENABLED=false` in API and worker env.
2. Remove the active `AI_PROVIDER_BFL_API_KEY` from shells and ignored env files used for smoke.
3. Restart API and worker processes so settings reload.
4. Refresh operations status and confirm BFL is blocked by rollout/calls/credential guardrails.
5. Keep local deterministic generation, targeted edits, reference guidance metadata, 3D preview, and handoff ZIP paths usable under their own local feature flags.

## Release Boundaries

V2 MVP remains concept-only and not print-ready. It does not prove production wrap output, print scale, bleed, DPI, color profile, verified production UV mapping, physical installability, automated licensing, quotes/orders/payments, marketplace/community flows, auth, billing, installer workflows, or production deployment. Hosted output quality, pricing, moderation, account status, mask/reference-image support, and commercial terms must be rechecked before any non-local output is treated as production-ready evidence.

## Verification Pointers

- Release baseline and final command evidence: `14-BASELINE-VALIDATION.md` and `14-VERIFICATION.md`.
- Docker smoke evidence: `14-DOCKER-SMOKE.md`.
- Hosted-provider smoke checklist: `14-HOSTED-SMOKE-RUNBOOK.md`.
- Browser UAT screenshots and metrics: `14-HUMAN-UAT.md` and `evidence/`.
- Public docs entry points: `README.md` and `docs/development.md`.
