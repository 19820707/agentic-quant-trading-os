# ADR 0016: CCXT Optional Read-Only Dependency Gate

Status: Proposed

## Context

CCXT may be useful for public crypto market data.

The platform currently has only skeleton/fake/mocked behavior.

Adding a real dependency can expand attack surface and operational risk.

## Decision

CCXT is not approved for installation yet.

CCXT is not approved for runtime use yet.

Any future dependency addition requires the approval gate in `docs/integrations/ccxt_approval_gate.md`.

Any future integration must remain public-read-only unless a separate ADR changes that.

No private endpoints, credentials or trading methods are allowed.

## Current Decision Update

- design approved: yes
- tests approved: yes
- dependency approved: no
- pyproject change approved: no
- import guard implementation approved: no
- real client factory approved: no
- production use approved: no

Import-guard implementation requires its own approval gate in `docs/integrations/ccxt_import_guard_implementation_approval_gate.md`.

That gate does not approve dependency installation, `pyproject.toml` changes, real client factory work or production use.

## Current Import-Guard Refinement Decision

- import guard refinement approved: yes
- dependency approved: no
- pyproject change approved: no
- real import approved: no
- real client factory approved: no
- network access approved: no
- credentials approved: no
- production use approved: no

## Consequences

- Slower dependency adoption.
- Stronger security and reliability posture.
- Clear approval trail.
- Prevents accidental transition from fake adapter to real exchange access.
