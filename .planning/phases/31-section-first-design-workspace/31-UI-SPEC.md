# Phase 31 UI Spec: Section-First Design Workspace

## Right Panel

- Add `分区工作台` near the top of the parameter panel.
- Show compact buttons for sections from the selected template detail.
- Active section button is visually selected.
- Selecting a section shows:
  - section label/id
  - related views
  - normalized bounds
  - real size in mm when available
  - edit scope state

## Preview/Edit Coupling

- Selecting a section sets targeted edit mode on.
- The selected section becomes a `safe_zone` style target with the section id and bounds.
- The selected view switches to the first view listed by the section.
- If no sections are available, show an explicit template-not-sectioned state.

## Visual Rules

- Dense operational layout, no marketing panels.
- No nested cards; section selector is one functional panel.
- Missing values render as `未提供`.
