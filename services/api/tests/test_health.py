from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

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
        entry["status"] in {"ok", "unavailable", "not_configured"}
        for entry in payload["dependencies"]
    )


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
