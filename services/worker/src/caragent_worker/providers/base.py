from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Protocol, Self

from caragent_core.generation import PromptPlan

JsonObject = dict[str, Any]


class ImageProviderError(RuntimeError):
    """Base error for normalized image-provider failures."""

    def __init__(
        self,
        message: str,
        *,
        provider_status: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.provider_status = provider_status
        self.status_code = status_code


class ImageProviderConfigurationError(ImageProviderError):
    """Raised when provider settings are incomplete or unsafe."""


class ImageProviderTimeoutError(ImageProviderError):
    """Raised when a provider does not finish within bounded polling."""


@dataclass(frozen=True, slots=True)
class MaskEditRequest:
    route_preference: str
    mask_artifact_id: str
    mask_content_type: str
    mask_width: int
    mask_height: int
    region: JsonObject
    target: JsonObject
    prompt_delta: JsonObject
    parent_version_id: str | None = None


@dataclass(frozen=True, slots=True)
class ImageGenerationRequest:
    prompt_text: str
    prompt_payload: JsonObject
    provider: str
    model: str
    parameters: JsonObject = field(default_factory=dict)
    input_artifact_ids: list[str] = field(default_factory=list)
    reference_usage: JsonObject | None = None
    estimated_cost: Decimal | None = None
    concept_label: str = "concept_preview"
    mask_edit: MaskEditRequest | None = None

    @classmethod
    def from_prompt_plan(cls, prompt_plan: PromptPlan) -> Self:
        reference_usage = prompt_plan.prompt_payload.get("reference_usage")
        return cls(
            concept_label=prompt_plan.concept_label,
            input_artifact_ids=list(prompt_plan.input_artifact_ids),
            model=prompt_plan.model,
            estimated_cost=prompt_plan.estimated_cost,
            parameters=dict(prompt_plan.parameters),
            prompt_payload=dict(prompt_plan.prompt_payload),
            prompt_text=prompt_plan.prompt_text,
            provider=prompt_plan.provider,
            reference_usage=(
                dict(reference_usage) if isinstance(reference_usage, dict) else None
            ),
        )


@dataclass(frozen=True, slots=True)
class ImageGenerationResult:
    image_bytes: bytes
    content_type: str
    width: int
    height: int
    provider: str
    model: str
    metadata: JsonObject = field(default_factory=dict)
    actual_cost: Decimal | None = None
    estimated_cost: Decimal | None = None


class ImageProvider(Protocol):
    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        """Generate image bytes for a normalized request."""


def sanitize_provider_error(message: str, *, secrets: Sequence[str] = ()) -> str:
    sanitized = " ".join(message.split())
    for secret in secrets:
        if secret:
            sanitized = sanitized.replace(secret, "[redacted]")
    return sanitized


def png_dimensions(image_bytes: bytes) -> tuple[int, int]:
    if not image_bytes.startswith(b"\x89PNG\r\n\x1a\n") or len(image_bytes) < 24:
        return 0, 0
    return (
        int.from_bytes(image_bytes[16:20], "big"),
        int.from_bytes(image_bytes[20:24], "big"),
    )
