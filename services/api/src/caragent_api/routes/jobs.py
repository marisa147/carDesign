from __future__ import annotations

import base64
import binascii
import hashlib
import json
import struct
import zipfile
from html import escape
from io import BytesIO
from typing import Annotated
from uuid import UUID, uuid4

from caragent_core.enums import ArtifactKind, ExportStatus
from caragent_core.generation.templates import resolve_vehicle_template
from caragent_core.handoff import (
    ENHANCED_HANDOFF_PACKAGE_FORMAT,
    HandoffPackageBuildError,
    HandoffPackageZipResult,
    build_handoff_package_zip,
)
from caragent_core.models import Artifact, DesignVersion, ExportRecord, GenerationJob
from caragent_core.preview3d import (
    Preview3DScreenshotArtifactMetadata,
    required_preview_3d_warning_ids,
)
from caragent_core.production_preflight import (
    PRODUCTION_PREFLIGHT_FORMAT,
    build_production_readiness_preflight_report,
)
from caragent_core.services import jobs, workspaces
from caragent_core.services.jobs import CONSTRUCTION_PACKAGE_FORMAT
from caragent_core.storage import ObjectStorage, build_object_key, validate_upload
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_api.config import ApiSettings
from caragent_api.dependencies import (
    CurrentUser,
    CurrentUserDependency,
    OwnedWorkspaceDependency,
    SessionDependency,
    get_object_storage,
    get_queue_client,
    require_workspace_owner,
)
from caragent_api.queue import QueueClient
from caragent_api.schemas import (
    ArtifactResponse,
    DesignVersionResponse,
    ExportCreateRequest,
    ExportResponse,
    FeedbackCreateRequest,
    FeedbackResponse,
    GenerationJobCancelRequest,
    GenerationJobCancelResponse,
    GenerationJobResponse,
    JobCreateRequest,
    JobCreateResponse,
    JobEventResponse,
    ModelRunResponse,
    Preview3DScreenshotCreateRequest,
    ProductionReadinessPreflightResponse,
    QueueRevokeResponse,
)

router = APIRouter(tags=["jobs"])

QueueDependency = Annotated[QueueClient, Depends(get_queue_client)]
StorageDependency = Annotated[ObjectStorage, Depends(get_object_storage)]

SCREENSHOT_CONTENT_TYPES = {"image/png", "image/webp"}
MAX_PREVIEW_3D_SCREENSHOT_BYTES = 5 * 1024 * 1024


def workspace_not_found(error: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workspace not found")


def job_not_found(error: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="job not found")


def job_validation_failed(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=str(error),
    )


def create_response(result: jobs.JobCreationResult) -> JobCreateResponse:
    payload = GenerationJobResponse.model_validate(result.job).model_dump()
    return JobCreateResponse(**payload, idempotent_reused=result.idempotent_reused)


def _artifact_response(artifact: Artifact) -> ArtifactResponse:
    response = ArtifactResponse.model_validate(artifact)
    return response.model_copy(
        update={
            "content_url": (f"/workspaces/{artifact.workspace_id}/artifacts/{artifact.id}/content"),
        },
    )


async def _get_owned_job(
    session: AsyncSession,
    job_id: UUID,
    current_user: CurrentUser,
) -> GenerationJob:
    try:
        job = await jobs.get_job(session, job_id)
    except jobs.JobNotFoundError as error:
        raise job_not_found(error) from error
    try:
        workspace = await workspaces.get_workspace(session, job.workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    require_workspace_owner(workspace, current_user)
    return job


@router.post(
    "/workspaces/{workspace_id}/jobs",
    response_model=JobCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_job(
    workspace_id: UUID,
    payload: JobCreateRequest,
    session: SessionDependency,
    current_user: CurrentUserDependency,
    _workspace: OwnedWorkspaceDependency,
) -> JobCreateResponse:
    try:
        result = await jobs.create_job(
            session,
            workspace_id,
            brief_id=payload.brief_id,
            estimated_cost=payload.estimated_cost,
            idempotency_key=payload.idempotency_key,
            metadata=payload.metadata,
            model=payload.model,
            operation=payload.operation,
            provider=payload.provider,
            requested_by=current_user.id,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except jobs.JobValidationError as error:
        raise job_validation_failed(error) from error
    return create_response(result)


@router.get("/workspaces/{workspace_id}/jobs", response_model=list[GenerationJobResponse])
async def list_jobs(
    workspace_id: UUID,
    session: SessionDependency,
    _workspace: OwnedWorkspaceDependency,
) -> list[GenerationJobResponse]:
    try:
        job_rows = await jobs.list_workspace_jobs(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [GenerationJobResponse.model_validate(job) for job in job_rows]


@router.get("/jobs/{job_id}", response_model=GenerationJobResponse)
async def get_job(
    job_id: UUID,
    session: SessionDependency,
    current_user: CurrentUserDependency,
) -> GenerationJobResponse:
    job = await _get_owned_job(session, job_id, current_user)
    return GenerationJobResponse.model_validate(job)


@router.post("/jobs/{job_id}/cancel", response_model=GenerationJobCancelResponse)
async def cancel_job(
    job_id: UUID,
    payload: GenerationJobCancelRequest,
    session: SessionDependency,
    queue: QueueDependency,
    current_user: CurrentUserDependency,
) -> GenerationJobCancelResponse:
    try:
        existing = await _get_owned_job(session, job_id, current_user)
        task_id = _extract_queue_task_id(existing.metadata_json)
        canceled = await jobs.cancel_job(
            session,
            job_id,
            reason=payload.reason,
            requested_by=current_user.id,
            source="api",
        )
    except jobs.JobNotFoundError as error:
        raise job_not_found(error) from error
    except jobs.JobValidationError as error:
        raise job_validation_failed(error) from error

    try:
        revoke_result = await queue.revoke_generation_task(task_id)
        queue_revoke = QueueRevokeResponse.model_validate(revoke_result)
    except Exception:
        queue_revoke = QueueRevokeResponse(
            detail="Queue revoke failed.",
            status="failed",
            task_id=task_id,
        )

    return GenerationJobCancelResponse(
        job=GenerationJobResponse.model_validate(canceled),
        queue_revoke=queue_revoke,
    )


@router.get("/jobs/{job_id}/events", response_model=list[JobEventResponse])
async def list_events(
    job_id: UUID,
    session: SessionDependency,
    current_user: CurrentUserDependency,
) -> list[JobEventResponse]:
    await _get_owned_job(session, job_id, current_user)
    try:
        event_rows = await jobs.list_job_events(session, job_id)
    except jobs.JobNotFoundError as error:
        raise job_not_found(error) from error
    return [JobEventResponse.model_validate(event) for event in event_rows]


@router.get("/workspaces/{workspace_id}/versions", response_model=list[DesignVersionResponse])
async def list_versions(
    workspace_id: UUID,
    session: SessionDependency,
    _workspace: OwnedWorkspaceDependency,
) -> list[DesignVersionResponse]:
    try:
        rows = await jobs.list_workspace_versions(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [DesignVersionResponse.model_validate(row) for row in rows]


@router.get("/workspaces/{workspace_id}/artifacts", response_model=list[ArtifactResponse])
async def list_artifacts(
    workspace_id: UUID,
    session: SessionDependency,
    _workspace: OwnedWorkspaceDependency,
) -> list[ArtifactResponse]:
    try:
        rows = await jobs.list_workspace_artifacts(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [_artifact_response(row) for row in rows]


@router.get(
    "/workspaces/{workspace_id}/artifacts/{artifact_id}/content",
    response_class=Response,
    responses={
        status.HTTP_200_OK: {
            "content": {
                "application/octet-stream": {"schema": {"format": "binary", "type": "string"}},
                "image/png": {"schema": {"format": "binary", "type": "string"}},
                "image/webp": {"schema": {"format": "binary", "type": "string"}},
            },
            "description": "Artifact binary content.",
        },
    },
)
async def get_artifact_content(
    workspace_id: UUID,
    artifact_id: UUID,
    session: SessionDependency,
    storage: StorageDependency,
    _workspace: OwnedWorkspaceDependency,
) -> Response:
    artifact = await session.get(Artifact, artifact_id)
    if artifact is None or artifact.workspace_id != workspace_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="artifact not found",
        )

    try:
        stored = await storage.get_object(artifact.object_key)
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="artifact content not found",
        ) from error

    return Response(
        content=stored.content,
        media_type=artifact.content_type or stored.content_type or "application/octet-stream",
    )


@router.post(
    "/workspaces/{workspace_id}/versions/{version_id}/preview-3d-screenshots",
    response_model=ArtifactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_preview_3d_screenshot(
    workspace_id: UUID,
    version_id: UUID,
    payload: Preview3DScreenshotCreateRequest,
    request: Request,
    session: SessionDependency,
    storage: StorageDependency,
    _workspace: OwnedWorkspaceDependency,
) -> ArtifactResponse:
    settings = _settings_from_request(request)
    if not settings.v2_lightweight_3d_preview_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED is disabled.",
        )

    try:
        version = await jobs.get_workspace_version(session, workspace_id, version_id)
        await _validate_preview_3d_source_artifact(session, workspace_id, version_id, payload)
        screenshot_bytes = _decode_screenshot_bytes(payload.image_base64)
        _validate_screenshot_upload(payload, screenshot_bytes)
        metadata = _preview_3d_screenshot_metadata(payload)
        object_key = build_object_key(
            workspace_id=workspace_id,
            kind=ArtifactKind.PREVIEW_3D_SCREENSHOT.value,
            record_id=uuid4(),
            filename=payload.filename,
        )
        await storage.put_object(object_key, screenshot_bytes, payload.content_type)
        artifact = await jobs.create_artifact(
            session,
            workspace_id,
            byte_size=len(screenshot_bytes),
            checksum_sha256=hashlib.sha256(screenshot_bytes).hexdigest(),
            content_type=payload.content_type,
            height=payload.height,
            job_id=version.job_id,
            kind=ArtifactKind.PREVIEW_3D_SCREENSHOT.value,
            metadata=metadata.model_dump(mode="json"),
            object_key=object_key,
            version_id=version.id,
            width=payload.width,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except (ValueError, jobs.JobValidationError) as error:
        raise job_validation_failed(error) from error

    return _artifact_response(artifact)


@router.get("/jobs/{job_id}/model-runs", response_model=list[ModelRunResponse])
async def list_model_runs(
    job_id: UUID,
    session: SessionDependency,
    current_user: CurrentUserDependency,
) -> list[ModelRunResponse]:
    await _get_owned_job(session, job_id, current_user)
    try:
        rows = await jobs.list_job_model_runs(session, job_id)
    except jobs.JobNotFoundError as error:
        raise job_not_found(error) from error
    return [ModelRunResponse.model_validate(row) for row in rows]


@router.get("/workspaces/{workspace_id}/feedback", response_model=list[FeedbackResponse])
async def list_feedback(
    workspace_id: UUID,
    session: SessionDependency,
    _workspace: OwnedWorkspaceDependency,
) -> list[FeedbackResponse]:
    try:
        rows = await jobs.list_workspace_feedback(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [FeedbackResponse.model_validate(row) for row in rows]


@router.post(
    "/workspaces/{workspace_id}/versions/{version_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_feedback(
    workspace_id: UUID,
    version_id: UUID,
    payload: FeedbackCreateRequest,
    session: SessionDependency,
    _workspace: OwnedWorkspaceDependency,
) -> FeedbackResponse:
    try:
        row = await jobs.record_feedback(
            session,
            workspace_id,
            version_id,
            approval_state=payload.approval_state,
            comment=payload.comment,
            metadata=payload.metadata,
            rating=payload.rating,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except jobs.JobValidationError as error:
        raise job_validation_failed(error) from error
    return FeedbackResponse.model_validate(row)


@router.get("/workspaces/{workspace_id}/exports", response_model=list[ExportResponse])
async def list_exports(
    workspace_id: UUID,
    session: SessionDependency,
    _workspace: OwnedWorkspaceDependency,
) -> list[ExportResponse]:
    try:
        rows = await jobs.list_workspace_exports(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [ExportResponse.model_validate(row) for row in rows]


@router.post(
    "/workspaces/{workspace_id}/versions/{version_id}/exports",
    response_model=ExportResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_export(
    workspace_id: UUID,
    version_id: UUID,
    payload: ExportCreateRequest,
    request: Request,
    session: SessionDependency,
    storage: StorageDependency,
    _workspace: OwnedWorkspaceDependency,
) -> ExportResponse:
    normalized_format = payload.format.strip().lower()
    try:
        if normalized_format == CONSTRUCTION_PACKAGE_FORMAT:
            row = await _create_construction_package_export(
                workspace_id=workspace_id,
                version_id=version_id,
                payload=payload,
                session=session,
                storage=storage,
            )
        elif normalized_format == ENHANCED_HANDOFF_PACKAGE_FORMAT:
            row = await _create_enhanced_handoff_export(
                workspace_id=workspace_id,
                version_id=version_id,
                payload=payload,
                request=request,
                session=session,
                storage=storage,
            )
        else:
            row = await jobs.record_export(
                session,
                workspace_id,
                version_id,
                artifact_id=payload.artifact_id,
                concept_label=payload.concept_label,
                export_format=payload.format,
                manifest=payload.manifest,
            )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except (HandoffPackageBuildError, jobs.JobValidationError) as error:
        raise job_validation_failed(error) from error
    return ExportResponse.model_validate(row)


@router.post(
    "/workspaces/{workspace_id}/versions/{version_id}/production-readiness-preflight",
    response_model=ProductionReadinessPreflightResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_production_readiness_preflight(
    workspace_id: UUID,
    version_id: UUID,
    session: SessionDependency,
    storage: StorageDependency,
    _workspace: OwnedWorkspaceDependency,
) -> ProductionReadinessPreflightResponse:
    try:
        version = await jobs.get_workspace_version(session, workspace_id, version_id)
        source_artifact = await _resolve_optional_generated_image_artifact(
            session,
            workspace_id,
            version_id,
        )
        report = build_production_readiness_preflight_report(
            source_artifact=source_artifact,
            version=version,
        )
        report_json = json.dumps(
            report.model_dump(mode="json"),
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        object_key = build_object_key(
            workspace_id=workspace_id,
            kind=ArtifactKind.EXPORT.value,
            record_id=uuid4(),
            filename="production-readiness-preflight.json",
        )
        await storage.put_object(object_key, report_json, "application/json")
        report_artifact = await jobs.create_artifact(
            session,
            workspace_id,
            byte_size=len(report_json),
            checksum_sha256=hashlib.sha256(report_json).hexdigest(),
            content_type="application/json",
            job_id=version.job_id,
            kind=ArtifactKind.EXPORT.value,
            metadata={
                "production_readiness_preflight": {
                    "blockers": list(report.blockers),
                    "missing_evidence": list(report.missing_evidence),
                    "print_ready_allowed": report.print_ready_allowed,
                    "schema_version": report.schema_version,
                    "status": report.status,
                },
            },
            object_key=object_key,
            version_id=version.id,
        )
        export = await jobs.record_export(
            session,
            workspace_id,
            version_id,
            artifact_id=report_artifact.id,
            concept_label="production-readiness-preflight",
            export_format=PRODUCTION_PREFLIGHT_FORMAT,
            manifest={"production_readiness_preflight": report.model_dump(mode="json")},
            status=ExportStatus.SUCCEEDED.value,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except jobs.JobValidationError as error:
        raise job_validation_failed(error) from error
    return ProductionReadinessPreflightResponse(
        export=ExportResponse.model_validate(export),
        report=report,
    )


async def _create_construction_package_export(
    *,
    workspace_id: UUID,
    version_id: UUID,
    payload: ExportCreateRequest,
    session: AsyncSession,
    storage: ObjectStorage,
) -> ExportRecord:
    version = await jobs.get_workspace_version(session, workspace_id, version_id)
    source_artifact = await _resolve_handoff_source_artifact(
        session,
        workspace_id,
        version_id,
        payload.artifact_id,
    )
    source_object = await storage.get_object(source_artifact.object_key)
    source_content_type = (
        source_object.content_type or source_artifact.content_type or "application/octet-stream"
    )
    _validate_construction_source_image(source_artifact, source_object.content, source_content_type)
    manifest = _construction_package_manifest(version, source_artifact)
    package_bytes = _build_construction_package_zip(
        manifest=manifest,
        source_bytes=source_object.content,
        source_content_type=source_content_type,
    )
    package_object_key = build_object_key(
        workspace_id=workspace_id,
        kind=ArtifactKind.EXPORT.value,
        record_id=uuid4(),
        filename="construction-package.zip",
    )
    await storage.put_object(package_object_key, package_bytes, "application/zip")
    package_artifact = await jobs.create_artifact(
        session,
        workspace_id,
        byte_size=len(package_bytes),
        checksum_sha256=hashlib.sha256(package_bytes).hexdigest(),
        content_type="application/zip",
        job_id=version.job_id,
        kind=ArtifactKind.EXPORT.value,
        metadata={
            "format": CONSTRUCTION_PACKAGE_FORMAT,
            "package_files": manifest["files"],
            "source_artifact_id": str(source_artifact.id),
            "template": manifest["template"],
            "warning": manifest["warning"],
        },
        object_key=package_object_key,
        version_id=version.id,
    )
    export_manifest = {
        **manifest,
        "package_artifact": {
            "content_type": "application/zip",
            "object_key": package_object_key,
        },
    }
    return await jobs.record_export(
        session,
        workspace_id,
        version_id,
        artifact_id=package_artifact.id,
        concept_label=payload.concept_label,
        export_format=CONSTRUCTION_PACKAGE_FORMAT,
        manifest=export_manifest,
        status=ExportStatus.SUCCEEDED.value,
    )


def _construction_package_manifest(
    version: DesignVersion,
    source_artifact: Artifact,
) -> dict[str, object]:
    parameters = getattr(version, "parameters", None)
    params = parameters if isinstance(parameters, dict) else {}
    raw_preview_spec = params.get("preview_spec")
    preview_spec = raw_preview_spec if isinstance(raw_preview_spec, dict) else {}
    raw_template = preview_spec.get("template")
    template = raw_template if isinstance(raw_template, dict) else {}
    template_id = _optional_manifest_text(template.get("id"))
    template_view = _optional_manifest_text(template.get("view")) or "side"
    resolution = resolve_vehicle_template(vehicle_template_id=template_id, view=template_view)

    raw_section_design = params.get("section_design")
    section_design = raw_section_design if isinstance(raw_section_design, dict) else {}
    raw_section_design_sections = section_design.get("sections")
    section_design_sections = (
        raw_section_design_sections if isinstance(raw_section_design_sections, list) else []
    )
    sections = section_design_sections or resolution.sections
    raw_safe_zones = preview_spec.get("safe_zones")
    safe_zones: list[object] = (
        raw_safe_zones
        if isinstance(raw_safe_zones, list) and raw_safe_zones
        else list(resolution.safe_zones)
    )
    raw_warnings = preview_spec.get("warnings")
    warnings: list[object] = raw_warnings if isinstance(raw_warnings, list) else []
    canvas = _construction_canvas(preview_spec, resolution.canvas_width, resolution.canvas_height)
    construction_evidence = {
        "canvas": canvas,
        "dimensions": resolution.dimensions or {},
        "export_config": resolution.export_config or {},
        "forbidden_zones": resolution.forbidden_zones,
        "safe_zones": safe_zones,
        "scale": resolution.scale or {},
        "section_ids": [
            str(section.get("id"))
            for section in sections
            if isinstance(section, dict) and section.get("id")
        ],
        "sections": sections,
        "template": {
            "id": resolution.template_id,
            "label": resolution.template_label,
            "version": _template_version(resolution.authorization),
            "view": resolution.view,
        },
    }
    return {
        "construction_evidence": construction_evidence,
        "files": [
            "manifest.json",
            "construction/layered.svg",
            "construction/package.pdf",
            "preview/source.png",
            "warnings.md",
        ],
        "format": CONSTRUCTION_PACKAGE_FORMAT,
        "safe_zone_count": len(safe_zones),
        "section_design": section_design,
        "source_artifact_id": str(source_artifact.id),
        "source_artifact_object_key": source_artifact.object_key,
        "template": construction_evidence["template"],
        "version_id": str(version.id),
        "warning": "Quasi-construction package; not print-shop certified.",
        "warnings": warnings,
    }


def _build_construction_package_zip(
    *,
    manifest: dict[str, object],
    source_bytes: bytes,
    source_content_type: str,
) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "manifest.json",
            json.dumps(manifest, ensure_ascii=False, indent=2),
        )
        archive.writestr("construction/layered.svg", _construction_svg(manifest))
        archive.writestr("construction/package.pdf", _construction_pdf(manifest))
        archive.writestr("preview/source.png", source_bytes)
        archive.writestr(
            "warnings.md",
            _construction_warnings_markdown(manifest, source_content_type),
        )
    return buffer.getvalue()


def _construction_svg(manifest: dict[str, object]) -> str:
    evidence = _construction_evidence(manifest)
    canvas = _json_dict(evidence.get("canvas"))
    canvas_width = _int_manifest_value(canvas.get("width"), 1536)
    canvas_height = _int_manifest_value(canvas.get("height"), 768)
    raw_template = _json_dict(evidence.get("template")) or _json_dict(manifest.get("template"))
    template_id = _xml_attr(str(raw_template.get("id", "unknown-template")))
    source_artifact_id = _xml_attr(str(manifest.get("source_artifact_id", "")))
    lines = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{canvas_width}" height="{canvas_height}" '
            f'viewBox="0 0 {canvas_width} {canvas_height}">'
        ),
        f"  <title>carAgent construction package - {template_id}</title>",
        (
            '  <image id="source-preview" href="../preview/source.png" x="0" y="0" '
            f'width="{canvas_width}" height="{canvas_height}" opacity="0.45" '
            f'data-source-artifact-id="{source_artifact_id}"/>'
        ),
        (
            f'  <g id="base"><rect width="{canvas_width}" height="{canvas_height}" '
            'fill="#f8fafc"/></g>'
        ),
        (
            '  <g id="body"><rect x="120" y="260" width="1296" height="260" '
            'rx="44" fill="none" stroke="#1f2937" stroke-width="3"/></g>'
        ),
        (
            '  <g id="window"><rect x="430" y="210" width="520" height="150" '
            'fill="none" stroke="#0284c7" stroke-width="2"/></g>'
        ),
        (
            '  <g id="wheel"><circle cx="390" cy="520" r="70" fill="none" stroke="#111827" '
            'stroke-width="4"/><circle cx="1180" cy="520" r="70" fill="none" stroke="#111827" '
            'stroke-width="4"/></g>'
        ),
        '  <g id="handle"><rect x="760" y="375" width="60" height="10" fill="#1f2937"/></g>',
        (
            '  <g id="panel_lines"><path d="M500 260 L500 520 M960 260 L960 520" '
            'stroke="#64748b" stroke-dasharray="8 8"/></g>'
        ),
        '  <g id="artwork_sections">',
    ]
    for section in _json_list(evidence.get("sections")):
        if isinstance(section, dict):
            lines.append(
                _svg_rect_for_item("section", section, canvas_width, canvas_height, "#06b6d4"),
            )
    lines.append("  </g>")
    lines.append('  <g id="safe_zones">')
    for zone in _json_list(evidence.get("safe_zones")):
        if isinstance(zone, dict):
            lines.append(_svg_rect_for_item("safe", zone, canvas_width, canvas_height, "#22c55e"))
    lines.append("  </g>")
    lines.append('  <g id="forbidden_zones">')
    for zone in _json_list(evidence.get("forbidden_zones")):
        if isinstance(zone, dict):
            lines.append(
                _svg_rect_for_item("forbidden", zone, canvas_width, canvas_height, "#ef4444"),
            )
    lines.append("  </g>")
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


def _construction_pdf(manifest: dict[str, object]) -> bytes:
    evidence = _construction_evidence(manifest)
    raw_template = _json_dict(evidence.get("template")) or _json_dict(manifest.get("template"))
    raw_export_config = _json_dict(evidence.get("export_config"))
    lines = [
        f"carAgent construction package {manifest.get('version_id', '')}",
        f"Template: {raw_template.get('label', raw_template.get('id', 'unknown'))}",
        f"Source artifact: {manifest.get('source_artifact_id', '')}",
        f"Sections: {', '.join(str(item) for item in _json_list(evidence.get('section_ids'))[:8])}",
        f"Bleed mm: {raw_export_config.get('bleed_mm', 'n/a')}",
        f"Safe margin mm: {raw_export_config.get('safe_margin_mm', 'n/a')}",
        str(manifest.get("warning", "Quasi-construction package; not print-shop certified.")),
    ]
    text_ops = ["BT", "/F1 12 Tf", "72 720 Td"]
    for index, line in enumerate(lines):
        if index > 0:
            text_ops.append("0 -18 Td")
        text_ops.append(f"({_pdf_text(line)}) Tj")
    text_ops.append("ET")
    stream = "\n".join(text_ops).encode("latin-1", "replace")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    return _pdf_document(objects)


def _validate_construction_source_image(
    source_artifact: Artifact,
    source_bytes: bytes,
    source_content_type: str,
) -> None:
    if source_artifact.kind != ArtifactKind.GENERATED_IMAGE.value:
        raise jobs.JobValidationError("Handoff source concept image artifact not found")
    normalized_content_type = source_content_type.split(";", 1)[0].strip().lower()
    if normalized_content_type != "image/png" or not source_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        raise jobs.JobValidationError("Construction package source concept image must be image/png")


def _construction_evidence(manifest: dict[str, object]) -> dict[str, object]:
    raw_evidence = manifest.get("construction_evidence")
    return raw_evidence if isinstance(raw_evidence, dict) else {}


def _construction_canvas(
    preview_spec: dict[str, object],
    default_width: int,
    default_height: int,
) -> dict[str, int]:
    raw_canvas = preview_spec.get("canvas")
    canvas = raw_canvas if isinstance(raw_canvas, dict) else {}
    return {
        "height": _int_manifest_value(canvas.get("height"), default_height),
        "width": _int_manifest_value(canvas.get("width"), default_width),
    }


def _template_version(authorization: dict[str, object] | None) -> str | None:
    if not isinstance(authorization, dict):
        return None
    value = authorization.get("version")
    return value.strip() if isinstance(value, str) and value.strip() else None


def _svg_rect_for_item(
    prefix: str,
    item: dict[str, object],
    canvas_width: int,
    canvas_height: int,
    stroke: str,
) -> str:
    item_id = _xml_id(str(item.get("id", "unknown")))
    bounds = _item_bounds(item)
    x = bounds["x"] * canvas_width
    y = bounds["y"] * canvas_height
    width = bounds["width"] * canvas_width
    height = bounds["height"] * canvas_height
    label = _xml_attr(str(item.get("label", item_id)))
    return (
        f'    <rect id="{prefix}-{item_id}" x="{x:.2f}" y="{y:.2f}" '
        f'width="{width:.2f}" height="{height:.2f}" fill="none" stroke="{stroke}" '
        f'stroke-width="2" data-label="{label}"/>'
    )


def _item_bounds(item: dict[str, object]) -> dict[str, float]:
    raw_bounds = item.get("bounds")
    source = raw_bounds if isinstance(raw_bounds, dict) else item
    return {
        "height": _float_manifest_value(source.get("height"), 0.0),
        "width": _float_manifest_value(source.get("width"), 0.0),
        "x": _float_manifest_value(source.get("x"), 0.0),
        "y": _float_manifest_value(source.get("y"), 0.0),
    }


def _json_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _json_list(value: object) -> list[object]:
    return value if isinstance(value, list) else []


def _optional_manifest_text(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _int_manifest_value(value: object, fallback: int) -> int:
    if isinstance(value, int) and value > 0:
        return value
    return fallback


def _float_manifest_value(value: object, fallback: float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return fallback


def _xml_id(value: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)
    return _xml_attr(cleaned or "unknown")


def _xml_attr(value: str) -> str:
    return escape(value, quote=True)


def _pdf_text(value: object) -> str:
    text = str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
    return text.encode("latin-1", "replace").decode("latin-1")


def _pdf_document(objects: list[bytes]) -> bytes:
    body = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(body))
        body.extend(f"{index} 0 obj\n".encode("ascii"))
        body.extend(obj)
        body.extend(b"\nendobj\n")
    xref_offset = len(body)
    body.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    body.extend(b"0000000000 65535 f \n")
    for offset in offsets:
        body.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    body.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii"),
    )
    return bytes(body)


def _construction_warnings_markdown(
    manifest: dict[str, object],
    source_content_type: str,
) -> str:
    return "\n".join(
        [
            "# Construction Package Warnings",
            "",
            str(manifest["warning"]),
            f"Source content type: {source_content_type}",
            (
                "Layered SVG/PDF/PNG are concept construction aids, "
                "not certified print production files."
            ),
        ]
    )


async def _create_enhanced_handoff_export(
    *,
    workspace_id: UUID,
    version_id: UUID,
    payload: ExportCreateRequest,
    request: Request,
    session: AsyncSession,
    storage: ObjectStorage,
) -> ExportRecord:
    settings = _settings_from_request(request)
    if not settings.v2_enhanced_handoff_package_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="V2_ENHANCED_HANDOFF_PACKAGE_ENABLED is disabled.",
        )

    version = await jobs.get_workspace_version(session, workspace_id, version_id)
    source_artifact = await _resolve_handoff_source_artifact(
        session,
        workspace_id,
        version_id,
        payload.artifact_id,
    )
    screenshot_artifacts = await _list_handoff_screenshot_artifacts(
        session,
        workspace_id,
        version_id,
    )
    model_runs = (
        await jobs.list_job_model_runs(session, version.job_id)
        if version.job_id is not None
        else []
    )
    review_notes = await _handoff_review_notes(session, workspace_id, version_id)
    package_object_key = build_object_key(
        workspace_id=workspace_id,
        kind=ArtifactKind.EXPORT.value,
        record_id=uuid4(),
        filename="enhanced-concept-handoff.zip",
    )
    package = await build_handoff_package_zip(
        model_runs=model_runs,
        package_object_key=package_object_key,
        review_notes=review_notes,
        screenshot_artifacts=screenshot_artifacts,
        source_artifact=source_artifact,
        storage=storage,
        version=version,
    )
    await storage.put_object(package_object_key, package.content, package.content_type)
    package_artifact = await jobs.create_artifact(
        session,
        workspace_id,
        byte_size=package.byte_size,
        checksum_sha256=package.checksum_sha256,
        content_type=package.content_type,
        job_id=version.job_id,
        kind=ArtifactKind.EXPORT.value,
        metadata=_handoff_package_artifact_metadata(package),
        object_key=package_object_key,
        version_id=version.id,
    )
    return await jobs.record_export(
        session,
        workspace_id,
        version_id,
        artifact_id=package_artifact.id,
        concept_label=payload.concept_label,
        export_format=ENHANCED_HANDOFF_PACKAGE_FORMAT,
        manifest=_handoff_export_manifest(package),
        status=ExportStatus.SUCCEEDED.value,
    )


async def _resolve_handoff_source_artifact(
    session: AsyncSession,
    workspace_id: UUID,
    version_id: UUID,
    artifact_id: UUID | None,
) -> Artifact:
    if artifact_id is not None:
        artifact = await session.get(Artifact, artifact_id)
        if artifact is None or artifact.workspace_id != workspace_id:
            raise jobs.JobValidationError("Handoff source artifact not found for workspace")
        if artifact.version_id != version_id:
            raise jobs.JobValidationError("Handoff source artifact not found for version")
        if artifact.kind != ArtifactKind.GENERATED_IMAGE.value:
            raise jobs.JobValidationError("Handoff source concept image artifact not found")
        return artifact

    artifacts = await jobs.list_workspace_artifacts(session, workspace_id)
    candidates = [
        artifact
        for artifact in artifacts
        if artifact.version_id == version_id and artifact.kind == ArtifactKind.GENERATED_IMAGE.value
    ]
    if not candidates:
        raise jobs.JobValidationError("Handoff source concept image artifact not found")
    return candidates[-1]


async def _resolve_optional_generated_image_artifact(
    session: AsyncSession,
    workspace_id: UUID,
    version_id: UUID,
) -> Artifact | None:
    artifacts = await jobs.list_workspace_artifacts(session, workspace_id)
    candidates = [
        artifact
        for artifact in artifacts
        if artifact.version_id == version_id and artifact.kind == ArtifactKind.GENERATED_IMAGE.value
    ]
    return candidates[-1] if candidates else None


async def _list_handoff_screenshot_artifacts(
    session: AsyncSession,
    workspace_id: UUID,
    version_id: UUID,
) -> list[Artifact]:
    artifacts = await jobs.list_workspace_artifacts(session, workspace_id)
    return [
        artifact
        for artifact in artifacts
        if artifact.version_id == version_id
        and artifact.kind == ArtifactKind.PREVIEW_3D_SCREENSHOT.value
    ]


async def _handoff_review_notes(
    session: AsyncSession,
    workspace_id: UUID,
    version_id: UUID,
) -> list[str]:
    feedback_rows = await jobs.list_workspace_feedback(session, workspace_id)
    return [
        feedback.comment
        for feedback in feedback_rows
        if feedback.version_id == version_id and feedback.comment
    ]


def _handoff_export_manifest(package: HandoffPackageZipResult) -> dict[str, object]:
    manifest = package.manifest.model_dump(mode="json")
    package_artifact = dict(manifest["package_artifact"])
    package_artifact["byte_size"] = package.byte_size
    package_artifact["checksum_sha256"] = package.checksum_sha256
    manifest["package_artifact"] = package_artifact
    return manifest


def _handoff_package_artifact_metadata(package: HandoffPackageZipResult) -> dict[str, object]:
    manifest = _handoff_export_manifest(package)
    return {
        "handoff_package": {
            "files": manifest["files"],
            "format": manifest["format"],
            "package_artifact": manifest["package_artifact"],
            "schema_version": manifest["schema_version"],
            "source_artifact_id": str(package.manifest.source_artifact.id),
            "warning_count": len(package.manifest.warnings.items),
        },
    }


def _extract_queue_task_id(metadata: object) -> str | None:
    if not isinstance(metadata, dict):
        return None
    queue_metadata = metadata.get("queue")
    if not isinstance(queue_metadata, dict):
        return None
    task_id = queue_metadata.get("task_id")
    return task_id if isinstance(task_id, str) and task_id else None


def _settings_from_request(request: Request) -> ApiSettings:
    settings = getattr(request.app.state, "settings", None)
    if isinstance(settings, ApiSettings):
        return settings
    raise RuntimeError("API settings are not configured")


async def _validate_preview_3d_source_artifact(
    session: AsyncSession,
    workspace_id: UUID,
    version_id: UUID,
    payload: Preview3DScreenshotCreateRequest,
) -> None:
    source = payload.preview_3d.source
    if source.workspace_id != workspace_id:
        raise jobs.JobValidationError("Preview3D source workspace does not match request")
    if source.version_id != version_id:
        raise jobs.JobValidationError("Preview3D source version does not match request")

    source_artifact = await session.get(Artifact, source.artifact_id)
    if source_artifact is None or source_artifact.workspace_id != workspace_id:
        raise jobs.JobValidationError("Preview3D source artifact not found for workspace")
    if source_artifact.version_id != version_id:
        raise jobs.JobValidationError("Preview3D source artifact not found for version")


def _decode_screenshot_bytes(image_base64: str) -> bytes:
    try:
        return base64.b64decode(image_base64, validate=True)
    except (binascii.Error, ValueError) as error:
        raise ValueError("Screenshot image_base64 is invalid") from error


def _validate_screenshot_upload(
    payload: Preview3DScreenshotCreateRequest,
    content: bytes,
) -> None:
    if payload.content_type not in SCREENSHOT_CONTENT_TYPES:
        raise ValueError(f"Unsupported screenshot content type: {payload.content_type}")
    validate_upload(
        byte_size=len(content),
        content_type=payload.content_type,
        filename=payload.filename,
        max_upload_bytes=MAX_PREVIEW_3D_SCREENSHOT_BYTES,
    )
    actual_width, actual_height = _read_screenshot_dimensions(payload.content_type, content)
    if (payload.width, payload.height) != (actual_width, actual_height):
        raise ValueError(
            "Declared screenshot dimensions "
            f"{payload.width}x{payload.height} do not match actual screenshot dimensions "
            f"{actual_width}x{actual_height}"
        )


def _read_screenshot_dimensions(content_type: str, content: bytes) -> tuple[int, int]:
    if content_type == "image/png":
        return _read_png_dimensions(content)
    if content_type == "image/webp":
        return _read_webp_dimensions(content)
    raise ValueError(f"Unsupported screenshot content type: {content_type}")


def _read_png_dimensions(content: bytes) -> tuple[int, int]:
    signature = b"\x89PNG\r\n\x1a\n"
    if len(content) < 33 or not content.startswith(signature):
        raise ValueError("Screenshot bytes do not match PNG magic")
    ihdr_length = struct.unpack("!I", content[8:12])[0]
    if ihdr_length != 13 or content[12:16] != b"IHDR":
        raise ValueError("Screenshot PNG is missing a valid IHDR chunk")
    width, height = struct.unpack("!II", content[16:24])
    return width, height


def _read_webp_dimensions(content: bytes) -> tuple[int, int]:
    if len(content) < 20 or content[:4] != b"RIFF" or content[8:12] != b"WEBP":
        raise ValueError("Screenshot bytes do not match WebP magic")

    offset = 12
    while offset + 8 <= len(content):
        chunk_type = content[offset : offset + 4]
        chunk_size = struct.unpack("<I", content[offset + 4 : offset + 8])[0]
        chunk_start = offset + 8
        chunk_end = chunk_start + chunk_size
        if chunk_end > len(content):
            break
        chunk = content[chunk_start:chunk_end]

        if chunk_type == b"VP8X" and len(chunk) >= 10:
            width = int.from_bytes(chunk[4:7], "little") + 1
            height = int.from_bytes(chunk[7:10], "little") + 1
            return width, height
        if chunk_type == b"VP8L" and len(chunk) >= 5 and chunk[0] == 0x2F:
            bits = int.from_bytes(chunk[1:5], "little")
            return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
        if chunk_type == b"VP8 " and len(chunk) >= 10 and chunk[3:6] == b"\x9d\x01\x2a":
            width = struct.unpack("<H", chunk[6:8])[0] & 0x3FFF
            height = struct.unpack("<H", chunk[8:10])[0] & 0x3FFF
            return width, height

        offset = chunk_end + (chunk_size % 2)

    raise ValueError("Screenshot WebP is missing readable dimensions")


def _preview_3d_screenshot_metadata(
    payload: Preview3DScreenshotCreateRequest,
) -> Preview3DScreenshotArtifactMetadata:
    return Preview3DScreenshotArtifactMetadata.model_validate(
        {
            "preview_3d_screenshot": {
                "camera": payload.preview_3d.camera.model_dump(mode="json"),
                "preview_3d": payload.preview_3d.model_dump(mode="json"),
                "shell_id": payload.preview_3d.compatibility.shell_id,
                "source_artifact_id": payload.preview_3d.source.artifact_id,
                "warning_ids": required_preview_3d_warning_ids(),
            },
        },
    )
