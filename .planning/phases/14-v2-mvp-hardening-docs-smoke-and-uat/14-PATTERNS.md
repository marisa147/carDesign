# Phase 14 Pattern Map

This file points execution agents at local patterns to reuse during Phase 14. It is not a replacement for reading the referenced files.

## Validation Patterns

| Need | Reuse |
|------|-------|
| Aggregate validation reporting | `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-VERIFICATION.md` |
| Browser UAT evidence table | `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-HUMAN-UAT.md`, `.planning/phases/12-lightweight-3d-preview-mvp/12-HUMAN-UAT.md` |
| Milestone notes | `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-MILESTONE-NOTES.md` |
| Summary format | `.planning/phases/13-enhanced-concept-handoff-package-mvp/13-07-SUMMARY.md` |
| Release docs wording | `README.md`, `docs/development.md` |

## Command Patterns

| Command | Notes |
|---------|-------|
| `corepack pnpm validate` | Full local aggregate; may need elevated host shell on Windows because of child-process and uv cache permissions. |
| `corepack pnpm smoke:worker -- --dry-run` | Provider-off queue wiring evidence without Docker/API/worker. |
| `corepack pnpm smoke:local` | Docker-backed PostgreSQL/Redis/MinIO plus migration/data/generation smoke; do not treat Docker-unavailable allowance as completion evidence. |
| `corepack pnpm compat:v1` | Static V1 route/schema/client compatibility guard. |
| `corepack pnpm migration:safety` | Static Alembic head and ledger table guard. |

## Documentation Patterns

- Keep public docs concise and operational.
- Keep `.planning/phases/14...` artifacts detailed enough for release audit.
- Repeat limitations near relevant commands, not only in a final disclaimer.
- Never include real credentials or provider secrets in evidence.

---
*Phase 14 patterns mapped: 2026-06-19*
