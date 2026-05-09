# CCXT Optional Dependency Approval Gate

## Purpose

This is the formal gate for future optional CCXT dependency changes.

This document does not approve installation.

This document does not approve runtime use.

This document does not approve production use.

## Current Decision State

```yaml
approved: false
dependency_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
private_endpoints_allowed: false
trading_methods_allowed: false
```

## Decision Update: Import-Guard Groundwork

The import guard design document has been reviewed.

The import guard test plan has been reviewed.

The fail-closed import guard safety skeleton exists.

This does not approve installing `ccxt`.

This does not approve modifying `pyproject.toml`.

This does not approve real runtime use.

This does not approve production use.

This does not approve network access.

This does not approve credentials.

This does not approve a real exchange client factory.

The only proposed next step is a further import-guard control-plane refinement, if separately reviewed.

See `docs/integrations/ccxt_import_guard_implementation_approval_gate.md` for the narrower gate that would be required before allowing any import-guard implementation refinement.

`import_guard_implementation_proposed` remains true, and `import_guard_change_allowed` is true only for narrow fail-closed import-guard refinement.

Import-guard refinement is now allowed only for local fail-closed control-plane code and tests.

This does not approve dependency installation, real imports, `pyproject.toml` changes, real client factories, network access, credentials or production use.

```yaml
approved: false
dependency_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
private_endpoints_allowed: false
trading_methods_allowed: false
pyproject_change_allowed: false
import_guard_design_approved: true
import_guard_tests_approved: true
import_guard_implementation_proposed: true
import_guard_change_allowed: true
real_client_factory_allowed: false
manual_smoke_test_allowed: false
```

## Required Approvals Before Changing pyproject.toml

- dependency review approval
- security approval
- risk architecture approval
- platform reliability approval
- maintainer approval
- CI impact approval

## Required Evidence Before Dependency Approval

- `docs/integrations/ccxt_dependency_review.md` exists
- `docs/integrations/ccxt_optional_dependency_proposal.md` exists
- fake-client adapter tests pass
- mocked integration tests pass
- scaffold audit passes
- CI passes
- no credentials introduced
- no network tests introduced
- prohibited methods denylist remains enforced

## Allowed Future Change After Approval

- optional dependency declaration only
- import guard only
- public read-only client factory disabled by default
- fake/mocked tests only in CI
- manually-run public smoke test only after separate approval

## Explicitly Forbidden Without Separate Approval

- real exchange client in CI
- live network tests in CI
- API keys
- private endpoints
- authenticated clients
- order submission
- order cancellation
- transfer
- withdrawal
- leverage changes
- account reads
- position reads
- portfolio mutation
- risk approval
- execution approval

## Runtime Controls Required Before Enabling Real Read-Only Use

- feature flag default false
- public endpoints only
- method allowlist
- dangerous method denylist
- timeout policy
- rate-limit policy
- stale data guard
- structured errors
- metrics
- audit event for configuration changes
- rollback plan

## Rollback

- remove optional dependency
- disable feature flag
- block adapter registration
- use fake/in-memory adapter
- preserve audit trail

## Approval Record

| Role | Status | Approver | Date | Notes |
| --- | --- | --- | --- | --- |
| Dependency review | Pending | TBD | TBD | TBD |
| Security | Pending | TBD | TBD | TBD |
| Risk architecture | Pending | TBD | TBD | TBD |
| Platform reliability | Pending | TBD | TBD | TBD |
| Maintainer | Pending | TBD | TBD | TBD |
| CI impact | Pending | TBD | TBD | TBD |

## Decision

Current decision: rejected by default / not approved.

Any future approval must be explicit and reviewed in a separate PR.
