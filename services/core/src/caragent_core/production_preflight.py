from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PRODUCTION_PREFLIGHT_SCHEMA_VERSION = 1
PRODUCTION_PREFLIGHT_FORMAT = "production_readiness_preflight"
PRODUCTION_PREFLIGHT_DISCLAIMER = (
    "Concept preflight only; this is not print-ready production artwork."
)
REQUIRED_PRODUCTION_EVIDENCE_IDS: tuple[str, ...] = (
    "licensed_real_vehicle_template",
    "verified_scale",
    "bleed_spec",
    "color_profile",
    "dpi_target",
    "verified_uv_mapping",
    "installer_notes",
)

JsonObject = dict[str, object]


class ProductionPreflightBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProductionReadinessCheck(ProductionPreflightBaseModel):
    evidence: JsonObject = Field(default_factory=dict)
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    message: str = Field(min_length=1)
    severity: Literal["info", "warning", "blocker"] = "warning"
    status: Literal["ready", "warning", "missing", "blocked"]


class TemplateValidationReport(ProductionPreflightBaseModel):
    catalog_eligible: bool = False
    license_status: str = "unknown"
    safe_zone_count: int = Field(default=0, ge=0)
    schema_version: int = Field(default=PRODUCTION_PREFLIGHT_SCHEMA_VERSION, ge=1, le=1)
    source_type: str = "unknown"
    template: JsonObject = Field(default_factory=dict)
    validation_status: Literal["concept_valid", "missing_template"] = "missing_template"
    warning_count: int = Field(default=0, ge=0)


class ProductionReadinessPreflightReport(ProductionPreflightBaseModel):
    blockers: list[str] = Field(default_factory=list)
    checks: list[ProductionReadinessCheck] = Field(default_factory=list)
    disclaimer: str = PRODUCTION_PREFLIGHT_DISCLAIMER
    missing_evidence: list[str] = Field(default_factory=list)
    print_ready_allowed: bool = False
    schema_version: int = Field(default=PRODUCTION_PREFLIGHT_SCHEMA_VERSION, ge=1, le=1)
    status: Literal["concept_only"] = "concept_only"
    template_validation: TemplateValidationReport
    version_id: str
    workspace_id: str


def build_template_validation_report(parameters: Mapping[str, object]) -> TemplateValidationReport:
    preview_spec = _mapping_value(parameters.get("preview_spec"))
    template = _template_mapping(parameters)
    source = _mapping_value(template.get("source"))
    readiness = _mapping_value(template.get("readiness"))
    safe_zones = _sequence_value(preview_spec.get("safe_zones"))
    warnings = _sequence_value(preview_spec.get("warnings"))
    source_type = _text(source.get("source_type") or template.get("source_type"), "unknown")
    license_status = _text(
        source.get("license_status") or template.get("license_status"),
        "unknown",
    )
    catalog_eligible = bool(
        readiness.get("catalog_eligible", template.get("catalog_eligible", False)),
    )
    validation_status: Literal["concept_valid", "missing_template"] = (
        "concept_valid" if template.get("id") else "missing_template"
    )

    return TemplateValidationReport(
        catalog_eligible=catalog_eligible,
        license_status=license_status,
        safe_zone_count=len(safe_zones),
        source_type=source_type,
        template=_json_object(template),
        validation_status=validation_status,
        warning_count=len(warnings),
    )


def build_production_readiness_preflight_report(
    *,
    source_artifact: object | None = None,
    version: Any,
) -> ProductionReadinessPreflightReport:
    parameters = _mapping_value(getattr(version, "parameters", None))
    template_validation = build_template_validation_report(parameters)
    checks = [
        _concept_image_check(source_artifact),
        _template_source_check(template_validation),
        _missing_check(
            "licensed_real_vehicle_template",
            "Licensed real-vehicle template",
            "No licensed real-vehicle production template evidence is attached.",
        ),
        _missing_check(
            "verified_scale",
            "Verified scale",
            "No installer-verified scale or physical measurement evidence is attached.",
        ),
        _missing_check(
            "bleed_spec",
            "Bleed specification",
            "No production bleed or trim allowance specification is attached.",
        ),
        _missing_check(
            "color_profile",
            "Color profile",
            "No print color profile evidence is attached.",
        ),
        _missing_check(
            "dpi_target",
            "DPI target",
            "No production DPI target or raster resolution evidence is attached.",
        ),
        _missing_check(
            "verified_uv_mapping",
            "Verified UV mapping",
            "No vehicle-specific UV/wrap geometry validation evidence is attached.",
        ),
        _missing_check(
            "installer_notes",
            "Installer notes",
            "No installer-reviewed application notes are attached.",
        ),
        ProductionReadinessCheck(
            id="print_ready_export_blocked",
            label="Print-ready export",
            message="Print-ready PSD/AI/PDF export remains blocked for this concept.",
            severity="blocker",
            status="blocked",
        ),
    ]
    missing_evidence = [
        check.id for check in checks if check.status in {"blocked", "missing"}
    ]
    blockers = [check.id for check in checks if check.status == "blocked"]

    return ProductionReadinessPreflightReport(
        blockers=blockers,
        checks=checks,
        missing_evidence=missing_evidence,
        template_validation=template_validation,
        version_id=str(version.id),
        workspace_id=str(version.workspace_id),
    )


def _concept_image_check(source_artifact: object | None) -> ProductionReadinessCheck:
    if source_artifact is None:
        return ProductionReadinessCheck(
            id="concept_image",
            label="Concept image",
            message="No generated concept image artifact is attached.",
            severity="blocker",
            status="blocked",
        )
    return ProductionReadinessCheck(
        evidence={"artifact_id": str(getattr(source_artifact, "id", ""))},
        id="concept_image",
        label="Concept image",
        message="A generated concept image artifact is available for review.",
        severity="info",
        status="ready",
    )


def _template_source_check(report: TemplateValidationReport) -> ProductionReadinessCheck:
    if report.validation_status == "missing_template":
        return ProductionReadinessCheck(
            id="template_source_license",
            label="Template source/license",
            message="No template source/license metadata is attached.",
            severity="blocker",
            status="blocked",
        )
    return ProductionReadinessCheck(
        evidence={
            "catalog_eligible": report.catalog_eligible,
            "license_status": report.license_status,
            "source_type": report.source_type,
        },
        id="template_source_license",
        label="Template source/license",
        message="Template source and license metadata are present for concept review.",
        severity="info",
        status="ready",
    )


def _missing_check(check_id: str, label: str, message: str) -> ProductionReadinessCheck:
    return ProductionReadinessCheck(
        id=check_id,
        label=label,
        message=message,
        severity="warning",
        status="missing",
    )


def _template_mapping(parameters: Mapping[str, object]) -> Mapping[str, object]:
    preview_spec = _mapping_value(parameters.get("preview_spec"))
    preview_template = _mapping_value(preview_spec.get("template"))
    if preview_template:
        return preview_template
    return _mapping_value(parameters.get("vehicle_template"))


def _sequence_value(value: object) -> Sequence[object]:
    if isinstance(value, str) or value is None:
        return []
    if isinstance(value, Sequence):
        return value
    return []


def _mapping_value(value: object) -> Mapping[str, object]:
    if isinstance(value, Mapping):
        return value
    return {}


def _json_object(value: Mapping[str, object]) -> JsonObject:
    return {str(key): _json_safe_value(item) for key, item in value.items()}


def _json_safe_value(value: object) -> object:
    if isinstance(value, Mapping):
        return _json_object(value)
    if isinstance(value, Sequence) and not isinstance(value, str):
        return [_json_safe_value(item) for item in value]
    return value


def _text(value: object, fallback: str) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else fallback


__all__ = [
    "PRODUCTION_PREFLIGHT_DISCLAIMER",
    "PRODUCTION_PREFLIGHT_FORMAT",
    "PRODUCTION_PREFLIGHT_SCHEMA_VERSION",
    "REQUIRED_PRODUCTION_EVIDENCE_IDS",
    "ProductionReadinessCheck",
    "ProductionReadinessPreflightReport",
    "TemplateValidationReport",
    "build_production_readiness_preflight_report",
    "build_template_validation_report",
]
