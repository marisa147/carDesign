from __future__ import annotations

import asyncio
import base64
import json
from dataclasses import replace
from decimal import Decimal

import httpx
import pytest
from caragent_core.editing import EditIntent
from caragent_core.generation import build_prompt_plan, create_generation_brief

from caragent_worker.config import WorkerSettings
from caragent_worker.providers import (
    BflImageProvider,
    ImageGenerationRequest,
    ImageProviderConfigurationError,
    ImageProviderError,
    ImageProviderTimeoutError,
    LocalDeterministicImageProvider,
    MaskEditRequest,
    select_image_provider,
)
from caragent_worker.recomposition import (
    DeterministicRecompositionError,
    recompose_targeted_edit,
)


def test_local_provider_returns_deterministic_png_without_external_calls() -> None:
    request = build_image_request()
    provider = LocalDeterministicImageProvider(width=320, height=160)

    result = asyncio.run(provider.generate(request))
    repeated = asyncio.run(provider.generate(request))

    assert result.image_bytes == repeated.image_bytes
    assert result.image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    assert png_dimensions(result.image_bytes) == (320, 160)
    assert result.content_type == "image/png"
    assert result.provider == "local-deterministic"
    assert result.model == "local-concept-v1"
    assert result.actual_cost == Decimal("0.0000")
    assert result.estimated_cost == Decimal("0.0000")
    assert result.metadata["external_calls"] is False
    assert result.metadata["concept_label"] == "concept_preview"
    assert result.metadata["width"] == 320
    assert result.metadata["height"] == 160


def test_local_provider_mirrors_preview_spec_metadata_and_overlay_output() -> None:
    request = build_image_request(text=["MOON DRIVE"])
    changed_text_request = build_image_request(text=["STAR RUN"])
    provider = LocalDeterministicImageProvider(width=320, height=160)

    result = asyncio.run(provider.generate(request))
    changed = asyncio.run(provider.generate(changed_text_request))

    assert result.metadata["preview_spec"]["overlay_layers"] == [
        {"id": "text-1", "kind": "text", "text": "MOON DRIVE", "zone_id": "door-main"},
    ]
    assert result.metadata["overlay_layer_count"] == 1
    assert result.metadata["safe_zone_count"] >= 5
    assert result.metadata["warning_count"] == 0
    assert result.image_bytes != changed.image_bytes


@pytest.mark.parametrize(
    ("instruction", "target_id", "expected"),
    [
        ("move x=0.40 y=0.42", "text-1", {"x": 0.4, "y": 0.42}),
        ("scale=1.25 opacity=0.50", "text-1", {"opacity": 0.5}),
        ("visible=false", "text-1", {"visible": False}),
        ("text=STAR RUN", "text-1", {"text": "STAR RUN"}),
        ("logo=logo-2", "logo-1", {"asset_id": "logo-2"}),
    ],
)
def test_recomposition_helper_applies_safe_overlay_changes(
    instruction: str,
    target_id: str,
    expected: dict[str, object],
) -> None:
    intent = build_edit_intent(target_id=target_id, instruction=instruction)

    result = recompose_targeted_edit(
        parent_preview_spec(),
        intent,
        height=160,
        width=320,
    )

    layer = next(
        item for item in result.preview_spec["overlay_layers"] if item["id"] == target_id
    )
    for key, value in expected.items():
        assert layer[key] == value
    assert result.image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    assert result.metadata["recomposition_route"] == "deterministic_recomposition"
    assert result.metadata["target"] == {"id": target_id, "type": "overlay_layer"}
    assert set(result.metadata["changed_fields"])


def test_recomposition_helper_rejects_unknown_overlay_target() -> None:
    intent = build_edit_intent(target_id="missing-layer", instruction="text=STAR RUN")

    with pytest.raises(DeterministicRecompositionError, match="target not found"):
        recompose_targeted_edit(parent_preview_spec(), intent, height=160, width=320)


def test_hosted_provider_is_not_selected_when_provider_calls_are_disabled() -> None:
    settings = WorkerSettings(
        ai_provider_default="bfl",
        ai_provider_calls_enabled=False,
        ai_provider_bfl_api_key="bfl-secret",
    )

    provider = select_image_provider(settings)

    assert isinstance(provider, LocalDeterministicImageProvider)


def test_bfl_provider_is_selected_when_hosted_calls_are_enabled() -> None:
    settings = WorkerSettings(
        ai_provider_default="bfl",
        ai_provider_calls_enabled=True,
        ai_provider_bfl_api_key="bfl-secret",
    )

    provider = select_image_provider(settings)

    assert isinstance(provider, BflImageProvider)


def test_unsupported_hosted_provider_fails_fast_when_calls_are_enabled() -> None:
    settings = WorkerSettings(
        ai_provider_default="openai",
        ai_provider_calls_enabled=True,
        ai_provider_openai_api_key="openai-secret",
    )

    with pytest.raises(ImageProviderConfigurationError, match="Unsupported image provider"):
        select_image_provider(settings)


def test_named_local_fallback_provider_uses_configured_local_dimensions() -> None:
    settings = WorkerSettings(ai_local_image_height=90, ai_local_image_width=180)
    request = build_image_request()

    provider = select_image_provider(settings, provider_name="local-deterministic")
    result = asyncio.run(provider.generate(request))

    assert isinstance(provider, LocalDeterministicImageProvider)
    assert png_dimensions(result.image_bytes) == (180, 90)
    assert result.metadata["external_calls"] is False


def test_bfl_provider_requires_api_key_before_hosted_calls() -> None:
    with pytest.raises(ImageProviderConfigurationError, match="AI_PROVIDER_BFL_API_KEY"):
        BflImageProvider(api_key=None)


def test_image_generation_request_can_carry_mask_edit_metadata() -> None:
    request = replace(build_image_request(), mask_edit=build_mask_edit_request())

    assert request.mask_edit is not None
    assert request.mask_edit.route_preference == "provider_masked_generation"
    assert request.mask_edit.mask_artifact_id == "11111111-1111-1111-1111-111111111111"
    assert request.mask_edit.region["unit"] == "normalized"
    assert request.mask_edit.prompt_delta["instructions"] == ["Repaint the selected door text."]


def test_bfl_provider_rejects_mask_edit_metadata_before_submit() -> None:
    request = replace(build_bfl_image_request(), mask_edit=build_mask_edit_request())
    submitted_paths: list[str] = []

    def handler(http_request: httpx.Request) -> httpx.Response:
        submitted_paths.append(http_request.url.path)
        return httpx.Response(500, text="should not be called")

    client = httpx.AsyncClient(
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )
    provider = BflImageProvider(api_key="bfl-secret", client=client)

    try:
        with pytest.raises(ImageProviderConfigurationError, match="provider_masked_generation"):
            asyncio.run(provider.generate(request))
    finally:
        asyncio.run(client.aclose())

    assert submitted_paths == []


def test_bfl_provider_submits_polls_and_downloads_result_bytes() -> None:
    request = build_bfl_image_request()
    seen_x_key_headers: list[str | None] = []
    seen_authorization_headers: list[str | None] = []

    def handler(http_request: httpx.Request) -> httpx.Response:
        if http_request.url.host == "api.test":
            seen_x_key_headers.append(http_request.headers.get("x-key"))
            seen_authorization_headers.append(http_request.headers.get("Authorization"))
            if http_request.url.path == "/v1/flux-2-pro-preview":
                payload = json.loads(http_request.content)
                assert payload["prompt"] == request.prompt_text
                assert payload["output_format"] == "png"
                assert "prompt_payload" not in payload
                return httpx.Response(
                    200,
                    json={
                        "cost": 0.03,
                        "id": "bfl-request-1",
                        "input_mp": 0.5,
                        "output_mp": 1.0,
                        "polling_url": "https://poll.test/v1/get_result?id=bfl-request-1",
                    },
                )
        if http_request.url.host == "poll.test":
            seen_x_key_headers.append(http_request.headers.get("x-key"))
            seen_authorization_headers.append(http_request.headers.get("Authorization"))
            assert http_request.url.path == "/v1/get_result"
            assert http_request.url.params["id"] == "bfl-request-1"
            return httpx.Response(
                200,
                json={
                    "id": "bfl-request-1",
                    "status": "Ready",
                    "result": {
                        "sample": "https://delivery.test/result.png?token=signed-secret",
                        "seed": 123,
                    },
                },
            )
        if http_request.url.host == "delivery.test":
            return httpx.Response(
                200,
                content=ONE_BY_ONE_PNG,
                headers={"content-type": "image/png"},
            )
        return httpx.Response(404, text="unexpected request")

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(base_url="https://api.test", transport=transport)
    provider = BflImageProvider(
        api_key="bfl-secret",
        client=client,
        max_poll_attempts=2,
        poll_interval_seconds=0,
    )

    try:
        result = asyncio.run(provider.generate(request))
    finally:
        asyncio.run(client.aclose())

    assert seen_x_key_headers == ["bfl-secret", "bfl-secret"]
    assert seen_authorization_headers == [None, None]
    assert result.image_bytes == ONE_BY_ONE_PNG
    assert result.content_type == "image/png"
    assert result.width == 1
    assert result.height == 1
    assert result.provider == "bfl"
    assert result.model == "flux-2-pro-preview"
    assert result.actual_cost == Decimal("0.0300")
    assert result.metadata["external_calls"] is True
    assert result.metadata["request_id"] == "bfl-request-1"
    assert result.metadata["input_mp"] == 0.5
    assert result.metadata["output_mp"] == 1.0
    assert result.metadata["seed"] == 123
    rendered_metadata = json.dumps(result.metadata, sort_keys=True)
    assert "signed-secret" not in rendered_metadata
    assert "delivery.test/result.png" not in rendered_metadata


def test_bfl_provider_times_out_with_bounded_polling() -> None:
    request = build_bfl_image_request()

    def handler(http_request: httpx.Request) -> httpx.Response:
        if http_request.url.path == "/v1/flux-2-pro-preview":
            return httpx.Response(
                200,
                json={
                    "id": "slow-request",
                    "polling_url": "https://api.test/v1/get_result?id=slow-request",
                },
            )
        return httpx.Response(200, json={"id": "slow-request", "status": "Pending"})

    client = httpx.AsyncClient(
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )
    provider = BflImageProvider(
        api_key="bfl-secret",
        client=client,
        max_poll_attempts=2,
        poll_interval_seconds=0,
    )

    try:
        with pytest.raises(ImageProviderTimeoutError, match="timed out"):
            asyncio.run(provider.generate(request))
    finally:
        asyncio.run(client.aclose())


def test_bfl_provider_sanitizes_provider_errors() -> None:
    request = build_bfl_image_request()

    def handler(_http_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="bfl-secret leaked by upstream")

    client = httpx.AsyncClient(
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )
    provider = BflImageProvider(api_key="bfl-secret", client=client)

    try:
        with pytest.raises(ImageProviderError) as exc_info:
            asyncio.run(provider.generate(request))
    finally:
        asyncio.run(client.aclose())

    assert "bfl-secret" not in str(exc_info.value)
    assert "[redacted]" in str(exc_info.value)


@pytest.mark.parametrize(
    ("status_code", "expected_status"),
    [
        (400, "provider_validation"),
        (402, "insufficient_credits"),
        (429, "rate_limited"),
    ],
)
def test_bfl_provider_maps_http_errors_to_provider_status(
    status_code: int,
    expected_status: str,
) -> None:
    request = build_bfl_image_request()

    def handler(_http_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, text="bfl-secret provider error")

    client = httpx.AsyncClient(
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )
    provider = BflImageProvider(api_key="bfl-secret", client=client)

    try:
        with pytest.raises(ImageProviderError) as exc_info:
            asyncio.run(provider.generate(request))
    finally:
        asyncio.run(client.aclose())

    assert exc_info.value.provider_status == expected_status
    assert "bfl-secret" not in str(exc_info.value)


def test_bfl_provider_maps_moderation_status_to_sanitized_error() -> None:
    request = build_bfl_image_request()

    def handler(http_request: httpx.Request) -> httpx.Response:
        if http_request.url.path == "/v1/flux-2-pro-preview":
            return httpx.Response(
                200,
                json={
                    "id": "moderated-request",
                    "polling_url": "https://api.test/v1/get_result?id=moderated-request",
                },
            )
        return httpx.Response(
            200,
            json={
                "id": "moderated-request",
                "message": "bfl-secret request rejected by policy",
                "status": "Request Moderated",
            },
        )

    client = httpx.AsyncClient(
        base_url="https://api.test",
        transport=httpx.MockTransport(handler),
    )
    provider = BflImageProvider(
        api_key="bfl-secret",
        client=client,
        max_poll_attempts=1,
        poll_interval_seconds=0,
    )

    try:
        with pytest.raises(ImageProviderError) as exc_info:
            asyncio.run(provider.generate(request))
    finally:
        asyncio.run(client.aclose())

    assert "moderated" in str(exc_info.value).lower()
    assert "bfl-secret" not in str(exc_info.value)
    assert exc_info.value.provider_status == "request_moderated"


def build_image_request(*, text: list[str] | None = None) -> ImageGenerationRequest:
    brief = create_generation_brief(
        original_request="White coupe with Sakura heroine, teal ribbons, and MOON DRIVE text.",
        character_theme="Sakura heroine",
        palette=["white", "teal"],
        text=text or ["MOON DRIVE"],
    )
    return ImageGenerationRequest.from_prompt_plan(build_prompt_plan(brief))


def build_edit_intent(*, target_id: str, instruction: str) -> EditIntent:
    return EditIntent.model_validate(
        {
            "mask": {
                "artifact_id": "11111111-1111-1111-1111-111111111111",
                "content_type": "image/png",
                "height": 160,
                "width": 320,
            },
            "mode": "targeted_edit",
            "prompt_delta": {
                "instructions": [instruction],
                "summary": instruction,
            },
            "region": {
                "height": 0.24,
                "type": "rectangle",
                "unit": "normalized",
                "width": 0.34,
                "x": 0.32,
                "y": 0.47,
            },
            "route_preference": "deterministic_recomposition",
            "schema_version": 1,
            "target": {"id": target_id, "type": "overlay_layer"},
        },
    )


def parent_preview_spec() -> dict[str, object]:
    return {
        "canvas": {"height": 768, "width": 1536},
        "overlay_layers": [
            {"id": "text-1", "kind": "text", "text": "MOON DRIVE", "zone_id": "door-main"},
            {"asset_id": "logo-1", "id": "logo-1", "kind": "logo", "zone_id": "rear-quarter"},
        ],
        "safe_zones": [
            {
                "height": 0.24,
                "id": "door-main",
                "kind": "body",
                "label": "Door / main side panel",
                "width": 0.34,
                "x": 0.32,
                "y": 0.47,
            },
            {
                "height": 0.2,
                "id": "rear-quarter",
                "kind": "body",
                "label": "Rear quarter panel",
                "width": 0.18,
                "x": 0.64,
                "y": 0.43,
            },
        ],
        "template": {
            "id": "generic-side-coupe",
            "label": "Generic side-view coupe",
            "view": "side",
        },
        "warnings": [],
    }


def build_bfl_image_request() -> ImageGenerationRequest:
    return replace(
        build_image_request(),
        model="flux-2-pro-preview",
        parameters={"output_format": "png"},
        provider="bfl",
    )


def build_mask_edit_request() -> MaskEditRequest:
    return MaskEditRequest(
        mask_artifact_id="11111111-1111-1111-1111-111111111111",
        mask_content_type="image/png",
        mask_height=768,
        mask_width=1536,
        parent_version_id="22222222-2222-2222-2222-222222222222",
        prompt_delta={
            "instructions": ["Repaint the selected door text."],
            "summary": "Repaint door text",
        },
        region={
            "height": 0.2,
            "type": "rectangle",
            "unit": "normalized",
            "width": 0.4,
            "x": 0.2,
            "y": 0.35,
        },
        route_preference="provider_masked_generation",
        target={"id": "door-main", "type": "safe_zone"},
    )


def png_dimensions(image_bytes: bytes) -> tuple[int, int]:
    return (
        int.from_bytes(image_bytes[16:20], "big"),
        int.from_bytes(image_bytes[20:24], "big"),
    )


ONE_BY_ONE_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+ip9s"
    "AAAAASUVORK5CYII=",
)
