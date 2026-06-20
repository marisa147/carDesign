# Phase 20 Validation Strategy

## Automated Checks

- Root aggregate validation or equivalent focused command set covers web/contracts/core/API/worker lint, typecheck, and tests.
- Contract drift check must pass after any doc/API changes.
- Template-pack validation command must pass for all five MVP templates and the legacy alias.
- Docker/local smoke should run with Compose when Docker is available; otherwise record the Docker blocker and run smoke dry/static fallbacks.
- Worker smoke dry run must pass without hosted credentials.

## Browser UAT

- Desktop 1440x900: template catalog, selected template evidence, local generation state, targeted edit controls, 3D fallback/labels, enhanced ZIP, production preflight.
- Mobile 390x900: same core signals, no horizontal overflow.
- Evidence should include screenshots or, if browser automation is blocked, test-backed DOM assertions plus a documented blocker.

## Release Audit

- All V3-REL requirements must be mapped to Phase 20 evidence.
- All v3.0 requirements must be complete or explicitly deferred before milestone archive.

