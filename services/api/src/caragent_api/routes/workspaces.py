from __future__ import annotations

from typing import Annotated
from uuid import UUID

from caragent_core.services import workspaces
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_api.dependencies import get_db_session
from caragent_api.schemas import (
    DesignBriefCreateRequest,
    DesignBriefResponse,
    MessageCreateRequest,
    MessageResponse,
    WorkspaceCreateRequest,
    WorkspaceResponse,
)

router = APIRouter(tags=["workspaces"])

SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def workspace_not_found(error: Exception) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="workspace not found")


def workspace_validation_failed(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail=str(error),
    )


@router.post(
    "/workspaces",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    payload: WorkspaceCreateRequest,
    session: SessionDependency,
) -> WorkspaceResponse:
    workspace = await workspaces.create_workspace(
        session,
        owner_id=payload.owner_id,
        title=payload.title,
    )
    return WorkspaceResponse.model_validate(workspace)


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(workspace_id: UUID, session: SessionDependency) -> WorkspaceResponse:
    try:
        workspace = await workspaces.get_workspace(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return WorkspaceResponse.model_validate(workspace)


@router.post(
    "/workspaces/{workspace_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    workspace_id: UUID,
    payload: MessageCreateRequest,
    session: SessionDependency,
) -> MessageResponse:
    try:
        message = await workspaces.create_message(
            session,
            workspace_id,
            content=payload.content,
            role=payload.role,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except workspaces.WorkspaceValidationError as error:
        raise workspace_validation_failed(error) from error
    return MessageResponse.model_validate(message)


@router.get("/workspaces/{workspace_id}/messages", response_model=list[MessageResponse])
async def list_messages(workspace_id: UUID, session: SessionDependency) -> list[MessageResponse]:
    try:
        messages = await workspaces.list_messages(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [MessageResponse.model_validate(message) for message in messages]


@router.post(
    "/workspaces/{workspace_id}/briefs",
    response_model=DesignBriefResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_design_brief(
    workspace_id: UUID,
    payload: DesignBriefCreateRequest,
    session: SessionDependency,
) -> DesignBriefResponse:
    try:
        brief = await workspaces.create_design_brief(
            session,
            workspace_id,
            payload=payload.payload,
            title=payload.title,
            source_message_id=payload.source_message_id,
        )
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    except workspaces.WorkspaceValidationError as error:
        raise workspace_validation_failed(error) from error
    return DesignBriefResponse.model_validate(brief)


@router.get("/workspaces/{workspace_id}/briefs", response_model=list[DesignBriefResponse])
async def list_design_briefs(
    workspace_id: UUID,
    session: SessionDependency,
) -> list[DesignBriefResponse]:
    try:
        briefs = await workspaces.list_design_briefs(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise workspace_not_found(error) from error
    return [DesignBriefResponse.model_validate(brief) for brief in briefs]
