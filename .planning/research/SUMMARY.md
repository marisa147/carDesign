# v4 Research Summary: Real Generation Closure And Reliability

**Source:** `C:/Users/25858/Downloads/carAgent_CODE_REVIEW.md`
**Synthesized:** 2026-06-22

## Stack Additions

- Keep the existing Next.js, FastAPI, SQLAlchemy, Celery, Redis, PostgreSQL, MinIO/S3, Pillow, and OpenAPI contract stack.
- Add a shared object storage factory used by both API and Worker. Local mode should use a configured shared file root; non-local mode should use S3-compatible storage.
- Add a transactional outbox table for job dispatch. Celery remains the execution queue, but PostgreSQL becomes the committed dispatch ledger.
- Add lightweight image validation helpers for real PNG/WebP/JPEG magic, dimensions, and max-pixel checks.

## Feature Table Stakes

- Users can explicitly submit a saved brief for generation and see a queued/running/succeeded job update in the workbench.
- Users can see the real generated image bytes in the 2D preview, not only an object key.
- API and Worker read/write artifacts through the same object storage abstraction.
- Job dispatch cannot race ahead of the committed database row.
- Worker progress and failures are visible through short committed state transitions.
- 3D screenshot capture stores real canvas bytes and rejects mismatched dimensions.
- Parameter edits can clear optional text/list/reference fields.
- The local deterministic generation path uses template package masks instead of drawing an unrelated abstract vehicle.

## Watch Out For

- Do not weaken the existing concept-only boundary: v4 improves reliability and fidelity, but still does not claim print-ready wrap output, verified UV mapping, commercial ordering, billing, or marketplace readiness.
- Do not scatter storage code through API and Worker entrypoints; keep storage setup behind one factory contract.
- Do not block HTTP handlers on long provider calls or keep DB transactions open across network calls.
- Do not let the LLM parser write directly to durable records. It should return a strict draft that deterministic normalization validates.

## Recommended Build Order

1. Real generation entrypoint, artifact content route, and 2D image rendering.
2. Shared object storage settings/factory and content metadata preservation.
3. Outbox dispatch plus worker short-transaction status transitions.
4. Real 3D screenshot capture and clearable brief patches.
5. Structured brief parser boundary and template compositor.
6. Auth/ownership, upload/download hardening, atomic quota, and observability.
