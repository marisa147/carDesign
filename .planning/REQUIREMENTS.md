# Requirements: 痛车设计生成 Agent v4

**Defined:** 2026-06-22
**Core Value:** 用户能用自然语言快速得到一套可预览、可迭代、可导出的高质量痛车设计方案。

## v4 Requirements

### Generation Closure

- [ ] **GENC-01**: User can explicitly generate a first 2D concept from the active workbench brief without using a hidden or separate proof page.
- [ ] **GENC-02**: User can see queued, running, succeeded, failed, and canceled job state refresh automatically while a generation job is active.
- [ ] **GENC-03**: User can view the actual generated image in the 2D preview panel, with PreviewSpec overlays still available above it.
- [ ] **GENC-04**: User can resume an existing workspace and still see the latest generated image through a stable artifact content URL.

### Object Storage

- [ ] **STOR-01**: API and Worker use one shared object storage factory and compatible settings for local and S3-compatible modes.
- [ ] **STOR-02**: Local file storage preserves object content type and metadata needed for later reads.
- [ ] **STOR-03**: API can stream an artifact only after validating the artifact belongs to the requested workspace.
- [ ] **STOR-04**: Storage contract tests prove API uploads and Worker outputs can be read back through the same object key.

### Queue And Worker Reliability

- [ ] **RELY-01**: Generation, iteration, and retry job creation cannot enqueue a Celery task before the job transaction is committed.
- [ ] **RELY-02**: A durable dispatch outbox records pending job delivery and supports idempotent resend.
- [ ] **RELY-03**: Worker claims queued jobs with a conditional state transition so duplicate workers cannot both run the same job.
- [ ] **RELY-04**: Worker commits running/progress/failure/success state in short units of work instead of one long transaction around provider calls.
- [ ] **RELY-05**: API-visible job events reflect worker progress while provider calls are still in flight.

### Preview And Editing Correctness

- [ ] **PREV-01**: 3D preview screenshot capture uploads real WebGL canvas bytes instead of a hardcoded 1x1 PNG.
- [ ] **PREV-02**: API rejects 3D screenshot uploads when MIME, magic bytes, or actual image dimensions do not match the request.
- [ ] **PREV-03**: User can clear optional brief strings, lists, and reference assignments from the parameter panel.

### Agent And Template Fidelity

- [ ] **AGNT-01**: Natural-language brief parsing has a strict `BriefParser` boundary with deterministic fallback and no direct database writes by LLM output.
- [ ] **AGNT-02**: Local concept generation uses template package base and masks for body, window, wheel, handle, and panel lines.
- [ ] **AGNT-03**: Template compositor output prevents decorative layers from covering windows, wheels, and handles unless an explicit future production workflow allows it.

### Hardening And Observability

- [ ] **HARD-01**: Workspace-owned resources require server-derived ownership checks instead of trusting client supplied owner/requester fields.
- [ ] **HARD-02**: Upload and provider-download paths validate stream size, MIME, magic bytes, image dimensions, and unsafe URLs.
- [ ] **HARD-03**: Hosted provider quota and rate limit checks reserve and settle usage atomically.
- [ ] **HARD-04**: Logs and status records include request/job/model-run trace identifiers and queue age or running duration.

## Future Requirements

### Production Delivery

- **PROD-01**: User can export print-ready PSD/AI/PDF-style handoff with verified scale, bleed, color profile, DPI, and installer notes.
- **PROD-02**: User can preview verified vehicle-specific UV mapped wraps.
- **PROD-03**: User can order, quote, pay, or route a design to an installer network.

### Marketplace And Licensing

- **MRKT-01**: User can browse or purchase licensed vehicle templates in a marketplace.
- **MRKT-02**: System can automatically verify commercial character and brand licensing evidence.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Print-ready production export | v4 fixes concept workflow reliability and real artifact display; production wrap evidence remains missing. |
| Verified UV/true 3D vehicle mapping | The 3D preview remains concept-only until real vehicle shells and UV validation exist. |
| Marketplace, order, quote, payment, installer workflows | Commercial workflow is downstream of trustworthy generation, storage, auth, and production evidence. |
| Hosted provider production readiness claims | Provider quality, pricing, moderation, account access, quota behavior, and commercial terms remain unstable and must be re-verified separately. |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GENC-01 | Phase 21 | Pending |
| GENC-02 | Phase 21 | Pending |
| GENC-03 | Phase 21 | Pending |
| GENC-04 | Phase 21 | Pending |
| STOR-01 | Phase 22 | Pending |
| STOR-02 | Phase 22 | Pending |
| STOR-03 | Phase 22 | Pending |
| STOR-04 | Phase 22 | Pending |
| RELY-01 | Phase 23 | Pending |
| RELY-02 | Phase 23 | Pending |
| RELY-03 | Phase 23 | Pending |
| RELY-04 | Phase 23 | Pending |
| RELY-05 | Phase 23 | Pending |
| PREV-01 | Phase 24 | Pending |
| PREV-02 | Phase 24 | Pending |
| PREV-03 | Phase 24 | Pending |
| AGNT-01 | Phase 25 | Pending |
| AGNT-02 | Phase 25 | Pending |
| AGNT-03 | Phase 25 | Pending |
| HARD-01 | Phase 26 | Pending |
| HARD-02 | Phase 26 | Pending |
| HARD-03 | Phase 26 | Pending |
| HARD-04 | Phase 26 | Pending |

**Coverage:**
- v4 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0

---
*Requirements defined: 2026-06-22*
*Last updated: 2026-06-22 after v4 milestone initialization*
