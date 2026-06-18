from __future__ import annotations

import asyncio
from decimal import Decimal

import httpx
from pydantic import SecretStr

from caragent_worker.providers.base import (
    ImageGenerationRequest,
    ImageGenerationResult,
    ImageProviderConfigurationError,
    ImageProviderError,
    ImageProviderTimeoutError,
    JsonObject,
    png_dimensions,
    sanitize_provider_error,
)

BFL_PROVIDER = "bfl"


class BflImageProvider:
    def __init__(
        self,
        *,
        api_key: SecretStr | str | None,
        base_url: str = "https://api.bfl.ai",
        client: httpx.AsyncClient | None = None,
        max_poll_attempts: int = 30,
        poll_interval_seconds: float = 1.0,
        result_path: str = "/v1/get_result",
        submit_path: str = "/v1/flux-pro",
        timeout_seconds: float = 30.0,
    ) -> None:
        api_key_value = _secret_value(api_key)
        if not api_key_value:
            raise ImageProviderConfigurationError("AI_PROVIDER_BFL_API_KEY is required")

        self._api_key = api_key_value
        self._base_url = base_url
        self._client = client
        self._max_poll_attempts = max_poll_attempts
        self._poll_interval_seconds = poll_interval_seconds
        self._result_path = result_path
        self._submit_path = submit_path
        self._timeout_seconds = timeout_seconds

    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        client = self._client or httpx.AsyncClient(base_url=self._base_url)
        try:
            request_id = await self._submit(client, request)
            result_payload = await self._poll_until_ready(client, request_id)
            result_url = _extract_result_url(result_payload)
            image_response = await client.get(result_url, timeout=self._timeout_seconds)
            if image_response.is_error:
                raise self._error_from_response("BFL result download failed", image_response)

            width, height = png_dimensions(image_response.content)
            result_metadata = result_payload.get("result")
            metadata: JsonObject = {
                "external_calls": True,
                "request_id": request_id,
                "result_url": result_url,
            }
            if isinstance(result_metadata, dict):
                metadata.update(
                    {
                        key: value
                        for key, value in result_metadata.items()
                        if key not in {"sample", "url", "image_url"}
                    },
                )

            return ImageGenerationResult(
                actual_cost=Decimal("0.0000"),
                content_type=image_response.headers.get("content-type", "image/png"),
                estimated_cost=request.estimated_cost,
                height=height,
                image_bytes=image_response.content,
                metadata=metadata,
                model=request.model,
                provider=BFL_PROVIDER,
                width=width,
            )
        except ImageProviderError:
            raise
        except httpx.HTTPError as exc:
            raise ImageProviderError(
                sanitize_provider_error(str(exc), secrets=[self._api_key]),
            ) from exc
        finally:
            if self._client is None:
                await client.aclose()

    async def _submit(
        self,
        client: httpx.AsyncClient,
        request: ImageGenerationRequest,
    ) -> str:
        response = await client.post(
            self._submit_path,
            headers=self._headers(),
            json={
                "model": request.model,
                "parameters": request.parameters,
                "prompt": request.prompt_text,
                "prompt_payload": request.prompt_payload,
            },
            timeout=self._timeout_seconds,
        )
        if response.is_error:
            raise self._error_from_response("BFL submit failed", response)

        payload = _json_payload(response)
        request_id = str(payload.get("id") or payload.get("request_id") or "")
        if not request_id:
            raise ImageProviderError("BFL submit response did not include a request id")
        return request_id

    async def _poll_until_ready(
        self,
        client: httpx.AsyncClient,
        request_id: str,
    ) -> JsonObject:
        for _attempt in range(self._max_poll_attempts):
            response = await client.get(
                self._result_path,
                headers=self._headers(),
                params={"id": request_id},
                timeout=self._timeout_seconds,
            )
            if response.is_error:
                raise self._error_from_response("BFL poll failed", response)

            payload = _json_payload(response)
            status = str(payload.get("status", "")).lower()
            if status in {"ready", "succeeded", "success", "completed"}:
                return payload
            if status in {"failed", "error"}:
                message = str(
                    payload.get("error") or payload.get("message") or "BFL generation failed",
                )
                raise ImageProviderError(
                    sanitize_provider_error(message, secrets=[self._api_key]),
                )
            if self._poll_interval_seconds > 0:
                await asyncio.sleep(self._poll_interval_seconds)

        raise ImageProviderTimeoutError(
            f"BFL generation timed out after {self._max_poll_attempts} poll attempts",
        )

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"}

    def _error_from_response(self, prefix: str, response: httpx.Response) -> ImageProviderError:
        detail = sanitize_provider_error(response.text, secrets=[self._api_key])
        return ImageProviderError(f"{prefix}: HTTP {response.status_code}: {detail}")


def _secret_value(api_key: SecretStr | str | None) -> str | None:
    if isinstance(api_key, SecretStr):
        return api_key.get_secret_value()
    return api_key


def _json_payload(response: httpx.Response) -> JsonObject:
    payload = response.json()
    if not isinstance(payload, dict):
        raise ImageProviderError("Provider response was not a JSON object")
    return payload


def _extract_result_url(payload: JsonObject) -> str:
    result = payload.get("result")
    if isinstance(result, dict):
        for key in ("sample", "url", "image_url"):
            value = result.get(key)
            if isinstance(value, str) and value:
                return value

    value = payload.get("result_url")
    if isinstance(value, str) and value:
        return value

    raise ImageProviderError("BFL result response did not include an image URL")
