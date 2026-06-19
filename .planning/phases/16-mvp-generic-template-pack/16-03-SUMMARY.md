---
phase: 16
plan: 3
status: completed
requirements:
  - V3-PACK-03
---

# Summary 16.03: Template Package Validation Command

## Completed

- Added `caragent_core.generation.validate_template_pack`.
- Validator checks template ids, required asset slots, PNG dimensions, RGBA encoding, non-empty mask pixels, source/license metadata, readiness, and normalized safe-zone bounds.
- Command runs from `services/core` with:

```powershell
uv run python -m caragent_core.generation.validate_template_pack
```

## Evidence

- `services/core/src/caragent_core/generation/validate_template_pack.py`
- `services/core/tests/test_template_pack.py`
- Validation output: `Validated 5 MVP vehicle templates.`
