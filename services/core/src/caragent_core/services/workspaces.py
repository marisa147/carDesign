from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from caragent_core.enums import DesignBriefStatus, MessageRole, WorkspaceStatus
from caragent_core.models import DesignBrief, Message, Workspace
from caragent_core.repositories import workspaces as workspace_repository


class WorkspaceNotFoundError(LookupError):
    pass


class WorkspaceValidationError(ValueError):
    pass


async def create_workspace(
    session: AsyncSession,
    *,
    title: str | None = None,
    owner_id: str | None = None,
) -> Workspace:
    workspace = Workspace(
        owner_id=owner_id,
        status=WorkspaceStatus.ACTIVE.value,
        title=(title or "Untitled workspace").strip() or "Untitled workspace",
    )
    session.add(workspace)
    await session.flush()
    return workspace


async def get_workspace(session: AsyncSession, workspace_id: UUID) -> Workspace:
    workspace = await workspace_repository.get_workspace(session, workspace_id)
    if workspace is None:
        raise WorkspaceNotFoundError(f"Workspace not found: {workspace_id}")
    return workspace


async def create_message(
    session: AsyncSession,
    workspace_id: UUID,
    *,
    role: str,
    content: str,
) -> Message:
    await get_workspace(session, workspace_id)

    normalized_role = role.strip().lower()
    allowed_roles = {item.value for item in MessageRole}
    if normalized_role not in allowed_roles:
        raise WorkspaceValidationError(f"Unsupported message role: {role}")

    normalized_content = content.strip()
    if not normalized_content:
        raise WorkspaceValidationError("Message content is required")

    message = Message(
        content=normalized_content,
        role=normalized_role,
        sequence=await workspace_repository.next_message_sequence(session, workspace_id),
        workspace_id=workspace_id,
    )
    session.add(message)
    await session.flush()
    return message


async def list_messages(session: AsyncSession, workspace_id: UUID) -> list[Message]:
    await get_workspace(session, workspace_id)
    return await workspace_repository.list_messages(session, workspace_id)


async def create_design_brief(
    session: AsyncSession,
    workspace_id: UUID,
    *,
    payload: dict[str, object],
    title: str | None = None,
    source_message_id: UUID | None = None,
) -> DesignBrief:
    await get_workspace(session, workspace_id)
    if not payload:
        raise WorkspaceValidationError("Design brief payload is required")

    brief = DesignBrief(
        payload=payload,
        source_message_id=source_message_id,
        status=DesignBriefStatus.DRAFT.value,
        title=(title or "").strip() or None,
        workspace_id=workspace_id,
    )
    session.add(brief)
    await session.flush()
    return brief


async def list_design_briefs(session: AsyncSession, workspace_id: UUID) -> list[DesignBrief]:
    await get_workspace(session, workspace_id)
    return await workspace_repository.list_design_briefs(session, workspace_id)
