# CCXT Read-Only Adapter Safety Harness

## 1. Purpose

This harness defines the safety requirements for a future CCXT read-only market data adapter.

It must be completed before any CCXT adapter implementation begins. This document is not an adapter implementation and does not add the `ccxt` dependency.

## 2. Scope

The future CCXT adapter is limited to read-only market data.

Allowed future capabilities:

- fetch OHLCV bars
- fetch recent trades
- fetch order book snapshots
- fetch funding rates where supported
- fetch open interest where supported
- report adapter health
- map external data into internal market data value objects

Forbidden capabilities:

- create OrderIntent
- create ApprovedOrder
- submit orders
- create orders
- cancel orders
- modify orders
- place orders
- execute trades
- withdraw funds
- transfer funds
- approve risk
- approve execution

## 3. Required Internal Interfaces

The future adapter must implement the internal `ReadOnlyMarketDataAdapter` interface.

It must return internal value objects from `packages.common.market_data` only.

It must register through the internal market data adapter registry after local tests exist.

## 4. Credential Boundary

The future CCXT read-only adapter must not require credentials for unit tests.

It must not include:

- API keys
- secret keys
- passwords
- bearer tokens
- withdrawal keys
- broad-scope exchange credentials

If future read-only public endpoints require configuration, that configuration must not include trade credentials or withdrawal permissions.

## 5. Network Boundary

Unit tests must not call network.

Any future network behavior must be explicit, isolated from unit tests and covered by separate integration-test policy.

Future network calls must have:

- explicit timeouts
- bounded retries
- rate-limit handling
- stale data behavior
- structured errors
- redaction before error reporting

## 6. Prohibited Method Names

The future non-execution CCXT adapter must not expose methods named:

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

These names are only allowed in future approved execution-engine adapters behind ApprovedOrder flow.

## 7. Testing Harness Requirements

Before implementation, tests must prove:

- no `ccxt` import is required for unit tests
- fake/in-memory exchange clients are used first
- no network is called
- no credentials are required
- prohibited method names are absent
- returned data maps to internal market data value objects
- adapter registry behavior remains safe
- errors are redacted before reporting
- scaffold_audit.py passes

## 8. Review Gates

Before implementation, reviewers must confirm:

- external adapter review checklist completed
- external adapter safety policy followed
- dependency addition explicitly approved
- license reviewed
- security risk reviewed
- read-only boundary documented
- CI quality gates updated
- no deterministic-risk-gateway bypass
- no live trading behavior

## 9. Current Decision

Current status: approved for safety harness only.

This PR must not add CCXT, implement CCXT, call exchanges, install dependencies, add credentials or implement live trading.
