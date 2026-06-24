# Phase 29 Context: Template Management And Authorization

## Goal

Make template provenance visible and importable through product UI. Users must be able to inspect installed template package details, upload a template package for validation, and understand whether a template is maintained internal, user-provided, or third-party authorized without reading hidden metadata.

## Requirements

- TMPL-01: User can open a template management page and inspect installed template package details.
- TMPL-02: User can import a template package containing SVG/PNG/JSON assets and see validation results.
- TMPL-03: User can review structured authorization status including source, authorization file reference, scope, expiration, commercial-use flag, reviewer, and version history.
- TMPL-04: User can distinguish maintained internal templates, user-provided templates, and third-party authorized templates without relying on hidden metadata.

## Current System

- API already exposes `/templates`, `/templates/{template_id}`, and thumbnail content.
- Phase 28 added `toyota_gr86_brz_v1` with supported views, sections, forbidden zones, dimensions, scale, export config, and authorization metadata.
- Frontend has provider settings pages under `/settings/bfl` and `/settings/gpt`; a template management page can reuse that operational settings layout.
- Contract generation is partially blocked by local Node/Corepack/orval issues, so OpenAPI must still be exported and generated TypeScript kept aligned manually when necessary.

## Scope

In scope:
- Add an API validation endpoint for uploaded template packages.
- Validate zip package structure, JSON manifests, SVG/PNG asset presence, dimensions, and authorization fields.
- Add a template management settings page that lists installed packages, shows authorization metadata, and uploads a package for validation.
- Add focused API and frontend helper/page coverage.

Out of scope:
- Persisting imported templates into the runtime registry.
- Full template authoring UI.
- Commercial license workflow automation.
- Section-first customization, GPT section generation, and export packaging; these remain Phase 31-33 work.
