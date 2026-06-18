import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from caragent_worker.config import WorkerSettings

ENV_KEYS = (
    "RUNTIME_MODE",
    "REDIS_URL",
    "AI_PROVIDER_DEFAULT",
    "AI_PROVIDER_MODEL",
    "AI_PROVIDER_CALLS_ENABLED",
    "AI_GENERATION_MAX_ATTEMPTS",
    "AI_PROVIDER_FALLBACK_ENABLED",
    "AI_PROVIDER_FALLBACK_NAME",
    "AI_HOSTED_DAILY_CALL_LIMIT",
    "AI_HOSTED_RATE_LIMIT_PER_MINUTE",
    "AI_MAX_ESTIMATED_COST_PER_JOB",
    "AI_PROVIDER_OPENAI_API_KEY",
    "AI_PROVIDER_FAL_API_KEY",
    "AI_PROVIDER_BFL_API_KEY",
    "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED",
    "V2_TARGETED_REGENERATION_ENABLED",
    "V2_REFERENCE_GUIDANCE_ENABLED",
    "V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED",
    "V2_ENHANCED_HANDOFF_PACKAGE_ENABLED",
    "OPENAI_API_KEY",
    "STABILITY_API_KEY",
    "FAL_API_KEY",
    "REPLICATE_API_TOKEN",
)


def clear_worker_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_worker_settings_parse_runtime_redis_and_provider_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_worker_env(monkeypatch)
    monkeypatch.setenv("RUNTIME_MODE", "local")
    monkeypatch.setenv("REDIS_URL", "redis://redis.example:6379/4")
    monkeypatch.setenv("AI_PROVIDER_DEFAULT", "openai")
    monkeypatch.setenv("AI_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("AI_GENERATION_MAX_ATTEMPTS", "3")
    monkeypatch.setenv("AI_PROVIDER_FALLBACK_ENABLED", "true")
    monkeypatch.setenv("AI_PROVIDER_FALLBACK_NAME", "local-deterministic")
    monkeypatch.setenv("AI_HOSTED_DAILY_CALL_LIMIT", "25")
    monkeypatch.setenv("AI_HOSTED_RATE_LIMIT_PER_MINUTE", "4")
    monkeypatch.setenv("AI_MAX_ESTIMATED_COST_PER_JOB", "0.7500")
    monkeypatch.setenv("AI_PROVIDER_OPENAI_API_KEY", "openai-secret")
    monkeypatch.setenv("AI_PROVIDER_FAL_API_KEY", "fal-secret")
    monkeypatch.setenv("AI_PROVIDER_BFL_API_KEY", "bfl-secret")

    settings = WorkerSettings()

    assert settings.runtime_mode == "local"
    assert settings.redis_url == "redis://redis.example:6379/4"
    assert settings.ai_provider_default == "openai"
    assert settings.ai_provider_calls_enabled is True
    assert settings.ai_generation_max_attempts == 3
    assert settings.ai_provider_fallback_enabled is True
    assert settings.ai_provider_fallback_name == "local-deterministic"
    assert settings.ai_hosted_daily_call_limit == 25
    assert settings.ai_hosted_rate_limit_per_minute == 4
    assert str(settings.ai_max_estimated_cost_per_job) == "0.7500"
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


def test_worker_settings_reports_hosted_provider_configured() -> None:
    local_settings = WorkerSettings()
    hosted_settings = WorkerSettings(
        ai_provider_bfl_api_key="bfl-secret",
        ai_provider_calls_enabled=True,
        ai_provider_default="bfl",
    )

    assert local_settings.hosted_provider_configured is False
    assert hosted_settings.hosted_provider_configured is True
    assert "bfl-secret" not in str(hosted_settings.hosted_provider_configured)


def test_worker_settings_default_attempt_policy_is_safe_for_local_mode() -> None:
    settings = WorkerSettings()

    assert settings.ai_generation_max_attempts == 1
    assert settings.ai_provider_fallback_enabled is False
    assert settings.ai_provider_fallback_name == "local-deterministic"
    assert settings.ai_hosted_daily_call_limit is None
    assert settings.ai_hosted_rate_limit_per_minute is None
    assert settings.ai_max_estimated_cost_per_job is None


def test_worker_v2_readiness_flags_default_off_in_local_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_worker_env(monkeypatch)

    settings = WorkerSettings()

    assert settings.v2_hosted_provider_rollout_enabled is False
    assert settings.v2_targeted_regeneration_enabled is False
    assert settings.v2_reference_guidance_enabled is False
    assert settings.v2_lightweight_3d_preview_enabled is False
    assert settings.v2_enhanced_handoff_package_enabled is False
    assert settings.ai_provider_calls_enabled is False
    assert settings.ai_provider_openai_api_key is None
    assert settings.ai_provider_fal_api_key is None
    assert settings.ai_provider_bfl_api_key is None


def test_worker_settings_expose_safe_provider_capabilities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_worker_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER_DEFAULT", "bfl")
    monkeypatch.setenv("AI_PROVIDER_MODEL", "flux-2-pro-preview")
    monkeypatch.setenv("AI_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("AI_PROVIDER_BFL_API_KEY", "bfl-secret")
    monkeypatch.setenv("V2_HOSTED_PROVIDER_ROLLOUT_ENABLED", "true")
    monkeypatch.setenv("AI_HOSTED_DAILY_CALL_LIMIT", "10")
    monkeypatch.setenv("AI_HOSTED_RATE_LIMIT_PER_MINUTE", "2")
    monkeypatch.setenv("AI_MAX_ESTIMATED_COST_PER_JOB", "0.2500")

    settings = WorkerSettings()

    assert hasattr(settings, "provider_capability_map")
    capabilities = settings.provider_capability_map()
    assert set(capabilities) == {"local-deterministic", "bfl"}
    assert capabilities["local-deterministic"]["enabled"] is True
    assert capabilities["local-deterministic"]["credential_required"] is False
    assert capabilities["bfl"]["enabled"] is True
    assert capabilities["bfl"]["credential_configured"] is True
    assert capabilities["bfl"]["default_model"] == "flux-2-pro-preview"
    assert capabilities["bfl"]["guard_state"] == {
        "daily_call_limit": 10,
        "hosted_quota_guard_enabled": True,
        "max_estimated_cost_per_job": "0.2500",
        "rate_limit_per_minute": 2,
    }
    assert "bfl-secret" not in json.dumps(capabilities, sort_keys=True)


def test_worker_settings_block_hosted_capability_without_secrets_or_guards() -> None:
    settings = WorkerSettings(ai_provider_default="bfl")

    bfl = settings.provider_capability_map()["bfl"]

    assert bfl["enabled"] is False
    assert bfl["credential_configured"] is False
    assert "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED is disabled" in bfl["blocked_reasons"]
    assert "AI_PROVIDER_CALLS_ENABLED is disabled" in bfl["blocked_reasons"]
    assert "AI_PROVIDER_BFL_API_KEY is missing" in bfl["blocked_reasons"]
    assert "Hosted quota/rate/cost guards are incomplete" in bfl["blocked_reasons"]


def test_worker_settings_rejects_zero_quota_and_rate_limits() -> None:
    with pytest.raises(ValidationError):
        WorkerSettings(ai_hosted_daily_call_limit=0)
    with pytest.raises(ValidationError):
        WorkerSettings(ai_hosted_rate_limit_per_minute=0)
    with pytest.raises(ValidationError):
        WorkerSettings(ai_max_estimated_cost_per_job="0")


def test_worker_settings_rejects_unsupported_fallback_provider() -> None:
    with pytest.raises(ValidationError, match="Unsupported AI_PROVIDER_FALLBACK_NAME"):
        WorkerSettings(
            ai_provider_fallback_enabled=True,
            ai_provider_fallback_name="openai",
        )


def test_non_local_runtime_requires_explicit_redis_url(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_worker_env(monkeypatch)
    monkeypatch.setenv("RUNTIME_MODE", "production")

    with pytest.raises(ValidationError, match="REDIS_URL is required for non-local runtime modes"):
        WorkerSettings()
