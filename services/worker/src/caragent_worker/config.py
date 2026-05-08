from functools import lru_cache
from typing import Literal, Self

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

RuntimeMode = Literal["local", "development", "test", "staging", "production"]


class WorkerSettings(BaseSettings):
    """Runtime configuration for the Celery worker process."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_prefix="",
        extra="ignore",
    )

    runtime_mode: RuntimeMode = "local"
    redis_url: str = "redis://localhost:6379/0"
    ai_provider_openai_api_key: SecretStr | None = None
    ai_provider_fal_api_key: SecretStr | None = None
    ai_provider_bfl_api_key: SecretStr | None = None

    @model_validator(mode="after")
    def require_explicit_non_local_redis_url(self) -> Self:
        if self.runtime_mode != "local" and "redis_url" not in self.model_fields_set:
            raise ValueError("REDIS_URL is required for non-local runtime modes")
        return self


@lru_cache(maxsize=1)
def get_settings() -> WorkerSettings:
    return WorkerSettings()
