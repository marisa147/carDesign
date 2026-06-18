from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast

from caragent_core.database import session_scope
from caragent_core.storage import ObjectStorage
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from caragent_api.queue import QueueClient


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    session_factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with session_scope(session_factory) as session:
        yield session


def get_object_storage(request: Request) -> ObjectStorage:
    return cast(ObjectStorage, request.app.state.object_storage)


def get_queue_client(request: Request) -> QueueClient:
    return cast(QueueClient, request.app.state.queue_client)
