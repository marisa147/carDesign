# Template Governance

v3.0 treats vehicle templates as governed assets, not anonymous prompt hints. A template can be used for reusable catalog assets only when its source type, license status, usage scope, distribution flag, and audit timestamp are recorded.

## Source Policy

| Source type | Reusable assets | Template catalog | Evidence |
|-------------|-----------------|------------------|----------|
| `internal_original` | yes | yes | Internal creation record recommended |
| `licensed_template` | yes | conditional | Written license evidence required |
| `user_provided_with_rights` | yes | conditional | User rights confirmation and usage scope required |
| `third_party_reference_only` | no | no | Reference only; never reusable masks or thumbnails |
| `web_crawled_image` | no | no | Prohibited as template source |

The runtime policy table is exposed by `caragent_core.generation.template_source_policy_table()`.

## Registration Rules

Template registration uses `VehicleTemplateRecord` plus `TemplateSourceMetadata`.

Every reusable record must include:

- `source_type`
- `license_status`
- `rights_notes`
- `allowed_usage_scope`
- `distribution_allowed`
- `audit_timestamp`

`licensed_template` records must also include `license_evidence`. Records with `third_party_reference_only`, `web_crawled_image`, `blocked`, `missing`, or `reference_only` status are rejected before they can enter the reusable template registry.

## Readiness

`evaluate_template_readiness()` reports whether a template can appear as a catalog-ready reusable asset. Readiness checks include:

- source policy eligibility
- license status
- audit timestamp
- distribution flag
- required MVP asset slots

The legacy `generic-side-coupe` template remains supported and has an alias bridge from `generic_coupe_side_v1`. It resolves for existing v1/v2 payloads but is not catalog-complete until the v3 template pack supplies all required asset slots.

## Non-Production Boundary

Template source metadata and readiness reports do not make a design print-ready. They only prove provenance and MVP asset completeness. Verified scale, bleed, color profile, DPI, UV mapping, installer notes, and real vehicle licensing remain future production handoff work.
