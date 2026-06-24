from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from importlib.resources import files
from importlib.resources.abc import Traversable
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

SUPPORTED_TEMPLATE_ID = "generic-side-coupe"
SUPPORTED_TEMPLATE_LABEL = "Generic side-view coupe"
SUPPORTED_VIEW = "side"
SUPPORTED_CANVAS_WIDTH = 1536
SUPPORTED_CANVAS_HEIGHT = 768
MVP_COUPE_TEMPLATE_ID = "generic_coupe_side_v1"
MVP_SEDAN_TEMPLATE_ID = "generic_sedan_side_v1"
MVP_HATCHBACK_TEMPLATE_ID = "generic_hatchback_side_v1"
MVP_SUV_TEMPLATE_ID = "generic_suv_side_v1"
MVP_VAN_TEMPLATE_ID = "generic_van_side_v1"
GR86_BRZ_TEMPLATE_ID = "toyota_gr86_brz_v1"
DEFAULT_TEMPLATE_ID = MVP_COUPE_TEMPLATE_ID
MVP_TEMPLATE_IDS: tuple[str, ...] = (
    MVP_COUPE_TEMPLATE_ID,
    MVP_SEDAN_TEMPLATE_ID,
    MVP_HATCHBACK_TEMPLATE_ID,
    MVP_SUV_TEMPLATE_ID,
    MVP_VAN_TEMPLATE_ID,
)
MAINTAINED_TEMPLATE_IDS: tuple[str, ...] = (GR86_BRZ_TEMPLATE_ID,)
ALL_TEMPLATE_IDS: tuple[str, ...] = MVP_TEMPLATE_IDS + MAINTAINED_TEMPLATE_IDS
MVP_TEMPLATE_PACK_PACKAGE = "caragent_core.generation.template_pack.mvp_generic_side_v1"

SafeZone = dict[str, Any]
TemplateSection = dict[str, Any]
TemplateForbiddenZone = dict[str, Any]
TemplateDimensions = dict[str, Any]
TemplateScale = dict[str, Any]
TemplateExportConfig = dict[str, Any]
TemplateAuthorization = dict[str, Any]
TemplateViewAssets = dict[str, dict[str, str]]
TemplateSourceType = Literal[
    "internal_original",
    "licensed_template",
    "user_provided_with_rights",
    "third_party_reference_only",
    "web_crawled_image",
]
TemplateLicenseStatus = Literal[
    "approved",
    "conditional",
    "workspace_only",
    "reference_only",
    "blocked",
    "missing",
]
TemplateAssetSlot = Literal[
    "base",
    "body_mask",
    "window_mask",
    "wheel_mask",
    "handle_mask",
    "panel_lines",
    "safe_zones",
    "metadata",
    "thumbnail",
]

REQUIRED_TEMPLATE_ASSET_SLOTS: tuple[TemplateAssetSlot, ...] = (
    "base",
    "body_mask",
    "window_mask",
    "wheel_mask",
    "handle_mask",
    "panel_lines",
    "safe_zones",
    "metadata",
    "thumbnail",
)


@dataclass(frozen=True)
class TemplateSourcePolicy:
    source_type: TemplateSourceType
    label: str
    allowed_for_template_library: bool
    allowed_for_reusable_assets: bool
    requires_license_evidence: bool
    default_distribution_allowed: bool
    notes: str

    def as_public_dict(self) -> dict[str, object]:
        return {
            "allowed_for_reusable_assets": self.allowed_for_reusable_assets,
            "allowed_for_template_library": self.allowed_for_template_library,
            "default_distribution_allowed": self.default_distribution_allowed,
            "label": self.label,
            "notes": self.notes,
            "requires_license_evidence": self.requires_license_evidence,
            "source_type": self.source_type,
        }


TEMPLATE_SOURCE_POLICIES: dict[TemplateSourceType, TemplateSourcePolicy] = {
    "internal_original": TemplateSourcePolicy(
        allowed_for_reusable_assets=True,
        allowed_for_template_library=True,
        default_distribution_allowed=True,
        label="Internal original",
        notes="Internally created template assets are the preferred MVP source.",
        requires_license_evidence=False,
        source_type="internal_original",
    ),
    "licensed_template": TemplateSourcePolicy(
        allowed_for_reusable_assets=True,
        allowed_for_template_library=True,
        default_distribution_allowed=False,
        label="Licensed template",
        notes="Usable only within the written license scope.",
        requires_license_evidence=True,
        source_type="licensed_template",
    ),
    "user_provided_with_rights": TemplateSourcePolicy(
        allowed_for_reusable_assets=True,
        allowed_for_template_library=True,
        default_distribution_allowed=False,
        label="User provided with rights",
        notes="Workspace or authorization-scope use only unless distribution is explicit.",
        requires_license_evidence=False,
        source_type="user_provided_with_rights",
    ),
    "third_party_reference_only": TemplateSourcePolicy(
        allowed_for_reusable_assets=False,
        allowed_for_template_library=False,
        default_distribution_allowed=False,
        label="Third-party reference only",
        notes="May inform a brief, but cannot become reusable template assets or masks.",
        requires_license_evidence=True,
        source_type="third_party_reference_only",
    ),
    "web_crawled_image": TemplateSourcePolicy(
        allowed_for_reusable_assets=False,
        allowed_for_template_library=False,
        default_distribution_allowed=False,
        label="Web-crawled image",
        notes="Unauthorized crawled or screenshotted vehicle imagery is prohibited.",
        requires_license_evidence=True,
        source_type="web_crawled_image",
    ),
}

SUPPORTED_SAFE_ZONES: tuple[SafeZone, ...] = (
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
        "height": 0.16,
        "id": "side-window",
        "kind": "window",
        "label": "Side window",
        "width": 0.34,
        "x": 0.24,
        "y": 0.29,
    },
    {
        "height": 0.2,
        "id": "front-wheel-arch",
        "kind": "risky",
        "label": "Front wheel arch",
        "width": 0.16,
        "x": 0.16,
        "y": 0.58,
    },
    {
        "height": 0.2,
        "id": "rear-wheel-arch",
        "kind": "risky",
        "label": "Rear wheel arch",
        "width": 0.16,
        "x": 0.68,
        "y": 0.58,
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
)


class TemplateSourceMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: Literal[1] = 1
    source_type: TemplateSourceType
    license_status: TemplateLicenseStatus
    license_evidence: str | None = None
    rights_notes: str = ""
    allowed_usage_scope: str = ""
    distribution_allowed: bool = False
    audit_timestamp: str

    @field_validator(
        "allowed_usage_scope",
        "audit_timestamp",
        "license_evidence",
        "rights_notes",
        mode="before",
    )
    @classmethod
    def strip_optional_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class TemplateReadinessReport(BaseModel):
    model_config = ConfigDict(frozen=True)

    schema_version: Literal[1] = 1
    catalog_eligible: bool
    reusable_asset_allowed: bool
    required_asset_slots: list[TemplateAssetSlot] = Field(default_factory=list)
    missing_asset_slots: list[TemplateAssetSlot] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class VehicleTemplateRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    view: str = Field(min_length=1)
    canvas_width: int = Field(gt=0)
    canvas_height: int = Field(gt=0)
    source: TemplateSourceMetadata
    safe_zones: list[SafeZone] = Field(default_factory=list)
    aliases: tuple[str, ...] = ()
    asset_slots: dict[TemplateAssetSlot, str | None] = Field(default_factory=dict)
    supported_views: tuple[str, ...] = ()
    view_assets: TemplateViewAssets = Field(default_factory=dict)
    sections: list[TemplateSection] = Field(default_factory=list)
    forbidden_zones: list[TemplateForbiddenZone] = Field(default_factory=list)
    dimensions: TemplateDimensions | None = None
    scale: TemplateScale | None = None
    export_config: TemplateExportConfig | None = None
    authorization: TemplateAuthorization | None = None

    @field_validator("id", "label", "view", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("aliases", "supported_views", mode="before")
    @classmethod
    def normalize_string_tuple(cls, value: object) -> object:
        if value is None:
            return ()
        if isinstance(value, list | tuple):
            return tuple(
                item.strip().lower()
                for item in value
                if isinstance(item, str) and item.strip()
            )
        return value

    @model_validator(mode="after")
    def default_supported_views(self) -> VehicleTemplateRecord:
        if self.supported_views:
            return self
        return self.model_copy(update={"supported_views": (self.view,)})


class TemplateAuditItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    label: str
    view: str
    supported_views: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    source_type: TemplateSourceType
    license_status: TemplateLicenseStatus
    catalog_eligible: bool
    reusable_asset_allowed: bool
    distribution_allowed: bool
    missing_asset_slots: list[TemplateAssetSlot] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class TemplateResolution:
    template_id: str
    template_label: str
    view: str
    canvas_width: int
    canvas_height: int
    warnings: list[str]
    safe_zones: list[SafeZone]
    supported_views: list[str]
    sections: list[TemplateSection]
    forbidden_zones: list[TemplateForbiddenZone]
    dimensions: TemplateDimensions | None
    scale: TemplateScale | None
    export_config: TemplateExportConfig | None
    authorization: TemplateAuthorization | None
    template_source: TemplateSourceMetadata
    template_readiness: TemplateReadinessReport


class TemplateRegistry:
    def __init__(
        self,
        records: Iterable[VehicleTemplateRecord] = (),
        *,
        default_template_id: str = DEFAULT_TEMPLATE_ID,
    ) -> None:
        self._default_template_id = default_template_id
        self._records: dict[str, VehicleTemplateRecord] = {}
        self._aliases: dict[str, str] = {}
        for record in records:
            self.register(record)

    def register(self, record: VehicleTemplateRecord, *, replace: bool = False) -> None:
        validate_template_record(record)
        if not replace and record.id in self._records:
            raise ValueError(f"Template '{record.id}' is already registered.")
        for alias in record.aliases:
            existing = self._aliases.get(alias)
            if not replace and existing is not None and existing != record.id:
                raise ValueError(f"Template alias '{alias}' is already registered.")

        if replace:
            previous = self._records.get(record.id)
            if previous is not None:
                self._aliases.pop(previous.id, None)
                for alias in previous.aliases:
                    self._aliases.pop(alias, None)

        self._records[record.id] = record
        self._aliases[record.id] = record.id
        for alias in record.aliases:
            self._aliases[alias] = record.id

    def resolve(self, template_id: str) -> VehicleTemplateRecord | None:
        canonical_id = self._aliases.get(template_id.strip())
        if canonical_id is None:
            return None
        return self._records.get(canonical_id)

    def default_record(self) -> VehicleTemplateRecord:
        record = self.resolve(self._default_template_id)
        if record is None:
            raise LookupError(f"Default template '{self._default_template_id}' is not registered.")
        return record

    def list_records(self) -> list[VehicleTemplateRecord]:
        return list(self._records.values())

    def audit(self) -> list[TemplateAuditItem]:
        return [audit_template_record(record) for record in self.list_records()]


def template_source_policy_table() -> list[dict[str, object]]:
    return [
        TEMPLATE_SOURCE_POLICIES[source_type].as_public_dict()
        for source_type in sorted(TEMPLATE_SOURCE_POLICIES)
    ]


def source_policy(source_type: TemplateSourceType) -> TemplateSourcePolicy:
    return TEMPLATE_SOURCE_POLICIES[source_type]


def validate_template_record(record: VehicleTemplateRecord) -> None:
    policy = source_policy(record.source.source_type)
    if not policy.allowed_for_reusable_assets:
        raise ValueError(
            "Template source "
            f"'{record.source.source_type}' cannot be registered as reusable template assets.",
        )
    if policy.requires_license_evidence and not record.source.license_evidence:
        raise ValueError(
            f"Template '{record.id}' requires license evidence for source "
            f"'{record.source.source_type}'.",
        )
    if record.source.license_status in {"blocked", "missing", "reference_only"}:
        raise ValueError(
            f"Template '{record.id}' has non-reusable license status "
            f"'{record.source.license_status}'.",
        )
    if not record.source.allowed_usage_scope:
        raise ValueError(f"Template '{record.id}' requires an allowed usage scope.")
    if not record.source.rights_notes:
        raise ValueError(f"Template '{record.id}' requires rights notes.")
    if not record.source.audit_timestamp:
        raise ValueError(f"Template '{record.id}' requires an audit timestamp.")


def register_vehicle_template(
    record: VehicleTemplateRecord,
    *,
    registry: TemplateRegistry | None = None,
    replace: bool = False,
) -> None:
    (registry or TEMPLATE_REGISTRY).register(record, replace=replace)


def evaluate_template_readiness(record: VehicleTemplateRecord) -> TemplateReadinessReport:
    policy = source_policy(record.source.source_type)
    missing_asset_slots = [
        slot for slot in REQUIRED_TEMPLATE_ASSET_SLOTS if not record.asset_slots.get(slot)
    ]
    blocking_reasons: list[str] = []
    warnings: list[str] = []

    if not policy.allowed_for_template_library:
        blocking_reasons.append(
            f"Source type '{record.source.source_type}' is not allowed in the template catalog.",
        )
    if policy.requires_license_evidence and not record.source.license_evidence:
        blocking_reasons.append("License evidence is required but missing.")
    if record.source.license_status in {"blocked", "missing", "reference_only"}:
        blocking_reasons.append(
            f"License status '{record.source.license_status}' blocks reusable template use.",
        )
    if not record.source.audit_timestamp:
        blocking_reasons.append("Audit timestamp is missing.")
    if missing_asset_slots:
        warnings.append(
            "Template package is incomplete: "
            + ", ".join(missing_asset_slots)
            + " asset slot(s) missing.",
        )
    if not record.source.distribution_allowed:
        warnings.append("Template distribution is disabled by source metadata.")

    return TemplateReadinessReport(
        blocking_reasons=blocking_reasons,
        catalog_eligible=(
            not blocking_reasons
            and not missing_asset_slots
            and record.source.distribution_allowed
        ),
        missing_asset_slots=missing_asset_slots,
        required_asset_slots=list(REQUIRED_TEMPLATE_ASSET_SLOTS),
        reusable_asset_allowed=policy.allowed_for_reusable_assets and not blocking_reasons,
        warnings=warnings,
    )


def audit_template_record(record: VehicleTemplateRecord) -> TemplateAuditItem:
    readiness = evaluate_template_readiness(record)
    return TemplateAuditItem(
        aliases=list(record.aliases),
        supported_views=list(record.supported_views),
        blocking_reasons=list(readiness.blocking_reasons),
        catalog_eligible=readiness.catalog_eligible,
        distribution_allowed=record.source.distribution_allowed,
        id=record.id,
        label=record.label,
        license_status=record.source.license_status,
        missing_asset_slots=list(readiness.missing_asset_slots),
        reusable_asset_allowed=readiness.reusable_asset_allowed,
        source_type=record.source.source_type,
        view=record.view,
        warnings=list(readiness.warnings),
    )


def audit_vehicle_templates(registry: TemplateRegistry | None = None) -> list[TemplateAuditItem]:
    return (registry or TEMPLATE_REGISTRY).audit()


def list_vehicle_templates(registry: TemplateRegistry | None = None) -> list[VehicleTemplateRecord]:
    return (registry or TEMPLATE_REGISTRY).list_records()


def template_pack_root() -> Traversable:
    return files(MVP_TEMPLATE_PACK_PACKAGE)


def template_asset_resource(template_id: str, slot: TemplateAssetSlot) -> Traversable:
    record = TEMPLATE_REGISTRY.resolve(template_id)
    if record is None:
        raise KeyError(f"Unknown template '{template_id}'.")
    asset_path = record.asset_slots.get(slot)
    if not asset_path:
        raise KeyError(f"Template '{record.id}' does not define asset slot '{slot}'.")
    return template_pack_root().joinpath(record.id, asset_path)


def load_mvp_template_records() -> tuple[VehicleTemplateRecord, ...]:
    return tuple(_load_template_record(template_id) for template_id in ALL_TEMPLATE_IDS)


def _load_template_record(template_id: str) -> VehicleTemplateRecord:
    template_root = template_pack_root().joinpath(template_id)
    metadata = _read_json_object(template_root.joinpath("template.json"))
    safe_zones = _read_json_list(template_root.joinpath("safe_zones.json"))
    payload: dict[str, object] = {**metadata, "safe_zones": safe_zones}
    sections_resource = template_root.joinpath("sections.json")
    forbidden_resource = template_root.joinpath("forbidden_zones.json")
    if sections_resource.is_file():
        payload["sections"] = _read_json_list(sections_resource)
    if forbidden_resource.is_file():
        payload["forbidden_zones"] = _read_json_list(forbidden_resource)
    return VehicleTemplateRecord.model_validate(payload)


def _read_json_object(resource: Traversable) -> dict[str, object]:
    value = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object in {resource.name}.")
    return value


def _read_json_list(resource: Traversable) -> list[object]:
    value = json.loads(resource.read_text(encoding="utf-8"))
    if not isinstance(value, list):
        raise ValueError(f"Expected JSON list in {resource.name}.")
    return value


TEMPLATE_REGISTRY = TemplateRegistry(load_mvp_template_records())


def resolve_vehicle_template(
    *,
    vehicle_template_id: str | None = None,
    view: str | None = None,
    registry: TemplateRegistry | None = None,
) -> TemplateResolution:
    requested_template = (vehicle_template_id or DEFAULT_TEMPLATE_ID).strip()
    requested_view = (view or SUPPORTED_VIEW).strip().lower()
    template_registry = registry or TEMPLATE_REGISTRY
    record = template_registry.resolve(requested_template)
    warnings: list[str] = []

    if record is None:
        warnings.append(
            "Unsupported vehicle template "
            f"'{requested_template}' normalized to '{DEFAULT_TEMPLATE_ID}'.",
        )
        record = template_registry.default_record()

    resolved_view = requested_view if requested_view in record.supported_views else record.view
    if requested_view != resolved_view:
        warnings.append(
            f"Unsupported view '{requested_view}' normalized to '{resolved_view}'.",
        )

    return TemplateResolution(
        canvas_height=record.canvas_height,
        canvas_width=record.canvas_width,
        safe_zones=[dict(zone) for zone in record.safe_zones],
        supported_views=list(record.supported_views),
        sections=[dict(section) for section in record.sections],
        forbidden_zones=[dict(zone) for zone in record.forbidden_zones],
        dimensions=dict(record.dimensions) if record.dimensions is not None else None,
        scale=dict(record.scale) if record.scale is not None else None,
        export_config=dict(record.export_config) if record.export_config is not None else None,
        authorization=dict(record.authorization) if record.authorization is not None else None,
        template_id=record.id,
        template_label=record.label,
        template_readiness=evaluate_template_readiness(record),
        template_source=record.source,
        view=resolved_view,
        warnings=warnings,
    )


def supported_safe_zones() -> list[SafeZone]:
    return [dict(zone) for zone in TEMPLATE_REGISTRY.default_record().safe_zones]


def template_source_metadata_from_mapping(
    value: Mapping[str, object],
) -> TemplateSourceMetadata:
    return TemplateSourceMetadata.model_validate(dict(value))
