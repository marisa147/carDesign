from __future__ import annotations

from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from caragent_api import __version__
from caragent_api.config import ApiSettings, get_settings

DependencyStatus = Literal["ok", "unavailable", "not_configured"]


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
        return DependencyHealth(name=name, status="ok", detail="configured")
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
    app = FastAPI(
        title="carAgent API",
        version=__version__,
        summary="Control-plane API foundation for the carAgent workbench.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_credentials=active_settings.cors_allow_credentials,
        allow_methods=["GET"],
        allow_headers=["Authorization", "Content-Type"],
    )

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
