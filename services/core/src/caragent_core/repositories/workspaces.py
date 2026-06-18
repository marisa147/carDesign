from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from caragent_core.models import DesignBrief, Message, Workspace


async def get_workspace(session: AsyncSession, workspace_id: UUID) -> Workspace | None:
    return await session.get(Workspace, workspace_id)


async def next_message_sequence(session: AsyncSession, workspace_id: UUID) -> int:
    statement = select(func.max(Message.sequence)).where(
        Message.workspace_id == workspace_id,
    )
    value = await session.scalar(statement)
    return (value or 0) + 1


async def list_messages(session: AsyncSession, workspace_id: UUID) -> list[Message]:
    result = await session.scalars(
        select(Message)
        .where(Message.workspace_id == workspace_id)
        .order_by(Message.sequence.asc(), Message.created_at.asc()),
    )
    return list(result)


async def list_design_briefs(session: AsyncSession, workspace_id: UUID) -> list[DesignBrief]:
    result = await session.scalars(
        select(DesignBrief)
        .where(DesignBrief.workspace_id == workspace_id)
        .order_by(DesignBrief.created_at.asc()),
    )
    return list(result)
