from __future__ import annotations

from sqlalchemy import text

from caragent_core import __version__
from caragent_core.database import (
    create_engine,
    create_session_factory,
    redact_database_url,
    session_scope,
)
from caragent_core.models import metadata


def test_core_package_exports_version() -> None:
    assert __version__ == "0.1.0"


def test_models_expose_shared_metadata() -> None:
    assert "workspaces" in metadata.tables


async def test_database_helpers_create_async_session() -> None:
    engine = create_engine("sqlite+aiosqlite:///:memory:")
    session_factory = create_session_factory(engine)

    async with session_scope(session_factory) as session:
        result = await session.execute(text("select 1"))

    await engine.dispose()

    assert result.scalar_one() == 1


def test_redact_database_url_hides_password() -> None:
    rendered = redact_database_url(
        "postgresql+asyncpg://caragent:secret-password@localhost:5432/caragent",
    )

    assert "secret-password" not in rendered
    assert "***" in rendered
