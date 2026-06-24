from __future__ import annotations

import base64
import binascii
import ipaddress
import json
import re
from io import BytesIO
from typing import Any
from urllib.parse import urlparse

import httpx
from PIL import Image, UnidentifiedImageError
from pydantic import SecretStr

from caragent_worker.providers.base import (
    ImageGenerationRequest,
    ImageGenerationResult,
    ImageProviderConfigurationError,
    ImageProviderError,
    JsonObject,
    generation_route_for_request,
    png_dimensions,
    sanitize_provider_error,
)

OPENAI_PROVIDER = "openai"
OPENAI_DEFAULT_IMAGE_PATH = "/images/generations"
OPENAI_MAX_RESULT_IMAGE_BYTES = 20 * 1024 * 1024
OPENAI_ALLOWED_RESULT_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
CHAT_COMPLETIONS_SYSTEM_PROMPT = (
    "Generate a single pain-car concept image. Return only compact JSON with either "
    "{\"image_url\":\"https://...\"} or {\"image_base64\":\"...\"}. "
    "Do not return explanatory prose or a text-only design description."
)
_DATA_URL_RE = re.compile(
    r"data:image/(?:png|jpeg|jpg|webp);base64,([A-Za-z0-9+/=\r\n]+)",
    re.IGNORECASE,
)
_HTTP_URL_RE = re.compile(r"https?://[^\s)\]\"']+")


class OpenAIImageProvider:
    def __init__(
        self,
        *,
        api_key: SecretStr | str | None,
        base_url: str = "https://api.openai.com/v1",
        client: httpx.AsyncClient | None = None,
        image_path: str = OPENAI_DEFAULT_IMAGE_PATH,
        timeout_seconds: float = 30.0,
        allowed_image_hosts: tuple[str, ...] = (),
    ) -> None:
        api_key_value = _secret_value(api_key)
        if not api_key_value:
            raise ImageProviderConfigurationError("AI_PROVIDER_OPENAI_API_KEY is required")

        self._api_key = api_key_value
        self._base_url = base_url
        self._client = client
        self._image_path = image_path
        self._timeout_seconds = timeout_seconds
        self._allowed_image_hosts = tuple(
            host.strip().lower() for host in allowed_image_hosts if host.strip()
        )

    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        client = self._client or httpx.AsyncClient(base_url=self._base_url)
        chat_completion_mode = _is_chat_completions_path(self._image_path)
        try:
            response = await client.post(
                self._image_path,
                headers=self._headers(),
                json=(
                    _chat_completion_payload(request)
                    if chat_completion_mode
                    else _image_api_payload(request)
                ),
                timeout=self._timeout_seconds,
            )
            if response.is_error:
                raise self._error_from_response("OpenAI image generation failed", response)

            payload = _json_payload(response)
            metadata: JsonObject = {
                "external_calls": True,
                "generation_route": generation_route_for_request(request),
            }
            usage = payload.get("usage")
            if isinstance(usage, dict):
                metadata["usage"] = usage

            if chat_completion_mode:
                image_bytes = await _image_bytes_from_chat_completion(
                    payload,
                    client,
                    allowed_hosts=self._allowed_image_hosts,
                    timeout_seconds=self._timeout_seconds,
                )
                metadata["response_mode"] = "chat_completions"
            else:
                item = _first_data_item(payload)
                image_bytes = _decode_b64_png(item)
                revised_prompt = _optional_string(item.get("revised_prompt"))
                if revised_prompt is not None:
                    metadata["revised_prompt"] = revised_prompt

            image_bytes = _normalize_result_png(image_bytes)
            width, height = _validated_png_dimensions(image_bytes)
            return ImageGenerationResult(
                actual_cost=None,
                content_type="image/png",
                estimated_cost=request.estimated_cost,
                height=height,
                image_bytes=image_bytes,
                metadata=metadata,
                model=request.model,
                provider=OPENAI_PROVIDER,
                width=width,
            )
        except ImageProviderError:
            raise
        except httpx.HTTPError as exc:
            detail = _http_error_detail("OpenAI image generation failed", exc)
            raise ImageProviderError(
                sanitize_provider_error(detail, secrets=[self._api_key]),
            ) from exc
        finally:
            if self._client is None:
                await client.aclose()

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"}

    def _error_from_response(self, prefix: str, response: httpx.Response) -> ImageProviderError:
        detail = sanitize_provider_error(response.text, secrets=[self._api_key])
        return ImageProviderError(
            f"{prefix}: HTTP {response.status_code}: {detail}",
            provider_status=_http_provider_status(response.status_code),
            status_code=response.status_code,
        )


def _image_api_payload(request: ImageGenerationRequest) -> JsonObject:
    if request.mask_edit is not None:
        raise ImageProviderConfigurationError(
            "OpenAI provider_masked_generation is deferred for the current adapter.",
        )
    payload: JsonObject = {
        "model": request.model,
        "prompt": request.prompt_text,
    }
    payload.update(_supported_provider_parameters(request.parameters))
    return payload


def _chat_completion_payload(request: ImageGenerationRequest) -> JsonObject:
    if request.mask_edit is not None:
        raise ImageProviderConfigurationError(
            "OpenAI provider_masked_generation is deferred for the current adapter.",
        )
    return {
        "messages": [
            {"content": CHAT_COMPLETIONS_SYSTEM_PROMPT, "role": "system"},
            {"content": request.prompt_text, "role": "user"},
        ],
        "model": request.model,
    }


def _supported_provider_parameters(parameters: JsonObject) -> JsonObject:
    safe_parameters: JsonObject = {}
    for key, value in parameters.items():
        if key in {"input_artifact_ids", "prompt_payload", "reference_usage"}:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe_parameters[key] = value
    return safe_parameters


def _first_data_item(payload: JsonObject) -> JsonObject:
    data = payload.get("data")
    if not isinstance(data, list) or not data:
        raise ImageProviderError("OpenAI image response did not include data")
    first = data[0]
    if not isinstance(first, dict):
        raise ImageProviderError("OpenAI image response data item was not an object")
    return first


def _decode_b64_png(item: JsonObject) -> bytes:
    b64_json = item.get("b64_json")
    if not isinstance(b64_json, str) or not b64_json:
        raise ImageProviderError("OpenAI image response did not include b64_json")
    return _decode_png_base64(b64_json)


async def _image_bytes_from_chat_completion(
    payload: JsonObject,
    client: httpx.AsyncClient,
    *,
    allowed_hosts: tuple[str, ...],
    timeout_seconds: float,
) -> bytes:
    content = _first_chat_message_content(payload)
    reference = _image_reference_from_content(content)
    if reference is None:
        raise ImageProviderError(
            "OpenAI chat completion response did not include an image. "
            f"content_excerpt={_content_excerpt(content)}",
        )
    return await _bytes_from_image_reference(
        reference,
        client,
        allowed_hosts=allowed_hosts,
        timeout_seconds=timeout_seconds,
    )


def _first_chat_message_content(payload: JsonObject) -> object:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ImageProviderError("OpenAI chat completion response did not include choices")
    first = choices[0]
    if not isinstance(first, dict):
        raise ImageProviderError("OpenAI chat completion choice was not an object")
    message = first.get("message")
    if not isinstance(message, dict):
        raise ImageProviderError("OpenAI chat completion choice did not include a message")
    return message.get("content")


def _image_reference_from_content(content: object) -> str | None:
    if isinstance(content, str):
        stripped = content.strip()
        parsed = _try_parse_json(stripped)
        if parsed is not None:
            nested = _image_reference_from_content(parsed)
            if nested is not None:
                return nested
        data_url_match = _DATA_URL_RE.search(stripped)
        if data_url_match:
            return data_url_match.group(0)
        url_match = _HTTP_URL_RE.search(stripped)
        if url_match:
            return url_match.group(0)
        return None
    if isinstance(content, list):
        for item in content:
            reference = _image_reference_from_content(item)
            if reference is not None:
                return reference
        return None
    if isinstance(content, dict):
        for key in ("b64_json", "image_base64", "base64"):
            value = content.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        image_url = content.get("image_url")
        if isinstance(image_url, dict):
            url = image_url.get("url")
            if isinstance(url, str) and url.strip():
                return url.strip()
        for key in ("url", "data"):
            value = content.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


async def _bytes_from_image_reference(
    reference: str,
    client: httpx.AsyncClient,
    *,
    allowed_hosts: tuple[str, ...],
    timeout_seconds: float,
) -> bytes:
    data_url_match = _DATA_URL_RE.fullmatch(reference.strip())
    if data_url_match:
        return _decode_png_base64(data_url_match.group(1))
    if reference.startswith(("http://", "https://")):
        _validate_remote_image_url(reference, allowed_hosts=allowed_hosts)
        return await _download_remote_image(
            reference,
            client,
            timeout_seconds=timeout_seconds,
        )
    return _decode_png_base64(reference)


def _validate_remote_image_url(reference: str, *, allowed_hosts: tuple[str, ...]) -> None:
    parsed = urlparse(reference)
    if parsed.scheme.lower() != "https":
        raise ImageProviderError("OpenAI result image URL must use HTTPS")
    hostname = (parsed.hostname or "").strip().lower()
    if not hostname:
        raise ImageProviderError("OpenAI result image URL is missing a host")
    if allowed_hosts and hostname not in allowed_hosts:
        raise ImageProviderError("OpenAI result image URL host is not allowed")
    if hostname == "localhost" or hostname.endswith(".localhost"):
        raise ImageProviderError("OpenAI result image URL host is not public")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return
    if (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    ):
        raise ImageProviderError("OpenAI result image URL host is not public")


async def _download_remote_image(
    reference: str,
    client: httpx.AsyncClient,
    *,
    timeout_seconds: float,
) -> bytes:
    async with client.stream(
        "GET",
        reference,
        follow_redirects=False,
        timeout=timeout_seconds,
    ) as response:
        if response.is_redirect:
            raise ImageProviderError("OpenAI result image download redirects are not allowed")
        if response.is_error:
            raise ImageProviderError(
                f"OpenAI chat completion image download failed: HTTP {response.status_code}",
                provider_status=_http_provider_status(response.status_code),
                status_code=response.status_code,
            )
        content_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
        if content_type and content_type not in OPENAI_ALLOWED_RESULT_CONTENT_TYPES:
            raise ImageProviderError("OpenAI result image content type is not supported")
        content_length = response.headers.get("content-length")
        if content_length is not None:
            try:
                declared_size = int(content_length)
            except ValueError:
                declared_size = 0
            if declared_size > OPENAI_MAX_RESULT_IMAGE_BYTES:
                raise ImageProviderError("OpenAI result image exceeds maximum download size")

        content = bytearray()
        async for chunk in response.aiter_bytes():
            content.extend(chunk)
            if len(content) > OPENAI_MAX_RESULT_IMAGE_BYTES:
                raise ImageProviderError("OpenAI result image exceeds maximum download size")
        return bytes(content)


def _content_excerpt(content: object) -> str:
    if isinstance(content, str):
        value = content
    else:
        try:
            value = json.dumps(content, ensure_ascii=False)
        except TypeError:
            value = repr(content)
    value = " ".join(value.split())
    if len(value) > 240:
        return f"{value[:240]}..."
    return value


def _http_error_detail(prefix: str, exc: httpx.HTTPError) -> str:
    detail = str(exc).strip()
    if not detail:
        detail = type(exc).__name__
    return f"{prefix}: {detail}"


def _decode_png_base64(value: str) -> bytes:
    try:
        return base64.b64decode("".join(value.split()), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ImageProviderError("OpenAI image response base64 was invalid") from exc


def _normalize_result_png(content: bytes) -> bytes:
    width, height = png_dimensions(content)
    if width > 0 and height > 0:
        return content
    try:
        with Image.open(BytesIO(content)) as image:
            image.load()
            output = BytesIO()
            normalized = image.convert("RGBA") if image.mode not in {"RGB", "RGBA"} else image
            normalized.save(output, format="PNG")
            return output.getvalue()
    except (OSError, UnidentifiedImageError, ValueError) as exc:
        raise ImageProviderError("OpenAI result image is not a valid image") from exc


def _validated_png_dimensions(content: bytes) -> tuple[int, int]:
    width, height = png_dimensions(content)
    if width <= 0 or height <= 0:
        raise ImageProviderError("OpenAI result image is not a valid PNG")
    return width, height


def _is_chat_completions_path(path: str) -> bool:
    return path.rstrip("/").endswith("/chat/completions")


def _secret_value(api_key: SecretStr | str | None) -> str | None:
    if isinstance(api_key, SecretStr):
        return api_key.get_secret_value()
    return api_key


def _json_payload(response: httpx.Response) -> JsonObject:
    payload = response.json()
    if not isinstance(payload, dict):
        raise ImageProviderError("Provider response was not a JSON object")
    return payload


def _try_parse_json(value: str) -> Any | None:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def _optional_string(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    return None


def _http_provider_status(status_code: int) -> str:
    if status_code in {400, 422}:
        return "provider_validation"
    if status_code in {401, 403}:
        return "invalid_credentials"
    if status_code == 429:
        return "rate_limited"
    return f"http_{status_code}"
