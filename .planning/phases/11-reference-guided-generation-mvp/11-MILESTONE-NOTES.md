---
phase: 11-reference-guided-generation-mvp
status: complete
created: 2026-06-18
requirements: [V2-REF-01, V2-REF-02, V2-REF-03, V2-REF-04, V2-REF-05]
external_calls_default: false
---

# Phase 11 Milestone Notes

Phase 11 adds reference-guided generation as a local/provider-off MVP capability. Users can assign explicit reference roles, keep rights/source gates visible, see provider unsupported-role warnings, reuse references through child iterations, and inspect durable trace evidence after generation and export.

## What Shipped

- First-class reference roles: `character`, `style`, `vehicle`, `logo`, `palette`, and `inspiration`.
- Structured `reference_usage` contracts with compatibility for legacy `reference_asset_ids`.
- Rights/source snapshots for reference usage trace metadata.
- Provider capability metadata for reference inputs and supported/unsupported roles.
- Prompt planning that includes/omits references according to provider support and records warnings.
- Worker/provider handling that carries reference metadata, records local prompt-only trace, and fails closed for unsupported hosted reference-image input.
- Durable trace across model runs, artifacts, versions, job metadata/events, and concept export source data.
- Workbench UX for role assignment, eligibility, provider warnings, progress diagnostics, version trace, and child iteration reference reuse.
- Docs, UAT checklist, and verification evidence for V2-REF-01 through V2-REF-05.

## Requirement Closure

| Requirement | Status | Evidence |
|-------------|--------|----------|
| V2-REF-01 | Complete | Role schema, asset panel role controls, web tests, UAT checklist. |
| V2-REF-02 | Complete | Rights/source gates in API/worker and workbench eligibility tests. |
| V2-REF-03 | Complete | Provider capability map, prompt planner filtering, worker preflight tests. |
| V2-REF-04 | Complete | Unsupported-role warnings in API/worker metadata and workbench progress/provider UI. |
| V2-REF-05 | Complete | Durable reference trace metadata and export manifest source data. |

## Verification Snapshot

- Phase 11 focused core/API/worker/web checks passed.
- `corepack pnpm contracts:check` passed with full host access.
- `corepack pnpm smoke:worker -- --dry-run` passed.
- `corepack pnpm validate` passed with full host access.
- Live browser UAT remains a host-run checklist.
- Hosted reference smoke is manual-only and skipped in this agent run because real credentials, cost approval, and verified provider reference-image support were not provided.

## Operational Boundary

- Local deterministic provider records references as prompt guidance and trace metadata only.
- BFL reference-image input remains unsupported in the current capability map.
- Unsupported hosted reference roles must warn or fail closed before provider execution.
- No binary reference image data, provider keys, local paths, bearer tokens, or raw vendor payloads are stored in trace metadata or rendered in compact UI.
- Phase 11 output remains concept-preview evidence, not print-ready wrap production proof.

## Phase 12 Handoff

Phase 12 can build lightweight 3D preview on top of existing version/artifact/PreviewSpec surfaces. It should treat Phase 11 reference trace as source evidence for preview/export context, not as a guarantee of physically accurate wrap alignment.

Recommended next command:

```powershell
$gsd-plan-phase 12 --auto
```
