from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from caragent_api.config import ApiSettings
from caragent_api.config import get_settings
from caragent_api.main import create_app


HEALTH_DEPENDENCIES = {"database", "redis", "object_storage", "worker", "contracts"}


@pytest.fixture(autouse=True)
def clear_settings_cache() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_health_returns_typed_foundation_status() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["runtime_mode"] == "local"
    assert payload["api_version"] == "0.1.0"
    assert {entry["name"] for entry in payload["dependencies"]} == HEALTH_DEPENDENCIES
    assert all(
        entry["status"] in {"ok", "configured", "unavailable", "not_configured"}
        for entry in payload["dependencies"]
    )


def test_health_marks_configured_local_services_without_live_success() -> None:
    secret_values = {
        "db-secret-password",
        "redis-secret-password",
        "minio-secret-value",
    }
    settings = ApiSettings(
        database_url=(
            "postgresql+asyncpg://caragent:db-secret-password@localhost:5432/caragent"
        ),
        redis_url="redis://:redis-secret-password@localhost:6379/0",
        s3_endpoint_url="http://localhost:9000",
        s3_access_key_id="caragent-local",
        s3_secret_access_key=SecretStr("minio-secret-value"),
        s3_bucket="caragent-artifacts",
    )
    client = TestClient(create_app(settings))

    response = client.get("/health")

    assert response.status_code == 200
    response_text = response.text
    dependencies = dependencies_by_name(response.json())
    for name in ["database", "redis", "object_storage"]:
        assert dependencies[name]["status"] == "configured"
        assert dependencies[name]["status"] != "ok"
        assert "pnpm smoke:local" in dependencies[name]["detail"]

    for secret_value in secret_values:
        assert secret_value not in response_text


def test_health_marks_missing_local_service_config_as_not_configured() -> None:
    settings = ApiSettings(
        database_url="",
        redis_url="",
        s3_endpoint_url="",
        s3_access_key_id="",
        s3_secret_access_key=SecretStr(""),
        s3_bucket="",
    )
    client = TestClient(create_app(settings))

    response = client.get("/health")

    assert response.status_code == 200
    dependencies = dependencies_by_name(response.json())
    for name in ["database", "redis", "object_storage"]:
        assert dependencies[name]["status"] == "not_configured"


def test_cors_uses_configured_origins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "https://app.example")
    monkeypatch.setenv("CORS_ALLOW_CREDENTIALS", "true")
    get_settings.cache_clear()
    client = TestClient(create_app())

    allowed = client.options(
        "/health",
        headers={
            "Origin": "https://app.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    rejected = client.options(
        "/health",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert allowed.headers["access-control-allow-origin"] == "https://app.example"
    assert allowed.headers["access-control-allow-credentials"] == "true"
    assert "access-control-allow-origin" not in rejected.headers


def dependencies_by_name(payload: dict[str, object]) -> dict[str, dict[str, str]]:
    dependencies = payload["dependencies"]
    assert isinstance(dependencies, list)
    return {entry["name"]: entry for entry in dependencies}
