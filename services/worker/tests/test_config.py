import pytest
from pydantic import ValidationError

from caragent_worker.config import WorkerSettings


def test_worker_settings_parse_runtime_redis_and_provider_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RUNTIME_MODE", "local")
    monkeypatch.setenv("REDIS_URL", "redis://redis.example:6379/4")
    monkeypatch.setenv("AI_PROVIDER_OPENAI_API_KEY", "openai-secret")
    monkeypatch.setenv("AI_PROVIDER_FAL_API_KEY", "fal-secret")
    monkeypatch.setenv("AI_PROVIDER_BFL_API_KEY", "bfl-secret")

    settings = WorkerSettings()

    assert settings.runtime_mode == "local"
    assert settings.redis_url == "redis://redis.example:6379/4"
    assert settings.ai_provider_openai_api_key is not None
    assert settings.ai_provider_openai_api_key.get_secret_value() == "openai-secret"
    assert settings.ai_provider_fal_api_key is not None
    assert settings.ai_provider_fal_api_key.get_secret_value() == "fal-secret"
    assert settings.ai_provider_bfl_api_key is not None
    assert settings.ai_provider_bfl_api_key.get_secret_value() == "bfl-secret"


def test_worker_settings_redact_provider_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RUNTIME_MODE", "local")
    monkeypatch.setenv("AI_PROVIDER_OPENAI_API_KEY", "raw-openai-secret")
    monkeypatch.setenv("AI_PROVIDER_FAL_API_KEY", "raw-fal-secret")
    monkeypatch.setenv("AI_PROVIDER_BFL_API_KEY", "raw-bfl-secret")

    settings = WorkerSettings()
    rendered = f"{settings!r}\n{settings}\n{settings.model_dump_json()}"

    assert "raw-openai-secret" not in rendered
    assert "raw-fal-secret" not in rendered
    assert "raw-bfl-secret" not in rendered
    assert "**********" in rendered


def test_non_local_runtime_requires_explicit_redis_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("RUNTIME_MODE", "production")
    monkeypatch.delenv("REDIS_URL", raising=False)

    with pytest.raises(ValidationError, match="REDIS_URL is required for non-local runtime modes"):
        WorkerSettings()
