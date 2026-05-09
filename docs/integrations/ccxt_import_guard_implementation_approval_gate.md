# CCXT Import Guard Implementation Approval Gate

## Purpose

This is the formal approval gate for a future import-guard implementation refinement.

This gate is narrower than dependency approval.

This document does not approve installing `ccxt`.

This document does not approve importing `ccxt`.

This document does not approve `pyproject.toml` changes.

This document does not approve real exchange access.

## Current State

```yaml
ccxt_installed: false
ccxt_imported: false
pyproject_modified_for_ccxt: false
dependency_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
private_endpoints_allowed: false
trading_methods_allowed: false
real_client_factory_allowed: false
manual_smoke_test_allowed: false
import_guard_design_approved: true
import_guard_tests_approved: true
import_guard_implementation_proposed: true
import_guard_change_allowed: false
```

## What This Gate May Approve Later

- refining local fail-closed import-guard code
- improving local error classes
- improving feature-flag checks
- improving exchange allowlist checks
- improving credential-boundary tests
- improving no-import/no-network assertions
- improving documentation links from local errors

## What This Gate Must Not Approve

- `ccxt` dependency installation
- `ccxt` import
- `pyproject.toml` changes
- real exchange clients
- network access
- API keys
- credentials
- private endpoints
- authenticated clients
- account reads
- position reads
- order history reads
- order submission
- cancellation
- transfer
- withdrawal
- risk approval
- execution approval
- production use

## Required Evidence Before import_guard_change_allowed Can Become True

- PR #32 fail-closed import guard safety skeleton merged
- import guard test plan merged
- implementation gate checklist merged
- scaffold audit passes
- CI passes
- no `ccxt` dependency installed
- no `ccxt` import exists
- no `pyproject.toml` change exists
- no network tests exist
- no credentials exist
- no real exchange client exists

## Approval Record

| Role | Status | Approver | Date | Notes |
| --- | --- | --- | --- | --- |
| Security | Pending | TBD | TBD | TBD |
| Platform reliability | Pending | TBD | TBD | TBD |
| Risk architecture | Pending | TBD | TBD | TBD |
| Maintainer | Pending | TBD | TBD | TBD |
| CI impact | Pending | TBD | TBD | TBD |

## Decision State

```yaml
import_guard_change_allowed: false
pyproject_change_allowed: false
dependency_allowed: false
real_client_factory_allowed: false
network_access_allowed: false
credentials_allowed: false
production_use_allowed: false
```

## Future Allowed PR If Approved

- A future PR may refine `packages/sdk/market_data_adapters/ccxt_factory.py`.
- That PR must remain fail-closed.
- That PR must not import `ccxt`.
- That PR must not modify `pyproject.toml`.
- That PR must not create real clients.
- That PR must not call network.
- That PR must not read credentials.

## Non-Goals

- no dependency approval
- no runtime approval
- no production approval
- no real adapter activation
- no live exchange access
- no trading
