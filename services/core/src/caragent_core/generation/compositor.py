from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

JsonObject = dict[str, Any]


@dataclass(frozen=True, slots=True)
class TemplateCompositionRequest:
    prompt_text: str
    prompt_payload: JsonObject
    width: int
    height: int


@dataclass(frozen=True, slots=True)
class TemplateCompositionResult:
    image_bytes: bytes
    width: int
    height: int
    metadata: JsonObject = field(default_factory=dict)
    content_type: str = "image/png"


class TemplateCompositor(Protocol):
    def compose(self, request: TemplateCompositionRequest) -> TemplateCompositionResult:
        """Compose a concept image from governed template package assets."""