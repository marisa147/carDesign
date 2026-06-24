# Phase 23 Code Review

## Findings

No blocking findings after implementation and validation.

## Review Notes

- The route-level explicit commit is intentional: FastAPI yield dependencies commit after the route returns, but this phase needs Celery dispatch to occur after commit while preserving the existing `queued` response payload.
- The outbox replay primitive is in core (`list_ready_job_dispatches`) but no background dispatcher process was added in this phase; the API route now acts as the synchronous dispatcher for newly created rows.
- Worker transaction boundaries are shortened with explicit commits before provider calls and storage writes while keeping the existing generation pipeline structure intact.

## Residual Risk

- A live multi-worker race with PostgreSQL/Celery is covered by conditional SQL semantics and unit tests, but not by a Docker-backed concurrent smoke in this phase.
- If enqueue succeeds but the later queue metadata commit fails, the outbox row may need replay/manual repair. The task remains idempotent at worker claim time.
