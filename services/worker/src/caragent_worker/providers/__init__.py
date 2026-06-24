from __future__ import annotations

import httpx

from caragent_worker.config import WorkerSettings
from caragent_worker.providers.base import (
    FULL_CONCEPT_IMAGE_ROUTE,
    TEMPLATE_COMPOSITED_PREVIEW_ROUTE,
    ImageGenerationRequest,
    ImageGenerationResult,
    ImageProvider,
    ImageProviderConfigurationError,
    ImageProviderError,
    ImageProviderTimeoutError,
    MaskEditRequest,
    generation_route_for_request,
)
from caragent_worker.providers.bfl import BflImageProvider
from caragent_worker.providers.local import LocalDeterministicImageProvider
from caragent_worker.providers.openai import OpenAIImageProvider

__all__ = [
    "BflImageProvider",
    "FULL_CONCEPT_IMAGE_ROUTE",
    "ImageGenerationRequest",
    "ImageGenerationResult",
    "ImageProvider",
    "ImageProviderConfigurationError",
    "ImageProviderError",
    "ImageProviderTimeoutError",
    "LocalDeterministicImageProvider",
    "MaskEditRequest",
    "OpenAIImageProvider",
    "TEMPLATE_COMPOSITED_PREVIEW_ROUTE",
    "generation_route_for_request",
    "select_image_provider",
]

LOCAL_PROVIDER_NAMES = {"disabled", "local", "local-deterministic"}
BFL_PROVIDER_NAMES = {"bfl", "black-forest-labs"}
OPENAI_PROVIDER_NAMES = {"openai", "gpt"}


def select_image_provider(
    settings: WorkerSettings,
    *,
    client: httpx.AsyncClient | None = None,
    provider_name: str | None = None,
) -> ImageProvider:
    selected_name = (provider_name or settings.ai_provider_default).strip().lower()

    if provider_name is None and not settings.ai_provider_calls_enabled:
        return _local_provider(settings)
    if selected_name in LOCAL_PROVIDER_NAMES:
        return _local_provider(settings)
    if selected_name in BFL_PROVIDER_NAMES:
        return BflImageProvider(
            api_key=settings.ai_provider_bfl_api_key,
            base_url=settings.ai_provider_bfl_base_url,
            client=client,
            max_poll_attempts=settings.ai_generation_max_poll_attempts,
            poll_interval_seconds=settings.ai_generation_poll_interval_seconds,
            result_path=settings.ai_provider_bfl_result_path,
            submit_path=settings.ai_provider_bfl_submit_path,
            timeout_seconds=settings.ai_generation_timeout_seconds,
        )
    if selected_name in OPENAI_PROVIDER_NAMES:
        return OpenAIImageProvider(
            api_key=settings.ai_provider_openai_api_key,
            base_url=settings.ai_provider_openai_base_url,
            client=client,
            image_path=settings.ai_provider_openai_image_path,
            timeout_seconds=settings.ai_generation_timeout_seconds,
            allowed_image_hosts=settings.openai_allowed_image_hosts,
        )

    raise ImageProviderConfigurationError(f"Unsupported image provider: {selected_name}")


def _local_provider(settings: WorkerSettings) -> LocalDeterministicImageProvider:
    return LocalDeterministicImageProvider(
        height=settings.ai_local_image_height,
        width=settings.ai_local_image_width,
    )
