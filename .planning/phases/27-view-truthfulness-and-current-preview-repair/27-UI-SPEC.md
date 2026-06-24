# Phase 27 UI Spec: View Truthfulness And Current Preview Repair

## Surface

Primary surface: existing Workbench 2D preview panel and its side/front/rear/top view controls.

## Interaction Contract

- Keep four controls labeled `侧面`, `前视`, `后视`, and `俯视`.
- The currently selected view remains visually active.
- If a view is not available for the selected template/version, the preview panel must show an empty state containing `模板未提供该视图`.
- The empty state should also show the selected template id or label when available so the user understands the limitation belongs to the template package, not a failed generation.
- The UI must not stretch, duplicate, or relabel the side-view image as another view.

## Visual Constraints

- Use the existing workbench visual language and button sizing.
- Avoid landing-page or marketing-style treatment; this is an operational design workspace.
- The unavailable-view empty state should be quiet and compact, not a full-page modal.
- On mobile widths, controls must wrap or scroll without overlapping preview content.

## Required States

- Side-only template: side view shows the generated image/overlays; front/rear/top show unavailable state.
- Multi-view template fixture: available views show their own content or a ready placeholder for that view; missing views still show unavailable state.
- No selected version/artifact: preserve the existing no-preview state.
- Loading/running job: preserve existing progress behavior; do not show unavailable view as a job failure.

## Acceptance Checks

- A test or grep can find the literal string `模板未提供该视图` in the frontend source.
- UI state is derived from template/version capability metadata, not from the selected button alone.
- Side-only templates cannot produce four visually identical view panels.
