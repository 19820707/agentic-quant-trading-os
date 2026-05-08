# CCXT Import Guard Test Plan

## Purpose

This document defines required tests for a future CCXT import guard.

This document does not implement tests.

This document does not approve installing or importing `ccxt`.

This document does not enable real exchange access.

## Current State

```yaml
ccxt_installed: false
ccxt_imported: false
pyproject_modified_for_ccxt: false
import_guard_implemented: false
real_client_factory_implemented: false
network_access_allowed: false
credentials_allowed: false
production_enabled: false
```

## Test Principles

- fail closed by default
- no top-level `ccxt` import
- no network calls in CI
- no credentials or env var reads
- fake/mocked clients only
- deterministic local errors
- no trading methods
- no private endpoints
- no risk approval
- no execution approval

## Required Future Test Groups

### A. Missing Dependency Tests

- `ccxt` absent should raise a local explicit `CCXTDependencyUnavailable`-style error
- error message must not contain secrets
- error message must not attempt installation
- error message must link/point to approval docs

### B. Feature Flag Tests

- disabled feature flag fails closed
- enabled flag is ignored unless approval gate is true
- production flag remains false by default
- CI must not enable real client factory

### C. Import Behavior Tests

- no top-level `ccxt` import
- no import in package `__init__.py`
- import only inside dedicated gated factory
- importing `packages/sdk` must not import `ccxt`

### D. Exchange Allowlist Tests

- non-allowlisted exchange fails closed
- allowlisted exchange is only accepted after approval state is true
- `exchange_id` validation is explicit

### E. Credential Boundary Tests

- factory rejects `api_key` parameter
- factory rejects `secret` parameter
- factory does not read environment variables
- factory does not require broker/exchange API keys
- no credentials in logs/errors

### F. Method Allowlist/Denylist Tests

Allowed public methods only:

- `fetch_ohlcv`
- `fetch_trades`
- `fetch_order_book`
- approved public funding method if later allowed

Prohibited methods remain blocked:

- `create_order`
- `cancel_order`
- `edit_order`
- `withdraw`
- `transfer`
- `borrow`
- `repay`
- `set_leverage`
- `private_*` endpoints
- account reads
- position reads
- order history reads

### G. CI Safety Tests

- tests use mocks/fakes
- no socket/network
- no secrets
- no real exchange client
- no dependency installation during tests
- scaffold_audit passes

### H. Error Handling Tests

- missing method behavior is deterministic
- rate-limit-like fake exception becomes structured local error
- timeout-like fake exception becomes structured local error
- error messages are redacted

### I. Adapter Compatibility Tests

- future factory returns object compatible with `CCXTReadOnlyAdapter`
- adapter remains compatible with `ReadOnlyMarketDataAdapter`
- fake/mocked integration tests continue passing

## Explicitly Forbidden In Future Tests

- real exchange calls in CI
- API keys
- private endpoints
- authenticated clients
- account balance reads
- position reads
- order history reads
- live trading
- create/cancel/edit order operations
- withdraw/transfer operations
- production enablement

## Future Test File Candidates

- `tests/test_ccxt_import_guard.py`
- `tests/test_ccxt_factory_safety.py`
- `tests/test_ccxt_dependency_unavailable.py`

## Merge Gates Before Implementation

- approval gate reviewed
- implementation checklist reviewed
- test plan reviewed
- tests implemented first or with implementation
- scaffold_audit passes
- CI passes
- no credentials introduced
- no network introduced

## Relationship To Existing Docs

- `docs/integrations/ccxt_dependency_review.md`
- `docs/integrations/ccxt_optional_dependency_proposal.md`
- `docs/integrations/ccxt_approval_gate.md`
- `docs/integrations/ccxt_import_guard_design.md`
- `docs/integrations/ccxt_implementation_gate_checklist.md`
- `docs/adr/0016-ccxt-optional-readonly-dependency-gate.md`

## Non-Goals

- no `ccxt` installation
- no `pyproject.toml` change
- no import guard implementation
- no real client factory
- no network test
- no credentials
- no production use
- no trading
