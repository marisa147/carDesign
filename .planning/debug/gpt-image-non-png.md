---
status: resolved
trigger: GPT image generation failed after provider attempt
created: 2026-06-23
updated: 2026-06-23
---

# Current Focus

hypothesis: Codex/OpenAI relay chat-completion image generation is variable: it may return non-PNG image bytes, take longer than 30 seconds, return JSON image_url strings, or return text-only responses. The worker boundary must normalize image bytes and surface actionable provider errors.
next_action: resolved; retry generation from UI with restarted worker

# Evidence

- job e3a9bc68-7d5d-4694-afb9-9df4d9faba57 failed after 30.27s with empty provider error, matching httpx timeout behavior where str(ReadTimeout()) is empty.
- direct relay probes showed chat completions returning JSON image_url strings such as https://dummyimage.com and https://singlecolorimage.com.
- direct provider smoke after fixes succeeded 3/3 with PNG outputs of 1x1, 128x128, and 256x256.
- worker full test suite passed after the fixes.

# Resolution

root_cause: OpenAI/Codex relay mode is not a true image API. It returns image references through chat text with variable latency and sometimes non-PNG or text-only outputs; existing worker handling used a 30s timeout and hid empty HTTP timeout messages.
fix: Normalize valid provider image bytes to PNG, support relay image_url/base64 formats, raise readable timeout/no-image diagnostics, tighten relay prompt to JSON-only image references, and raise default generation timeout to 90s.
files_changed:
- services/worker/src/caragent_worker/providers/openai.py
- services/worker/src/caragent_worker/config.py
- services/worker/tests/test_image_providers.py
- services/worker/tests/test_config.py
- services/worker/.env
- services/api/.env
