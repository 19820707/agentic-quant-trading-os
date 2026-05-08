# CCXT Read-Only Market Data Adapter

## Status

Current status: read-only skeleton only.

This directory documents the CCXT integration boundary. The current Python skeleton uses injected fake/in-memory clients only. It does not install `ccxt`, does not import `ccxt`, does not call exchanges and does not contain credentials.

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

## Future Implementation Rules

A future adapter must implement only `ReadOnlyMarketDataAdapter`.

It must return internal market data value objects, register through the internal adapter registry, avoid dangerous method names, avoid hidden side effects and preserve the deterministic-risk-gateway boundary.

The current skeleton lives at `packages/sdk/market_data_adapters/ccxt_readonly.py` and remains read-only. It converts fake OHLCV rows, trade dictionaries and order book dictionaries into internal market data value objects.
