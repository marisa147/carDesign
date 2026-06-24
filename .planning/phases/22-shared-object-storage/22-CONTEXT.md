---
phase: 22
name: shared-object-storage
status: planned
created: 2026-06-22
requirements:
  - STOR-01
  - STOR-02
  - STOR-03
  - STOR-04
---

# Phase 22 Context

## Goal

Remove the API/Worker object storage split so uploads and generated artifacts use one shared storage protocol, one settings shape, and deterministic content reads.

## Requirements

- **STOR-01:** API and Worker use one shared object storage factory and compatible settings for local and S3-compatible modes.
- **STOR-02:** Local file storage preserves object content type and metadata needed for later reads.
- **STOR-03:** API can stream an artifact only after validating the artifact belongs to the requested workspace.
- **STOR-04:** Storage contract tests prove API uploads and Worker outputs can be read back through the same object key.

## Existing Evidence

- `caragent_core.storage` already owns `ObjectStorage`, `FileObjectStorage`, `InMemoryObjectStorage`, object key helpers, and upload validation.
- API startup now wires `app.state.object_storage` through `ObjectStorageFactory.from_settings()`.
- Worker generation now receives storage from `ObjectStorageFactory.from_settings(settings)`.
- Phase 21 introduced workspace-scoped artifact content streaming, so STOR-03 has a direct API regression target.

## Main Gap

The local file path and metadata work was mostly present, but S3-compatible mode still raised `NotImplementedError`. Phase 22 closes that by adding a client-backed `S3ObjectStorage` adapter with injectable fake-client contract tests and dynamic boto3 loading for real runtimes.

## Out Of Scope

- Queue dispatch outbox and worker short transactions remain Phase 23.
- 3D screenshot validation and parameter clearing remain Phase 24.
- Redis-backed quota settlement and auth hardening remain Phase 26.
