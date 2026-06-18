# Phase 3: First Text-To-2D Generation Slice - Validation Strategy

**Date:** 2026-06-17
**Status:** Ready for execution

## Must-Have Truths

1. Natural-language design input creates a reusable structured brief.
2. The system records selected template/view and warns when normalizing unsupported input.
3. Generation jobs run asynchronously through a worker path and use durable PostgreSQL job state.
4. Prompt text, prompt payload, provider, model, parameters, input assets, output artifact, and costs where available are traceable.
5. Local deterministic generation creates a real image artifact and generated design version without external calls.
6. Missing-rights references are blocked before provider execution.
7. Failed generation jobs have clear durable errors and an eligible retry path that preserves the original brief.

## Automated Verification Matrix

| Dimension | Required Evidence | Suggested Command |
|-----------|-------------------|-------------------|
| Brief parser | Typed payload tests for required fields, defaults, unsupported warnings, and reuse. | `cd services/core && uv run pytest -q tests/test_generation_briefs.py` |
| Prompt planner | Prompt text/payload includes normalized brief, template/view, references, and provider parameters. | `cd services/core && uv run pytest -q tests/test_prompt_plans.py` |
| Provider adapters | Local provider emits valid PNG bytes; hosted adapter uses mocked HTTP and bounded polling. | `cd services/worker && uv run pytest -q tests/test_image_providers.py` |
| Worker pipeline | Worker records events, model run, artifact, version, success, failure, and retry metadata. | `cd services/worker && uv run pytest -q tests/test_generation_tasks.py` |
| API | Brief creation/update/reuse, generation submission, validation, and retry routes pass. | `cd services/api && uv run pytest -q tests/test_generation.py` |
| Contracts | OpenAPI and generated TypeScript client are current. | `corepack pnpm contracts:check` |
| Web proof | Minimal UI can create/reuse brief and show generated result/status if included. | `corepack pnpm --filter @caragent/web test` |
| Aggregate | Root validation remains green. | `corepack pnpm validate` |
| Docker smoke | Local generation path runs without hosted provider keys. | `corepack pnpm infra:up`; `corepack pnpm smoke:local`; `corepack pnpm infra:down` |

## Human UAT

Phase 3 UAT should stay narrow:

1. Start infrastructure, API, worker/local task path, and web if Phase 3 web proof exists.
2. Create or resume a workspace.
3. Submit a natural-language brief for the supported template/view.
4. Confirm a structured brief exists and can be reused.
5. Submit generation.
6. Confirm job status/events progress to `succeeded`.
7. Confirm one generated artifact and one generated design version are visible from API-backed state.
8. Force or simulate a provider failure and confirm the error is readable and retry creates a new durable attempt.

Hosted provider UAT is optional and must be explicitly enabled with real credentials. It is not required for baseline Phase 3 completion.

## Blockers

- Any implementation that requires hosted provider credentials for normal tests or Docker smoke fails validation.
- Any successful job without model-run prompt trace, generated artifact, and generated design version fails validation.
- Any provider call that can include missing-rights assets fails validation.
- Any synchronous HTTP generation path in FastAPI fails the architecture boundary.
- Any route/schema change that leaves generated contracts stale fails the phase gate.
