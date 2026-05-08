from __future__ import annotations

import json
from functools import lru_cache
from typing import Annotated, Any, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

RuntimeMode = Literal["local", "development", "test", "staging", "production"]

LOCAL_DATABASE_URL = "postgresql+asyncpg://caragent:caragent@localhost:5432/caragent"
LOCAL_REDIS_URL = "redis://localhost:6379/0"
LOCAL_S3_ENDPOINT_URL = "http://localhost:9000"
LOCAL_S3_ACCESS_KEY_ID = "caragent-local"
LOCAL_S3_SECRET_ACCESS_KEY = "caragent-local-secret"
LOCAL_S3_BUCKET = "caragent-artifacts"
LOCAL_CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


class ApiSettings(BaseSettings):
    """Typed API runtime settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
        populate_by_name=True,
    )

    runtime_mode: RuntimeMode = Field(default="local", validation_alias="RUNTIME_MODE")
    api_version: str = Field(default="0.1.0", validation_alias="API_VERSION")
    database_url: str = Field(default=LOCAL_DATABASE_URL, validation_alias="DATABASE_URL")
    redis_url: str = Field(default=LOCAL_REDIS_URL, validation_alias="REDIS_URL")
    s3_endpoint_url: str = Field(default=LOCAL_S3_ENDPOINT_URL, validation_alias="S3_ENDPOINT_URL")
    s3_access_key_id: str = Field(default=LOCAL_S3_ACCESS_KEY_ID, validation_alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: SecretStr = Field(
        default=SecretStr(LOCAL_S3_SECRET_ACCESS_KEY),
        validation_alias="S3_SECRET_ACCESS_KEY",
    )
    s3_bucket: str = Field(default=LOCAL_S3_BUCKET, validation_alias="S3_BUCKET")
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: LOCAL_CORS_ORIGINS.copy(),
        validation_alias="CORS_ORIGINS",
    )
    cors_allow_credentials: bool = Field(default=True, validation_alias="CORS_ALLOW_CREDENTIALS")
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


@lru_cache
def get_settings() -> ApiSettings:
    """Return cached API settings for application startup."""

    return ApiSettings()
