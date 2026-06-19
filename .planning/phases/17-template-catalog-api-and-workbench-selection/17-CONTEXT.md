# Phase 17: Template Catalog API And Workbench Selection - Context

## Scope

Phase 17 exposes the Phase 16 template pack through typed API endpoints and lets Workbench users browse, filter, and select templates before generation. The selected template must persist through brief updates, job metadata, prompt plans, versions, artifacts, model runs, and export manifests.

## Requirements

- V3-CATALOG-01: Workbench users can browse, filter, and select supported templates and side views before generation.
- V3-CATALOG-02: API exposes template list/detail endpoints with thumbnail URLs, supported views, safe-zone summary, source/license status, and readiness flags.
- V3-CATALOG-03: Workbench shows template source/license warnings, unavailable states, and missing-rights reasons before submission.
- V3-CATALOG-04: Selected template persists through workspace parameters, generation jobs, prompt plans, versions, artifacts, model runs, and export metadata.
- V3-CATALOG-05: Users see stable fallback or block messages when a selected template is unavailable, unsupported, or not licensed for requested use.

## Boundaries

- Phase 17 does not add new template-aware rendering behavior beyond selecting the template id and showing its metadata.
- Phase 18 owns deeper selected-template generation, edit, 3D fallback, and contract compatibility validation.
- Template thumbnails are served from internal package resources, not object storage.

## Implementation Notes

- Add a separate templates router to keep catalog endpoints out of generation job routes.
- Let `PATCH /generation/briefs/{brief_id}` accept `vehicle_template_id` and `view` so selecting a template recomputes safe zones and source/readiness.
- Keep unsupported freeform ids normalized to the default template with visible warnings for generation brief creation/update.
- Keep blocked or non-catalog-ready templates disabled in the selector.
