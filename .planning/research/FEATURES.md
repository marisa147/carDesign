# Feature Landscape

**Project:** 痛车设计生成 Agent  
**Domain:** AI-assisted custom vehicle livery / itasha design generation  
**Researched:** 2026-05-07  
**Overall confidence:** MEDIUM-HIGH

## Research Position

The product should be treated as a wrap-design workflow tool, not a generic image chatbot. Current AI wrap products converge on upload/describe/generate/refine/export, while professional wrap services still rely on vehicle-specific briefs, panel-aware layout, previews/proofs, revisions, and print handoff. For v1, the right promise is: text-to-design concept, structured parameters, basic 2D preview, iteration history, and image export. Do not promise production-ready vinyl files until vehicle templates, panel geometry, resolution, bleed, color, and human proofing workflows are mature.

Itasha is more constrained than normal commercial wraps. The product must understand anime-style composition, large character placement, supporting graphics, typography, color harmony, and vehicle body interruptions such as door seams, wheel arches, mirrors, bumpers, and handles. A "good" itasha result is not just a pretty generated car image; it must plausibly survive layout, scale, and future print planning.

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Dependencies | Notes |
|---------|--------------|------------|--------------|-------|
| Conversational design brief intake | Users expect to describe vehicle, character, style, colors, text, references, and desired coverage in natural language. | Medium | Chat UI, structured design schema, validation rules | Ask clarifying questions only for missing critical fields: vehicle/template, wrap area, theme, key assets, colors, and text. |
| Structured design parameters | AI generation must be repeatable and editable; raw prompts alone are not enough. | Medium | Pydantic/JSON schema, prompt planner, project persistence | Expose vehicle, coverage zones, character count, placement intent, style, palette, typography, finish, and negative constraints. |
| Reference and asset upload | Wrap workflows commonly start from car photos, character art, logos, inspiration, and existing flat designs. | Medium | Object storage, metadata, file validation, preview thumbnails | Support image uploads in v1. Track source type and user-provided rights assertion. |
| Vehicle/template selection | Wraps must be built around an actual vehicle, not an abstract car. | Medium-High | Template registry, panel/view metadata, preview layout | v1 should support one or a small set of vehicles/templates. Do not attempt broad model coverage first. |
| Coverage area selection | Full wrap, both sides, hood, banner, partial decal, and side-only designs have different layout needs and prices. | Medium | Vehicle template zones, generation constraints | Required for roadmap even if v1 starts with side/hood preview only. |
| Itasha composition planning | Character placement, visual theme, background graphics, and typography define whether the design feels like itasha. | Medium | Prompt/style planner, design heuristics, template zones | Include character-focus, split-character, full-scene, cyberpunk, racing/JDM, idol, mecha, and game-style presets. |
| Multi-variant generation | Users expect several directions before choosing one. | High | Image generation provider/model, async task queue, storage | Generate 2-4 variants per run when cost allows. Track the seed/model/prompt/params for each. |
| Generation status, retry, and failure recovery | Image generation is slow and failure-prone; users need visible progress and safe retries. | Medium | Async jobs, status polling/streaming, error taxonomy | Table-stakes for trust. Include cancel/retry and partial failure handling. |
| 2D preview workspace | v1 needs an inspectable preview before export. | Medium | Frontend canvas/image viewer, template overlays, stored outputs | Minimum: zoom/pan, before/after, thumbnail history, view switching for supported panels. |
| Iteration controls | Custom design workflows are revision-heavy. Users expect regenerate, adjust colors, change style, move emphasis, and fix text. | Medium-High | Structured params, prompt planner, job lineage, optional masks | v1 can start with text-guided whole-image or zone-level revisions; pixel-perfect layer editing can wait. |
| Local/region editing path | Users will want to fix one character, text block, color zone, or background without losing the whole design. | High | Mask UI or predefined zones, inpainting/edit model, versioning | Important after MVP. Keep v1 architecture ready even if only coarse zones ship. |
| Version history and comparison | Wrap services use drafts and revisions; users need to return to earlier variants. | Medium | Project model, asset/task metadata, UI thumbnails | Store input, structured params, prompts, model/provider, outputs, status, feedback, and parent version. |
| Export image | Users need to download/share the result. | Low-Medium | Storage, export service, metadata manifest | v1: PNG/JPG preview plus metadata JSON. Later: layered/print handoff formats. |
| Lightweight quality checks | Low resolution, bad text, poor contrast, seam collisions, and over-crowding are common wrap issues. | Medium | Image analysis, template zones, heuristics | v1 can warn rather than block. Prioritize text legibility, resolution, face-near-seam, and missing source asset warnings. |
| Basic rights and safety gate | Itasha often involves anime/game characters and logos. The product needs user rights assertions and cannot imply licensed official output. | Medium | Upload metadata, policy copy, moderation checks | Require user confirmation for uploaded assets and avoid built-in libraries of copyrighted character art unless licensed. |
| Project/session persistence | Users need saved designs, uploaded assets, and task history. | Medium | Database, object storage, auth/session model | Anonymous local session is acceptable for prototype; account-based storage can follow. |
| Shareable proof or simple presentation view | Wrap decisions often involve friends, clients, or installers. | Low-Medium | Stable asset URLs, export permissions | Optional for v1 if image export exists; useful before commercial handoff. |

## Differentiators

Features that set the product apart. Not required for the first usable loop, but highly valuable.

| Feature | Value Proposition | Complexity | Dependencies | Notes |
|---------|-------------------|------------|--------------|-------|
| Itasha-aware design director | Converts fandom intent into practical wrap composition: character focus, theme, supporting graphics, Japanese typography, racing/JDM cues, color matching, and readability. | Medium | Style taxonomy, prompt templates, critique heuristics | This is the clearest domain-specific differentiator over generic car wrap generators. |
| Panel-aware composition scoring | Warns when faces, logos, or text cross door gaps, handles, wheel arches, or bumpers. | High | Accurate template zones, object detection/segmentation, rule engine | Build as advisory first. Later can drive automatic layout correction. |
| Multi-view consistency | Keeps the same livery concept coherent across side, hood, front, rear, and eventually 3D. | High | Template views, generation conditioning, image-to-image, consistency evaluation | Strong differentiator because one-off photorealistic car images do not prove wrap continuity. |
| Vehicle-photo-to-outline bootstrap | Lets users upload a car photo and receive a usable outline/mockup base when no exact template exists. | High | Segmentation, perspective correction, outline extraction, manual adjustment | Useful later to reduce template library dependence. Keep separate from print-ready claims. |
| Editable layered design model | Separates character art, background, typography, decals, masks, and template overlay instead of storing only flat images. | High | Canvas/layer data model, storage, image editing pipeline | Unlocks real revisions and future print handoff. Too large for initial MVP unless scoped tightly. |
| AI critique and comparison | Scores variants for visual balance, color harmony, theme adherence, print risk, text clarity, and user prompt match. | Medium | Vision model/evaluator, rubric, stored variants | Helps users choose among outputs and creates a feedback loop for regeneration. |
| Rights-aware asset workflow | Tracks whether assets are user-owned, licensed, public domain, commissioned, or unknown. | Medium-High | Asset metadata, user declarations, warnings, admin review | Important for anime/game character use. This is product risk management, not legal advice. |
| Print-shop handoff pack | Exports source/print-ready packages with templates separated from artwork, scale notes, bleed/safe-zone checks, fonts outlined, and color/profile notes. | High | Layer model, template dimensions, preflight engine, export pipeline | Defer until after v1. This is where the product becomes professionally useful, but it is easy to overpromise. |
| Wrap material and finish simulation | Lets users preview gloss, matte, metallic, chrome, carbon, holographic, or named film colors. | Medium-High | Material library, renderer/shader or image adjustment, color notes | 3D wrap tools already use film/color libraries; this can differentiate once preview quality is strong. |
| 3D preview with template mapping | Lets users rotate around the car and inspect continuity. | High | Three.js/R3F, model assets, UV mapping, texture generation, performance tuning | Roadmap feature, not v1 blocker. Start with architecture hooks and maybe a placeholder. |
| Installer/client collaboration | Comments, approvals, quote handoff, and export package review. | Medium | Auth, sharing, roles, annotation UI | Useful if the product later serves wrap shops. Not required for individual MVP. |
| Localized itasha copywriting | Generates tasteful slogans, series-inspired typography ideas, romaji/Japanese/English variants, and placement suggestions. | Medium | LLM copy agent, typography constraints, user review | Valuable if handled as editable suggestions, not final unreviewed text. |
| Community gallery/remix | Shows inspiration, presets, and remixable designs. | Medium | Accounts, moderation, publishing, licensing | Defer until core generation and history are stable. Useful for acquisition, risky for IP/moderation. |

## Anti-Features

Features to explicitly not build, or not promise, in v1.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| One-click production-ready full wrap from any prompt | Vehicle wrap production depends on scale, panel geometry, bleed, resolution, colors, material, and installer proofing. A flat AI image is not enough. | Promise concept export in v1; later add print preflight and human-reviewable handoff packs. |
| Supporting every vehicle model/template | Template coverage is a library business and creates unbounded QA. | Start with one or a few templates and design the registry so more can be added later. |
| Full 3D auto model generation | Generating accurate vehicle geometry/UVs is a different hard problem from livery concept generation. | Use known models/templates later; keep v1 on 2D preview. |
| Built-in copyrighted anime character library without licenses | Creates rights and takedown risk, and falsely implies official permission. | Accept user uploads with rights declarations; add licensed/public-domain/owned asset libraries only when available. |
| LoRA/training platform in v1 | Training workflows add GPU, dataset, consent, quality, and abuse complexity before product-market validation. | Use external generation APIs or preconfigured models; log data needed for future fine-tuning. |
| Photoshop/Illustrator clone | A full editor will consume the milestone and still be worse than existing design tools. | Build targeted controls: prompt params, zones, color/style switches, history, and export. |
| Full quote/order/payment/installer marketplace | Commerce and fulfillment distract from validating the design loop. | Export/share first; add installer handoff after the design output is trusted. |
| Social marketplace before private workflow | Public sharing invites moderation, IP, and quality issues before the core tool works. | Keep private projects/history first; add curated gallery later. |
| Unlimited free generations | Image generation has real cost and users need predictable usage feedback. | Show job cost/status and impose quotas or credits once beyond prototype. |
| Photorealistic lifestyle renders as the only output | Pretty car photos can hide bad panel alignment and cannot guide wrap production. | Always keep a 2D/template-facing preview path, even if photorealistic mockups are generated. |
| Legal/install guarantees | The app cannot certify copyright clearance, print color match, installer quality, or road legality. | Provide warnings, metadata, and proofing tools; require human review before production. |

## Feature Dependencies

```text
Asset upload -> rights metadata -> prompt planning -> generation quality
Structured design params -> reproducible generation -> iteration controls -> version history
Vehicle template registry -> 2D preview -> seam/safe-zone checks -> print handoff -> 3D mapping
Async task queue -> visible progress -> retries/failures -> reliable history
Layer model -> local edits -> print-shop handoff -> advanced export
Variant storage -> comparison UI -> AI critique -> feedback-driven regeneration
```

## MVP Recommendation

Prioritize:

1. Conversational brief intake with structured parameters for vehicle/template, wrap area, character/theme, color palette, text, references, and constraints.
2. Reference upload with asset metadata and user rights assertion.
3. One or a few vehicle templates with 2D preview, thumbnails, zoom/pan, and basic panel/zone overlays.
4. Async AI generation that returns multiple concept variants and records prompt/model/params/output lineage.
5. Iteration loop: regenerate, change style/color/text, and create a new version without losing history.
6. Export PNG/JPG plus metadata JSON, with warnings that the output is a concept preview, not production-ready print art.
7. Lightweight quality warnings for low resolution, missing vehicle/template, text issues, and obvious face/text placement risks.

Defer:

- Print-ready AI/PDF/PSD packages until there is a layer model, template dimensions, scaling, preflight, and proofing workflow.
- 3D preview until 2D concept generation and history are stable.
- Large template libraries, quote/order/payment, installer marketplace, community gallery, and LoRA training until after the core design loop is validated.

## Suggested Phase Shape

| Phase | Feature Focus | Rationale |
|-------|---------------|-----------|
| Phase 1: Core design loop | Brief schema, upload, async generation, 2D preview, history, image export | Proves the central text-to-design-to-export value. |
| Phase 2: Itasha controls | Itasha style presets, composition planner, editable parameters, better revisions | Makes the product domain-specific instead of generic AI image generation. |
| Phase 3: Template intelligence | Panel zones, seam/safe-zone warnings, quality checks, more templates | Reduces the gap between concept art and real wrap planning. |
| Phase 4: Pro handoff | Layered model, print preflight, source/print-ready export, collaboration | Enables designers/wrap shops without overpromising in v1. |
| Phase 5: 3D and orchestration | 3D preview, material simulation, multi-view consistency, multi-agent evaluation | Builds on stable 2D outputs and structured history. |

## Sources

| Source | What It Supports | Confidence |
|--------|------------------|------------|
| [WrapStudio AI](https://wrapstudio.ai/) | Current AI wrap workflow: brief/specifications, inspiration upload, vehicle library, refinement, multi-view concepts, 2D/3D outputs. | MEDIUM-HIGH |
| [CarConceptsAI](https://www.carconceptsai.com/) | Current user expectation for upload car photo, choose/describe style, receive multiple photorealistic directions, download/share. | MEDIUM-HIGH |
| [3D Changer](https://www.3dchanger.com/) | Professional visualization expectations: import designs, vehicle model library, wrap film colors, real-time 3D, export images/videos, VR. | MEDIUM-HIGH |
| [WrapsDesigner](https://app.wrapsdesigner.com/) | Emerging differentiator: generating vehicle outlines and wrap designs from user-uploaded photos. | MEDIUM |
| [10KWRAPS Itasha design tips](https://10kwraps.com/itasha/tips/) | Itasha-specific design concerns: character/theme choice, color matching, panel alignment, seams, wheel arches, high-resolution artwork, balanced layouts, supporting graphics. | MEDIUM |
| [YesWrap custom wrap design service](https://yeswrap.com/products/custom-wrap-design-service) | Professional custom-wrap workflow: exact vehicle details, references/logos, colors, VIN, draft PDF proof, revisions, source and print-ready file delivery. | MEDIUM-HIGH |
| [Alwan Wraps print format guide](https://alwanwraps.com/blogs/print-design-resource-center/whats-the-best-format-for-printing) | Print-handoff constraints: PDF, layers/transparency/color profiles, scale, DPI, vector preference, color-profile caveats. | MEDIUM-HIGH |
| [Gatorprints vehicle wrap requirements](https://www.gatorprints.com/shop/print/print-your-vehicle-wrap/) | Production constraints: preferred file types, scale/DPI, vector text/logos, embedded images, bleed, proportional scaling, separate template layer. | MEDIUM-HIGH |
| [U.S. Copyright Office fair use FAQ](https://www.copyright.gov/help/faq/faq-fairuse.html) and [17 U.S.C. 106 via Cornell LII](https://www.law.cornell.edu/uscode/text/17/106) | Rights risk for copyrighted character/logo workflows and why the product should require user rights assertions and avoid implied licensing. | HIGH |

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Table stakes | HIGH | Multiple current AI wrap tools and wrap-service workflows converge on upload/brief/generate/refine/preview/export. |
| Itasha-specific features | MEDIUM-HIGH | Sources agree on composition, character placement, color, panel alignment, and print planning; the niche has fewer authoritative product sources. |
| Differentiators | MEDIUM | Derived from gaps between AI concept generators and professional wrap workflows. Needs validation with target users. |
| Anti-features | HIGH | Strongly supported by project scope plus production/file/IP constraints. |

