# CCXT Read-Only Market Data Adapter

## Status

Current status: read-only skeleton only.

This directory documents the CCXT integration boundary. The current Python skeleton uses injected fake/in-memory clients only. It does not install `ccxt`, does not import `ccxt`, does not call exchanges and does not contain credentials.

Current control-plane status: design docs exist, mocked/fail-closed tests exist, `ccxt` remains uninstalled, `ccxt` remains unimported, `pyproject.toml` remains unchanged for `ccxt`, real client factory remains disallowed and production use remains disallowed.

See [CCXT Dependency Review And Production Readiness](../../../docs/integrations/ccxt_dependency_review.md) before any future real dependency declaration or integration work. The real integration is not approved yet.

See [CCXT Optional Dependency Proposal](../../../docs/integrations/ccxt_optional_dependency_proposal.md) for the proposed optional dependency gate. The optional dependency is proposed but not approved; `ccxt` is still not installed, real exchange access remains disabled and fake/mocked behavior is the only tested mode.

See [CCXT Optional Dependency Approval Gate](../../../docs/integrations/ccxt_approval_gate.md) and [ADR 0016](../../../docs/adr/0016-ccxt-optional-readonly-dependency-gate.md) for the formal approval record.

CCXT optional dependency remains not approved. Dependency, runtime and production flags remain false. Future changes require explicit approval in a separate PR.

See [CCXT Import Guard Design](../../../docs/integrations/ccxt_import_guard_design.md) for the design-only future import guard. The guard is not implemented, `ccxt` remains uninstalled, no real import exists, no real exchange access exists and fake/mocked behavior remains the only tested mode.

See [CCXT Implementation Gate Checklist](../../../docs/integrations/ccxt_implementation_gate_checklist.md) before any future implementation PR.

The implementation gate is not approval. `pyproject.toml` must not be changed until the gate is explicitly approved. `ccxt` remains uninstalled and unimported, and fake/mocked clients remain the only approved test mode.

See [CCXT Import Guard Test Plan](../../../docs/integrations/ccxt_import_guard_test_plan.md) for the future test design.

The test plan is documentation-only. No import guard tests are implemented by that plan, `ccxt` remains uninstalled and unimported, and fake/mocked behavior remains the only approved tested mode.

See [CCXT Import Guard Implementation Approval Gate](../../../docs/integrations/ccxt_import_guard_implementation_approval_gate.md) before any future import-guard implementation refinement.

That gate is narrower than dependency approval. `ccxt` remains uninstalled and unimported, `pyproject.toml` remains unchanged, real exchange clients remain disallowed and production use remains disallowed.

## Adapter Identity

- upstream project: https://github.com/ccxt/ccxt
- integration category: market-data
- integration mode: future dependency / adapter
- target interface: `ReadOnlyMarketDataAdapter`

## Allowed Future Operations

A future CCXT read-only adapter may support:

- fetch OHLCV
- fetch public trades
- fetch order book snapshots
- fetch funding rates where supported
- fetch market metadata where supported

## Prohibited Operations

A future CCXT read-only adapter must not expose or implement:

- buy
- sell
- order
- create_order
- submit_order
- cancel_order
- modify_order
- withdraw
- transfer
- execute
- place_order

It must never create `OrderIntent`, create `ApprovedOrder`, submit orders, cancel orders, modify orders, withdraw funds, transfer funds, access trade credentials, access withdrawal credentials, approve risk, approve execution or bypass deterministic-risk-gateway.

## Credential Policy

- no credentials for public market data by default
- no trade credentials
- no withdrawal credentials
- no credentials in unit tests
- no credentials in examples, logs, errors, audit events or reports

## Testing Policy

- unit tests must use fake/in-memory clients
- no network calls in unit tests
- no real exchange calls in CI
- no `ccxt` import is required for unit tests
- errors must be redacted before logging or reporting

## Registry Registration

The skeleton may be registered in `MarketDataAdapterRegistry` only with an injected fake/in-memory client.

Registry coverage does not install `ccxt`, create a real exchange client, use API keys, call private endpoints, expose execution methods or enable live trading.

Current status remains skeleton plus fake registry coverage only: no dependency installed, no real exchange client, no API keys and no private endpoints.

## Mocked Integration Tests

Mocked integration tests define the expected read-only behavior before any real dependency is approved.

They use fake/in-memory clients only. They do not install `ccxt`, import `ccxt`, access real exchanges, call network, use credentials, private endpoints or live trading paths.

## Import Guard Safety Tests

The local import guard placeholder is fail-closed by design.

It does not install `ccxt`, import `ccxt`, create a real exchange client, call network, read credentials, enable runtime behavior or approve production use. Current tests verify only local fail-closed safety behavior.

## Future Implementation Rules

A future adapter must implement only `ReadOnlyMarketDataAdapter`.

It must return internal market data value objects, register through the internal adapter registry, avoid dangerous method names, avoid hidden side effects and preserve the deterministic-risk-gateway boundary.

The current skeleton lives at `packages/sdk/market_data_adapters/ccxt_readonly.py` and remains read-only. It converts fake OHLCV rows, trade dictionaries and order book dictionaries into internal market data value objects.
