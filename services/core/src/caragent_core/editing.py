from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class EditTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["safe_zone", "overlay_layer"]
    id: str = Field(min_length=1)

    @field_validator("id", mode="before")
    @classmethod
    def strip_id(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class EditRegion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["rectangle"]
    unit: Literal["normalized"] = "normalized"
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    width: float = Field(gt=0, le=1)
    height: float = Field(gt=0, le=1)

    @model_validator(mode="after")
    def validate_bounds(self) -> EditRegion:
        if self.x + self.width > 1:
            raise ValueError("region x + width must be <= 1")
        if self.y + self.height > 1:
            raise ValueError("region y + height must be <= 1")
        return self


class PromptDelta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    instructions: list[str] = Field(min_length=1)

    @field_validator("summary", mode="before")
    @classmethod
    def strip_summary(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("instructions", mode="before")
    @classmethod
    def strip_instructions(cls, value: object) -> object:
        if isinstance(value, list):
            return [item.strip() for item in value if isinstance(item, str) and item.strip()]
        return value


class MaskAssetRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    artifact_id: UUID
    content_type: str = Field(min_length=1)
    width: int = Field(gt=0)
    height: int = Field(gt=0)

    @field_validator("content_type", mode="before")
    @classmethod
    def strip_content_type(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class EditIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal[1] = 1
    mode: Literal["targeted_edit"]
    route_preference: Literal["deterministic_recomposition", "provider_masked_generation"]
    target: EditTarget
    region: EditRegion
    prompt_delta: PromptDelta
    mask: MaskAssetRef
    parent_version_id: UUID | None = None
