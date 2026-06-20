# v3.0 Release Notes: Template Library And Production Readiness

**Status:** Ready to archive  
**Date:** 2026-06-20

## Shipped

- Template source governance for `internal_original`, `licensed_template`, `user_provided_with_rights`, `third_party_reference_only`, and `web_crawled_image`.
- Source/license/readiness metadata, audit output, prohibited-source blocking, and legacy `generic-side-coupe` compatibility.
- Internal-original MVP side-view template pack for coupe, sedan, hatchback, SUV, and van.
- Template package validation for required slots, PNG dimensions, masks, safe zones, metadata, readiness, and aliases.
- Template catalog API and Workbench selector with thumbnail, source/license/readiness, warning, unavailable, and selected-template persistence states.
- Template-aware local generation, PreviewSpec overlays, targeted edit regions, reference/provider trace, durable worker records, and export metadata.
- Lightweight 3D compatibility for supported coupe templates and explicit 2D fallback for unsupported MVP templates such as `generic_van_side_v1`.
- Concept-only production readiness preflight with durable JSON export artifacts.
- Enhanced handoff ZIP evidence for `production-readiness-preflight.json` and `template-validation.json`.
- V3 validation, Docker/local smoke, desktop/mobile Browser UAT, docs, and milestone audit evidence.

## Validation

- `corepack pnpm validate` passed.
- `uv run python -m caragent_core.generation.validate_template_pack` passed.
- `corepack pnpm compat:v1` passed.
- `corepack pnpm migration:safety` passed.
- `corepack pnpm smoke:worker -- --dry-run` passed.
- Docker-backed `infra:up` -> `smoke:local` -> `infra:down` passed.
- Desktop and mobile Browser UAT passed with no horizontal overflow.

## Still Not Production Handoff

v3.0 deliberately remains a concept design and review milestone. It does not ship:

- Print-ready PSD/AI/PDF exports.
- Verified scale, bleed, color profile, DPI, installer notes, or wrap-shop proof.
- Verified UV mapping or true production 3D geometry.
- Real licensed vehicle-specific template marketplace.
- Quotes, orders, payments, installer workflows, gallery, auth, billing, or collaboration.
- Automated legal-grade copyright/licensing verification.
- Hosted provider production-readiness claims.

## Future Promotions

1. Production handoff: add verified scale, bleed, color, DPI, installer notes, and print-ready package formats.
2. Real templates: add licensed vehicle-specific template coverage with shop feedback and QA.
3. True 3D/UV: replace lightweight concept shells with verified vehicle-specific UV mapping.
4. Business layer: add marketplace, quotes, orders, payments, installer routing, and collaboration after production evidence is stable.
5. Rights automation: add legal-grade verification only after source metadata and human review flows are proven.

