from __future__ import annotations

import asyncio
import base64
import json
from io import BytesIO

import httpx
import pytest
from caragent_core.generation import (
    PromptProviderSettings,
    build_prompt_plan,
    create_generation_brief,
)
from PIL import Image

from caragent_worker.config import WorkerSettings
from caragent_worker.providers import (
    FULL_CONCEPT_IMAGE_ROUTE,
    TEMPLATE_COMPOSITED_PREVIEW_ROUTE,
    ImageGenerationRequest,
    ImageProviderError,
    LocalDeterministicImageProvider,
    OpenAIImageProvider,
)
from caragent_worker.providers.openai import OPENAI_MAX_RESULT_IMAGE_BYTES


def _png_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGBA", (2, 1), (20, 160, 220, 255)).save(output, format="PNG")
    return output.getvalue()


def _request(
    *,
    provider: str = "openai",
    model: str = "gpt-image-2",
) -> ImageGenerationRequest:
    brief = create_generation_brief(
        original_request="White coupe with a cyan racing heroine.",
        palette=["white", "cyan", "black"],
        text=["MIKU RACING"],
    )
    plan = build_prompt_plan(
        brief,
        provider_settings=PromptProviderSettings(
            model=model,
            parameters={"quality": "medium", "size": "1536x768"},
            provider=provider,
        ),
    )
    return ImageGenerationRequest.from_prompt_plan(plan)


def _chat_response(image_url: str) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "choices": [
                {
                    "message": {
                        "content": json.dumps({"image_url": image_url}),
                    },
                },
            ],
        },
    )


def test_local_provider_records_template_composited_generation_route() -> None:
    provider = LocalDeterministicImageProvider(width=320, height=160)
    request = _request(
        provider="local-deterministic",
        model="local-concept-v1",
    )

    result = asyncio.run(provider.generate(request))

    assert result.metadata["generation_route"] == TEMPLATE_COMPOSITED_PREVIEW_ROUTE


def test_openai_provider_records_full_concept_generation_route() -> None:
    image = _png_bytes()

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/images/generations"
        return httpx.Response(
            200,
            json={"data": [{"b64_json": base64.b64encode(image).decode("ascii")}]},
        )

    client = httpx.AsyncClient(
        base_url="https://api.openai.test/v1",
        transport=httpx.MockTransport(handler),
    )
    provider = OpenAIImageProvider(api_key="secret", client=client)
    try:
        result = asyncio.run(provider.generate(_request()))
    finally:
        asyncio.run(client.aclose())

    assert result.metadata["generation_route"] == FULL_CONCEPT_IMAGE_ROUTE


@pytest.mark.parametrize(
    "image_url",
    [
        "http://images.example.test/concept.png",
        "https://127.0.0.1/concept.png",
        "https://localhost/concept.png",
    ],
)
def test_openai_provider_rejects_unsafe_remote_image_urls(image_url: str) -> None:
    seen_paths: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_paths.append(request.url.path)
        if request.url.path == "/v1/chat/completions":
            return _chat_response(image_url)
        return httpx.Response(500, text="remote download should not be attempted")

    client = httpx.AsyncClient(
        base_url="https://relay.example.test/v1",
        transport=httpx.MockTransport(handler),
    )
    provider = OpenAIImageProvider(
        api_key="secret",
        client=client,
        image_path="/chat/completions",
    )
    try:
        with pytest.raises(ImageProviderError, match="must use HTTPS|host is not public"):
            asyncio.run(provider.generate(_request(model="gpt-5.5")))
    finally:
        asyncio.run(client.aclose())

    assert seen_paths == ["/v1/chat/completions"]


def test_openai_provider_enforces_configured_result_host_allowlist() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            return _chat_response("https://untrusted.example.test/concept.png")
        return httpx.Response(500, text="remote download should not be attempted")

    client = httpx.AsyncClient(
        base_url="https://relay.example.test/v1",
        transport=httpx.MockTransport(handler),
    )
    provider = OpenAIImageProvider(
        api_key="secret",
        allowed_image_hosts=("trusted.example.test",),
        client=client,
        image_path="/chat/completions",
    )
    try:
        with pytest.raises(ImageProviderError, match="host is not allowed"):
            asyncio.run(provider.generate(_request(model="gpt-5.5")))
    finally:
        asyncio.run(client.aclose())


def test_openai_provider_rejects_oversized_remote_image_before_buffering() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            return _chat_response("https://images.example.test/concept.png")
        if request.url.host == "images.example.test":
            return httpx.Response(
                200,
                content=_png_bytes(),
                headers={
                    "content-length": str(OPENAI_MAX_RESULT_IMAGE_BYTES + 1),
                    "content-type": "image/png",
                },
            )
        return httpx.Response(404)

    client = httpx.AsyncClient(
        base_url="https://relay.example.test/v1",
        transport=httpx.MockTransport(handler),
    )
    provider = OpenAIImageProvider(
        api_key="secret",
        client=client,
        image_path="/chat/completions",
    )
    try:
        with pytest.raises(ImageProviderError, match="exceeds maximum download size"):
            asyncio.run(provider.generate(_request(model="gpt-5.5")))
    finally:
        asyncio.run(client.aclose())


def test_openai_provider_rejects_non_image_remote_content() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/chat/completions":
            return _chat_response("https://images.example.test/concept.png")
        if request.url.host == "images.example.test":
            return httpx.Response(
                200,
                content=b"not-an-image",
                headers={"content-type": "text/plain"},
            )
        return httpx.Response(404)

    client = httpx.AsyncClient(
        base_url="https://relay.example.test/v1",
        transport=httpx.MockTransport(handler),
    )
    provider = OpenAIImageProvider(
        api_key="secret",
        client=client,
        image_path="/chat/completions",
    )
    try:
        with pytest.raises(ImageProviderError, match="content type is not supported"):
            asyncio.run(provider.generate(_request(model="gpt-5.5")))
    finally:
        asyncio.run(client.aclose())


def test_worker_settings_normalize_openai_image_host_allowlist() -> None:
    settings = WorkerSettings(
        ai_provider_openai_allowed_image_hosts=" Images.Example.Test,cdn.example.test, ",
    )

    assert settings.openai_allowed_image_hosts == (
        "images.example.test",
        "cdn.example.test",
    )
