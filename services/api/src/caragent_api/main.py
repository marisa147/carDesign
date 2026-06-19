from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from caragent_core.database import create_engine, create_session_factory
from caragent_core.storage import FileObjectStorage
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from caragent_api import __version__
from caragent_api.config import ApiSettings, get_settings
from caragent_api.queue import CeleryQueueClient
from caragent_api.routes.assets import router as assets_router
from caragent_api.routes.generation import router as generation_router
from caragent_api.routes.jobs import router as jobs_router
from caragent_api.routes.operations import router as operations_router
from caragent_api.routes.templates import router as templates_router
from caragent_api.routes.workspaces import router as workspaces_router

DependencyStatus = Literal["ok", "configured", "unavailable", "not_configured"]


class DependencyHealth(BaseModel):
    name: str
    status: DependencyStatus
    detail: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    runtime_mode: str
    api_version: str
    dependencies: list[DependencyHealth]


def _configured_dependency(name: str, configured: bool) -> DependencyHealth:
    if configured:
        return DependencyHealth(
            name=name,
            status="configured",
            detail=("Dependency is configured; live validation is performed by pnpm smoke:local."),
        )
    return DependencyHealth(name=name, status="not_configured", detail="missing configuration")


def _build_dependency_health(settings: ApiSettings) -> list[DependencyHealth]:
    return [
        _configured_dependency("database", bool(settings.database_url)),
        _configured_dependency("redis", bool(settings.redis_url)),
        _configured_dependency(
            "object_storage",
            bool(
                settings.s3_endpoint_url
                and settings.s3_access_key_id
                and settings.s3_secret_access_key.get_secret_value()
                and settings.s3_bucket
            ),
        ),
        DependencyHealth(
            name="worker",
            status="not_configured",
            detail="Worker health is owned by services/worker.",
        ),
        DependencyHealth(
            name="contracts",
            status="ok",
            detail="OpenAPI export is available from this API app.",
        ),
    ]


def create_app(settings: ApiSettings | None = None) -> FastAPI:
    active_settings = settings or get_settings()
    database_engine = (
        create_engine(active_settings.database_url) if active_settings.database_url else None
    )

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        yield
        if database_engine is not None:
            await database_engine.dispose()

    app = FastAPI(
        title="carAgent API",
        version=__version__,
        summary="Control-plane API foundation for the carAgent workbench.",
        lifespan=lifespan,
    )
    if database_engine is not None:
        app.state.database_engine = database_engine
        app.state.session_factory = create_session_factory(database_engine)
    app.state.settings = active_settings
    app.state.object_storage = FileObjectStorage(Path(".cache/object-storage"))
    app.state.queue_client = CeleryQueueClient(
        database_url=active_settings.database_url,
        redis_url=active_settings.redis_url,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_credentials=active_settings.cors_allow_credentials,
        allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.include_router(workspaces_router)
    app.include_router(assets_router)
    app.include_router(jobs_router)
    app.include_router(generation_router)
    app.include_router(templates_router)
    app.include_router(operations_router)

    @app.get("/health", response_model=HealthResponse, tags=["health"])
    async def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            runtime_mode=active_settings.runtime_mode,
            api_version=active_settings.api_version,
            dependencies=_build_dependency_health(active_settings),
        )

    return app


app = create_app()
