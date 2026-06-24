from __future__ import annotations

from decimal import Decimal
from hashlib import sha256

from caragent_core.generation import TemplateCompositionRequest, TemplateCompositionResult

from caragent_worker.providers.base import (
    ImageGenerationRequest,
    ImageGenerationResult,
    JsonObject,
    generation_route_for_request,
)
from caragent_worker.template_compositor import PillowTemplateCompositor

LOCAL_PROVIDER = "local-deterministic"
LOCAL_MODEL = "local-concept-v1"


class LocalDeterministicImageProvider:
    def __init__(
        self,
        *,
        width: int = 1536,
        height: int = 768,
        provider: str = LOCAL_PROVIDER,
        model: str = LOCAL_MODEL,
        compositor: PillowTemplateCompositor | None = None,
    ) -> None:
        self._width = width
        self._height = height
        self._provider = provider
        self._model = model
        self._compositor = compositor or PillowTemplateCompositor()

    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        composition = _compose_concept_preview(
            request,
            compositor=self._compositor,
            width=self._width,
            height=self._height,
        )
        preview_spec = _preview_spec_from_payload(request.prompt_payload)
        reference_warnings = _json_list(request.prompt_payload.get("reference_warnings"))
        metadata: JsonObject = {
            "concept_label": request.concept_label,
            "external_calls": False,
            "generation_route": generation_route_for_request(
                request,
                template_composited=True,
            ),
            "height": composition.height,
            "input_artifact_ids": list(request.input_artifact_ids),
            "overlay_layer_count": len(_json_list(preview_spec.get("overlay_layers"))),
            "preview_spec": preview_spec,
            "prompt_digest": sha256(request.prompt_text.encode("utf-8")).hexdigest(),
            "reference_warning_count": _integer_from_payload(
                request.prompt_payload.get("reference_warning_count"),
                fallback=len(reference_warnings),
            ),
            "reference_warnings": reference_warnings,
            "safe_zone_count": len(_json_list(preview_spec.get("safe_zones"))),
            "template_compositor": dict(composition.metadata),
            "warning_count": len(_json_list(preview_spec.get("warnings"))),
            "width": composition.width,
        }
        metadata.update(_vehicle_template_trace_metadata(request.prompt_payload, preview_spec))
        if request.reference_usage is not None:
            metadata["reference_usage"] = dict(request.reference_usage)

        return ImageGenerationResult(
            actual_cost=Decimal("0.0000"),
            content_type=composition.content_type,
            estimated_cost=Decimal("0.0000"),
            height=composition.height,
            image_bytes=composition.image_bytes,
            metadata=metadata,
            model=self._model,
            provider=self._provider,
            width=composition.width,
        )


def render_local_concept_preview(
    request: ImageGenerationRequest,
    *,
    width: int,
    height: int,
) -> bytes:
    return _compose_concept_preview(
        request,
        compositor=PillowTemplateCompositor(),
        width=width,
        height=height,
    ).image_bytes


def _compose_concept_preview(
    request: ImageGenerationRequest,
    *,
    compositor: PillowTemplateCompositor,
    width: int,
    height: int,
) -> TemplateCompositionResult:
    return compositor.compose(
        TemplateCompositionRequest(
            height=height,
            prompt_payload=dict(request.prompt_payload),
            prompt_text=request.prompt_text,
            width=width,
        ),
    )


def _preview_spec_from_payload(prompt_payload: JsonObject) -> JsonObject:
    preview_spec = prompt_payload.get("preview_spec")
    return dict(preview_spec) if isinstance(preview_spec, dict) else {}


def _vehicle_template_trace_metadata(
    prompt_payload: JsonObject,
    preview_spec: JsonObject,
) -> JsonObject:
    template = prompt_payload.get("vehicle_template")
    if not isinstance(template, dict):
        preview_template = preview_spec.get("template")
        template = preview_template if isinstance(preview_template, dict) else {}
    template_id = _text(template.get("id"))
    if template_id is None:
        return {}

    canvas = preview_spec.get("canvas")
    canvas_value = canvas if isinstance(canvas, dict) else {}
    source = template.get("source")
    source_value = source if isinstance(source, dict) else {}
    readiness = template.get("readiness")
    readiness_value = readiness if isinstance(readiness, dict) else {}
    return {
        "vehicle_template": {
            "canvas": {
                "height": _integer_from_payload(canvas_value.get("height"), fallback=0),
                "width": _integer_from_payload(canvas_value.get("width"), fallback=0),
            },
            "catalog_eligible": bool(readiness_value.get("catalog_eligible", False)),
            "id": template_id,
            "label": _text(template.get("label")) or template_id,
            "license_status": _text(source_value.get("license_status")) or "unknown",
            "source_type": _text(source_value.get("source_type")) or "unknown",
            "view": _text(template.get("view")) or "unknown",
        },
    }


def _json_list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _integer_from_payload(value: object, *, fallback: int) -> int:
    if isinstance(value, int):
        return value
    return fallback


def _text(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None
