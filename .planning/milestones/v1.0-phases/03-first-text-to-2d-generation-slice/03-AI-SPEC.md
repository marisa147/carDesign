# AI-SPEC - Phase 03: First Text-To-2D Generation Slice

> AI design contract generated for Phase 3. Consumed by Phase 3 planning, execution, and later eval review.
> Locks provider architecture, implementation guidance, domain criteria, and evaluation strategy before implementation begins.

---

## 1. System Classification

**System Type:** Content Generation with structured extraction and asynchronous tool execution.

**Description:**
The system converts a pain-car natural-language request into a typed design brief, builds an auditable image prompt plan, runs a text-to-image provider through a worker-owned adapter, and persists the resulting 2D concept artifact and design version. A good result is not production-ready wrap art; it is a stored, inspectable concept render that reflects the requested vehicle/template, character/theme, style, palette, text intent, and references closely enough to iterate in later phases.

**Critical Failure Modes:**
1. The system silently loses or misreads user intent from the natural-language brief.
2. The system sends unconfirmed-rights reference assets or secret values to a hosted provider.
3. The worker marks a job succeeded without a stored generated artifact, model-run trace, and design version.
4. Provider failures leave the user with ambiguous state or no retry path.
5. The UI/API implies production-ready wrap quality when Phase 3 only delivers concept previews.

---

## 1b. Domain Context

**Industry Vertical:** Creative automotive concept design / itasha visual ideation.

**User Population:** Designers, car enthusiasts, and operators using a local MVP workbench to explore pain-car design concepts.

**Stakes Level:** Medium. Outputs are creative drafts, but IP/source rights, provider spend, and user trust matter.

**Output Consequence:** A successful output becomes a durable design version for preview, feedback, later iteration, and concept export. It is not suitable for installer production handoff.

### What Domain Experts Evaluate Against

| Dimension | Good | Bad | Stakes | Source |
|-----------|------|-----|--------|--------|
| Brief fidelity | Vehicle/view, character/theme, style, palette, text intent, and coverage are visibly represented. | Output ignores the vehicle or central theme. | High | Project requirements `GEN-01` through `GEN-07`. |
| Itasha plausibility | Composition reads like car livery/concept wrap art rather than a generic poster pasted near a car. | Character and graphics float disconnected from vehicle surface intent. | Medium | Project roadmap Phase 3 plus Phase 6 deferred controls. |
| Traceability | Stored prompt/model/provider/cost/artifact fields explain how the output was produced. | Only an image is stored; prompt/provider state is missing. | High | Phase 2 ledger decisions. |
| Rights discipline | Referenced assets have confirmed source/rights metadata before generation. | Missing-rights asset is used in hosted generation. | High | Phase 2 rights gate. |
| Concept labeling | Output is clearly treated as a concept preview. | UI/docs imply production-ready wrap deliverable. | Medium | v1 out-of-scope table. |

### Known Failure Modes in This Domain

- Text or logos can render inaccurately in raster image generation; deterministic overlay is deferred to Phase 6.
- Anime/character requests may collide with copyright or provider safety filters; Phase 3 must record source/rights and expose provider errors plainly.
- Vehicle model specificity can be over-promised; Phase 3 starts with one template/view and must warn on normalization.
- Provider result URLs can expire, so generated images must be copied into project object storage immediately.

### Regulatory / Compliance Context

No formal regulated-domain compliance is identified for Phase 3. The relevant constraints are IP/source-rights tracking, provider terms, no committed secrets, no raw key logging, and truthful concept-preview labeling.

### Domain Expert Roles for Evaluation

| Role | Responsibility |
|------|---------------|
| Product owner / designer | Review 10-20 reference prompts and mark whether concept outputs reflect brief intent. |
| Engineering reviewer | Verify traceability, rights gates, failure handling, and local deterministic repeatability. |

---

## 2. Framework Decision

**Selected Framework:** Direct provider-adapter pipeline using Pydantic contracts, Celery tasks, and small provider modules. No agent orchestration framework for Phase 3.

**Version:** Pin concrete Python dependencies during implementation. Expected additions: `httpx` for hosted provider HTTP calls and `Pillow` for deterministic local PNG generation.

**Rationale:**
Phase 3 is a narrow asynchronous image pipeline, not a multi-agent or RAG system. The existing architecture already has FastAPI, Pydantic, shared core services, Celery, PostgreSQL, and object storage. Direct adapters keep provider code isolated, make tests deterministic, and avoid adopting a broad AI framework before the typed pipeline proves itself.

**Alternatives Considered:**

| Framework | Ruled Out Because |
|-----------|------------------|
| LangChain | Adds broad abstractions for a simple text-to-image provider call and prompt trace path. |
| OpenAI Agents SDK | Useful for agent workflows, but Phase 3 does not need handoffs, tools, or multi-agent state. |
| CrewAI | Multi-agent role orchestration is explicitly deferred until typed artifacts are proven. |
| Provider SDK everywhere | Fast initially, but would violate the adapter boundary and make provider switching brittle. |

**Vendor Lock-In Accepted:** Partial. One hosted adapter may be implemented first, but provider/model names remain configuration-driven and the local deterministic provider remains the validation default.

---

## 3. Framework Quick Reference

### Installation

```bash
cd services/worker
uv add httpx pillow
```

### Core Imports

```python
from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel, Field
```

### Entry Point Pattern

```python
class ImageProvider(Protocol):
    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResult:
        ...


async def run_generation_job(job_id: UUID, settings: WorkerSettings) -> None:
    brief = await load_brief_for_job(job_id)
    prompt_plan = build_prompt_plan(brief)
    provider = select_provider(settings)
    result = await provider.generate(prompt_plan.to_provider_request())
    await persist_generated_artifact(job_id, prompt_plan, result)
```

### Key Abstractions

| Concept | What It Is | When You Use It |
|---------|------------|-----------------|
| `GenerationBriefPayload` | Typed normalized user intent. | Stored and reused before prompt planning. |
| `PromptPlan` | Exact prompt text, payload, provider parameters, template/view constraints. | Saved in `model_runs` and sent to provider adapter. |
| `ImageProvider` | Protocol for local and hosted image generators. | Worker selects one based on settings. |
| `ImageGenerationResult` | Generated bytes or downloadable URL plus metadata/cost/error fields. | Worker persists artifact and model run. |

### Common Pitfalls

1. Do not call providers from FastAPI handlers; keep expensive work in worker tasks.
2. Do not trust provider result URLs to remain available; copy output into project storage.
3. Do not rely on provider result state as the source of truth; PostgreSQL job/model-run/artifact rows are canonical.
4. Do not leak API keys or raw provider errors into job events or logs.
5. Do not require hosted provider access for baseline validation.

### Recommended Project Structure

```text
services/core/src/caragent_core/generation/
  briefs.py
  templates.py
  prompts.py
  providers.py

services/worker/src/caragent_worker/providers/
  base.py
  local.py
  bfl.py

services/worker/src/caragent_worker/tasks/jobs.py
```

---

## 4. Implementation Guidance

**Model Configuration:**
Use `AI_PROVIDER_DEFAULT`, `AI_PROVIDER_CALLS_ENABLED`, and provider-specific API-key env vars. Default remains local deterministic. Hosted adapter model names must be config-driven and checked against official docs during implementation.

**Core Pattern:**
FastAPI validates and stores brief/job intent, then Celery executes provider work. Core services own durable state transitions and record model-run/prompt/artifact/version state. Provider adapters return normalized results only.

**Tool Use:**
Use direct HTTP clients for hosted providers. If a provider SDK is introduced, isolate it behind an adapter module and mock it in worker tests.

**State Management:**
PostgreSQL stores jobs, events, briefs, model runs, artifacts, and versions. Object storage stores generated image bytes. Redis/Celery state is execution plumbing only.

**Context Window Strategy:**
Prompt planning should keep the generated prompt compact and structured: original request summary, normalized fields, template/view constraints, reference asset metadata, and rights/safety notes. Do not send entire conversation history in Phase 3.

---

## 4b. AI Systems Best Practices

### Structured Outputs with Pydantic

```python
class GenerationBriefPayload(BaseModel):
    original_request: str = Field(min_length=1)
    vehicle_template_id: str
    view: str
    character_theme: str
    style: str
    palette: list[str] = Field(default_factory=list)
    text: list[str] = Field(default_factory=list)
    coverage: str
    reference_asset_ids: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
```

Validation failures should return 422 before job creation when user input is incomplete, or durable failed job state when the issue is discovered in the worker.

### Async-First Design

The hosted provider adapter should use async HTTP requests and bounded polling where the provider uses asynchronous task IDs. Never block FastAPI request/response on provider completion.

### Prompt Engineering Discipline

Separate system constraints from user intent inside `PromptPlan`: keep the user request, normalized fields, template/view constraints, and provider parameters as distinct fields. Store the final prompt text exactly as sent.

### Context Window Management

Phase 3 uses a single-turn prompt plan built from the current brief and selected references. Multi-turn summarization and richer chat context are Phase 4+.

### Cost and Latency Budget

Record estimated and actual cost where provider data is available. Set a bounded hosted-provider timeout and max polling attempts. Local deterministic provider should run in seconds and cost zero.

---

## 5. Evaluation Strategy

### Dimensions

| Dimension | Rubric | Measurement Approach | Priority |
|-----------|--------|----------------------|----------|
| Brief schema validity | Required fields present; unsupported template/view normalized with warnings. | Code | Critical |
| Prompt trace completeness | Model run stores prompt text, prompt payload, provider, model, parameters, and input/output artifact links. | Code | Critical |
| Rights gate | Missing or unconfirmed reference rights block generation before provider call. | Code | Critical |
| Local output artifact | Local provider creates valid image bytes with dimensions and checksum stored. | Code | High |
| Failure/retry clarity | Forced provider failure records failed job, error event, sanitized latest_error, and retry creates a separate job. | Code | High |
| Concept quality | Output visibly reflects core brief fields in 10-20 curated prompts. | Human review, later optional LLM judge | Medium |

### Eval Tooling

**Primary Tool:** Code-based tests and a small human review dataset. Do not introduce a tracing/eval platform in Phase 3.

**Setup:**

```bash
cd services/core && uv run pytest -q tests/test_generation_*.py
cd services/worker && uv run pytest -q tests/test_generation_tasks.py
cd services/api && uv run pytest -q tests/test_generation.py
```

**CI/CD Integration:**

```bash
corepack pnpm validate
```

### Reference Dataset

**Size:** 10-20 examples to start.

**Composition:**
Include simple brief, unsupported template normalization, text request, color palette request, reference asset request with confirmed rights, missing-rights reference, provider failure, and retry.

**Labeling:**
Engineering labels code/trace correctness. Product/design reviewer labels concept alignment after hosted provider is enabled.

---

## 6. Guardrails

### Online (Real-Time)

| Guardrail | Trigger | Intervention |
|-----------|---------|--------------|
| Provider calls disabled | Hosted provider selected while `AI_PROVIDER_CALLS_ENABLED=false`. | Block before provider call and record clear failed/config error. |
| Missing provider key | Hosted provider enabled without required key. | Fail fast with sanitized configuration error. |
| Missing rights | Reference asset rights are not confirmed. | Reject request or fail job before provider call. |
| Unsupported template/view | User asks outside supported template/view. | Normalize and warn; do not claim broad support. |
| Provider error | Hosted call fails, times out, or returns no image. | Mark job failed with sanitized error and retry eligibility. |

### Offline (Flywheel)

| Metric | Sampling Strategy | Action on Degradation |
|--------|-------------------|-----------------------|
| Concept alignment | Review curated prompt outputs when hosted provider path changes. | Adjust prompt plan or provider/model configuration. |
| Failure rate | Inspect failed jobs by provider/model. | Improve adapter errors, timeouts, or fallback. |
| Cost drift | Compare estimated vs actual where provider data exists. | Adjust provider configuration or warnings. |

---

## 7. Production Monitoring

**Tracing Tool:** Internal model-run/job-event ledger for Phase 3. Langfuse/Arize/other external tracing is deferred until provider strategy hardens.

**Key Metrics to Track:**
- Job status counts by provider/model.
- Provider failure categories and sanitized latest errors.
- Time from queued to succeeded/failed.
- Estimated and actual cost where available.
- Count of blocked missing-rights references.

**Alert Thresholds:**
No production alerting in Phase 3. Verification should fail if local deterministic generation, rights gating, or prompt trace completeness regress.

**Smart Sampling Strategy:**
Sample failed hosted-provider jobs, outputs from newly configured provider/model combinations, and prompts with text/logo/reference requirements.

---

## Checklist

- [x] System type classified
- [x] Critical failure modes identified (>= 3)
- [x] Domain context researched
- [x] Regulatory/compliance context identified or explicitly noted
- [x] Domain expert roles defined for evaluation involvement
- [x] Framework selected with rationale documented
- [x] Alternatives considered and ruled out
- [x] Framework quick reference written
- [x] AI systems best practices written
- [x] Evaluation dimensions grounded in domain rubric ingredients
- [x] Each eval dimension has a concrete rubric
- [x] Eval tooling selected
- [x] Reference dataset spec written
- [x] CI/CD eval integration specified
- [x] Online guardrails defined
- [x] Production monitoring approach documented
