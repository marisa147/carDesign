from decimal import Decimal
from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

RuntimeMode = Literal["local", "development", "test", "staging", "production"]
SUPPORTED_FALLBACK_PROVIDERS = {"local", "local-deterministic"}


class WorkerSettings(BaseSettings):
    """Runtime configuration for the Celery worker process."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        extra="ignore",
        populate_by_name=True,
    )

    runtime_mode: RuntimeMode = Field(default="local", validation_alias="RUNTIME_MODE")
    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    ai_provider_default: str = Field(default="disabled", validation_alias="AI_PROVIDER_DEFAULT")
    ai_provider_model: str = Field(
        default="local-concept-v1",
        validation_alias="AI_PROVIDER_MODEL",
    )
    ai_provider_calls_enabled: bool = Field(
        default=False,
        validation_alias="AI_PROVIDER_CALLS_ENABLED",
    )
    ai_generation_timeout_seconds: float = Field(
        default=30.0,
        gt=0,
        validation_alias="AI_GENERATION_TIMEOUT_SECONDS",
    )
    ai_generation_poll_interval_seconds: float = Field(
        default=1.0,
        ge=0,
        validation_alias="AI_GENERATION_POLL_INTERVAL_SECONDS",
    )
    ai_generation_max_poll_attempts: int = Field(
        default=30,
        gt=0,
        validation_alias="AI_GENERATION_MAX_POLL_ATTEMPTS",
    )
    ai_generation_max_attempts: int = Field(
        default=1,
        gt=0,
        validation_alias="AI_GENERATION_MAX_ATTEMPTS",
    )
    ai_provider_fallback_enabled: bool = Field(
        default=False,
        validation_alias="AI_PROVIDER_FALLBACK_ENABLED",
    )
    ai_provider_fallback_name: str = Field(
        default="local-deterministic",
        validation_alias="AI_PROVIDER_FALLBACK_NAME",
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
    ai_local_image_width: int = Field(
        default=1536,
        gt=0,
        validation_alias="AI_LOCAL_IMAGE_WIDTH",
    )
    ai_local_image_height: int = Field(
        default=768,
        gt=0,
        validation_alias="AI_LOCAL_IMAGE_HEIGHT",
    )
    ai_provider_bfl_base_url: str = Field(
        default="https://api.bfl.ai",
        validation_alias="AI_PROVIDER_BFL_BASE_URL",
    )
    ai_provider_bfl_submit_path: str = Field(
        default="/v1/flux-pro",
        validation_alias="AI_PROVIDER_BFL_SUBMIT_PATH",
    )
    ai_provider_bfl_result_path: str = Field(
        default="/v1/get_result",
        validation_alias="AI_PROVIDER_BFL_RESULT_PATH",
    )
    ai_provider_openai_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="AI_PROVIDER_OPENAI_API_KEY",
    )
    ai_provider_fal_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="AI_PROVIDER_FAL_API_KEY",
    )
    ai_provider_bfl_api_key: SecretStr | None = Field(
        default=None,
        validation_alias="AI_PROVIDER_BFL_API_KEY",
    )

    @model_validator(mode="after")
    def require_explicit_non_local_redis_url(self) -> Self:
        if self.runtime_mode != "local" and "redis_url" not in self.model_fields_set:
            raise ValueError("REDIS_URL is required for non-local runtime modes")
        fallback_name = self.ai_provider_fallback_name.strip().lower()
        if self.ai_provider_fallback_enabled and fallback_name not in SUPPORTED_FALLBACK_PROVIDERS:
            raise ValueError("Unsupported AI_PROVIDER_FALLBACK_NAME")
        return self

    @property
    def hosted_provider_configured(self) -> bool:
        provider_name = self.ai_provider_default.strip().lower()
        provider_key = {
            "bfl": self.ai_provider_bfl_api_key,
            "black-forest-labs": self.ai_provider_bfl_api_key,
            "fal": self.ai_provider_fal_api_key,
            "openai": self.ai_provider_openai_api_key,
        }.get(provider_name)
        return bool(provider_key and provider_key.get_secret_value())


@lru_cache(maxsize=1)
def get_settings() -> WorkerSettings:
    return WorkerSettings()
