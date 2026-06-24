from __future__ import annotations

import json
from pathlib import Path

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
    "AI_PROVIDER_DEFAULT",
    "AI_PROVIDER_MODEL",
    "AI_PROVIDER_OPENAI_IMAGE_MODEL",
    "AI_PROVIDER_CALLS_ENABLED",
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
    monkeypatch.setenv("AI_PROVIDER_DEFAULT", "openai")
    monkeypatch.setenv("AI_PROVIDER_CALLS_ENABLED", "true")
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
    assert settings.ai_provider_default == "openai"
    assert settings.ai_provider_model == "local-concept-v1"
    assert settings.ai_provider_calls_enabled is True
    assert settings.ai_provider_openai_api_key is not None
    assert settings.ai_provider_openai_api_key.get_secret_value() == "openai-secret"
    assert settings.ai_provider_fal_api_key is not None
    assert settings.ai_provider_fal_api_key.get_secret_value() == "fal-secret"
    assert settings.ai_provider_bfl_api_key is not None
    assert settings.ai_provider_bfl_api_key.get_secret_value() == "bfl-secret"


def test_settings_load_documented_service_env_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    clear_api_env(monkeypatch)
    (tmp_path / ".env").write_text(
        "\n".join(
            [
                "RUNTIME_MODE=development",
                "DATABASE_URL=postgresql+asyncpg://api:api@db.internal/caragent",
                "REDIS_URL=redis://redis.internal:6379/2",
                "S3_ENDPOINT_URL=https://objects.internal",
                "S3_ACCESS_KEY_ID=api-access-key",
                "S3_SECRET_ACCESS_KEY=api-secret-key",
                "S3_BUCKET=api-artifacts",
                "CORS_ORIGINS=https://app.internal,https://ops.internal",
                "AI_PROVIDER_DEFAULT=fal",
                "AI_PROVIDER_CALLS_ENABLED=true",
                "AI_PROVIDER_OPENAI_API_KEY=api-openai-secret",
                "AI_PROVIDER_FAL_API_KEY=api-fal-secret",
                "AI_PROVIDER_BFL_API_KEY=api-bfl-secret",
            ],
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    settings = ApiSettings()

    assert settings.runtime_mode == "development"
    assert settings.database_url == "postgresql+asyncpg://api:api@db.internal/caragent"
    assert settings.redis_url == "redis://redis.internal:6379/2"
    assert settings.s3_endpoint_url == "https://objects.internal"
    assert settings.s3_access_key_id == "api-access-key"
    assert settings.s3_secret_access_key.get_secret_value() == "api-secret-key"
    assert settings.s3_bucket == "api-artifacts"
    assert settings.cors_origins == ["https://app.internal", "https://ops.internal"]
    assert settings.ai_provider_default == "fal"
    assert settings.ai_provider_model == "local-concept-v1"
    assert settings.ai_provider_calls_enabled is True
    assert settings.ai_provider_openai_api_key is not None
    assert settings.ai_provider_openai_api_key.get_secret_value() == "api-openai-secret"
    assert settings.ai_provider_fal_api_key is not None
    assert settings.ai_provider_fal_api_key.get_secret_value() == "api-fal-secret"
    assert settings.ai_provider_bfl_api_key is not None
    assert settings.ai_provider_bfl_api_key.get_secret_value() == "api-bfl-secret"


def test_legacy_provider_env_names_do_not_configure_api_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_api_env(monkeypatch)
    monkeypatch.setenv("OPENAI_API_KEY", "legacy-openai-secret")
    monkeypatch.setenv("STABILITY_API_KEY", "legacy-stability-secret")
    monkeypatch.setenv("FAL_API_KEY", "legacy-fal-secret")
    monkeypatch.setenv("REPLICATE_API_TOKEN", "legacy-replicate-secret")

    settings = ApiSettings()

    assert settings.ai_provider_default == "disabled"
    assert settings.ai_provider_calls_enabled is False
    assert settings.ai_provider_openai_api_key is None
    assert settings.ai_provider_fal_api_key is None
    assert settings.ai_provider_bfl_api_key is None


def test_v2_readiness_flags_default_off_in_local_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_api_env(monkeypatch)

    settings = ApiSettings()

    assert settings.v2_hosted_provider_rollout_enabled is False
    assert settings.v2_targeted_regeneration_enabled is False
    assert settings.v2_reference_guidance_enabled is False
    assert settings.v2_lightweight_3d_preview_enabled is False
    assert settings.v2_enhanced_handoff_package_enabled is False
    assert settings.ai_provider_calls_enabled is False
    assert settings.ai_provider_openai_api_key is None
    assert settings.ai_provider_fal_api_key is None
    assert settings.ai_provider_bfl_api_key is None


def test_settings_expose_browser_safe_provider_capabilities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_api_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER_DEFAULT", "bfl")
    monkeypatch.setenv("AI_PROVIDER_MODEL", "flux-2-pro-preview")
    monkeypatch.setenv("AI_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("AI_PROVIDER_BFL_API_KEY", "bfl-secret")
    monkeypatch.setenv("V2_HOSTED_PROVIDER_ROLLOUT_ENABLED", "true")
    monkeypatch.setenv("AI_HOSTED_DAILY_CALL_LIMIT", "10")
    monkeypatch.setenv("AI_HOSTED_RATE_LIMIT_PER_MINUTE", "2")
    monkeypatch.setenv("AI_MAX_ESTIMATED_COST_PER_JOB", "0.2500")

    settings = ApiSettings()

    assert hasattr(settings, "provider_capability_map")
    capabilities = settings.provider_capability_map()
    assert set(capabilities) == {"local-deterministic", "bfl", "openai"}

    local = capabilities["local-deterministic"]
    assert local["provider"] == "local-deterministic"
    assert local["display_name"] == "Local deterministic"
    assert local["credential_required"] is False
    assert local["credential_configured"] is True
    assert local["enabled"] is True
    assert local["blocked_reasons"] == []
    assert local["supports"]["generation"] is True
    assert local["supports"]["mask_aware_generation"] is False
    assert local["supports"]["reference_image_inputs"] is False
    assert local["supports"]["references"] is True
    assert local["supports"]["masks"] is False
    assert local["mask_input"]["accepted"] is False
    assert local["reference_input"]["accepted"] is False
    assert local["reference_input"]["prompt_guidance_roles"] == [
        "character",
        "style",
        "vehicle",
        "logo",
        "palette",
        "inspiration",
    ]
    assert local["reference_input"]["unsupported_roles"] == []
    assert local["supported_edit_routes"] == ["deterministic_recomposition"]
    assert "provider_masked_generation" in local["unsupported_edit_routes"]

    bfl = capabilities["bfl"]
    assert bfl["provider"] == "bfl"
    assert bfl["display_name"] == "BFL"
    assert bfl["credential_required"] is True
    assert bfl["credential_configured"] is True
    assert bfl["enabled"] is True
    assert bfl["default_model"] == "flux-2-pro-preview"
    assert bfl["blocked_reasons"] == []
    assert bfl["supports"]["generation"] is True
    assert bfl["supports"]["input_image_editing"] is True
    assert bfl["supports"]["mask_aware_generation"] is False
    assert bfl["supports"]["reference_image_inputs"] is False
    assert bfl["supports"]["references"] is False
    assert bfl["mask_input"]["accepted"] is False
    assert bfl["reference_input"]["accepted"] is False
    assert bfl["reference_input"]["unsupported_roles"] == [
        "character",
        "style",
        "vehicle",
        "logo",
        "palette",
        "inspiration",
    ]
    assert bfl["supported_edit_routes"] == []
    assert "provider_masked_generation" in bfl["unsupported_edit_routes"]
    assert bfl["guard_state"] == {
        "daily_call_limit": 10,
        "hosted_quota_guard_enabled": True,
        "max_estimated_cost_per_job": "0.2500",
        "rate_limit_per_minute": 2,
    }

    openai = capabilities["openai"]
    assert openai["provider"] == "openai"
    assert openai["display_name"] == "OpenAI GPT Image"
    assert openai["credential_required"] is True
    assert openai["credential_configured"] is False
    assert openai["enabled"] is False
    assert openai["default_model"] == "gpt-image-2"
    assert openai["supports"]["generation"] is True
    assert openai["supports"]["reference_image_inputs"] is False
    assert openai["supports"]["references"] is False
    assert "OpenAI credential is missing" in openai["blocked_reasons"]
    assert "api_key" not in json.dumps(openai, sort_keys=True).lower()
    assert "bfl-secret" not in json.dumps(capabilities, sort_keys=True)

def test_settings_keep_bfl_and_openai_models_independent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_api_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER_DEFAULT", "openai")
    monkeypatch.setenv("AI_PROVIDER_MODEL", "flux-2-pro")
    monkeypatch.setenv("AI_PROVIDER_OPENAI_IMAGE_MODEL", "gpt-image-1")
    monkeypatch.setenv("AI_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("AI_PROVIDER_BFL_API_KEY", "bfl-secret")
    monkeypatch.setenv("AI_PROVIDER_OPENAI_API_KEY", "openai-secret")
    monkeypatch.setenv("V2_HOSTED_PROVIDER_ROLLOUT_ENABLED", "true")
    monkeypatch.setenv("AI_HOSTED_DAILY_CALL_LIMIT", "10")
    monkeypatch.setenv("AI_HOSTED_RATE_LIMIT_PER_MINUTE", "2")
    monkeypatch.setenv("AI_MAX_ESTIMATED_COST_PER_JOB", "0.2500")

    capabilities = ApiSettings().provider_capability_map()

    assert capabilities["bfl"]["default_model"] == "flux-2-pro"
    assert capabilities["openai"]["default_model"] == "gpt-image-1"


def test_settings_keep_codex_relay_gpt_model_for_openai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_api_env(monkeypatch)
    monkeypatch.setenv("AI_PROVIDER_DEFAULT", "openai")
    monkeypatch.setenv("AI_PROVIDER_OPENAI_IMAGE_MODEL", "gpt-5.5")
    monkeypatch.setenv("AI_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("AI_PROVIDER_OPENAI_API_KEY", "openai-secret")
    monkeypatch.setenv("V2_HOSTED_PROVIDER_ROLLOUT_ENABLED", "true")
    monkeypatch.setenv("AI_HOSTED_DAILY_CALL_LIMIT", "10")
    monkeypatch.setenv("AI_HOSTED_RATE_LIMIT_PER_MINUTE", "2")
    monkeypatch.setenv("AI_MAX_ESTIMATED_COST_PER_JOB", "0.2500")

    openai = ApiSettings().provider_capability_map()["openai"]

    assert openai["default_model"] == "gpt-5.5"
    assert "gpt-5.5" in openai["allowed_models"]

def test_settings_block_hosted_capability_without_credentials_or_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear_api_env(monkeypatch)

    settings = ApiSettings(ai_provider_default="bfl")
    bfl = settings.provider_capability_map()["bfl"]

    assert bfl["enabled"] is False
    assert bfl["credential_configured"] is False
    assert bfl["guard_state"]["hosted_quota_guard_enabled"] is False
    assert "V2_HOSTED_PROVIDER_ROLLOUT_ENABLED is disabled" in bfl["blocked_reasons"]
    assert "AI_PROVIDER_CALLS_ENABLED is disabled" in bfl["blocked_reasons"]
    assert "AI_PROVIDER_BFL_API_KEY is missing" in bfl["blocked_reasons"]
    assert "Hosted quota/rate/cost guards are incomplete" in bfl["blocked_reasons"]


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
    monkeypatch.setenv("AI_PROVIDER_DEFAULT", "openai")
    monkeypatch.setenv("AI_PROVIDER_CALLS_ENABLED", "true")
    monkeypatch.setenv("AI_PROVIDER_OPENAI_API_KEY", "super-secret-provider-value")
    monkeypatch.setenv("AI_PROVIDER_FAL_API_KEY", "super-secret-fal-value")
    monkeypatch.setenv("AI_PROVIDER_BFL_API_KEY", "super-secret-bfl-value")

    settings = ApiSettings()
    rendered = f"{settings!s}\n{settings!r}\n{settings.model_dump_json()}"

    assert "super-secret-s3-value" not in rendered
    assert "super-secret-provider-value" not in rendered
    assert "super-secret-fal-value" not in rendered
    assert "super-secret-bfl-value" not in rendered
    assert "**********" in rendered



