from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

SUPPORTED_TEMPLATE_ID = "generic-side-coupe"
SUPPORTED_TEMPLATE_LABEL = "Generic side-view coupe"
SUPPORTED_VIEW = "side"
SUPPORTED_CANVAS_WIDTH = 1536
SUPPORTED_CANVAS_HEIGHT = 768
MVP_COUPE_TEMPLATE_ID = "generic_coupe_side_v1"

SafeZone = dict[str, Any]
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

    @field_validator("id", "label", "view", mode="before")
    @classmethod
    def strip_required_text(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("aliases", mode="before")
    @classmethod
    def normalize_aliases(cls, value: object) -> object:
        if value is None:
            return ()
        if isinstance(value, list | tuple):
            return tuple(item.strip() for item in value if isinstance(item, str) and item.strip())
        return value


class TemplateAuditItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    label: str
    view: str
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
    template_source: TemplateSourceMetadata
    template_readiness: TemplateReadinessReport


class TemplateRegistry:
    def __init__(self, records: Iterable[VehicleTemplateRecord] = ()) -> None:
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
        return self._records[SUPPORTED_TEMPLATE_ID]

    def list_records(self) -> list[VehicleTemplateRecord]:
        return list(self._records.values())

    def audit(self) -> list[TemplateAuditItem]:
        return [audit_template_record(record) for record in self.list_records()]


LEGACY_TEMPLATE_RECORD = VehicleTemplateRecord(
    aliases=(MVP_COUPE_TEMPLATE_ID,),
    asset_slots={},
    canvas_height=SUPPORTED_CANVAS_HEIGHT,
    canvas_width=SUPPORTED_CANVAS_WIDTH,
    id=SUPPORTED_TEMPLATE_ID,
    label=SUPPORTED_TEMPLATE_LABEL,
    safe_zones=[dict(zone) for zone in SUPPORTED_SAFE_ZONES],
    source=TemplateSourceMetadata(
        allowed_usage_scope="mvp_concept_preview",
        audit_timestamp="2026-06-19T00:00:00Z",
        distribution_allowed=True,
        license_evidence="internal-template-seed-v1",
        license_status="approved",
        rights_notes="Internal generic side-view vehicle silhouette for concept previews.",
        source_type="internal_original",
    ),
    view=SUPPORTED_VIEW,
)

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


TEMPLATE_REGISTRY = TemplateRegistry([LEGACY_TEMPLATE_RECORD])


def resolve_vehicle_template(
    *,
    vehicle_template_id: str | None = None,
    view: str | None = None,
    registry: TemplateRegistry | None = None,
) -> TemplateResolution:
    requested_template = (vehicle_template_id or SUPPORTED_TEMPLATE_ID).strip()
    requested_view = (view or SUPPORTED_VIEW).strip().lower()
    template_registry = registry or TEMPLATE_REGISTRY
    record = template_registry.resolve(requested_template)
    warnings: list[str] = []

    if record is None:
        warnings.append(
            "Unsupported vehicle template "
            f"'{requested_template}' normalized to '{SUPPORTED_TEMPLATE_ID}'.",
        )
        record = template_registry.default_record()

    if requested_view != record.view:
        warnings.append(
            f"Unsupported view '{requested_view}' normalized to '{record.view}'.",
        )

    return TemplateResolution(
        canvas_height=record.canvas_height,
        canvas_width=record.canvas_width,
        safe_zones=[dict(zone) for zone in record.safe_zones],
        template_id=record.id,
        template_label=record.label,
        template_readiness=evaluate_template_readiness(record),
        template_source=record.source,
        view=record.view,
        warnings=warnings,
    )


def supported_safe_zones() -> list[SafeZone]:
    return [dict(zone) for zone in TEMPLATE_REGISTRY.default_record().safe_zones]


def template_source_metadata_from_mapping(
    value: Mapping[str, object],
) -> TemplateSourceMetadata:
    return TemplateSourceMetadata.model_validate(dict(value))
