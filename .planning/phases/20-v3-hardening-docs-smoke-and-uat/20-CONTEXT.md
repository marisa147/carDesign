# Phase 20: V3 Hardening, Docs, Smoke, And UAT - Context

**Gathered:** 2026-06-20
**Status:** Ready for execution
**Source:** ROADMAP Phase 20 plus `C:/Users/25858/Downloads/MVP_FINAL.md`

<domain>
## Phase Boundary

Close v3.0 by proving the template library and production-readiness surfaces are reliable from a clean local path. This phase is evidence and documentation oriented: run focused validation, run local/Docker smoke when available, capture desktop/mobile Browser UAT evidence, update docs/release notes, audit requirement closure, and prepare the milestone for archive.

</domain>

<decisions>
## Implementation Decisions

### V3 Release Evidence
- Treat local deterministic generation as the required no-cost baseline.
- Keep hosted provider calls disabled and manual-only; do not require real provider credentials.
- Preserve concept-only labels on 3D, handoff, and production readiness preflight surfaces.
- Validate all five MVP templates and the legacy `generic-side-coupe` alias.
- Ensure Phase 20 evidence covers template catalog selection, template-aware generation/preview/edit, enhanced handoff ZIP evidence, and production preflight.

### Smoke And UAT
- Prefer existing root commands: `pnpm validate`, `pnpm contracts:check`, `pnpm smoke:local`, `pnpm smoke:worker -- --dry-run`.
- If Docker daemon is unavailable, record the blocker honestly and run dry-run/static fallback checks, but do not claim Docker smoke passed.
- Browser UAT must cover desktop and mobile widths and record DOM overflow plus key V3 signals.

### the agent's Discretion
- Use seeded local data or deterministic tests if live API/worker/browser orchestration is blocked by the sandbox.
- Update README/development docs with V3 sections rather than rewriting older milestone material.
- Keep release notes concise and explicit about future production handoff promotions.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Milestone Scope
- `.planning/ROADMAP.md` — Phase 20 goals, requirements, and plan list.
- `.planning/REQUIREMENTS.md` — V3-REL-01..05 closure requirements.
- `.planning/STATE.md` — Current milestone state and prior Phase 15-19 decisions.
- `C:/Users/25858/Downloads/MVP_FINAL.md` — Final MVP boundaries, acceptance criteria, and future V3 directions.

### Prior Evidence Patterns
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-DOCKER-SMOKE.md` — Docker smoke evidence format.
- `.planning/phases/14-v2-mvp-hardening-docs-smoke-and-uat/14-HUMAN-UAT.md` — Browser UAT evidence format.
- `.planning/phases/19-concept-handoff-and-production-readiness-preflight/19-VERIFICATION.md` — Latest V3 preflight validation evidence.

### Runtime Commands
- `package.json` — Root validation and smoke commands.
- `scripts/validate-all.mjs` — Aggregate validation sequence.
- `scripts/smoke-local.mjs` — Docker-backed local smoke.
- `scripts/smoke-worker-queue.mjs` — Worker smoke dry/live command.
- `README.md` and `docs/development.md` — User-facing runbooks to update for V3.
</canonical_refs>

<specifics>
## Specific Ideas

- Add V3 release notes and a V3 Browser UAT artifact under Phase 20.
- Add a V3 milestone audit file before archive readiness.
- Update README/development docs with focused Phase 15-20 command blocks and final V3 scope.
- Include any sandbox limitations in verification notes instead of hiding them.
</specifics>

<deferred>
## Deferred Ideas

- Print-ready PSD/AI/PDF handoff, verified scale/bleed/color/DPI, verified UV mapping, installer notes, real licensed vehicle templates, marketplace, quoting, payment, installer workflows, and automated legal licensing remain outside v3.0.
</deferred>

---

*Phase: 20-v3-hardening-docs-smoke-and-uat*
*Context gathered: 2026-06-20*

