from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

RuntimeMode = Literal["local", "development", "test", "staging", "production"]


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
    redis_url: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    ai_provider_default: str = Field(default="disabled", validation_alias="AI_PROVIDER_DEFAULT")
    ai_provider_calls_enabled: bool = Field(
        default=False,
        validation_alias="AI_PROVIDER_CALLS_ENABLED",
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
        return self


@lru_cache(maxsize=1)
def get_settings() -> WorkerSettings:
    return WorkerSettings()
