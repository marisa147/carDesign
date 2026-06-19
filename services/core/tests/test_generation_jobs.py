from __future__ import annotations

import json
from collections.abc import AsyncIterator
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from caragent_core.database import create_engine, create_session_factory, session_scope
from caragent_core.enums import ArtifactKind, ModelRunStatus
from caragent_core.models import metadata
from caragent_core.preview3d import (
    GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL_ID,
    Preview3DScreenshotArtifactMetadata,
    Preview3DSpec,
    build_preview_3d_spec,
)
from caragent_core.services import jobs, workspaces


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)

    yield create_session_factory(engine)

    await engine.dispose()


async def test_model_run_completion_helpers_store_output_and_timestamps(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Generation")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="generation-001",
            operation="generate_2d_concept",
        )
        model_run = await jobs.create_model_run(
            session,
            created.job.id,
            model="local-concept-v1",
            provider="local-deterministic",
            status=ModelRunStatus.RUNNING.value,
        )
        artifact = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=512,
            checksum_sha256="a" * 64,
            content_type="image/png",
            height=768,
            job_id=created.job.id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace.id}/generated/concept.png",
            width=1536,
        )

        completed = await jobs.complete_model_run(
            session,
            model_run.id,
            actual_cost=Decimal("0.0000"),
            output_artifact_id=artifact.id,
        )

    assert completed.status == ModelRunStatus.SUCCEEDED.value
    assert completed.output_artifact_id == artifact.id
    assert completed.actual_cost == Decimal("0.0000")
    assert completed.completed_at is not None
    assert completed.error_message is None


async def test_model_run_failure_helper_sanitizes_error_text(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Generation")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="generation-002",
            operation="generate_2d_concept",
        )
        model_run = await jobs.create_model_run(
            session,
            created.job.id,
            model="local-concept-v1",
            provider="local-deterministic",
            status=ModelRunStatus.RUNNING.value,
        )

        failed = await jobs.fail_model_run(
            session,
            model_run.id,
            error_message="provider-secret\nfailed",
            secrets=["provider-secret"],
        )

    assert failed.status == ModelRunStatus.FAILED.value
    assert failed.completed_at is not None
    assert failed.error_message == "[redacted] failed"
    assert "provider-secret" not in failed.error_message


async def test_mask_artifact_metadata_can_be_stored_without_binary_payload(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Targeted edit")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="targeted-edit-001",
            operation="generate_2d_concept",
            metadata={
                "edit_intent": {
                    "mode": "targeted_edit",
                    "route_preference": "deterministic_recomposition",
                    "schema_version": 1,
                },
            },
        )
        artifact = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=256,
            content_type="image/png",
            height=768,
            job_id=created.job.id,
            kind="mask",
            metadata={
                "edit_region": {
                    "height": 0.2,
                    "type": "rectangle",
                    "unit": "normalized",
                    "width": 0.4,
                    "x": 0.2,
                    "y": 0.35,
                },
                "parent_version_id": "22222222-2222-2222-2222-222222222222",
                "target": {"id": "door-main", "type": "safe_zone"},
            },
            object_key=f"workspaces/{workspace.id}/masks/door-main.png",
            width=1536,
        )

    assert artifact.kind == "mask"
    assert artifact.metadata_json["target"] == {"id": "door-main", "type": "safe_zone"}
    assert "mask_bytes" not in artifact.metadata_json


async def test_preview_3d_screenshot_artifact_metadata_can_be_stored_without_binary_payload(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="3D preview")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="preview-3d-001",
            operation="generate_2d_concept",
        )
        version = await jobs.create_design_version(
            session,
            workspace.id,
            job_id=created.job.id,
            parameters={"preview_3d": preview_3d_spec().model_dump(mode="json")},
            title="3D source concept",
        )
        metadata_payload = preview_3d_screenshot_metadata().model_dump(mode="json")
        artifact = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=1024,
            checksum_sha256="b" * 64,
            content_type="image/png",
            height=720,
            job_id=created.job.id,
            kind=ArtifactKind.PREVIEW_3D_SCREENSHOT.value,
            metadata=metadata_payload,
            object_key=f"workspaces/{workspace.id}/preview_3d_screenshot/{version.id}/capture.png",
            version_id=version.id,
            width=1280,
        )

    assert artifact.kind == "preview_3d_screenshot"
    assert artifact.version_id == version.id
    assert artifact.metadata_json["preview_3d_screenshot"]["shell_id"] == (
        "generic-side-coupe-lightweight-v1"
    )
    rendered = str(artifact.metadata_json).lower()
    assert "base64" not in rendered
    assert "image_bytes" not in rendered
    assert "binary" not in rendered


def test_preview_3d_resolver_links_generic_side_coupe_shell() -> None:
    spec = build_preview_3d_spec(
        artifact_id="33333333-3333-3333-3333-333333333333",
        artifact_object_key="workspaces/ws/generated_image/artifact/concept.png",
        preview_spec=preview_spec_payload(),
        version_id="22222222-2222-2222-2222-222222222222",
        workspace_id="11111111-1111-1111-1111-111111111111",
    )

    assert spec.compatibility.status == "compatible"
    assert spec.compatibility.shell_id == GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL_ID
    assert spec.shell is not None
    assert spec.shell.id == GENERIC_SIDE_COUPE_LIGHTWEIGHT_SHELL_ID
    assert spec.shell.template_id == "generic-side-coupe"
    assert "side-decal-plane" in spec.shell.material_slots
    assert spec.camera.preset_id == "front-left-default"
    assert spec.source.preview_spec_template_id == "generic-side-coupe"
    assert spec.source.preview_spec_view == "side"
    assert str(spec.source.artifact_id) == "33333333-3333-3333-3333-333333333333"
    assert spec.materials.source_kind == "preview_spec"
    assert spec.materials.safe_zone_overlays[0]["id"] == "door-main"
    assert spec.materials.safe_zone_overlays[0]["slot"] == "side-decal-plane"
    assert spec.materials.overlay_layers[0]["id"] == "text-1"
    assert spec.materials.overlay_layers[0]["slot"] == "side-decal-plane"
    assert [warning.id for warning in spec.warnings] == [
        "non_production_preview",
        "uv_not_verified",
        "single_shell_fixture",
    ]


def test_preview_3d_resolver_returns_explicit_fallback_for_unknown_template() -> None:
    spec = build_preview_3d_spec(
        artifact_id="33333333-3333-3333-3333-333333333333",
        artifact_object_key="workspaces/ws/generated_image/artifact/concept.png",
        preview_spec=preview_spec_payload(template_id="unknown-template"),
        version_id="22222222-2222-2222-2222-222222222222",
        workspace_id="11111111-1111-1111-1111-111111111111",
    )

    assert spec.compatibility.status == "incompatible"
    assert spec.compatibility.shell_id is None
    assert spec.compatibility.reason is not None
    assert "unknown-template" in spec.compatibility.reason
    assert spec.shell is None
    assert spec.source.preview_spec_template_id == "unknown-template"
    assert spec.materials.safe_zone_overlays[0]["id"] == "door-main"
    assert spec.warnings[0].id == "non_production_preview"


async def test_phase_13_handoff_report_helpers_render_safe_metadata(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    from caragent_core.handoff import (
        build_handoff_reference_manifest,
        build_handoff_warning_report,
        render_handoff_notes_markdown,
        render_handoff_prompt_trace_markdown,
        render_handoff_references_json,
        render_handoff_warnings_markdown,
    )

    reference_asset_id = "66666666-6666-6666-6666-666666666666"
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Handoff reports")
        created = await jobs.create_job(
            session,
            workspace.id,
            idempotency_key="handoff-reports-001",
            operation="generate_2d_concept",
        )
        source_artifact = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=1024,
            checksum_sha256="a" * 64,
            content_type="image/png",
            height=768,
            job_id=created.job.id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            object_key=f"workspaces/{workspace.id}/generated/concept.png",
            width=1536,
        )
        version = await jobs.create_design_version(
            session,
            workspace.id,
            job_id=created.job.id,
            parameters={
                "included_reference_asset_ids": [reference_asset_id],
                "omitted_reference_asset_ids": ["77777777-7777-7777-7777-777777777777"],
                "preview_3d": preview_3d_spec().model_dump(mode="json"),
                "preview_spec": preview_spec_payload(),
                "reference_roles": {"character": [reference_asset_id]},
                "reference_warning_count": 1,
                "rights_snapshot": {
                    reference_asset_id: {
                        "rights_status": "confirmed",
                        "source_label": "User upload",
                    },
                },
                "unsupported_reference_roles": ["vehicle"],
            },
            title="Handoff report source",
        )
        model_run = await jobs.create_model_run(
            session,
            created.job.id,
            actual_cost=Decimal("0.0000"),
            estimated_cost=Decimal("0.0000"),
            input_artifact_ids=[reference_asset_id],
            model="local-concept-v1",
            output_artifact_id=source_artifact.id,
            prompt_text="Moon drive prompt api_key=secret image_base64 C:\\tmp\\concept.png",
            provider="local-simulation",
            status=ModelRunStatus.SUCCEEDED.value,
        )

        warning_report = build_handoff_warning_report(
            preview_3d=version.parameters["preview_3d"],
            preview_3d_screenshot={"warning_ids": ["non_production_preview", "uv_not_verified"]},
            preview_spec=version.parameters["preview_spec"],
        )
        reference_manifest = build_handoff_reference_manifest(version.parameters)
        notes_markdown = render_handoff_notes_markdown(
            references=reference_manifest,
            review_notes=["Approved for concept discussion."],
            safe_zones=version.parameters["preview_spec"]["safe_zones"],
            template=version.parameters["preview_spec"]["template"],
            warnings=warning_report,
        )
        warnings_markdown = render_handoff_warnings_markdown(warning_report)
        prompt_markdown = render_handoff_prompt_trace_markdown(model_runs=[model_run])
        references_json = render_handoff_references_json(reference_manifest)

    assert notes_markdown.startswith("# Concept Handoff Notes")
    assert warnings_markdown.startswith("# Warning Report")
    assert prompt_markdown.startswith("# Prompt Trace")
    assert "Concept handoff package for review only" in notes_markdown
    assert "door-main" in notes_markdown
    assert "non_production_preview" in warnings_markdown
    assert "uv_not_verified" in warnings_markdown
    assert reference_asset_id in references_json
    assert "local-simulation" in prompt_markdown
    assert "local-concept-v1" in prompt_markdown
    assert json.loads(references_json)["schema_version"] == 1

    rendered = "\n".join(
        [notes_markdown, warnings_markdown, prompt_markdown, references_json],
    ).lower()
    assert "api_key" not in rendered
    assert "secret" not in rendered
    assert "image_base64" not in rendered
    assert "c:\\" not in rendered


def preview_3d_spec() -> Preview3DSpec:
    return Preview3DSpec.model_validate(
        {
            "camera": {
                "preset_id": "front-left-default",
                "position": {"x": 2.8, "y": 1.4, "z": 4.2},
                "target": {"x": 0.0, "y": 0.4, "z": 0.0},
                "zoom": 1.0,
            },
            "compatibility": {
                "shell_id": "generic-side-coupe-lightweight-v1",
                "status": "compatible",
            },
            "materials": {
                "decal_strategy": "preview_spec_projection",
                "overlay_layers": [
                    {"id": "text-1", "slot": "side-decal-plane", "text": "MOON DRIVE"},
                ],
                "safe_zone_overlays": [
                    {
                        "height": 0.24,
                        "id": "door-main",
                        "slot": "side-decal-plane",
                        "width": 0.34,
                        "x": 0.32,
                        "y": 0.47,
                    },
                ],
                "source_artifact_id": "33333333-3333-3333-3333-333333333333",
                "source_kind": "preview_spec",
            },
            "mode": "lightweight_shell",
            "shell": {
                "dimensions": {"height": 1.4, "length": 4.4, "width": 1.8},
                "id": "generic-side-coupe-lightweight-v1",
                "label": "Generic side coupe lightweight shell",
                "material_slots": ["body", "side-decal-plane", "glass", "wheel"],
                "template_id": "generic-side-coupe",
            },
            "source": {
                "artifact_id": "33333333-3333-3333-3333-333333333333",
                "artifact_object_key": "workspaces/ws/generated_image/artifact/concept.png",
                "preview_spec_template_id": "generic-side-coupe",
                "preview_spec_view": "side",
                "version_id": "22222222-2222-2222-2222-222222222222",
                "workspace_id": "11111111-1111-1111-1111-111111111111",
            },
        },
    )


def preview_spec_payload(template_id: str = "generic-side-coupe") -> dict[str, object]:
    return {
        "canvas": {"height": 768, "width": 1536},
        "overlay_layers": [
            {"id": "text-1", "kind": "text", "text": "MOON DRIVE", "zone_id": "door-main"},
            {"asset_id": "logo-1", "id": "logo-1", "kind": "logo", "zone_id": "rear-quarter"},
        ],
        "safe_zones": [
            {
                "height": 0.24,
                "id": "door-main",
                "kind": "body",
                "label": "Door / main side panel",
                "width": 0.34,
                "x": 0.32,
                "y": 0.47,
            },
            {
                "height": 0.2,
                "id": "rear-quarter",
                "kind": "body",
                "label": "Rear quarter panel",
                "width": 0.18,
                "x": 0.64,
                "y": 0.43,
            },
        ],
        "template": {
            "id": template_id,
            "label": "Generic side-view coupe",
            "view": "side",
        },
    }


def preview_3d_screenshot_metadata() -> Preview3DScreenshotArtifactMetadata:
    spec = preview_3d_spec()
    dumped = spec.model_dump(mode="json")
    return Preview3DScreenshotArtifactMetadata.model_validate(
        {
            "preview_3d_screenshot": {
                "camera": dumped["camera"],
                "preview_3d": dumped,
                "shell_id": "generic-side-coupe-lightweight-v1",
                "source_artifact_id": "33333333-3333-3333-3333-333333333333",
                "warning_ids": ["non_production_preview", "uv_not_verified"],
            },
        },
    )
