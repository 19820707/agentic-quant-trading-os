# CCXT Implementation Gate Checklist

## Purpose

This checklist controls future implementation of CCXT optional dependency work.

It does not approve installing CCXT.

It does not approve importing CCXT.

It does not approve runtime use.

It does not approve production use.

## Current State

```yaml
ccxt_installed: false
ccxt_imported: false
pyproject_modified_for_ccxt: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
private_endpoints_allowed: false
trading_methods_allowed: false
```

## Required Documents Before Implementation

- `docs/integrations/ccxt_dependency_review.md`
- `docs/integrations/ccxt_optional_dependency_proposal.md`
- `docs/integrations/ccxt_approval_gate.md`
- `docs/integrations/ccxt_import_guard_design.md`
- `docs/adr/0016-ccxt-optional-readonly-dependency-gate.md`

## Required Technical Baseline

- CCXT read-only adapter skeleton exists
- CCXT fake-client registry registration exists
- mocked integration tests pass
- dangerous method denylist tests pass
- market data adapter interface tests pass
- scaffold audit passes
- CI quality gates pass
- no credentials exist
- no network tests exist

## Required Approvals

- [ ] dependency review approved
- [ ] security review approved
- [ ] platform reliability review approved
- [ ] risk architecture review approved
- [ ] maintainer approval granted
- [ ] CI impact reviewed
- [ ] rollback plan reviewed

## Required Implementation Constraints

- optional dependency only
- no top-level import
- import guarded inside dedicated factory only
- feature flag default false
- fail closed if feature flag disabled
- fail closed if dependency missing
- fail closed if exchange is not allowlisted
- no API key parameters
- no environment credential reads
- no authenticated clients
- no private endpoints
- public read-only methods only
- no trading methods
- no execution approval
- no risk decisioning

## Required Tests Before Implementation Merge

- missing dependency test
- disabled feature flag test
- non-allowlisted exchange test
- no env read test
- no credential parameter test
- no private endpoint test
- dangerous method denylist test
- fake/mocked adapter tests
- scaffold audit
- CI passes

## Explicitly Forbidden In The Implementation PR

- live exchange network calls in CI
- real API keys
- credentials in docs/tests/examples
- private endpoints
- authenticated trading clients
- `create_order`
- `cancel_order`
- `edit_order`
- `withdraw`
- `transfer`
- `set_leverage`
- account balance reads
- position reads
- order history reads
- live trading
- production enablement

## Manual Smoke Test Policy

- manual only
- non-CI only
- public endpoints only
- no credentials
- disabled by default
- separate approval required
- results documented in a later PR

## Rollback Criteria

- unexpected dependency behavior
- unsafe method exposure
- CI instability
- rate-limit failures
- stale data behavior
- dependency security advisory
- operator concern

## Rollback Procedure

- disable feature flag
- block CCXT adapter registration
- remove optional dependency if needed
- fall back to fake/in-memory adapter
- preserve audit trail
- open incident/postmortem if production-adjacent

## Implementation PR Readiness Decision

```yaml
implementation_ready: false
pyproject_change_allowed: false
import_guard_change_allowed: false
real_client_factory_allowed: false
manual_smoke_test_allowed: false
production_use_allowed: false
```

## Non-Goals

- no live trading
- no execution engine integration
- no private market data
- no account access
- no portfolio mutation
- no risk approval
- no broker credential handling
- no production deployment
