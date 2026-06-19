---
phase: 13
slug: enhanced-concept-handoff-package-mvp
status: complete
created: 2026-06-19
---

# Phase 13 Research

## Current Repo Evidence

| Area | Finding | Implication |
|------|---------|-------------|
| Export ledger | `ExportRecord` already stores workspace/version/artifact link, format, status, concept label, manifest, requested/completed timestamps. | Phase 13 should extend this path instead of adding a parallel package ledger. |
| Artifact ledger | `ArtifactKind.EXPORT` already exists and artifact rows can link to version/job with content type, bytes, checksum, dimensions, and metadata. | ZIP packages can be represented as immutable export artifacts. |
| Storage | `ObjectStorage` only exposes `put_object`; file/in-memory implementations do not yet expose reads. | Package creation must add a safe read method before including concept image or screenshot bytes. |
| Existing manifest | `record_export` already merges version parameters, source artifact id/key, reference trace metadata, and concept-only disclaimer. | Handoff manifest builder can reuse this provenance and make it stricter. |
| Reference trace | Phase 11 persists `reference_usage`, `rights_snapshot`, roles, included/omitted ids, and unsupported roles into version/artifact/job/export metadata. | Handoff packages can validate rights/source completeness from existing version parameters. |
| 3D screenshots | Phase 12 persists `preview_3d_screenshot` artifacts with shell, camera, warning ids, source artifact, dimensions, content type, and object key. | Handoff packages can include optional screenshot artifacts and warning evidence without re-rendering 3D. |
| Feature flag | `V2_ENHANCED_HANDOFF_PACKAGE_ENABLED` and `NEXT_PUBLIC_V2_ENHANCED_HANDOFF_PACKAGE_ENABLED` already exist and default off. | API and UI can stay disabled by default while tests enable the flag. |
| Web export UI | Existing export panel creates PNG/JPG concept export records and previews manifest fields. | Phase 13 should evolve this panel into an export mode/package preview/history surface. |

## Recommended Architecture

Use a narrow package builder that is deterministic and provider-off:

1. Resolve selected version, required concept image artifact, optional screenshot artifacts, job model runs, and current exports.
2. Validate workspace/version ownership and rights/source snapshots.
3. Build a typed `HandoffPackageManifest` with schema version 1.
4. Render Markdown notes, warning report, prompt trace, and reference manifest from the same typed data.
5. Read required/optional artifact bytes from object storage.
6. Write a ZIP to object storage as an immutable `ArtifactKind.EXPORT` artifact.
7. Record an export row with `format: "enhanced_concept_handoff_zip"`, `status: "succeeded"`, package artifact id, manifest, and completed timestamp.
8. Return the same `ExportResponse` shape through existing list/create exports endpoints.

The first implementation can run synchronously in the API route because package construction is local, small, and deterministic in MVP. If ZIP generation grows expensive later, move it behind the worker using the same ledger contract.

## Manifest Shape

Candidate top-level JSON:

```json
{
  "schema_version": 1,
  "package_type": "enhanced_concept_handoff",
  "format": "enhanced_concept_handoff_zip",
  "disclaimer": "Concept handoff package for review only. Not print-ready production artwork.",
  "workspace_id": "...",
  "version_id": "...",
  "brief_id": "...",
  "parent_version_id": null,
  "source_artifact": {
    "id": "...",
    "object_key": "workspaces/.../concept.png",
    "content_type": "image/png",
    "byte_size": 123,
    "checksum_sha256": "...",
    "width": 1536,
    "height": 768"
  },
  "package_artifact": {
    "object_key": "workspaces/.../export/.../concept-handoff.zip",
    "content_type": "application/zip"
  },
  "files": [
    {"path": "manifest.json", "kind": "manifest", "required": true},
    {"path": "handoff-notes.md", "kind": "notes", "required": true}
  ],
  "template": {"id": "generic-side-coupe", "view": "side", "safe_zones": []},
  "warnings": {"items": [], "blocked": [], "optional_missing": []},
  "prompt_trace": {"summary": "...", "model_run_ids": []},
  "provider_trace": {"provider": "local-simulation", "model": "local-concept-v1"},
  "references": {"included_reference_asset_ids": [], "rights_snapshot": {}},
  "preview_3d": {"screenshots": [], "warning_ids": []},
  "review_notes": []
}
```

Tests should assert shape and required keys without depending on timestamp ordering beyond stable presence.

## ZIP Strategy

Python standard library `zipfile` is sufficient. Build bytes in memory with `io.BytesIO` and write deterministic names:

- `manifest.json`
- `handoff-notes.md`
- `warnings.md`
- `prompt-trace.md`
- `references.json`
- `images/concept.<extension>`
- `screenshots/<artifact-id>.<extension>` for optional screenshots

Use `ZIP_DEFLATED`. For deterministic tests, inspect `ZipFile.namelist()` and JSON payloads rather than byte-for-byte ZIP equality.

## Rights And Safety Strategy

Block package creation when:

- Enhanced handoff feature flag is off.
- Selected version does not belong to workspace.
- Required source artifact is missing, does not belong to selected version/workspace, or cannot be read from object storage.
- Required reference usage identifies included references but rights/source snapshot is absent, missing `rights_status: confirmed`, missing both `source_label` and `source_url`, or has rejected rights.
- Manifest/notes would include forbidden tokens such as `api_key`, `secret`, `image_base64`, local Windows paths, or raw bytes.

Warn, but do not block, when:

- No Phase 12 3D screenshots exist.
- PreviewSpec has warning items.
- Unsupported reference roles or omitted references are present.
- Preview3D includes concept-only/UV-not-verified warnings.

## UI Strategy

Extend `ExportPanel`:

- Add a compact mode switch for `PNG`, `JPG`, and `ZIP`.
- Use `FileArchive`, `Download`, `FileJson`, `ShieldAlert`, and similar lucide icons.
- Show package readiness rows for concept image, references, 3D screenshots, warnings, and notes.
- Disable the ZIP action when browser public flag is off or blocking readiness is present.
- Keep existing export history but visibly distinguish `ZIP` package exports from PNG/JPG records.
- Do not create nested cards inside cards; existing compact bordered operational rows are acceptable.

## Validation Matrix

| Requirement | Validation |
|-------------|------------|
| V2-HANDOFF-01 | API/web tests create enhanced ZIP export for selected version. |
| V2-HANDOFF-02 | Manifest/ZIP tests assert concept image, optional screenshots, safe-zone/warning report, prompt/provider trace, template metadata, references, and disclaimer. |
| V2-HANDOFF-03 | ZIP inspection tests assert stable `manifest.json` and Markdown notes. |
| V2-HANDOFF-04 | Core/API tests assert immutable package artifact and export rows do not overwrite prior exports. |
| V2-HANDOFF-05 | Core/API/web tests assert missing rights/source metadata blocks or warns safely. |

## Risks And Mitigations

| Risk | Mitigation |
|------|------------|
| Package implies print-ready production handoff | Persistent concept-only disclaimer in manifest, notes, UI, docs, and tests. |
| Manifest leaks secrets or binary payloads | Sanitization assertions over manifest/notes and explicit forbidden-token tests. |
| ZIP cannot include source bytes because storage is write-only | Add `get_object` to storage protocol and implementations in the first plan. |
| Export route becomes slow | Keep MVP package small; document worker migration if package grows. |
| Rights guard blocks too much | Only block missing/rejected required reference rights; optional 3D screenshot absence remains a warning. |

## RESEARCH COMPLETE
