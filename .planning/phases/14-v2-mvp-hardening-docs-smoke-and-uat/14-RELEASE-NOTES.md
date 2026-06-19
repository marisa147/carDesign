---
phase: 14-v2-mvp-hardening-docs-smoke-and-uat
artifact: release-notes
status: complete
created: 2026-06-19
requirements: [V2-REL-01, V2-REL-02, V2-REL-03, V2-REL-04, V2-REL-05]
---

# V2 MVP Release Notes

## Release Summary

V2 MVP upgrades the V1 concept-generation workbench into a richer concept review workflow. The release adds a guarded Hosted Provider path, Targeted editing and comparison, Reference guidance with rights/source gates, a lightweight 3D concept preview, enhanced concept handoff ZIPs, and Phase 14 release hardening evidence.

The release remains provider-off by default, concept-only, and not print-ready.

## What Shipped

- Hosted Provider rollout path for BFL behind `V2_HOSTED_PROVIDER_ROLLOUT_ENABLED`, `AI_PROVIDER_CALLS_ENABLED`, provider capability metadata, credentials, quota/rate/cost guards, and operations diagnostics.
- Targeted edit selection, mask preview, deterministic recomposition for safe layer changes, provider-mask guardrails, retry-safe failure metadata, and parent/child comparison evidence.
- Reference guidance with six roles, rights/source snapshots, provider unsupported-role warnings, durable reference trace metadata, and child-iteration reference reuse.
- Lightweight 3D preview using `Preview3DSpec`, one `generic-side-coupe-lightweight-v1` shell, camera controls, screenshot artifact persistence, fallback states, and persistent non-production/UV-not-verified labels.
- Enhanced handoff package export as `enhanced_concept_handoff_zip` with stable manifest JSON, Markdown reports, prompt/provider trace, reference manifest, concept image, optional 3D screenshots, immutable export records, and rights/source guardrails.
- Phase 14 release hardening: aggregate validation, contract drift check, V1 compatibility, migration safety, Docker smoke, hosted-provider smoke runbook, Browser UAT, feature flag reference, docs check, and final traceability.

## Validation Evidence

- `corepack pnpm validate` passed in an elevated host run.
- `corepack pnpm contracts:check` passed after a manual regenerate confirmed no true contract drift.
- `corepack pnpm compat:v1` passed.
- `corepack pnpm migration:safety` passed.
- `corepack pnpm smoke:worker -- --dry-run` passed.
- Docker smoke passed for local PostgreSQL, Redis, MinIO, Alembic, durable data, and local deterministic generation.
- Browser UAT passed on desktop and mobile for hosted guard visibility, Targeted edit controls/comparison, Reference warnings, 3D preview labels, enhanced handoff ZIP preview/history, and no horizontal overflow.

## Hosted Provider Notes

Hosted Provider smoke is manual-only for this release. Operators must use `14-HOSTED-SMOKE-RUNBOOK.md`, real credentials in ignored env files, explicit cost approval, `AI_HOSTED_DAILY_CALL_LIMIT`, `AI_HOSTED_RATE_LIMIT_PER_MINUTE`, `AI_MAX_ESTIMATED_COST_PER_JOB`, a one-job cap, and reversal steps. This release does not claim live hosted output quality, account readiness, pricing stability, moderation readiness, mask/reference-image support, or commercial terms.

## Deferred Scope

V2 MVP does not include production wrap output, print-ready PSD/AI/PDF handoff, verified scale/bleed/color/DPI, verified production UV mapping, full vehicle-template coverage, auth, billing, marketplace/community flows, quotes/orders/payments, installer workflows, automated legal licensing verification, or production deployment. These remain deferred to later milestones.

## Upgrade Notes

- Keep real `.env` files ignored.
- Keep all V2 server and browser feature flags disabled unless running a specific local/manual validation.
- Browser `NEXT_PUBLIC_V2_*` flags are public UI hints only; API/worker `V2_*` flags, provider capabilities, quota guards, rights/source gates, and route validation remain authoritative.
- Re-run the Phase 14 command set before using these notes as fresh release evidence.
