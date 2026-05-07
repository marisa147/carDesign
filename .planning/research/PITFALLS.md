# Domain Pitfalls

**Domain:** AI vehicle livery / itasha design generator
**Project:** carAgent - itasha design generation Agent
**Researched:** 2026-05-07
**Scope:** v1 text-to-design MVP with basic 2D preview, history, export, and an extensible path toward 3D preview and multi-agent orchestration.
**Overall confidence:** HIGH for AI image control limits, async job risks, copyright/trademark exposure, and cost controls; MEDIUM for vehicle-wrap production specifics because exact specs vary by vendor, material, printer, and installer.

## Phase Labels Used

These phase names are recommendations for roadmap planning, mapped to the current seed plan.

| Phase | Roadmap Meaning | Pitfalls It Must Address |
|-------|-----------------|--------------------------|
| Phase 1: MVP Guardrails | Text input, structured parameters, one or few vehicle templates, image generation, history, image export | IP, cost, traceability, UX scope, minimum async state |
| Phase 2: Controlled Generation | Reference images, masks, inpainting, style iteration, evaluation loop | Controllability, text/logo legibility, regeneration discipline |
| Phase 3: Production-Aware 2D Preview | Template zones, side/front/rear views, safe areas, bleed notes, export package | Texture fit, preview mismatch, print-readiness boundaries |
| Phase 4: Job Reliability and Cost Ops | Queue hardening, retries, cancellation, observability, quotas, provider adapters | Async failures, duplicate jobs, runaway spend, provider drift |
| Phase 5+: 3D and Multi-Agent Expansion | UV-mapped 3D preview, richer orchestration, multi-vehicle templates | 3D mismatch, agent complexity, scaling integration risk |

## Critical Pitfalls

### Pitfall 1: Treating prompt-only image generation as a layout engine

**What goes wrong:** The product promises "design my car wrap" but only sends a prompt to an image model. Results look visually rich but fail at exact character placement, side-panel continuity, readable text, decal hierarchy, and template-specific layout.

**Why it happens:** Diffusion tools can use controls such as ControlNet, IP-Adapter, inpainting, masks, image-to-image, depth, and edge maps, but these are conditioning tools, not guarantees of production layout. OpenAI's image guide also flags limitations around precise rendering, text, consistency, and composition.

**Warning signs:**
- Regeneration is the main answer to every bad output.
- Structured parameters are parsed but not used as hard constraints.
- The same prompt changes character position, side balance, or text placement across runs.
- There is no editable layer model for decals, text, background, and accents.
- "Use this exact reference character pose" is accepted without showing confidence or control mode.

**Prevention strategy:**
- Phase 1 must store a structured design spec before generation: vehicle template, view, palette, character placement zone, text strings, decal density, style, excluded zones, and export intent.
- Phase 2 must add control inputs deliberately: masks for vehicle panels, reference image conditioning, inpainting for local edits, and separate layer generation for character art, background graphics, text, and accents.
- Use regeneration only after showing which parameter changed. Every result should link back to the exact structured spec, prompt, model, seed if available, references, and generated artifacts.
- For v1, constrain the promise to "concept design preview" unless the system uses a verified template and layer/export pipeline.

**Roadmap phase:** Phase 1 for structured parameters; Phase 2 for controllable generation.

**Confidence:** HIGH.

### Pitfall 2: Ignoring copyright, character IP, trademarks, and commercial-use rights

**What goes wrong:** Users request known anime characters, game characters, brand logos, sponsor marks, or vehicle OEM badges. The app generates an attractive design and export button, implying the result is safe to print, sell, or publicly display.

**Why it happens:** Itasha workflows naturally involve copyrighted characters and recognizable marks. AI output ownership and copyrightability are not the same as clearance for third-party characters, trademarks, logos, reference images, or commercial printing. The US Copyright Office states that copyright protection still depends on human authorship; OpenAI's terms assign output rights between OpenAI and the user but also leave the user responsible for input/output use.

**Warning signs:**
- No rights fields exist for uploaded or referenced assets.
- "Commercial use" appears in UI copy without a clearance workflow.
- Exported files contain known characters/logos without any rights status.
- The app accepts "official X logo" or "draw character Y exactly" as normal prompts.
- History records omit the source image, license status, or user attestation.

**Prevention strategy:**
- Phase 1 must add an asset rights model: `source`, `owner`, `license_status`, `allowed_use`, `commercial_clearance`, `attribution_required`, and `user_attested_rights`.
- Add prompt/asset risk flags for known characters, logos, brands, public figures, and "official" marks. Do not claim legal clearance automatically.
- Export should clearly separate "concept preview" from "print/commercial-ready package." Commercial-ready export requires user-provided licensed assets or explicit clearance metadata.
- Provide a generic/inspired-by path: style, colors, layout, and user-owned art rather than exact protected character reproduction.
- Log provider, model, prompt, uploaded references, generated output, and rights flags for auditability.

**Roadmap phase:** Phase 1 must include this before any export; Phase 3 should enforce it in export packaging.

**Confidence:** HIGH.

### Pitfall 3: Designing pretty pictures that cannot fit a vehicle wrap

**What goes wrong:** The result looks good as a rectangular render but fails when mapped to doors, windows, wheel arches, mirrors, handles, panel seams, curvature, or wrap installer requirements. The exported image is not useful for even a rough production conversation.

**Why it happens:** Vehicle livery design is spatial and physical. It needs templates, panel zones, safe areas, bleed, resolution assumptions, and installer-specific requirements. A generic 1024x1024 or 16:9 render cannot represent wrap geometry.

**Warning signs:**
- No vehicle template or view is selected before generation.
- Designs place faces/text over windows, wheel arches, handles, or panel breaks.
- The export is a single beauty render with no separated side/front/rear assets.
- The same design is reused across sedans, coupes, vans, and SUVs.
- The app says "download wrap" but only provides a preview PNG.

**Prevention strategy:**
- Phase 1 should limit support to one or a few templates and call output a concept image.
- Phase 3 must introduce production-aware 2D templates with protected zones, bleed/safe-area overlays, view-specific canvases, and warnings when generated content crosses risky regions.
- Keep text and logos as editable/vector or high-resolution overlay layers where possible; do not rely on raster AI text for final export.
- Export a package with preview image, source design layers, structured parameters, template ID, and notes about installer verification.
- Defer "print-ready wrap files" until template accuracy, resolution, color workflow, and installer review are supported.

**Roadmap phase:** Phase 1 for scoped templates; Phase 3 for production-aware 2D preview and export.

**Confidence:** HIGH for the risk; MEDIUM for exact print specs because shops vary.

### Pitfall 4: Async generation failures create duplicate charges, lost jobs, and confusing UI states

**What goes wrong:** Long-running image tasks time out, retry, or get duplicated. Users see stuck progress, pay twice for the same generation, lose outputs after refresh, or cannot tell whether a failed job can be retried safely.

**Why it happens:** Image generation, inpainting, upscaling, and future 3D previews are slow and failure-prone. Celery supports retries and task state, but distributed task queues have at-least-once behavior patterns, so tasks must be idempotent and observable.

**Warning signs:**
- The frontend assumes a synchronous API call for image generation.
- There is no persistent job table separate from Celery task IDs.
- Retry buttons create new provider calls without idempotency keys.
- No state model exists for queued, running, retrying, failed, cancelled, succeeded, and expired.
- Users cannot cancel, resume, or see partial failure details.

**Prevention strategy:**
- Phase 1 must create a durable `generation_job` record before dispatching any worker task.
- Store idempotency keys at the job step level: parse, prompt plan, image generation, inpaint, upscale, export.
- Phase 4 must harden retries with max retry counts, exponential backoff, timeout classes, cancellation, dead-letter/manual review states, and separate retry policies for provider errors vs validation errors.
- Persist artifacts as soon as they are produced. Do not depend on temporary provider URLs as the source of truth.
- Frontend should poll or subscribe to a job-state API and show recoverable vs terminal failure explicitly.

**Roadmap phase:** Phase 1 for minimum persistent job state; Phase 4 for queue hardening.

**Confidence:** HIGH.

### Pitfall 5: Preview mismatch between 2D output, 3D view, and exported file

**What goes wrong:** The user approves a preview that cannot be reproduced in export, or a 3D view stretches, clips, mirrors, or misaligns decals compared with the 2D concept.

**Why it happens:** Three.js / React Three Fiber can load textures and display materials, but correct vehicle-wrap preview depends on model UVs, texture coordinates, panel mapping, camera assumptions, lighting, and matching the same source assets across preview and export. A nice 3D car render is not automatically a wrap proof.

**Warning signs:**
- 3D preview is planned before 2D templates are trustworthy.
- The preview uses one raster image mapped to the whole car.
- There is no test comparing preview output with exported artifacts.
- UI labels say "3D model generation" when it is only a stylized render or placeholder.
- Designs look correct from one camera angle but break on opposite sides or around curves.

**Prevention strategy:**
- v1 should make 2D concept preview the truth source. 3D can be disabled, labelled as experimental, or represented as a later roadmap capability.
- Phase 3 should add deterministic 2D views first: left, right, front, rear, top if supported.
- Phase 5 should only ship 3D preview with a known vehicle model, verified UV mapping, texture bounds, mirrored-side handling, and screenshot/export comparison tests.
- The export pipeline should use the same stored layers and template transforms as the preview, not a separate best-effort render path.

**Roadmap phase:** Phase 3 for 2D/export consistency; Phase 5+ for real 3D preview.

**Confidence:** HIGH.

### Pitfall 6: UX overpromises precision, availability, and print readiness

**What goes wrong:** The UI looks like a professional wrap workstation and implies exact control: real-time updates, high-fidelity 3D, export/share, parameter sliders, and history. Users then discover the system cannot guarantee layout, rights, color, exact character fidelity, or printable output.

**Why it happens:** The UI reference already presents 2D render, 3D model, parameter tuning, export, history, and share in one screen. That is a good north star, but v1 cannot honestly support every affordance as production-grade.

**Warning signs:**
- Buttons for 3D, export, share, and commercial output exist before the backend can enforce their states.
- Loading/progress bars show fake percentages.
- "Auto optimize" changes major design parameters without explaining what changed.
- Chat replies sound certain when the generation is only a best-effort concept.
- The user cannot inspect structured parameters before spending generation credits.

**Prevention strategy:**
- Phase 1 UI must gate unavailable features as disabled, beta, or "coming later" rather than pretending they work.
- Add a pre-generation review card that shows model/template, character/reference assets, text, palette, cost estimate, and rights warnings.
- Use honest status labels: concept preview, production-aware export, experimental 3D preview, failed validation, needs user clearance.
- Avoid exact claims such as "print-ready", "licensed", "real-time", or "guaranteed match" until the corresponding validation exists.

**Roadmap phase:** Phase 1 for wording and gating; Phase 3 for export claims.

**Confidence:** HIGH.

### Pitfall 7: Runaway generation cost and latency

**What goes wrong:** Users iterate freely through high-quality generations, inpainting, upscaling, and future 3D jobs. The system spends API/GPU budget faster than the product can monetize or debug.

**Why it happens:** Image APIs price by model, size, quality, and volume; self-hosted diffusion shifts cost to GPUs, queue capacity, storage, and maintenance. Failed jobs and duplicate retries can also spend money.

**Warning signs:**
- No per-job cost estimate before generation.
- "Regenerate" calls the most expensive model every time.
- Failed validation happens after the expensive provider call.
- Upscale runs automatically on every draft.
- History stores many full-resolution variants without retention policy.

**Prevention strategy:**
- Phase 1 should introduce budget fields on every job: estimated cost, actual provider cost, image count, quality tier, output size, and user/session quota.
- Use a draft-to-final flow: cheap planning/thumbnail first, high-quality generation and upscale only after user confirmation.
- Phase 4 should add cancellation, duplicate suppression, provider rate-limit handling, quota policies, cache reuse for identical inputs, and cost dashboards.
- Treat history as product data with retention and cleanup rules, not an infinite artifact dump.

**Roadmap phase:** Phase 1 for visible cost estimate and ledgers; Phase 4 for operational controls.

**Confidence:** HIGH.

## Moderate Pitfalls

### Pitfall 8: AI-rendered text and logos are unreadable or legally risky

**What goes wrong:** Slogans, kana/kanji, sponsor text, racing numbers, and logos are generated as pixels. They are misspelled, warped, unreadable, or too low-resolution for export. If the app generates exact commercial logos, it also increases trademark risk.

**Warning signs:**
- Text strings are passed only inside the image prompt.
- No OCR/readability check exists.
- Users cannot edit text after generation.
- Logo prompts use "official" or "exact" without user-provided licensed artwork.

**Prevention strategy:**
- Treat text as a layout layer controlled by the app. Generate text content with an LLM if useful, but render it with fonts/vector/text layers.
- Use AI images for background, style, and character composition; use deterministic overlays for slogans, names, numbers, and sponsor-like marks.
- Add a Phase 2 validation step for text readability and blocked/risky logo requests.

**Roadmap phase:** Phase 2.

**Confidence:** HIGH.

### Pitfall 9: No reproducibility across iterations

**What goes wrong:** A user likes "option 2" but cannot recreate, tweak, compare, or export it later because only the preview image was stored.

**Warning signs:**
- History stores image URL and timestamp only.
- Prompt templates and negative prompts are not versioned.
- Provider/model version, seed, dimensions, references, masks, and post-processing steps are missing.
- User feedback is free text not attached to a specific generation version.

**Prevention strategy:**
- Phase 1 must store generation lineage: structured spec, prompt plan, model/provider, parameters, seed when available, input asset hashes, masks, outputs, edit operations, cost, job state, and feedback.
- Phase 2 should make each edit a child version rather than overwriting the prior result.
- Add a diff view for parameters before visual diffing becomes necessary.

**Roadmap phase:** Phase 1.

**Confidence:** HIGH.

### Pitfall 10: Multi-agent orchestration before artifact contracts

**What goes wrong:** The architecture adds requirement parsing, prompt planning, copywriting, image generation, control, post-processing, preview, and evaluation agents early. Failures become hard to diagnose because agents exchange vague text instead of typed artifacts.

**Warning signs:**
- Agents pass prose summaries instead of schemas.
- No owner exists for the canonical design spec.
- Each agent can silently rewrite the user's intent.
- Debugging requires reading chat logs rather than inspecting artifacts.

**Prevention strategy:**
- Phase 1 should implement one reliable pipeline with typed artifacts before adding many agents.
- Define contracts early: `DesignBrief`, `AssetManifest`, `GenerationPlan`, `ControlPlan`, `PreviewPackage`, `ExportPackage`, and `EvaluationResult`.
- Phase 2 can split responsibilities only when each handoff is schema-validated and logged.

**Roadmap phase:** Phase 1 for contracts; Phase 2/5 for expansion.

**Confidence:** HIGH.

### Pitfall 11: Provider lock-in hides capability and policy differences

**What goes wrong:** The app hardcodes one image provider's prompt format, image size options, URL handling, safety behavior, pricing model, or editing API. Later switching to SDXL/FLUX/DALL-E/other providers becomes a rewrite.

**Warning signs:**
- Database fields are named after one provider's API.
- Provider response JSON is stored as the app's canonical data model.
- UI exposes model-specific parameters without abstraction.
- Safety, cost, and retry behavior are not normalized.

**Prevention strategy:**
- Phase 1 should define provider-neutral job and artifact schemas.
- Use provider adapters that translate internal `GenerationPlan` into provider calls and normalize output metadata.
- Store raw provider payloads separately for audit, not as the primary product model.
- Phase 4 should add provider health checks, model capability flags, and pricing configuration.

**Roadmap phase:** Phase 1 and Phase 4.

**Confidence:** HIGH.

## Minor Pitfalls

### Pitfall 12: Treating generated URLs as durable storage

**What goes wrong:** Provider-hosted URLs expire or change. History thumbnails break, exports disappear, and users cannot reopen old schemes.

**Warning signs:**
- The database stores only external image URLs.
- No object storage upload happens after generation.
- There is no thumbnail/full-res derivative policy.

**Prevention strategy:**
- Phase 1 must ingest generated assets into MinIO/S3 immediately and store object keys plus checksums.
- Keep derivatives explicit: thumbnail, preview, source image, mask, upscale, export.
- Add retention rules before public sharing.

**Roadmap phase:** Phase 1.

**Confidence:** HIGH.

### Pitfall 13: Color expectations drift from screen to print

**What goes wrong:** Users approve neon/cyber colors on a monitor, then printed wrap colors differ because the MVP never modeled printer, vinyl, lighting, ICC profile, or installer workflow.

**Warning signs:**
- UI labels output as "final" or "print accurate."
- No color profile or print disclaimer exists.
- Export has no notes for printer/installer verification.

**Prevention strategy:**
- v1 should label colors as visual concept only.
- Phase 3 should add export notes and, later, printer profile support if the product moves toward production files.
- Do not attempt color guarantees until real print/vendor workflow exists.

**Roadmap phase:** Phase 3.

**Confidence:** MEDIUM.

### Pitfall 14: Unsafe or unsuitable user uploads

**What goes wrong:** Users upload copyrighted reference packs, private vehicle photos, offensive content, low-resolution art, or images that cannot support the requested output.

**Warning signs:**
- Upload accepts any file without metadata, preview, or validation.
- The system does not record who supplied the asset or whether it is allowed for generation.
- Poor-quality inputs are silently used and blamed on the model.

**Prevention strategy:**
- Phase 1 should validate upload type, size, resolution, and user rights attestation.
- Phase 2 should add quality checks for character references and vehicle photos before spending generation credits.
- Store uploads as assets with metadata, not as anonymous chat attachments.

**Roadmap phase:** Phase 1 and Phase 2.

**Confidence:** HIGH.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|----------------|------------|
| Phase 1: MVP Guardrails | Export implies commercial/print readiness before rights and template checks exist | Ship concept export only; add rights metadata, scoped templates, cost estimate, and durable artifact storage |
| Phase 1: MVP Guardrails | History cannot reproduce results | Store full generation lineage, not just preview image URLs |
| Phase 2: Controlled Generation | Prompt tweaks masquerade as control | Add masks, layer model, inpainting, reference conditioning, and validation checks |
| Phase 2: Controlled Generation | AI text/logos degrade output quality | Render text/logo layers deterministically; require licensed user-uploaded logos for exact marks |
| Phase 3: Production-Aware 2D Preview | Preview and export diverge | Use the same template/layer transforms for preview and export; add safe zones and warnings |
| Phase 3: Production-Aware 2D Preview | Users think v1 output is print ready | Use "concept" vs "production-aware" labels and export notes |
| Phase 4: Job Reliability and Cost Ops | Retries duplicate provider charges | Add idempotency keys, cancellation, retry budgets, and per-step cost ledgers |
| Phase 4: Job Reliability and Cost Ops | Queue failures become invisible | Add durable job states, worker logs, failure categories, and user-facing recovery paths |
| Phase 5+: 3D and Multi-Agent Expansion | 3D preview becomes a misleading beauty render | Require verified UV templates, screenshot/export comparison tests, and experimental labeling until proven |
| Phase 5+: 3D and Multi-Agent Expansion | Multi-agent flow becomes untraceable | Use typed artifact contracts and schema validation before adding agents |

## Roadmap Prevention Summary

1. Start narrower than the UI mockup: one or a few templates, concept-level 2D output, honest export, durable history.
2. Make structured design specs the core product object. Prompts are implementation details, not the source of truth.
3. Add rights and cost guardrails before generation/export, not after users have already produced risky or expensive outputs.
4. Delay "print-ready" and real 3D claims until template accuracy, layer export, UV mapping, and validation exist.
5. Build the async/job model as product infrastructure in v1, because every generation, retry, preview, and export depends on it.

## Sources

- Hugging Face Diffusers documentation via Context7, `/huggingface/diffusers`: ControlNet, IP-Adapter, image-to-image, and inpainting pipelines. Confidence: HIGH.
- Celery documentation via Context7, `/websites/celeryq_dev_en_stable`: task retry, state handling, and distributed task behavior. Confidence: HIGH.
- React Three Fiber documentation via Context7, `/pmndrs/react-three-fiber`: texture loading, Canvas lifecycle, and performance patterns. Confidence: HIGH.
- OpenAI image generation guide: https://developers.openai.com/api/docs/guides/image-generation. Confidence: HIGH for OpenAI-specific image API limitations and cost/latency considerations.
- OpenAI Terms of Use: https://openai.com/policies/terms-of-use. Confidence: HIGH for OpenAI-specific input/output responsibility and output ownership framing.
- US Copyright Office, Copyright and Artificial Intelligence Part 2 - Copyrightability Report: https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf. Confidence: HIGH for US copyrightability/human-authorship framing.
- USPTO trademark basics: https://www.uspto.gov/trademarks/basics. Confidence: HIGH for trademark scope and brand-mark risk framing.
- 10K Wraps, car wrap file requirements: https://10kwraps.com/car-wrap-file-requirements-resolution-bleed-fonts/. Confidence: MEDIUM for industry print-prep guidance.
- Alwan Wraps, print design resource center: https://alwanwraps.com/blogs/print-design-resource-center/whats-the-best-format-for-printing. Confidence: MEDIUM for industry print-file guidance.
