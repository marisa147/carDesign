---
phase: 09-hosted-provider-rollout-mvp
artifact: milestone-notes
created: 2026-06-18T09:35:11Z
status: complete
---

# Phase 9 Milestone Notes

Phase 9 is complete. The project now has a controlled hosted-provider rollout path while preserving local deterministic generation as the default provider-off path.

## Delivered

- Browser-safe provider capability metadata and guard state.
- BFL hosted image adapter using the official submit/poll/download flow behind the worker provider boundary.
- API and worker hosted preflight gates for rollout flag, calls flag, credentials, supported provider/model, and quota/rate/cost guards.
- Durable provider/model/parameter/cost/fallback/failure trace metadata.
- Hosted failure classification for moderation, provider validation, credits, rate limits, timeout, provider-not-found, and generic provider errors.
- Workbench `生成模式` selector with `本地概念` and `BFL 托管`, blocked-state labels, quota/rate/cost visibility, and safe diagnostics.
- Provider-off verification evidence, hosted provider runbook, and manual provider-on UAT checklist.

## Evidence

- `09-VERIFICATION.md` records provider-off focused API, worker, web, contract, smoke dry-run, docs token check, and aggregate validation evidence.
- `09-HUMAN-UAT.md` records provider-off automated workbench coverage, host browser checklist, and provider-on BFL manual skip.
- `README.md` and `docs/development.md` document default-off behavior, provider-off commands, provider-on BFL prerequisites, and disable-after-smoke instructions.

## Requirement Coverage

- V2-PROVIDER-01: Complete via config/capability/env/docs/tests.
- V2-PROVIDER-02: Complete via API/worker preflight and workbench selector payload tests.
- V2-PROVIDER-03: Complete via provider trace persistence and cost/fallback/error metadata tests.
- V2-PROVIDER-04: Complete via safe failure classification and UI/API diagnostics tests.
- V2-PROVIDER-05: Complete via local deterministic default/fallback path and provider-off validation.

## Manual Hosted Smoke

Live provider-on BFL smoke was skipped in this agent run because no real BFL credential or cost-spend approval was provided. This is intentional and truthful: Phase 9 proves the controlled rollout path and records exact manual prerequisites, but it does not claim live hosted output quality, account readiness, pricing behavior, moderation behavior, or production readiness.

## Residual Risks

- Hosted BFL quality, pricing, moderation, account access, and commercial terms must be rechecked before treating hosted output as product/release evidence.
- Provider-on smoke can spend money and must keep daily/rate/cost guards low.
- The aiosqlite event-loop-close warning observed during API aggregate tests remains a non-blocking test cleanup warning with exit code 0.
- Future phases that add masks, references, or 3D preview must extend provider capability checks instead of assuming every provider supports every input type.

## Phase 10 Readiness

Phase 10 can build on:

- Stable provider intent fields on generation and iteration submission.
- Durable parent/child version lineage from earlier phases.
- Provider capability and guard metadata available to the workbench.
- Safe diagnostics available in operations and progress surfaces.
- Local deterministic fallback path for targeted recomposition work.

