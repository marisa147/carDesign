# Phase 19 Validation Strategy

## Automated Checks

- Core report tests verify required missing evidence ids.
- Core ZIP tests verify preflight and template validation files are included and sanitized.
- API tests verify version-scoped preflight creates a durable export artifact.
- API tests verify print-ready formats remain blocked.
- Frontend tests verify preflight request, report rendering, enhanced ZIP evidence, and disabled print-ready gates.
- Contracts are regenerated and checked after the new endpoint.

## Manual/UAT Deferred

Desktop/mobile Browser UAT for the full v3 milestone remains Phase 20 scope.

