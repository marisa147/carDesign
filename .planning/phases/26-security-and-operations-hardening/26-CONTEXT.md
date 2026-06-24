# Phase 26 Context: Security And Operations Hardening

## Objective

Close the v4 reliability loop by hardening workspace ownership, untrusted binary
inputs, hosted quota accounting, and job trace metadata without rewriting the
generation pipeline.

## Scope

- Derive API ownership from the request context and reject cross-workspace access
  for workspace-owned resources.
- Validate uploaded images and provider-downloaded images by bytes, content type,
  dimensions, and bounded size.
- Add an atomic reserve/settle quota abstraction for hosted provider calls.
- Persist trace identifiers and timing metadata around worker claim/provider
  execution so status events are easier to correlate.

## Constraints

- Keep local development usable without an external auth provider by using a
  deterministic local user fallback.
- Preserve existing job/event tables and the Phase 23 short-transaction worker
  structure.
- Keep hosted provider rollout behind existing feature flags and guardrails.

