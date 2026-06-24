from __future__ import annotations

from typing import Annotated
from uuid import UUID

from caragent_core.models import Asset
from caragent_core.services import assets, workspaces
from caragent_core.storage import ObjectStorage
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from caragent_api.dependencies import (
    CurrentUser,
    CurrentUserDependency,
    OwnedWorkspaceDependency,
    SessionDependency,
    get_object_storage,
    require_workspace_owner,
)
from caragent_api.schemas import AssetResponse, AssetRightsUpdateRequest

router = APIRouter(tags=["assets"])

StorageDependency = Annotated[ObjectStorage, Depends(get_object_storage)]
UploadedFile = Annotated[UploadFile, File()]
AssetKindForm = Annotated[str, Form()]


def asset_not_found(error: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="asset not found")


def workspace_not_found(error: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workspace not found")


def asset_validation_failed(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=str(error),
    )


@router.post(
    "/workspaces/{workspace_id}/assets",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_asset(
    workspace_id: UUID,
    session: SessionDependency,
    storage: StorageDependency,
    file: UploadedFile,
    _workspace: OwnedWorkspaceDependency,
    kind: AssetKindForm = "reference",
) -> AssetResponse:
    try:
        asset = await assets.create_asset(
            session,
            storage,
            workspace_id,
            byte_content=await file.read(),
            content_type=file.content_type or "application/octet-stream",
            filename=file.filename or "upload",
            kind=kind,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except assets.AssetValidationError as error:
        raise asset_validation_failed(error) from error
    return AssetResponse.model_validate(asset)


@router.get("/workspaces/{workspace_id}/assets", response_model=list[AssetResponse])
async def list_assets(
    workspace_id: UUID,
    session: SessionDependency,
    _workspace: OwnedWorkspaceDependency,
) -> list[AssetResponse]:
    try:
        asset_rows = await assets.list_assets(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [AssetResponse.model_validate(asset) for asset in asset_rows]


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: UUID,
    session: SessionDependency,
    current_user: CurrentUserDependency,
) -> AssetResponse:
    try:
        asset = await _get_owned_asset(session, asset_id, current_user)
    except assets.AssetNotFoundError as error:
        raise asset_not_found(error) from error
    return AssetResponse.model_validate(asset)


@router.patch("/assets/{asset_id}/rights", response_model=AssetResponse)
async def update_asset_rights(
    asset_id: UUID,
    payload: AssetRightsUpdateRequest,
    session: SessionDependency,
    current_user: CurrentUserDependency,
) -> AssetResponse:
    try:
        await _get_owned_asset(session, asset_id, current_user)
        asset = await assets.update_asset_rights(
            session,
            asset_id,
            rights_notes=payload.rights_notes,
            rights_status=payload.rights_status,
            source_label=payload.source_label,
            source_url=payload.source_url,
        )
    except assets.AssetNotFoundError as error:
        raise asset_not_found(error) from error
    except assets.AssetValidationError as error:
        raise asset_validation_failed(error) from error
    return AssetResponse.model_validate(asset)


async def _get_owned_asset(
    session: SessionDependency,
    asset_id: UUID,
    current_user: CurrentUser,
) -> Asset:
    asset = await assets.get_asset(session, asset_id)
    try:
        workspace = await workspaces.get_workspace(session, asset.workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise assets.AssetNotFoundError(f"Asset workspace not found: {asset_id}") from error
    require_workspace_owner(workspace, current_user)
    return asset