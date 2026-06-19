# Phase 18 Validation Strategy

## Automated Checks

- Core prompt and brief tests verify every MVP template resolves to valid PreviewSpec template metadata and existing overlay safe zones.
- Worker generation tests run the local deterministic provider path against every MVP template.
- Worker reference trace tests assert template context is stored alongside reference roles and rights snapshots.
- Worker targeted recomposition tests assert selected-template safe zones and mask metadata are preserved.
- Frontend tests assert canonical coupe 3D compatibility, unsupported-template fallback, template-aware preview labels, targeted edit region submission, and stale target clearing.
- Contracts checks confirm generated TypeScript still compiles and archived v1/v2 legacy PreviewSpec fixtures remain compatible.

## Manual/UAT Deferred

Browser UAT across desktop/mobile remains Phase 20 scope. Phase 18 focuses on deterministic automated proof.

