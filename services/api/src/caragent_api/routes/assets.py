from __future__ import annotations

from typing import Annotated
from uuid import UUID

from caragent_core.services import assets, workspaces
from caragent_core.storage import ObjectStorage
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_api.dependencies import get_db_session, get_object_storage
from caragent_api.schemas import AssetResponse, AssetRightsUpdateRequest

router = APIRouter(tags=["assets"])

SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]
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
async def list_assets(workspace_id: UUID, session: SessionDependency) -> list[AssetResponse]:
    try:
        asset_rows = await assets.list_assets(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [AssetResponse.model_validate(asset) for asset in asset_rows]


@router.get("/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: UUID, session: SessionDependency) -> AssetResponse:
    try:
        asset = await assets.get_asset(session, asset_id)
    except assets.AssetNotFoundError as error:
        raise asset_not_found(error) from error
    return AssetResponse.model_validate(asset)


@router.patch("/assets/{asset_id}/rights", response_model=AssetResponse)
async def update_asset_rights(
    asset_id: UUID,
    payload: AssetRightsUpdateRequest,
    session: SessionDependency,
) -> AssetResponse:
    try:
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
