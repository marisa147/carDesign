from __future__ import annotations

from decimal import Decimal
from typing import Any

from caragent_core.enums import ReferenceRole

ProviderCapabilityMap = dict[str, dict[str, Any]]

LOCAL_PROVIDER = "local-deterministic"
BFL_PROVIDER = "bfl"
OPENAI_PROVIDER = "openai"
BFL_ALIASES = ("bfl", "black-forest-labs")
OPENAI_ALIASES = ("openai", "gpt")
BFL_DEFAULT_MODEL = "flux-2-pro-preview"
OPENAI_DEFAULT_IMAGE_MODEL = "gpt-image-2"
LOCAL_DEFAULT_MODEL = "local-concept-v1"
DETERMINISTIC_RECOMPOSITION_ROUTE = "deterministic_recomposition"
PROVIDER_MASKED_GENERATION_ROUTE = "provider_masked_generation"
REFERENCE_ROLE_VALUES = [role.value for role in ReferenceRole]


def build_provider_capability_map(
    *,
    default_provider: str,
    bfl_default_model: str,
    openai_default_model: str,
    provider_calls_enabled: bool,
    bfl_key_configured: bool,
    openai_key_configured: bool = False,
    v2_hosted_provider_rollout_enabled: bool,
    hosted_daily_call_limit: int | None,
    hosted_rate_limit_per_minute: int | None,
    max_estimated_cost_per_job: Decimal | None,
) -> ProviderCapabilityMap:
    """Return browser-safe provider capability metadata."""

    normalized_provider = normalize_provider_name(default_provider)
    guard_state = build_guard_state(
        hosted_daily_call_limit=hosted_daily_call_limit,
        hosted_rate_limit_per_minute=hosted_rate_limit_per_minute,
        max_estimated_cost_per_job=max_estimated_cost_per_job,
    )
    bfl_blocked_reasons = _hosted_blocked_reasons(
        credential_configured=bfl_key_configured,
        credential_env_name="AI_PROVIDER_BFL_API_KEY",
        provider_calls_enabled=provider_calls_enabled,
        v2_hosted_provider_rollout_enabled=v2_hosted_provider_rollout_enabled,
        hosted_quota_guard_enabled=guard_state["hosted_quota_guard_enabled"],
    )
    openai_blocked_reasons = _hosted_blocked_reasons(
        credential_configured=openai_key_configured,
        credential_env_name="AI_PROVIDER_OPENAI_API_KEY",
        provider_calls_enabled=provider_calls_enabled,
        v2_hosted_provider_rollout_enabled=v2_hosted_provider_rollout_enabled,
        hosted_quota_guard_enabled=guard_state["hosted_quota_guard_enabled"],
    )
    bfl_model = _hosted_default_model(bfl_default_model, provider_default=BFL_DEFAULT_MODEL)
    openai_model = _hosted_default_model(
        openai_default_model,
        provider_default=OPENAI_DEFAULT_IMAGE_MODEL,
    )

    return {
        LOCAL_PROVIDER: {
            "aliases": ["local", LOCAL_PROVIDER],
            "blocked_reasons": [],
            "caveats": ["Deterministic local concept preview provider for tests and fallback."],
            "credential_configured": True,
            "credential_required": False,
            "default_model": LOCAL_DEFAULT_MODEL,
            "display_name": "Local deterministic",
            "enabled": True,
            "estimated_cost": None,
            "guard_state": guard_state,
            "provider": LOCAL_PROVIDER,
            "selected_by_default": normalized_provider not in BFL_ALIASES + OPENAI_ALIASES,
            "supports": {
                "generation": True,
                "mask_aware_generation": False,
                "masks": False,
                "reference_image_inputs": False,
                "references": True,
            },
            "mask_input": {
                "accepted": False,
                "blocked_reason": "Local deterministic provider does not call image-edit APIs.",
                "content_types": [],
                "required": False,
            },
            "reference_input": {
                "accepted": False,
                "blocked_reason": (
                    "Local deterministic provider records references as prompt guidance "
                    "metadata only."
                ),
                "content_types": [],
                "prompt_guidance_roles": REFERENCE_ROLE_VALUES,
                "supported_roles": [],
                "unsupported_roles": [],
            },
            "supported_edit_routes": [DETERMINISTIC_RECOMPOSITION_ROUTE],
            "unsupported_edit_routes": [PROVIDER_MASKED_GENERATION_ROUTE],
        },
        BFL_PROVIDER: {
            "aliases": list(BFL_ALIASES),
            "allowed_models": [
                "flux-2-pro-preview",
                "flux-2-pro",
                "flux-2-flex",
            ],
            "blocked_reasons": bfl_blocked_reasons,
            "caveats": [
                "Hosted BFL calls are paid external calls and remain concept-preview only.",
                "Result delivery URLs are short-lived and must be stored before browser use.",
                (
                    "Current adapter uses FLUX.2 image editing/generation endpoints; "
                    "explicit mask input is only verified in FLUX.1 Fill docs and is "
                    "deferred."
                ),
            ],
            "credential_configured": bfl_key_configured,
            "credential_required": True,
            "default_model": bfl_model,
            "display_name": "BFL",
            "enabled": not bfl_blocked_reasons,
            "estimated_cost": {
                "basis": "configured guard plus provider response cost when available",
                "max_per_job": guard_state["max_estimated_cost_per_job"],
            },
            "guard_state": guard_state,
            "provider": BFL_PROVIDER,
            "selected_by_default": normalized_provider in BFL_ALIASES,
            "supports": {
                "generation": True,
                "input_image_editing": True,
                "mask_aware_generation": False,
                "masks": False,
                "reference_image_inputs": False,
                "references": False,
            },
            "mask_input": {
                "accepted": False,
                "blocked_reason": (
                    "Explicit mask payload support is not verified for the current "
                    "FLUX.2 adapter route."
                ),
                "content_types": [],
                "required": False,
            },
            "reference_input": {
                "accepted": False,
                "blocked_reason": (
                    "Reference image input is not verified for the current FLUX.2 "
                    "adapter route."
                ),
                "content_types": [],
                "prompt_guidance_roles": [],
                "supported_roles": [],
                "unsupported_roles": REFERENCE_ROLE_VALUES,
            },
            "supported_edit_routes": [],
            "unsupported_edit_routes": [PROVIDER_MASKED_GENERATION_ROUTE],
        },
        OPENAI_PROVIDER: {
            "aliases": list(OPENAI_ALIASES),
            "allowed_models": [
                "gpt-image-2",
                "gpt-image-1.5",
                "gpt-image-1",
                "gpt-image-1-mini",
                "gpt-5.5",
            ],
            "blocked_reasons": openai_blocked_reasons,
            "caveats": [
                (
                    "Hosted OpenAI image calls are paid external calls and remain "
                    "concept-preview only."
                ),
                (
                    "This adapter uses the Image API, or chat completions when routed "
                    "through an OpenAI-compatible relay."
                ),
                "Reference images and mask-aware edits are not enabled in this adapter yet.",
            ],
            "credential_configured": openai_key_configured,
            "credential_required": True,
            "default_model": openai_model,
            "display_name": "OpenAI GPT Image",
            "enabled": not openai_blocked_reasons,
            "estimated_cost": {
                "basis": "configured guard plus provider response usage when available",
                "max_per_job": guard_state["max_estimated_cost_per_job"],
            },
            "guard_state": guard_state,
            "provider": OPENAI_PROVIDER,
            "selected_by_default": normalized_provider in OPENAI_ALIASES,
            "supports": {
                "generation": True,
                "input_image_editing": False,
                "mask_aware_generation": False,
                "masks": False,
                "reference_image_inputs": False,
                "references": False,
            },
            "mask_input": {
                "accepted": False,
                "blocked_reason": "OpenAI mask-aware edits are not wired in this adapter yet.",
                "content_types": [],
                "required": False,
            },
            "reference_input": {
                "accepted": False,
                "blocked_reason": "OpenAI reference images are not wired in this adapter yet.",
                "content_types": [],
                "prompt_guidance_roles": [],
                "supported_roles": [],
                "unsupported_roles": REFERENCE_ROLE_VALUES,
            },
            "supported_edit_routes": [],
            "unsupported_edit_routes": [PROVIDER_MASKED_GENERATION_ROUTE],
        },
    }


def build_guard_state(
    *,
    hosted_daily_call_limit: int | None,
    hosted_rate_limit_per_minute: int | None,
    max_estimated_cost_per_job: Decimal | None,
) -> dict[str, Any]:
    guard_enabled = (
        hosted_daily_call_limit is not None
        and hosted_rate_limit_per_minute is not None
        and max_estimated_cost_per_job is not None
    )
    return {
        "daily_call_limit": hosted_daily_call_limit,
        "hosted_quota_guard_enabled": guard_enabled,
        "max_estimated_cost_per_job": (
            f"{max_estimated_cost_per_job:.4f}"
            if max_estimated_cost_per_job is not None
            else None
        ),
        "rate_limit_per_minute": hosted_rate_limit_per_minute,
    }


def normalize_provider_name(provider: str | None) -> str:
    normalized = (provider or "").strip().lower()
    return normalized or "disabled"


def provider_capabilities_as_list(capabilities: ProviderCapabilityMap) -> list[dict[str, Any]]:
    return [
        capabilities[LOCAL_PROVIDER],
        capabilities[BFL_PROVIDER],
        capabilities[OPENAI_PROVIDER],
    ]


def _hosted_default_model(default_model: str, *, provider_default: str) -> str:
    model = default_model.strip()
    if not model or model in {
        LOCAL_DEFAULT_MODEL,
        BFL_DEFAULT_MODEL,
        OPENAI_DEFAULT_IMAGE_MODEL,
    }:
        return provider_default
    if provider_default == OPENAI_DEFAULT_IMAGE_MODEL and not model.startswith("gpt-"):
        return provider_default
    if provider_default == BFL_DEFAULT_MODEL and model.startswith("gpt-image-"):
        return provider_default
    return model


def _hosted_blocked_reasons(
    *,
    credential_configured: bool,
    credential_env_name: str,
    provider_calls_enabled: bool,
    v2_hosted_provider_rollout_enabled: bool,
    hosted_quota_guard_enabled: bool,
) -> list[str]:
    reasons: list[str] = []
    if not v2_hosted_provider_rollout_enabled:
        reasons.append("V2_HOSTED_PROVIDER_ROLLOUT_ENABLED is disabled")
    if not provider_calls_enabled:
        reasons.append("AI_PROVIDER_CALLS_ENABLED is disabled")
    if not credential_configured:
        if credential_env_name == "AI_PROVIDER_OPENAI_API_KEY":
            reasons.append("OpenAI credential is missing")
        else:
            reasons.append(f"{credential_env_name} is missing")
    if not hosted_quota_guard_enabled:
        reasons.append("Hosted quota/rate/cost guards are incomplete")
    return reasons



