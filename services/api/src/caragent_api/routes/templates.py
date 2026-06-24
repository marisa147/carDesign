from __future__ import annotations

import json
import zipfile
from io import BytesIO
from typing import Annotated, Any

from caragent_core.generation import (
    VehicleTemplateRecord,
    evaluate_template_readiness,
    list_vehicle_templates,
    template_asset_resource,
)
from fastapi import APIRouter, File, HTTPException, Query, Response, UploadFile, status

from caragent_api.schemas import (
    TemplateCatalogItemResponse,
    TemplateDetailResponse,
    TemplatePackageValidationIssue,
    TemplatePackageValidationResponse,
    TemplateSafeZoneSummaryResponse,
)

router = APIRouter(tags=["templates"])


@router.get("/templates", response_model=list[TemplateCatalogItemResponse])
async def list_templates(
    view: Annotated[str | None, Query(max_length=40)] = None,
    catalog_eligible: bool | None = None,
) -> list[TemplateCatalogItemResponse]:
    records = list_vehicle_templates()
    if view:
        normalized_view = view.strip().lower()
        records = [record for record in records if normalized_view in record.supported_views]
    if catalog_eligible is not None:
        records = [
            record
            for record in records
            if evaluate_template_readiness(record).catalog_eligible is catalog_eligible
        ]
    return [_catalog_item(record) for record in records]


@router.post("/templates/validate-package", response_model=TemplatePackageValidationResponse)
async def validate_template_package(
    package: Annotated[
        UploadFile, File(description="Template package zip containing JSON and PNG/SVG assets")
    ],
) -> TemplatePackageValidationResponse:
    filename = package.filename or "template-package.zip"
    if not filename.lower().endswith(".zip"):
        return TemplatePackageValidationResponse(
            accepted=False,
            issues=[
                TemplatePackageValidationIssue(
                    severity="error",
                    code="unsupported_package_type",
                    message="Template package must be a .zip file.",
                    path=filename,
                )
            ],
        )
    content = await package.read()
    return _validate_template_package_zip(content)


@router.get("/templates/{template_id}/thumbnail.png", response_class=Response)
async def get_template_thumbnail(template_id: str) -> Response:
    record = _find_template(template_id)
    try:
        content = template_asset_resource(record.id, "thumbnail").read_bytes()
    except (FileNotFoundError, KeyError) as error:
        raise _template_not_found(template_id) from error

    return Response(
        content=content,
        headers={"Cache-Control": "public, max-age=3600"},
        media_type="image/png",
    )


@router.get("/templates/{template_id}", response_model=TemplateDetailResponse)
async def get_template(template_id: str) -> TemplateDetailResponse:
    record = _find_template(template_id)
    return TemplateDetailResponse(
        **_catalog_item(record).model_dump(mode="json"),
        asset_slots={slot: value for slot, value in record.asset_slots.items()},
        safe_zones=[dict(zone) for zone in record.safe_zones],
        view_assets={view: dict(assets) for view, assets in record.view_assets.items()},
        sections=[dict(section) for section in record.sections],
        forbidden_zones=[dict(zone) for zone in record.forbidden_zones],
        dimensions=dict(record.dimensions) if record.dimensions is not None else None,
        scale=dict(record.scale) if record.scale is not None else None,
        export_config=dict(record.export_config) if record.export_config is not None else None,
        authorization=dict(record.authorization) if record.authorization is not None else None,
    )


def _find_template(template_id: str) -> VehicleTemplateRecord:
    requested = template_id.strip()
    for record in list_vehicle_templates():
        if record.id == requested or requested in record.aliases:
            return record
    raise _template_not_found(template_id)


def _template_not_found(template_id: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"template not found: {template_id}",
    )


def _catalog_item(record: VehicleTemplateRecord) -> TemplateCatalogItemResponse:
    return TemplateCatalogItemResponse(
        aliases=list(record.aliases),
        canvas_height=record.canvas_height,
        canvas_width=record.canvas_width,
        id=record.id,
        label=record.label,
        readiness=evaluate_template_readiness(record),
        safe_zone_summary=[_safe_zone_summary(zone) for zone in record.safe_zones],
        source=record.source,
        supported_views=list(record.supported_views),
        thumbnail_url=f"/templates/{record.id}/thumbnail.png",
        view=record.view,
    )


def _safe_zone_summary(zone: dict[str, object]) -> TemplateSafeZoneSummaryResponse:
    return TemplateSafeZoneSummaryResponse(
        height=_number(zone.get("height")),
        id=str(zone.get("id", "")),
        kind=str(zone.get("kind", "")),
        label=str(zone.get("label", "")),
        width=_number(zone.get("width")),
        x=_number(zone.get("x")),
        y=_number(zone.get("y")),
    )


def _number(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return 0.0
    return float(value)


_REQUIRED_JSON_FILES = {
    "template.json",
    "safe_zones.json",
    "sections.json",
    "forbidden_zones.json",
}
_REQUIRED_AUTHORIZATION_FIELDS = {
    "source",
    "authorization_file",
    "scope",
    "expires_at",
    "commercial_use",
    "reviewer",
    "version_history",
}
_REQUIRED_TEMPLATE_FIELDS = {
    "id",
    "label",
    "supported_views",
    "view_assets",
    "dimensions",
    "export_config",
    "authorization",
}
_ALLOWED_ASSET_SUFFIXES = {".png", ".svg"}
_MAX_TEMPLATE_PACKAGE_BYTES = 20 * 1024 * 1024


def _validate_template_package_zip(content: bytes) -> TemplatePackageValidationResponse:
    issues: list[TemplatePackageValidationIssue] = []
    if len(content) > _MAX_TEMPLATE_PACKAGE_BYTES:
        issues.append(
            _issue(
                "error",
                "package_too_large",
                "Template package exceeds the 20 MiB validation limit.",
                None,
            )
        )
        return TemplatePackageValidationResponse(accepted=False, issues=issues)

    try:
        archive = zipfile.ZipFile(BytesIO(content))
    except zipfile.BadZipFile:
        return TemplatePackageValidationResponse(
            accepted=False,
            issues=[
                _issue("error", "invalid_zip", "Template package is not a valid zip file.", None)
            ],
        )

    with archive:
        names = [
            info.filename.replace("\\", "/") for info in archive.infolist() if not info.is_dir()
        ]
        files_checked = sorted(names)
        for name in names:
            if _is_unsafe_zip_path(name):
                issues.append(
                    _issue("error", "unsafe_path", "Package contains an unsafe file path.", name)
                )
        if any(issue.code == "unsafe_path" for issue in issues):
            return TemplatePackageValidationResponse(
                accepted=False,
                files_checked=files_checked,
                issues=issues,
            )

        root = _common_package_root(names)
        logical_names = {_strip_root(name, root): name for name in names}
        json_payloads: dict[str, Any] = {}
        for required in sorted(_REQUIRED_JSON_FILES):
            physical_name = logical_names.get(required)
            if physical_name is None:
                issues.append(
                    _issue("error", "missing_file", f"Missing required file: {required}.", required)
                )
                continue
            try:
                json_payloads[required] = json.loads(archive.read(physical_name).decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                issues.append(_issue("error", "invalid_json", f"Invalid JSON: {error}.", required))

        template = json_payloads.get("template.json")
        if isinstance(template, dict):
            _validate_template_manifest(template, logical_names, issues)
        elif "template.json" in json_payloads:
            issues.append(
                _issue(
                    "error",
                    "invalid_manifest",
                    "template.json must be a JSON object.",
                    "template.json",
                )
            )

        _validate_json_list(json_payloads, "safe_zones.json", issues)
        _validate_json_list(json_payloads, "sections.json", issues)
        _validate_json_list(json_payloads, "forbidden_zones.json", issues)

        error_count = sum(1 for issue in issues if issue.severity == "error")
        authorization = template.get("authorization") if isinstance(template, dict) else None
        return TemplatePackageValidationResponse(
            accepted=error_count == 0,
            template_id=str(template.get("id"))
            if isinstance(template, dict) and template.get("id")
            else None,
            label=str(template.get("label"))
            if isinstance(template, dict) and template.get("label")
            else None,
            source_class=_source_class(template.get("source"), authorization)
            if isinstance(template, dict)
            else None,
            authorization=authorization if isinstance(authorization, dict) else None,
            files_checked=files_checked,
            issues=issues,
        )


def _validate_template_manifest(
    template: dict[str, Any],
    logical_names: dict[str, str],
    issues: list[TemplatePackageValidationIssue],
) -> None:
    for field in sorted(_REQUIRED_TEMPLATE_FIELDS):
        if field not in template:
            issues.append(
                _issue(
                    "error",
                    "missing_manifest_field",
                    f"Missing template field: {field}.",
                    "template.json",
                )
            )

    supported_views = template.get("supported_views")
    view_assets = template.get("view_assets")
    if not isinstance(supported_views, list) or not all(
        isinstance(view, str) for view in supported_views
    ):
        issues.append(
            _issue(
                "error",
                "invalid_supported_views",
                "supported_views must be a string array.",
                "template.json",
            )
        )
        supported_views = []
    if not isinstance(view_assets, dict):
        issues.append(
            _issue(
                "error",
                "invalid_view_assets",
                "view_assets must be an object keyed by view.",
                "template.json",
            )
        )
        view_assets = {}

    for view in supported_views:
        assets = view_assets.get(view)
        if not isinstance(assets, dict):
            issues.append(
                _issue(
                    "error",
                    "missing_view_assets",
                    f"Missing assets for view: {view}.",
                    "template.json",
                )
            )
            continue
        for slot in ("base", "panel_lines"):
            asset_path = assets.get(slot)
            if not isinstance(asset_path, str) or not asset_path:
                issues.append(
                    _issue(
                        "error",
                        "missing_view_asset",
                        f"Missing {slot} asset for view: {view}.",
                        "template.json",
                    )
                )
                continue
            _validate_asset_reference(asset_path, logical_names, issues)

    dimensions = template.get("dimensions")
    if not isinstance(dimensions, dict) or not _positive_number(dimensions.get("overall_length")):
        issues.append(
            _issue(
                "error",
                "invalid_dimensions",
                "dimensions.overall_length must be a positive number.",
                "template.json",
            )
        )

    export_config = template.get("export_config")
    if not isinstance(export_config, dict) or not isinstance(export_config.get("formats"), list):
        issues.append(
            _issue(
                "error",
                "invalid_export_config",
                "export_config.formats must list supported outputs.",
                "template.json",
            )
        )

    authorization = template.get("authorization")
    if not isinstance(authorization, dict):
        issues.append(
            _issue(
                "error",
                "missing_authorization",
                "authorization metadata is required.",
                "template.json",
            )
        )
        return
    missing_auth = sorted(
        field for field in _REQUIRED_AUTHORIZATION_FIELDS if field not in authorization
    )
    for field in missing_auth:
        issues.append(
            _issue(
                "error",
                "missing_authorization_field",
                f"Missing authorization field: {field}.",
                "template.json",
            )
        )
    version_history = authorization.get("version_history")
    if "version_history" in authorization and not isinstance(version_history, list):
        issues.append(
            _issue(
                "error",
                "invalid_version_history",
                "authorization.version_history must be an array.",
                "template.json",
            )
        )
    auth_file = authorization.get("authorization_file")
    if isinstance(auth_file, str) and auth_file:
        _validate_asset_reference(
            auth_file, logical_names, issues, allowed_suffixes={".json", ".md", ".txt", ".pdf"}
        )


def _validate_asset_reference(
    asset_path: str,
    logical_names: dict[str, str],
    issues: list[TemplatePackageValidationIssue],
    *,
    allowed_suffixes: set[str] = _ALLOWED_ASSET_SUFFIXES,
) -> None:
    normalized = asset_path.replace("\\", "/").lstrip("/")
    if _is_unsafe_zip_path(normalized):
        issues.append(
            _issue("error", "unsafe_reference", "Asset reference uses an unsafe path.", asset_path)
        )
        return
    suffix = "." + normalized.rsplit(".", 1)[-1].lower() if "." in normalized else ""
    if suffix not in allowed_suffixes:
        issues.append(
            _issue(
                "error",
                "unsupported_asset_type",
                "Asset reference must use an allowed extension.",
                asset_path,
            )
        )
    if normalized not in logical_names:
        issues.append(
            _issue(
                "error",
                "missing_asset",
                "Referenced asset is missing from the package.",
                asset_path,
            )
        )


def _validate_json_list(
    json_payloads: dict[str, Any],
    path: str,
    issues: list[TemplatePackageValidationIssue],
) -> None:
    payload = json_payloads.get(path)
    if payload is not None and not isinstance(payload, list):
        issues.append(_issue("error", "invalid_json_shape", f"{path} must be a JSON array.", path))


def _common_package_root(names: list[str]) -> str:
    parts = [name.split("/") for name in names]
    if parts and all(len(part) > 1 and part[0] == parts[0][0] for part in parts):
        return parts[0][0]
    return ""


def _strip_root(name: str, root: str) -> str:
    if root and name.startswith(f"{root}/"):
        return name[len(root) + 1 :]
    return name


def _is_unsafe_zip_path(name: str) -> bool:
    normalized = name.replace("\\", "/")
    return (
        normalized.startswith("/")
        or normalized.startswith("../")
        or "/../" in normalized
        or normalized == ".."
    )


def _positive_number(value: object) -> bool:
    return not isinstance(value, bool) and isinstance(value, int | float) and value > 0


def _source_class(source: object, authorization: object) -> str:
    source_type = source.get("source_type") if isinstance(source, dict) else None
    auth_source = authorization.get("source") if isinstance(authorization, dict) else None
    if source_type == "internal_original" or auth_source == "internal_generated":
        return "maintained_internal"
    if source_type == "user_provided_with_rights":
        return "user_provided"
    if source_type == "licensed_template":
        return "third_party_authorized"
    if source_type == "third_party_reference_only":
        return "reference_only"
    return "unknown"


def _issue(
    severity: str, code: str, message: str, path: str | None
) -> TemplatePackageValidationIssue:
    return TemplatePackageValidationIssue(severity=severity, code=code, message=message, path=path)
