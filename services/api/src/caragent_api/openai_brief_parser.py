from __future__ import annotations

import json
from typing import Any

import httpx
from caragent_core.generation import BriefDraft, BriefParserInput

from caragent_api.config import ApiSettings

JsonObject = dict[str, Any]


SYSTEM_PROMPT = """
You parse pain-car concept requests into a strict BriefDraft JSON object.
Return only fields that are supported by the schema. Do not invent database ids.
When the user leaves design details open or asks you to decide,
infer and complete missing visual design details such as character placement,
supporting graphics, racing cues, typography intent, color harmony, coverage, palette,
and text direction. Do not just classify the request; produce a usable concept draft.
Use the user's language when preserving requested text, but keep concise design labels.
""".strip()


async def parse_openai_brief(
    parser_input: BriefParserInput,
    *,
    client: httpx.AsyncClient | None = None,
    settings: ApiSettings,
) -> BriefDraft:
    api_key = (
        settings.ai_provider_openai_api_key.get_secret_value()
        if settings.ai_provider_openai_api_key is not None
        else ""
    )
    if not api_key:
        raise ValueError("AI_PROVIDER_OPENAI_API_KEY is missing.")

    active_client = client or httpx.AsyncClient(base_url=settings.ai_provider_openai_base_url)
    try:
        response = await active_client.post(
            settings.ai_provider_openai_responses_path,
            headers={"Authorization": f"Bearer {api_key}"},
            json=_request_payload(parser_input, settings=settings),
            timeout=30.0,
        )
        if response.is_error:
            detail = _sanitize_provider_text(response.text, secret=api_key)
            raise ValueError(
                f"OpenAI brief parser failed: HTTP {response.status_code}: {detail}",
            )
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("OpenAI brief parser response was not a JSON object.")
        return BriefDraft.model_validate(_extract_brief_draft(payload))
    except httpx.HTTPError as error:
        raise ValueError(_sanitize_provider_text(str(error), secret=api_key)) from error
    finally:
        if client is None:
            await active_client.aclose()


def _request_payload(parser_input: BriefParserInput, *, settings: ApiSettings) -> JsonObject:
    schema = BriefDraft.model_json_schema()
    if _uses_chat_completions(settings.ai_provider_openai_responses_path):
        return {
            "messages": [
                {"role": "system", "content": _chat_system_prompt()},
                {
                    "role": "user",
                    "content": "Parse this input into brief_draft json:\n"
                    + json.dumps(
                        parser_input.model_dump(mode="json", exclude_none=True),
                        ensure_ascii=False,
                    ),
                },
            ],
            "model": settings.ai_provider_openai_text_model,
            "response_format": {"type": "json_object"},
        }

    return {
        "model": settings.ai_provider_openai_text_model,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps(
                    parser_input.model_dump(mode="json", exclude_none=True),
                    ensure_ascii=False,
                ),
            },
        ],
        "text": {
            "format": {
                "name": "brief_draft",
                "schema": schema,
                "strict": True,
                "type": "json_schema",
            },
        },
    }


def _uses_chat_completions(path: str) -> bool:
    return path.rstrip("/").endswith("/chat/completions")


def _chat_system_prompt() -> str:
    return (
        f"{SYSTEM_PROMPT}\n"
        "Return only a valid JSON object matching the BriefDraft schema. "
        "The response must be plain json. Do not wrap it in markdown. "
        "Use only these top-level keys when known: original_request, vehicle_template_id, "
        "view, character_theme, character_focus, style, palette, text, "
        "supporting_graphics, racing_cues, typography_intent, color_harmony, "
        "coverage, reference_asset_ids, reference_usage, overlay_logo_asset_ids. "
        "Return a flat object only; never use nested keys like base_vehicle, theme, or graphics."
    )


def _extract_brief_draft(payload: JsonObject) -> JsonObject:
    parsed = payload.get("output_parsed")
    if isinstance(parsed, dict):
        return parsed

    choices = payload.get("choices")
    if isinstance(choices, list):
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            message = choice.get("message")
            if not isinstance(message, dict):
                continue
            parsed_message = message.get("parsed")
            if isinstance(parsed_message, dict):
                return parsed_message
            content = message.get("content")
            if isinstance(content, str) and content.strip():
                return _json_object_from_text(content)
            if isinstance(content, list):
                for content_item in content:
                    if not isinstance(content_item, dict):
                        continue
                    text_value = content_item.get("text")
                    if isinstance(text_value, str) and text_value.strip():
                        return _json_object_from_text(text_value)

    output = payload.get("output")
    if isinstance(output, list):
        for output_item in output:
            if not isinstance(output_item, dict):
                continue
            content = output_item.get("content")
            if not isinstance(content, list):
                continue
            for content_item in content:
                if not isinstance(content_item, dict):
                    continue
                text_value = content_item.get("text")
                if isinstance(text_value, str) and text_value.strip():
                    return _json_object_from_text(text_value)

    output_text = payload.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return _json_object_from_text(output_text)

    raise ValueError("OpenAI brief parser response did not include a draft JSON object.")


def _json_object_from_text(value: str) -> JsonObject:
    value = _strip_markdown_json_fence(value)
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as error:
        raise ValueError("OpenAI brief parser response text was not valid JSON.") from error
    if not isinstance(parsed, dict):
        raise ValueError("OpenAI brief parser draft was not a JSON object.")
    return parsed


def _strip_markdown_json_fence(value: str) -> str:
    stripped = value.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.splitlines()
    if len(lines) >= 3 and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()
    return stripped


def _sanitize_provider_text(value: str, *, secret: str) -> str:
    sanitized = " ".join(value.split())
    return sanitized.replace(secret, "[redacted]") if secret else sanitized




