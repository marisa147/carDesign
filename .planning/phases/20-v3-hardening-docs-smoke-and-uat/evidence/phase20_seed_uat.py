from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from uuid import UUID

from caragent_core.database import create_engine, create_session_factory, session_scope
from caragent_core.enums import (
    ArtifactKind,
    AssetKind,
    DesignVersionStatus,
    ExportStatus,
    FeedbackApprovalState,
    JobStatus,
    ModelRunStatus,
    RightsStatus,
)
from caragent_core.generation.templates import resolve_vehicle_template
from caragent_core.models import Asset, metadata
from caragent_core.production_preflight import (
    build_production_readiness_preflight_report,
    build_template_validation_report,
)
from caragent_core.services import jobs, workspaces


async def main() -> None:
    args = parse_args()
    db_path = sqlite_path_from_url(args.database_url)
    if db_path is not None and db_path.exists():
        db_path.unlink()

    engine = create_engine(args.database_url)
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)

    session_factory = create_session_factory(engine)
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(
            session,
            title="Phase 20 V3 UAT workspace",
        )
        user_message = await workspaces.create_message(
            session,
            workspace.id,
            role="user",
            content="白色厢式车，蓝紫电音角色，侧面大面积痛车，验证 V3 模板和生产预检。",
        )
        await workspaces.create_message(
            session,
            workspace.id,
            role="assistant",
            content="结构化 brief 已保存，使用 generic_van_side_v1 进行概念验证。",
        )

        reference_id = "11111111-1111-1111-1111-111111111111"
        missing_reference_id = "22222222-2222-2222-2222-222222222222"
        add_asset(
            workspace_id=workspace.id,
            asset_id=UUID(reference_id),
            filename="phase20-reference.png",
            rights_status=RightsStatus.CONFIRMED.value,
            source_label="Phase 20 seeded reference",
        )
        add_asset(
            workspace_id=workspace.id,
            asset_id=UUID(missing_reference_id),
            filename="phase20-missing-rights.png",
            rights_status=RightsStatus.MISSING.value,
            source_label=None,
        )
        session.add_all(add_asset.assets)

        template = resolve_vehicle_template(vehicle_template_id="generic_van_side_v1")
        preview_spec = {
            "canvas": {"height": 768, "width": 1536},
            "overlay_layers": [
                {
                    "id": "text-1",
                    "kind": "text",
                    "text": "ELECTRIC VAN",
                    "zone_id": template.safe_zones[0]["id"],
                },
                {
                    "asset_id": "logo-1",
                    "id": "logo-1",
                    "kind": "logo",
                    "zone_id": template.safe_zones[-1]["id"],
                },
            ],
            "safe_zones": [
                {
                    "height": zone["height"],
                    "id": zone["id"],
                    "kind": zone["kind"],
                    "label": zone["label"],
                    "width": zone["width"],
                    "x": zone["x"],
                    "y": zone["y"],
                }
                for zone in template.safe_zones[:3]
            ],
            "template": {
                "id": template.template_id,
                "label": template.template_label,
                "readiness": {"catalog_eligible": template.template_readiness.catalog_eligible},
                "source": {
                    "license_status": template.template_source.license_status,
                    "source_type": template.template_source.source_type,
                },
                "view": template.view,
            },
            "warnings": [
                {
                    "id": "non_production_template",
                    "message": "MVP generic van template is concept-only and not production scale evidence.",
                    "severity": "warning",
                }
            ],
        }
        rights_snapshot = {
            reference_id: {
                "asset_id": reference_id,
                "rights_status": "confirmed",
                "source_label": "Phase 20 seeded reference",
                "source_url": None,
            },
            missing_reference_id: {
                "asset_id": missing_reference_id,
                "rights_status": "missing",
                "source_label": None,
                "source_url": None,
            },
        }
        parameters = {
            "character_focus": "door heroine with rear quarter mascot",
            "character_theme": "electric idol heroine",
            "color_harmony": "white base with blue and violet accents",
            "concept_label": "phase20_v3_uat",
            "coverage": "large side coverage",
            "included_reference_asset_ids": [reference_id],
            "omitted_reference_asset_ids": [missing_reference_id],
            "palette": ["white", "blue", "violet"],
            "preview_spec": preview_spec,
            "reference_roles": {"character": [reference_id], "style": [missing_reference_id]},
            "reference_warning_count": 1,
            "rights_snapshot": rights_snapshot,
            "style": "clean cyber itasha",
            "text": ["ELECTRIC VAN"],
            "unsupported_reference_roles": ["style"],
            "vehicle_template_id": template.template_id,
            "vehicle_template": preview_spec["template"],
            "view": "side",
        }
        brief = await workspaces.create_design_brief(
            session,
            workspace.id,
            payload=parameters,
            source_message_id=user_message.id,
            title="Phase 20 V3 UAT brief",
        )
        created = await jobs.create_job(
            session,
            workspace.id,
            brief_id=brief.id,
            idempotency_key="phase20-v3-uat",
            metadata={"stage": "seed", "template": {"id": template.template_id, "view": template.view}},
            operation="generate_2d_concept",
            provider="local-deterministic",
            requested_by="phase20-uat",
        )
        await jobs.transition_job_status(
            session,
            created.job.id,
            status=JobStatus.RUNNING.value,
            message="Phase 20 UAT fixture generation started.",
            source="phase20-seed",
        )
        await jobs.transition_job_status(
            session,
            created.job.id,
            status=JobStatus.SUCCEEDED.value,
            message="Phase 20 UAT fixture generation completed.",
            metadata={"external_calls": False, "stage": "seed", "template": {"id": template.template_id}},
            source="phase20-seed",
        )
        version = await jobs.create_design_version(
            session,
            workspace.id,
            brief_id=brief.id,
            job_id=created.job.id,
            parameters=parameters,
            status=DesignVersionStatus.GENERATED.value,
            summary="Phase 20 V3 concept preview with template, handoff, and preflight evidence.",
            title="Phase 20 V3 UAT ready version",
        )
        concept = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=2048,
            checksum_sha256="a" * 64,
            content_type="image/png",
            height=768,
            job_id=created.job.id,
            kind=ArtifactKind.GENERATED_IMAGE.value,
            metadata={"concept_label": "phase20_v3_uat", "preview_spec": preview_spec},
            object_key=f"workspaces/{workspace.id}/generated_image/phase20/concept.png",
            version_id=version.id,
            width=1536,
        )
        await jobs.create_model_run(
            session,
            created.job.id,
            input_artifact_ids=[reference_id],
            model="local-concept-v1",
            output_artifact_id=concept.id,
            parameters={"external_calls": False, "vehicle_template": {"id": template.template_id}},
            prompt_payload={"preview_spec": preview_spec, "vehicle_template_id": template.template_id},
            prompt_text="Phase 20 V3 UAT prompt for a generic van side-view itasha concept.",
            provider="local-deterministic",
            status=ModelRunStatus.SUCCEEDED.value,
        )
        await jobs.record_feedback(
            session,
            workspace.id,
            version.id,
            approval_state=FeedbackApprovalState.APPROVED.value,
            comment="Phase 20 UAT concept accepted for release evidence.",
            rating=5,
        )
        await jobs.record_export(
            session,
            workspace.id,
            version.id,
            artifact_id=concept.id,
            concept_label="phase20-v3-png",
            export_format="png",
            manifest={"requested_by": "phase20-uat"},
            status=ExportStatus.SUCCEEDED.value,
        )

        preflight = build_production_readiness_preflight_report(
            source_artifact=concept,
            version=version,
        )
        preflight_artifact = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=4096,
            checksum_sha256="b" * 64,
            content_type="application/json",
            job_id=created.job.id,
            kind=ArtifactKind.EXPORT.value,
            object_key=f"workspaces/{workspace.id}/export/phase20/production-readiness-preflight.json",
            version_id=version.id,
        )
        await jobs.record_export(
            session,
            workspace.id,
            version.id,
            artifact_id=preflight_artifact.id,
            concept_label="production-readiness-preflight",
            export_format="production_readiness_preflight",
            manifest={"production_readiness_preflight": preflight.model_dump(mode="json")},
            status=ExportStatus.SUCCEEDED.value,
        )

        handoff_artifact = await jobs.create_artifact(
            session,
            workspace.id,
            byte_size=8192,
            checksum_sha256="c" * 64,
            content_type="application/zip",
            job_id=created.job.id,
            kind=ArtifactKind.EXPORT.value,
            object_key=f"workspaces/{workspace.id}/export/phase20/enhanced-concept-handoff.zip",
            version_id=version.id,
        )
        template_validation = build_template_validation_report(parameters)
        handoff_files = [
            {"kind": "manifest", "path": "manifest.json"},
            {"kind": "notes", "path": "handoff-notes.md"},
            {"kind": "warnings", "path": "warnings.md"},
            {
                "kind": "production_readiness_preflight",
                "path": "production-readiness-preflight.json",
            },
            {"kind": "template_validation", "path": "template-validation.json"},
            {"kind": "prompt_trace", "path": "prompt-trace.md"},
            {"kind": "references", "path": "references.json"},
            {"kind": "concept_image", "path": "images/concept.png"},
        ]
        await jobs.record_export(
            session,
            workspace.id,
            version.id,
            artifact_id=handoff_artifact.id,
            concept_label="phase20-v3-handoff",
            export_format="enhanced_concept_handoff_zip",
            manifest={
                "files": handoff_files,
                "format": "enhanced_concept_handoff_zip",
                "production_readiness_preflight": preflight.model_dump(mode="json"),
                "template_validation": template_validation.model_dump(mode="json"),
            },
            status=ExportStatus.SUCCEEDED.value,
        )

    payload = {
        "artifact_id": str(concept.id),
        "brief_id": str(brief.id),
        "external_calls": False,
        "job_id": str(created.job.id),
        "template_id": template.template_id,
        "version_id": str(version.id),
        "workspace_id": str(workspace.id),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    await engine.dispose()


def add_asset(
    *,
    workspace_id: UUID,
    asset_id: UUID,
    filename: str,
    rights_status: str,
    source_label: str | None,
) -> Asset:
    asset = Asset(
        byte_size=256,
        checksum_sha256="d" * 64,
        content_type="image/png",
        id=asset_id,
        kind=AssetKind.REFERENCE.value,
        object_key=f"workspaces/{workspace_id}/reference/{asset_id}/{filename}",
        original_filename=filename,
        rights_status=rights_status,
        source_label=source_label,
        workspace_id=workspace_id,
    )
    add_asset.assets.append(asset)
    return asset


add_asset.assets: list[Asset] = []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def sqlite_path_from_url(database_url: str) -> Path | None:
    prefix = "sqlite+aiosqlite:///"
    if not database_url.startswith(prefix):
        return None
    return Path(database_url.removeprefix(prefix))


if __name__ == "__main__":
    asyncio.run(main())
