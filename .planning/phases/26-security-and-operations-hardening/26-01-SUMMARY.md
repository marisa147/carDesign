# Phase 26 Summary: Security And Operations Hardening

## Completed

- Added request-derived user identity through `X-CarAgent-User`, with `local-user`
  as the local/dev fallback.
- Workspace creation now derives `owner_id` server-side and workspace-owned API
  routes reject cross-owner access.
- Asset upload validation now checks declared MIME/extension, magic bytes,
  decoded image dimensions, byte size, and pixel bounds.
- BFL provider result downloads now reject non-HTTPS URLs, optional disallowed
  hosts, oversized responses, wrong MIME, and invalid PNG bytes.
- Hosted provider preflight now creates an atomic reserve record and settles it
  after success or failure.
- Worker RUNNING/completion/failure metadata now includes trace id, job id,
  model run id, queue age, and running duration.
- OpenAPI and generated TypeScript contracts were regenerated after auth
  dependency changes.

## Notes

- The quota store is behind a small reserve/settle interface. Local/dev/test
  runtimes use the in-memory implementation; non-local runtimes select the
  Redis-backed implementation through the same worker pipeline.
- Local unauthenticated development continues to work through the deterministic
  `local-user` fallback.

