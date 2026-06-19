from __future__ import annotations

from typing import Annotated

from caragent_core.generation import (
    VehicleTemplateRecord,
    evaluate_template_readiness,
    list_vehicle_templates,
    template_asset_resource,
)
from fastapi import APIRouter, HTTPException, Query, Response, status

from caragent_api.schemas import (
    TemplateCatalogItemResponse,
    TemplateDetailResponse,
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
        records = [record for record in records if record.view == normalized_view]
    if catalog_eligible is not None:
        records = [
            record
            for record in records
            if evaluate_template_readiness(record).catalog_eligible is catalog_eligible
        ]
    return [_catalog_item(record) for record in records]


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
        supported_views=[record.view],
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
