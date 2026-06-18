from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import UUID

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from caragent_core.database import create_engine, create_session_factory, session_scope
from caragent_core.enums import AssetKind, RightsStatus
from caragent_core.models import metadata
from caragent_core.services import assets, workspaces
from caragent_core.storage import MAX_UPLOAD_BYTES, InMemoryObjectStorage, build_object_key


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)

    yield create_session_factory(engine)

    await engine.dispose()


def test_build_object_key_is_workspace_scoped_and_unique() -> None:
    workspace_id = UUID("00000000-0000-0000-0000-000000000123")
    first = build_object_key(
        workspace_id=workspace_id,
        kind=AssetKind.LOGO.value,
        record_id=UUID("00000000-0000-0000-0000-000000000001"),
        filename="Miku Logo!!.png",
    )
    second = build_object_key(
        workspace_id=workspace_id,
        kind=AssetKind.LOGO.value,
        record_id=UUID("00000000-0000-0000-0000-000000000002"),
        filename="Miku Logo!!.png",
    )

    assert first == (
        "workspaces/00000000-0000-0000-0000-000000000123/"
        "logo/00000000-0000-0000-0000-000000000001/miku-logo.png"
    )
    assert second != first


async def test_create_asset_validates_and_stores_metadata(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    storage = InMemoryObjectStorage()
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Assets")
        asset = await assets.create_asset(
            session,
            storage,
            workspace.id,
            byte_content=b"\x89PNG\r\n\x1a\nimage-bytes",
            content_type="image/png",
            filename="reference.png",
            kind=AssetKind.REFERENCE.value,
        )

    assert asset.object_key in storage.objects
    assert asset.byte_size == 19
    assert asset.checksum_sha256 is not None
    assert asset.rights_status == RightsStatus.MISSING.value


async def test_create_asset_rejects_unsupported_file_type(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    storage = InMemoryObjectStorage()
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Assets")

        with pytest.raises(assets.AssetValidationError, match="Unsupported"):
            await assets.create_asset(
                session,
                storage,
                workspace.id,
                byte_content=b"not an image",
                content_type="text/plain",
                filename="notes.txt",
                kind=AssetKind.REFERENCE.value,
            )


async def test_create_asset_rejects_too_large_file_before_storage_write(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    storage = InMemoryObjectStorage()
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Assets")

        with pytest.raises(assets.AssetValidationError, match="exceeds"):
            await assets.create_asset(
                session,
                storage,
                workspace.id,
                byte_content=b"x" * (MAX_UPLOAD_BYTES + 1),
                content_type="image/png",
                filename="large.png",
                kind=AssetKind.REFERENCE.value,
            )

    assert storage.objects == {}


async def test_rights_metadata_controls_asset_usability(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    storage = InMemoryObjectStorage()
    async with session_scope(session_factory) as session:
        workspace = await workspaces.create_workspace(session, title="Rights")
        asset = await assets.create_asset(
            session,
            storage,
            workspace.id,
            byte_content=b"\x89PNG\r\n\x1a\nimage-bytes",
            content_type="image/png",
            filename="reference.png",
            kind=AssetKind.REFERENCE.value,
        )

        with pytest.raises(assets.AssetRightsError):
            await assets.require_confirmed_rights(session, asset.id)

        updated = await assets.update_asset_rights(
            session,
            asset.id,
            rights_status=RightsStatus.CONFIRMED.value,
            source_label="User-provided reference",
            source_url="https://example.test/reference",
            rights_notes="User confirmed usage rights.",
        )
        usable = await assets.require_confirmed_rights(session, asset.id)

    assert updated.rights_status == RightsStatus.CONFIRMED.value
    assert updated.rights_confirmed_at is not None
    assert usable.id == asset.id
