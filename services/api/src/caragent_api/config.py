from __future__ import annotations

import json
from decimal import Decimal
from functools import lru_cache
from typing import Annotated, Any, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

RuntimeMode = Literal["local", "development", "test", "staging", "production"]

LOCAL_DATABASE_URL = "postgresql+asyncpg://caragent:caragent_local_password@localhost:5432/caragent"
LOCAL_REDIS_URL = "redis://localhost:6379/0"
LOCAL_S3_ENDPOINT_URL = "http://localhost:9000"
LOCAL_S3_ACCESS_KEY_ID = "caragent_minio"
LOCAL_S3_SECRET_ACCESS_KEY = "caragent_minio_local_password"  # noqa: S105
LOCAL_S3_BUCKET = "caragent-local"
LOCAL_CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


class ApiSettings(BaseSettings):
    """Typed API runtime settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    runtime_mode: RuntimeMode = Field(default="local", validation_alias="RUNTIME_MODE")
    api_version: str = Field(default="0.1.0", validation_alias="API_VERSION")
    database_url: str = Field(default=LOCAL_DATABASE_URL, validation_alias="DATABASE_URL")
    redis_url: str = Field(default=LOCAL_REDIS_URL, validation_alias="REDIS_URL")
    s3_endpoint_url: str = Field(default=LOCAL_S3_ENDPOINT_URL, validation_alias="S3_ENDPOINT_URL")
    s3_access_key_id: str = Field(
        default=LOCAL_S3_ACCESS_KEY_ID,
        validation_alias="S3_ACCESS_KEY_ID",
    )
    s3_secret_access_key: SecretStr = Field(
        default=SecretStr(LOCAL_S3_SECRET_ACCESS_KEY),
        validation_alias="S3_SECRET_ACCESS_KEY",
    )
    s3_bucket: str = Field(default=LOCAL_S3_BUCKET, validation_alias="S3_BUCKET")
    object_storage_backend: Literal["file", "s3"] | None = Field(
        default=None,
        validation_alias="OBJECT_STORAGE_BACKEND",
    )
    object_storage_local_root: str = Field(
        default=".runtime/object-storage",
        validation_alias="OBJECT_STORAGE_LOCAL_ROOT",
    )
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: LOCAL_CORS_ORIGINS.copy(),
        validation_alias="CORS_ORIGINS",
    )
    cors_allow_credentials: bool = Field(default=True, validation_alias="CORS_ALLOW_CREDENTIALS")
    ai_provider_default: str = Field(default="disabled", validation_alias="AI_PROVIDER_DEFAULT")
    ai_provider_model: str = Field(
        default="local-concept-v1",
        validation_alias="AI_PROVIDER_MODEL",
    )
    ai_provider_calls_enabled: bool = Field(
        default=False,
        validation_alias="AI_PROVIDER_CALLS_ENABLED",
    )
    ai_hosted_daily_call_limit: int | None = Field(
        default=None,
        gt=0,
        validation_alias="AI_HOSTED_DAILY_CALL_LIMIT",
    )
    ai_hosted_rate_limit_per_minute: int | None = Field(
        default=None,
        gt=0,
        validation_alias="AI_HOSTED_RATE_LIMIT_PER_MINUTE",
    )
    ai_max_estimated_cost_per_job: Decimal | None = Field(
        default=None,
        gt=0,
        validation_alias="AI_MAX_ESTIMATED_COST_PER_JOB",
    )
    ai_provider_openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="AI_PROVIDER_OPENAI_API_KEY",
    )
    ai_provider_openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias="AI_PROVIDER_OPENAI_BASE_URL",
    )
    ai_provider_openai_image_model: str = Field(
        default="gpt-image-2",
        validation_alias="AI_PROVIDER_OPENAI_IMAGE_MODEL",
    )
    ai_provider_openai_responses_path: str = Field(
        default="/responses",
        validation_alias="AI_PROVIDER_OPENAI_RESPONSES_PATH",
    )
    ai_provider_openai_text_model: str = Field(
        default="gpt-5.5",
        validation_alias="AI_PROVIDER_OPENAI_TEXT_MODEL",
    )
    ai_brief_parser_provider: str = Field(
        default="deterministic",
        validation_alias="AI_BRIEF_PARSER_PROVIDER",
    )
    ai_brief_parser_fallback_enabled: bool = Field(
        default=True,
        validation_alias="AI_BRIEF_PARSER_FALLBACK_ENABLED",
    )
    ai_provider_fal_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="AI_PROVIDER_FAL_API_KEY",
    )
    ai_provider_bfl_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="AI_PROVIDER_BFL_API_KEY",
    )
    v2_hosted_provider_rollout_enabled: bool = Field(
        default=False,
        validation_alias="V2_HOSTED_PROVIDER_ROLLOUT_ENABLED",
    )
    v2_targeted_regeneration_enabled: bool = Field(
        default=False,
        validation_alias="V2_TARGETED_REGENERATION_ENABLED",
    )
    v2_reference_guidance_enabled: bool = Field(
        default=False,
        validation_alias="V2_REFERENCE_GUIDANCE_ENABLED",
    )
    v2_lightweight_3d_preview_enabled: bool = Field(
        default=False,
        validation_alias="V2_LIGHTWEIGHT_3D_PREVIEW_ENABLED",
    )
    v2_enhanced_handoff_package_enabled: bool = Field(
        default=False,
        validation_alias="V2_ENHANCED_HANDOFF_PACKAGE_ENABLED",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str] | Any:
        if not isinstance(value, str):
            return value

        raw_value = value.strip()
        if not raw_value:
            return []

        if raw_value.startswith("["):
            parsed = json.loads(raw_value)
            if not isinstance(parsed, list):
                msg = "CORS_ORIGINS JSON value must be a list."
                raise ValueError(msg)
            return parsed

        return [origin.strip() for origin in raw_value.split(",") if origin.strip()]

    @model_validator(mode="after")
    def validate_runtime_settings(self) -> ApiSettings:
        self._validate_cors_policy()
        self._validate_non_local_required_settings()
        return self

    def _validate_cors_policy(self) -> None:
        has_wildcard_origin = "*" in self.cors_origins
        if has_wildcard_origin and (self.runtime_mode != "local" or self.cors_allow_credentials):
            msg = (
                "Wildcard CORS origins are only allowed in local mode with "
                "CORS_ALLOW_CREDENTIALS=false."
            )
            raise ValueError(msg)

    def _validate_non_local_required_settings(self) -> None:
        if self.runtime_mode == "local":
            return

        missing: list[str] = []
        checks = {
            "DATABASE_URL": (self.database_url, LOCAL_DATABASE_URL),
            "REDIS_URL": (self.redis_url, LOCAL_REDIS_URL),
            "S3_ENDPOINT_URL": (self.s3_endpoint_url, LOCAL_S3_ENDPOINT_URL),
            "S3_ACCESS_KEY_ID": (self.s3_access_key_id, LOCAL_S3_ACCESS_KEY_ID),
            "S3_SECRET_ACCESS_KEY": (
                self.s3_secret_access_key.get_secret_value(),
                LOCAL_S3_SECRET_ACCESS_KEY,
            ),
            "S3_BUCKET": (self.s3_bucket, LOCAL_S3_BUCKET),
        }

        for env_name, (value, local_default) in checks.items():
            if not value or value == local_default:
                missing.append(env_name)

        if not self.cors_origins:
            missing.append("CORS_ORIGINS")

        if missing:
            msg = f"Non-local runtime requires explicit settings: {', '.join(missing)}"
            raise ValueError(msg)

    def provider_capability_map(self) -> dict[str, dict[str, Any]]:
        from caragent_core.provider_capabilities import build_provider_capability_map

        bfl_key_configured = bool(
            self.ai_provider_bfl_api_key and self.ai_provider_bfl_api_key.get_secret_value()
        )
        openai_key_configured = bool(
            self.ai_provider_openai_api_key
            and self.ai_provider_openai_api_key.get_secret_value()
        )
        return build_provider_capability_map(
            bfl_key_configured=bfl_key_configured,
            openai_key_configured=openai_key_configured,
            bfl_default_model=self.ai_provider_model,
            openai_default_model=self.ai_provider_openai_image_model,
            default_provider=self.ai_provider_default,
            hosted_daily_call_limit=self.ai_hosted_daily_call_limit,
            hosted_rate_limit_per_minute=self.ai_hosted_rate_limit_per_minute,
            max_estimated_cost_per_job=self.ai_max_estimated_cost_per_job,
            provider_calls_enabled=self.ai_provider_calls_enabled,
            v2_hosted_provider_rollout_enabled=self.v2_hosted_provider_rollout_enabled,
        )


@lru_cache
def get_settings() -> ApiSettings:
    """Return cached API settings for application startup."""

    return ApiSettings()
