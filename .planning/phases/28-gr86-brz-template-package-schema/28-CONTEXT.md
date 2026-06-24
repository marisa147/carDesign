# Phase 28: GR86/BRZ Template Package Schema - Context

**Gathered:** 2026-06-23
**Status:** Ready for planning
**Source:** v5 roadmap and Phase 28 requirements

<domain>
## Phase Boundary

Phase 28 creates the first deep real-vehicle template package contract and a maintained Toyota GR86/Subaru BRZ package fixture. The goal is to make the template system capable of representing four distinct views, practical body sections, safe/forbidden zones, real dimensions, scale, export configuration, and authorization metadata.

This phase does not build the template management import UI, section-first workspace, GPT section generation, or construction package exporter. It provides the schema, registry, package assets, API exposure, and validator foundation those phases will consume.
</domain>

<decisions>
## Implementation Decisions

### Locked Decisions
- First deep vehicle template id: `toyota_gr86_brz_v1`.
- The package represents Toyota GR86/Subaru BRZ as a maintained project template, not a web-crawled template.
- Required views for the deep package: `side`, `front`, `rear`, and `top`.
- The package must include sections, safe zones, forbidden zones, real-unit dimensions, scale metadata, export config, and authorization status.
- The generic MVP side-only templates must keep working.
- Phase 28 may use internally generated schematic assets as maintained placeholders, but they must be stored as project package assets and labeled as internal/maintained, not as real licensed Toyota artwork.

### the agent's Discretion
- Exact dataclass/Pydantic shapes may extend existing `VehicleTemplateRecord` rather than creating a second registry.
- The validator may support both legacy MVP side-only package rules and the new deep template rules.
- API response fields should be additive to avoid breaking current frontend contracts.
</decisions>

<canonical_refs>
## Canonical References

### Planning
- `.planning/ROADMAP.md` — Phase 28 goal and success criteria.
- `.planning/REQUIREMENTS.md` — TPLG-01..04.
- `.planning/STATE.md` — current milestone state and constraints.

### Code
- `services/core/src/caragent_core/generation/templates.py` — template schema, registry, resolution, source/readiness.
- `services/core/src/caragent_core/generation/validate_template_pack.py` — package validator.
- `services/api/src/caragent_api/routes/templates.py` — template catalog/detail API.
- `services/api/src/caragent_api/schemas.py` — template API response schemas.
- `services/api/tests/test_templates.py` — catalog/detail route tests.
</canonical_refs>

<specifics>
## Specific Ideas

- Add `supported_views` to template records; legacy records can default to `[view]`.
- Add `view_asset_slots` or equivalent mapping so a template can have four distinct base images.
- Add `sections`, `forbidden_zones`, `dimensions`, `scale`, `export_config`, and `authorization` typed metadata.
- Make `/templates?view=front` return the GR86/BRZ package once it supports front view.
- Make `/templates/toyota_gr86_brz_v1` expose the construction metadata.
</specifics>

<deferred>
## Deferred Ideas

- Template package upload/import UI is Phase 29.
- Section-first preview/workspace behavior is Phase 31.
- SVG/PDF/PNG construction package export is Phase 33.
</deferred>

---

*Phase: 28-gr86-brz-template-package-schema*
*Context gathered: 2026-06-23 via roadmap execution*
