from __future__ import annotations

import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

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
BFL_DEFAULT_SUBMIT_PATH = "/v1/flux-2-pro-preview"


@dataclass(frozen=True, slots=True)
class BflSubmitInfo:
    request_id: str
    polling_url: str | None
    cost: Decimal | None
    metadata: JsonObject


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
        submit_path: str = BFL_DEFAULT_SUBMIT_PATH,
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
            submit_info = await self._submit(client, request)
            result_payload = await self._poll_until_ready(client, submit_info)
            result_url = _extract_result_url(result_payload)
            image_response = await client.get(result_url, timeout=self._timeout_seconds)
            if image_response.is_error:
                raise self._error_from_response("BFL result download failed", image_response)

            width, height = png_dimensions(image_response.content)
            result_metadata = result_payload.get("result")
            metadata: JsonObject = {
                "cost": _json_safe_decimal(submit_info.cost),
                "external_calls": True,
                "request_id": submit_info.request_id,
            }
            metadata.update(submit_info.metadata)
            if isinstance(result_metadata, dict):
                metadata.update(
                    {
                        key: value
                        for key, value in result_metadata.items()
                        if key not in {"sample", "url", "image_url"}
                    },
                )

            return ImageGenerationResult(
                actual_cost=submit_info.cost,
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
    ) -> BflSubmitInfo:
        response = await client.post(
            self._submit_path,
            headers=self._headers(),
            json=_submit_payload(request),
            timeout=self._timeout_seconds,
        )
        if response.is_error:
            raise self._error_from_response("BFL submit failed", response)

        payload = _json_payload(response)
        request_id = str(payload.get("id") or payload.get("request_id") or "")
        if not request_id:
            raise ImageProviderError("BFL submit response did not include a request id")
        cost = _decimal_or_none(payload.get("cost"))
        metadata = {
            key: value
            for key, value in payload.items()
            if key in {"input_mp", "output_mp"}
        }
        return BflSubmitInfo(
            cost=cost,
            metadata=metadata,
            polling_url=_optional_string(payload.get("polling_url")),
            request_id=request_id,
        )

    async def _poll_until_ready(
        self,
        client: httpx.AsyncClient,
        submit_info: BflSubmitInfo,
    ) -> JsonObject:
        for _attempt in range(self._max_poll_attempts):
            response = await self._poll_once(client, submit_info)
            if response.is_error:
                raise self._error_from_response("BFL poll failed", response)

            payload = _json_payload(response)
            status = _normalize_status(payload.get("status"))
            if status in {"ready", "succeeded", "success", "completed"}:
                return payload
            if status in {
                "content_moderated",
                "error",
                "failed",
                "request_moderated",
                "task_not_found",
            }:
                message = str(
                    payload.get("error") or payload.get("message") or "BFL generation failed",
                )
                raise ImageProviderError(
                    sanitize_provider_error(
                        f"BFL generation {status.replace('_', ' ')}: {message}",
                        secrets=[self._api_key],
                    ),
                    provider_status=status,
                )
            if self._poll_interval_seconds > 0:
                await asyncio.sleep(self._poll_interval_seconds)

        raise ImageProviderTimeoutError(
            f"BFL generation timed out after {self._max_poll_attempts} poll attempts",
        )

    async def _poll_once(
        self,
        client: httpx.AsyncClient,
        submit_info: BflSubmitInfo,
    ) -> httpx.Response:
        if submit_info.polling_url:
            return await client.get(
                submit_info.polling_url,
                headers=self._headers(),
                timeout=self._timeout_seconds,
            )
        return await client.get(
            self._result_path,
            headers=self._headers(),
            params={"id": submit_info.request_id},
            timeout=self._timeout_seconds,
        )

    def _headers(self) -> dict[str, str]:
        return {"x-key": self._api_key}

    def _error_from_response(self, prefix: str, response: httpx.Response) -> ImageProviderError:
        detail = sanitize_provider_error(response.text, secrets=[self._api_key])
        return ImageProviderError(
            f"{prefix}: HTTP {response.status_code}: {detail}",
            provider_status=_http_provider_status(response.status_code),
            status_code=response.status_code,
        )


def _secret_value(api_key: SecretStr | str | None) -> str | None:
    if isinstance(api_key, SecretStr):
        return api_key.get_secret_value()
    return api_key


def _json_payload(response: httpx.Response) -> JsonObject:
    payload = response.json()
    if not isinstance(payload, dict):
        raise ImageProviderError("Provider response was not a JSON object")
    return payload


def _submit_payload(request: ImageGenerationRequest) -> JsonObject:
    payload: JsonObject = {"prompt": request.prompt_text}
    payload.update(request.parameters)
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


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _json_safe_decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return f"{value:.4f}"


def _normalize_status(value: object) -> str:
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def _optional_string(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _http_provider_status(status_code: int) -> str:
    if status_code in {400, 422}:
        return "provider_validation"
    if status_code == 402:
        return "insufficient_credits"
    if status_code == 429:
        return "rate_limited"
    return f"http_{status_code}"
