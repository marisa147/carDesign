---
status: in_progress
date: 2026-06-22
slug: gpt-provider-mode
---

# Quick Task 260622: GPT Provider Mode

## Goal

Add an OpenAI/GPT mode so hosted text brief parsing and image generation can use GPT/OpenAI instead of BFL, while keeping BFL and local deterministic providers available.

## Design

- Add `openai` provider capabilities, status normalization, provider intent validation, and worker selection.
- Add OpenAI settings endpoints and a web settings page for API key, base URL, image model, text model, rollout/call toggles, and quota guards.
- Implement an OpenAI image provider using the Image API for single-prompt image generation.
- Implement an OpenAI brief parser adapter behind explicit settings, returning strict `BriefDraft` only.
- Keep deterministic parser and local provider as fallback when GPT is disabled or unconfigured.

## Verification

- Backend tests for OpenAI settings, provider status, provider selection, Image API payload/response handling, and GPT parser.
- Frontend tests for OpenAI settings client/page and provider selector normalization.
- Regenerate OpenAPI/TypeScript contracts and run focused API/worker/web validation.
