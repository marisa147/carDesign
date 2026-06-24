from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, cast
from uuid import UUID

from caragent_core.database import session_scope
from caragent_core.models import Workspace
from caragent_core.services import workspaces
from caragent_core.storage import ObjectStorage
from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from caragent_api.queue import QueueClient

LOCAL_USER_ID = "local-user"


@dataclass(frozen=True, slots=True)
class CurrentUser:
    id: str


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with session_scope(session_factory) as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def get_current_user(
    x_caragent_user: Annotated[str | None, Header(alias="X-CarAgent-User")] = None,
) -> CurrentUser:
    user_id = (x_caragent_user or LOCAL_USER_ID).strip()
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="current user is required",
        )
    return CurrentUser(id=user_id[:128])


CurrentUserDependency = Annotated[CurrentUser, Depends(get_current_user)]


async def get_owned_workspace(
    workspace_id: UUID,
    session: SessionDependency,
    current_user: CurrentUserDependency,
) -> Workspace:
    try:
        workspace = await workspaces.get_workspace(session, workspace_id)
    except workspaces.WorkspaceNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="workspace not found",
        ) from error
    require_workspace_owner(workspace, current_user)
    return workspace


OwnedWorkspaceDependency = Annotated[Workspace, Depends(get_owned_workspace)]


def require_workspace_owner(workspace: Workspace, current_user: CurrentUser) -> None:
    if workspace.owner_id and workspace.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="workspace access denied",
        )


def get_object_storage(request: Request) -> ObjectStorage:
    return cast(ObjectStorage, request.app.state.object_storage)


def get_queue_client(request: Request) -> QueueClient:
    return cast(QueueClient, request.app.state.queue_client)