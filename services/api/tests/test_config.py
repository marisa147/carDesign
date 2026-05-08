from __future__ import annotations

import pytest
from pydantic import ValidationError

from caragent_api.config import ApiSettings


ENV_KEYS = (
    "DATABASE_URL",
    "REDIS_URL",
    "S3_ENDPOINT_URL",
    "S3_ACCESS_KEY_ID",
    "S3_SECRET_ACCESS_KEY",
    "S3_BUCKET",
    "CORS_ORIGINS",
    "RUNTIME_MODE",
    "AI_PROVIDER_OPENAI_API_KEY",
    "AI_PROVIDER_FAL_API_KEY",
    "AI_PROVIDER_BFL_API_KEY",
)


def clear_api_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_settings_parse_required_foundation_env(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_api_env(monkeypatch)
    monkeypatch.setenv("RUNTIME_MODE", "development")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://api:api@db.example/caragent")
    monkeypatch.setenv("REDIS_URL", "redis://redis.example:6379/1")
    monkeypatch.setenv("S3_ENDPOINT_URL", "https://storage.example")
    monkeypatch.setenv("S3_ACCESS_KEY_ID", "example-access-key")
    monkeypatch.setenv("S3_SECRET_ACCESS_KEY", "example-s3-secret")
    monkeypatch.setenv("S3_BUCKET", "caragent-test-artifacts")
    monkeypatch.setenv("CORS_ORIGINS", "https://app.example,https://admin.example")
    monkeypatch.setenv("AI_PROVIDER_OPENAI_API_KEY", "openai-secret")
    monkeypatch.setenv("AI_PROVIDER_FAL_API_KEY", "fal-secret")
    monkeypatch.setenv("AI_PROVIDER_BFL_API_KEY", "bfl-secret")

    settings = ApiSettings()

    assert settings.runtime_mode == "development"
    assert settings.database_url == "postgresql+asyncpg://api:api@db.example/caragent"
    assert settings.redis_url == "redis://redis.example:6379/1"
    assert settings.s3_endpoint_url == "https://storage.example"
    assert settings.s3_access_key_id == "example-access-key"
    assert settings.s3_secret_access_key.get_secret_value() == "example-s3-secret"
    assert settings.s3_bucket == "caragent-test-artifacts"
    assert settings.cors_origins == ["https://app.example", "https://admin.example"]
    assert settings.ai_provider_openai_api_key is not None
    assert settings.ai_provider_openai_api_key.get_secret_value() == "openai-secret"
    assert settings.ai_provider_fal_api_key is not None
    assert settings.ai_provider_fal_api_key.get_secret_value() == "fal-secret"
    assert settings.ai_provider_bfl_api_key is not None
    assert settings.ai_provider_bfl_api_key.get_secret_value() == "bfl-secret"


def test_non_local_runtime_rejects_wildcard_cors(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_api_env(monkeypatch)
    monkeypatch.setenv("RUNTIME_MODE", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://api:api@db.example/caragent")
    monkeypatch.setenv("REDIS_URL", "redis://redis.example:6379/1")
    monkeypatch.setenv("S3_ENDPOINT_URL", "https://storage.example")
    monkeypatch.setenv("S3_ACCESS_KEY_ID", "example-access-key")
    monkeypatch.setenv("S3_SECRET_ACCESS_KEY", "example-s3-secret")
    monkeypatch.setenv("S3_BUCKET", "caragent-test-artifacts")
    monkeypatch.setenv("CORS_ORIGINS", "*")

    with pytest.raises(ValidationError, match="Wildcard CORS"):
        ApiSettings()


def test_settings_repr_masks_secret_values(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_api_env(monkeypatch)
    monkeypatch.setenv("S3_SECRET_ACCESS_KEY", "super-secret-s3-value")
    monkeypatch.setenv("AI_PROVIDER_OPENAI_API_KEY", "super-secret-provider-value")

    settings = ApiSettings()
    rendered = f"{settings!s}\n{settings!r}"

    assert "super-secret-s3-value" not in rendered
    assert "super-secret-provider-value" not in rendered
    assert "**********" in rendered
