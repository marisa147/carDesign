# Phase 7: Operations And Provider Strategy - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `07-CONTEXT.md` - this log preserves the alternatives considered.

**Date:** 2026-06-18
**Phase:** 7 - Operations And Provider Strategy
**Mode:** auto-selected defaults from prior roadmap/context because the user requested autonomous progress without confirmation.
**Areas discussed:** operational priority, provider enablement, failure/retry/fallback, cancellation/quota, operator surface, Windows runtime

---

## Operational Priority

| Option | Description | Selected |
|--------|-------------|----------|
| Local ops first | Harden truthful local/dev health, worker visibility, and failure evidence before production dashboards. | yes |
| Production console first | Build a broader operator dashboard and deployment-oriented controls. | |
| Let the agent decide | Planner chooses later. | |

**Selected:** Local ops first.
**Rationale:** v1 is still a local concept-generation MVP; Phase 6 exposed a concrete stale-worker issue that local ops can address immediately.

---

## Provider Enablement

| Option | Description | Selected |
|--------|-------------|----------|
| Hosted opt-in | Keep local deterministic default; hosted calls require explicit config and secrets. | yes |
| Hosted default | Enable a hosted provider when any key exists. | |
| Provider marketplace | Build broad provider switching/matrix now. | |

**Selected:** Hosted opt-in.
**Rationale:** Project docs repeatedly keep hosted calls disabled by default; provider docs/terms are time-sensitive and need research before rollout.

---

## Failure, Retry, And Fallback

| Option | Description | Selected |
|--------|-------------|----------|
| Classified durable failures | Store normalized categories and sanitized details in job/model-run/event records. | yes |
| Free-text only | Continue storing only `latest_error` messages. | |
| Silent fallback | Hide failures by falling back automatically. | |

**Selected:** Classified durable failures.
**Rationale:** OPS requirements call for separate provider, validation, storage, queue, and unknown failure classes. Silent fallback would undermine operator trust.

---

## Cancellation And Quotas

| Option | Description | Selected |
|--------|-------------|----------|
| Queued-first cancellation and preflight quotas | Reliably cancel queued jobs first; make running cancellation best-effort; check quotas before paid calls. | yes |
| Full provider cancellation | Promise interruption of every running provider call. | |
| Billing system | Implement credits/payments. | |

**Selected:** Queued-first cancellation and preflight quotas.
**Rationale:** This matches OPS-05 and OPS-06 without dragging billing or provider-specific hard cancellation into v1.

---

## Operator Surface

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse workbench/progress surfaces | Add small typed status/config/recent-failure views to existing surfaces. | yes |
| New admin app | Build a separate dashboard. | |
| Logs only | Expose no UI/API summary beyond logs. | |

**Selected:** Reuse workbench/progress surfaces.
**Rationale:** The existing workbench already shows jobs/events/history; Phase 7 should stay compact and operational.

---

## Windows Runtime

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit solo worker path | Document or encode Windows `--pool=solo` and verify live queue consumption. | yes |
| Ignore runtime detail | Leave worker startup as-is. | |
| Replace Celery | Change queue technology now. | |

**Selected:** Explicit solo worker path.
**Rationale:** Phase 6 UAT found the current Windows worker path can be stale or unstable. A pragmatic v1 fix is a truthful runbook/health check, not a queue rewrite.

---

## the agent's Discretion

- Exact endpoint names and response schemas.
- Exact retry backoff and rate-limit store implementation.
- Exact UI placement inside existing workbench/progress/future-gate surfaces.

## Deferred Ideas

- Auth/accounts.
- Billing/credit purchase/payment.
- Production deployment/CI release pipeline.
- Broad provider marketplace.
