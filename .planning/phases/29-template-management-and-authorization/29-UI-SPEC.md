# Phase 29 UI Spec: Template Management And Authorization

## Route

- Add `/settings/templates` as an operational template management page.
- Header matches existing settings pages with a back-to-workbench action.

## Primary Layout

- Top summary band: count of installed templates, count of maintained templates, count with commercial use allowed, and upload validation state.
- Installed template list: compact selectable rows/cards with label, template id, source class, supported views, readiness, dimensions, and thumbnail.
- Detail panel: selected template metadata with sections count, forbidden zones count, export formats, scale, and structured authorization.
- Import panel: zip upload control plus validation result summary and issue list.

## Authorization Display

Show explicit fields when available:
- Source class: maintained internal, user provided, third-party authorized, or reference-only.
- Authorization file reference.
- Scope.
- Expiration.
- Commercial use flag.
- Reviewer.
- Version history.

Fallback fields should render as `未提供` instead of hiding the row.

## Interaction Rules

- Selecting a template updates the detail panel without navigation.
- Uploading a zip package calls the validation endpoint and displays accepted/errors/warnings.
- Validation issues must identify file path and issue type when available.
- Page should remain dense and workbench-like; no marketing hero or explanatory landing layout.

## Empty/Error States

- Template list loading: show a compact loading line.
- Template fetch error: show an alert with retry via page refresh.
- No file selected: upload button disabled.
- Invalid package: keep issue list visible and do not imply import success.
