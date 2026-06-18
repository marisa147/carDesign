from __future__ import annotations

import hashlib
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_core.enums import AssetKind, RightsStatus
from caragent_core.models import Asset, utc_now
from caragent_core.services import workspaces
from caragent_core.storage import ObjectStorage, build_object_key, validate_upload


class AssetNotFoundError(LookupError):
    pass


class AssetValidationError(ValueError):
    pass


class AssetRightsError(PermissionError):
    pass


async def create_asset(
    session: AsyncSession,
    storage: ObjectStorage,
    workspace_id: UUID,
    *,
    byte_content: bytes,
    content_type: str,
    filename: str,
    kind: str,
) -> Asset:
    await workspaces.get_workspace(session, workspace_id)

    normalized_kind = kind.strip().lower()
    if normalized_kind not in {asset_kind.value for asset_kind in AssetKind}:
        raise AssetValidationError(f"Unsupported asset kind: {kind}")

    try:
        validate_upload(
            byte_size=len(byte_content),
            content_type=content_type,
            filename=filename,
        )
    except ValueError as error:
        raise AssetValidationError(str(error)) from error

    asset_id = uuid4()
    object_key = build_object_key(
        filename=filename,
        kind=normalized_kind,
        record_id=asset_id,
        workspace_id=workspace_id,
    )
    await storage.put_object(object_key, byte_content, content_type)

    asset = Asset(
        byte_size=len(byte_content),
        checksum_sha256=hashlib.sha256(byte_content).hexdigest(),
        content_type=content_type,
        id=asset_id,
        kind=normalized_kind,
        object_key=object_key,
        original_filename=filename,
        rights_status=RightsStatus.MISSING.value,
        workspace_id=workspace_id,
    )
    session.add(asset)
    await session.flush()
    return asset


async def get_asset(session: AsyncSession, asset_id: UUID) -> Asset:
    asset = await session.get(Asset, asset_id)
    if asset is None:
        raise AssetNotFoundError(f"Asset not found: {asset_id}")
    return asset


async def update_asset_rights(
    session: AsyncSession,
    asset_id: UUID,
    *,
    rights_status: str,
    source_label: str | None = None,
    source_url: str | None = None,
    rights_notes: str | None = None,
) -> Asset:
    asset = await get_asset(session, asset_id)
    normalized_status = rights_status.strip().lower()
    if normalized_status not in {status.value for status in RightsStatus}:
        raise AssetValidationError(f"Unsupported rights status: {rights_status}")

    if normalized_status == RightsStatus.CONFIRMED.value and not (source_label or source_url):
        raise AssetValidationError("Confirmed rights require source_label or source_url")

    asset.rights_status = normalized_status
    asset.source_label = source_label
    asset.source_url = source_url
    asset.rights_notes = rights_notes
    asset.rights_confirmed_at = (
        utc_now() if normalized_status == RightsStatus.CONFIRMED.value else None
    )
    await session.flush()
    return asset


async def require_confirmed_rights(session: AsyncSession, asset_id: UUID) -> Asset:
    asset = await get_asset(session, asset_id)
    if asset.rights_status != RightsStatus.CONFIRMED.value:
        raise AssetRightsError(f"Asset rights are not confirmed: {asset_id}")
    return asset


async def list_assets(session: AsyncSession, workspace_id: UUID) -> list[Asset]:
    await workspaces.get_workspace(session, workspace_id)
    result = await session.scalars(
        select(Asset)
        .where(Asset.workspace_id == workspace_id)
        .order_by(Asset.created_at.asc()),
    )
    return list(result)
