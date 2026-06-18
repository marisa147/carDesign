from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from caragent_core.database import create_engine, create_session_factory, session_scope
from caragent_core.enums import MessageRole
from caragent_core.models import metadata
from caragent_core.services import workspaces


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)

    yield create_session_factory(engine)

    await engine.dispose()


async def test_create_and_resume_workspace_across_sessions(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        created = await workspaces.create_workspace(session, title="Sakura GT86")
        workspace_id = created.id

    async with session_scope(session_factory) as session:
        resumed = await workspaces.get_workspace(session, workspace_id)

    assert resumed.id == workspace_id
    assert resumed.title == "Sakura GT86"
    assert resumed.status == "active"


async def test_append_and_list_workspace_messages_in_order(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Message history")
        await workspaces.create_message(
            session,
            workspace.id,
            role=MessageRole.USER.value,
            content="Make a pink racing itasha.",
        )
        await workspaces.create_message(
            session,
            workspace.id,
            role=MessageRole.ASSISTANT.value,
            content="Drafting a structured brief.",
        )

    async with session_scope(session_factory) as session:
        messages = await workspaces.list_messages(session, workspace.id)

    assert [message.sequence for message in messages] == [1, 2]
    assert [message.content for message in messages] == [
        "Make a pink racing itasha.",
        "Drafting a structured brief.",
    ]


async def test_create_and_list_structured_briefs(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Briefs")
        brief = await workspaces.create_design_brief(
            session,
            workspace.id,
            payload={"vehicle": "GT86", "palette": ["pink", "white"]},
            title="Initial brief",
        )

    async with session_scope(session_factory) as session:
        briefs = await workspaces.list_design_briefs(session, workspace.id)

    assert [item.id for item in briefs] == [brief.id]
    assert briefs[0].payload == {"vehicle": "GT86", "palette": ["pink", "white"]}


async def test_empty_message_content_is_rejected(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Validation")

        with pytest.raises(workspaces.WorkspaceValidationError, match="content"):
            await workspaces.create_message(session, workspace.id, role="user", content="  ")
