from __future__ import annotations

from decimal import Decimal
from typing import Any

ProviderCapabilityMap = dict[str, dict[str, Any]]

LOCAL_PROVIDER = "local-deterministic"
BFL_PROVIDER = "bfl"
BFL_ALIASES = ("bfl", "black-forest-labs")
BFL_DEFAULT_MODEL = "flux-2-pro-preview"
LOCAL_DEFAULT_MODEL = "local-concept-v1"
DETERMINISTIC_RECOMPOSITION_ROUTE = "deterministic_recomposition"
PROVIDER_MASKED_GENERATION_ROUTE = "provider_masked_generation"


def build_provider_capability_map(
    *,
    default_provider: str,
    default_model: str,
    provider_calls_enabled: bool,
    bfl_key_configured: bool,
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
    bfl_blocked_reasons = _bfl_blocked_reasons(
        provider_calls_enabled=provider_calls_enabled,
        bfl_key_configured=bfl_key_configured,
        v2_hosted_provider_rollout_enabled=v2_hosted_provider_rollout_enabled,
        hosted_quota_guard_enabled=guard_state["hosted_quota_guard_enabled"],
    )
    bfl_model = _bfl_default_model(default_model)

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
            "selected_by_default": normalized_provider not in BFL_ALIASES,
            "supports": {
                "generation": True,
                "mask_aware_generation": False,
                "masks": False,
                "references": False,
            },
            "mask_input": {
                "accepted": False,
                "blocked_reason": "Local deterministic provider does not call image-edit APIs.",
                "content_types": [],
                "required": False,
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
    return [capabilities[LOCAL_PROVIDER], capabilities[BFL_PROVIDER]]


def _bfl_default_model(default_model: str) -> str:
    model = default_model.strip()
    if not model or model == LOCAL_DEFAULT_MODEL:
        return BFL_DEFAULT_MODEL
    return model


def _bfl_blocked_reasons(
    *,
    provider_calls_enabled: bool,
    bfl_key_configured: bool,
    v2_hosted_provider_rollout_enabled: bool,
    hosted_quota_guard_enabled: bool,
) -> list[str]:
    reasons: list[str] = []
    if not v2_hosted_provider_rollout_enabled:
        reasons.append("V2_HOSTED_PROVIDER_ROLLOUT_ENABLED is disabled")
    if not provider_calls_enabled:
        reasons.append("AI_PROVIDER_CALLS_ENABLED is disabled")
    if not bfl_key_configured:
        reasons.append("AI_PROVIDER_BFL_API_KEY is missing")
    if not hosted_quota_guard_enabled:
        reasons.append("Hosted quota/rate/cost guards are incomplete")
    return reasons
