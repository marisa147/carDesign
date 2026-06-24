# Phase 32 Context: GPT Sectioned Generation Pipeline

## Goal

Convert completed briefs into section-level GPT design plans and regenerable outputs while keeping prompt/model/template trace durable.

## Requirements

- GPTD-01: GPT mode can produce an overall design direction from the completed brief and template context.
- GPTD-02: The system can split the design direction into section-level prompts and constraints tied to GR86/BRZ template sections.
- GPTD-03: User can regenerate an individual section while preserving the remaining section plan and template trace.
- GPTD-04: GPT-generated artwork outputs are recorded with prompt, model, section ids, template version, and provider trace.

## Current System

- `build_prompt_plan()` already creates provider/model prompt text and prompt_payload.
- Worker persists prompt_payload to model runs and propagates selected-template trace across artifacts, versions, job operations, and events.
- Section UI now creates targeted edit scopes from template sections.
- GPT/OpenAI provider exists behind config-driven provider settings.

## Scope

In scope:
- Add deterministic sectioned design plan into prompt_payload.
- Include overall direction, section prompts, section bounds/views, template id, model/provider, and regeneration target metadata.
- Preserve the plan across model_run prompt payload and worker output metadata.
- Use targeted edit metadata to mark section regeneration target.

Out of scope:
- True per-section image compositing.
- Multi-artifact section outputs.
- New persisted section-plan table.
