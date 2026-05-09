from pathlib import Path

import pytest
from pydantic import ValidationError

from caragent_worker.config import WorkerSettings


ENV_KEYS = (
    "RUNTIME_MODE",
    "REDIS_URL",
    "AI_PROVIDER_DEFAULT",
    "AI_PROVIDER_CALLS_ENABLED",
    "AI_PROVIDER_OPENAI_API_KEY",
    "AI_PROVIDER_FAL_API_KEY",
    "AI_PROVIDER_BFL_API_KEY",
    "OPENAI_API_KEY",
    "STABILITY_API_KEY",
    "FAL_API_KEY",
    "REPLICATE_API_TOKEN",
)


def clear_worker_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_worker_settings_parse_runtime_redis_and_provider_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_worker_env(monkeypatch)
    monkeypatch.setenv("RUNTIME_MODE", "local")
    monkeypatch.setenv("REDIS_URL", "redis://redis.example:6379/4")
    monkeypatch.setenv("AI_PROVIDER_DEFAULT", "openai")
    monkeypatch.setenv("AI_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("AI_PROVIDER_OPENAI_API_KEY", "openai-secret")
    monkeypatch.setenv("AI_PROVIDER_FAL_API_KEY", "fal-secret")
    monkeypatch.setenv("AI_PROVIDER_BFL_API_KEY", "bfl-secret")

    settings = WorkerSettings()

    assert settings.runtime_mode == "local"
    assert settings.redis_url == "redis://redis.example:6379/4"
    assert settings.ai_provider_default == "openai"
    assert settings.ai_provider_calls_enabled is True
    assert settings.ai_provider_openai_api_key is not None
    assert settings.ai_provider_openai_api_key.get_secret_value() == "openai-secret"
    assert settings.ai_provider_fal_api_key is not None
    assert settings.ai_provider_fal_api_key.get_secret_value() == "fal-secret"
    assert settings.ai_provider_bfl_api_key is not None
    assert settings.ai_provider_bfl_api_key.get_secret_value() == "bfl-secret"


def test_worker_settings_load_documented_service_env_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    clear_worker_env(monkeypatch)
    (tmp_path / ".env").write_text(
        "\n".join(
            [
                "RUNTIME_MODE=development",
                "REDIS_URL=redis://redis.internal:6379/5",
                "AI_PROVIDER_DEFAULT=bfl",
                "AI_PROVIDER_CALLS_ENABLED=true",
                "AI_PROVIDER_OPENAI_API_KEY=worker-openai-secret",
                "AI_PROVIDER_FAL_API_KEY=worker-fal-secret",
                "AI_PROVIDER_BFL_API_KEY=worker-bfl-secret",
            ],
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    settings = WorkerSettings()

    assert settings.runtime_mode == "development"
    assert settings.redis_url == "redis://redis.internal:6379/5"
    assert settings.ai_provider_default == "bfl"
    assert settings.ai_provider_calls_enabled is True
    assert settings.ai_provider_openai_api_key is not None
    assert settings.ai_provider_openai_api_key.get_secret_value() == "worker-openai-secret"
    assert settings.ai_provider_fal_api_key is not None
    assert settings.ai_provider_fal_api_key.get_secret_value() == "worker-fal-secret"
    assert settings.ai_provider_bfl_api_key is not None
    assert settings.ai_provider_bfl_api_key.get_secret_value() == "worker-bfl-secret"


def test_legacy_provider_env_names_do_not_configure_worker_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_worker_env(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "legacy-openai-secret")
    monkeypatch.setenv("STABILITY_API_KEY", "legacy-stability-secret")
    monkeypatch.setenv("FAL_API_KEY", "legacy-fal-secret")
    monkeypatch.setenv("REPLICATE_API_TOKEN", "legacy-replicate-secret")

    settings = WorkerSettings()

    assert settings.ai_provider_default == "disabled"
    assert settings.ai_provider_calls_enabled is False
    assert settings.ai_provider_openai_api_key is None
    assert settings.ai_provider_fal_api_key is None
    assert settings.ai_provider_bfl_api_key is None


def test_worker_settings_redact_provider_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_worker_env(monkeypatch)
    monkeypatch.setenv("RUNTIME_MODE", "local")
    monkeypatch.setenv("AI_PROVIDER_DEFAULT", "fal")
    monkeypatch.setenv("AI_PROVIDER_CALLS_ENABLED", "true")
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
    clear_worker_env(monkeypatch)
    monkeypatch.setenv("RUNTIME_MODE", "production")

    with pytest.raises(ValidationError, match="REDIS_URL is required for non-local runtime modes"):
        WorkerSettings()
