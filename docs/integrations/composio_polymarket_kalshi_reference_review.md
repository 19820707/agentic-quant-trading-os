# Composio Polymarket Kalshi Reference Review

## Purpose

This document reviews `Composio-HQ/polymarket-kalshi-arbitrage-bot` as a high-risk reference for cross-venue prediction-market research.

Repository: https://github.com/Composio-HQ/polymarket-kalshi-arbitrage-bot

This review does not approve cloning, installing, vendoring, importing, running, configuring or deploying the repository.

## Current Decision State

```text
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
wallet_access_allowed: false
private_endpoints_allowed: false
polymarket_clob_client_allowed: false
kalshi_api_runtime_allowed: false
ethers_allowed: false
dotenv_allowed: false
trading_methods_allowed: false
order_submission_allowed: false
```

## What Is Useful

The repository is useful only as a reference for:

- cross-venue price normalization to cents
- venue status tracking
- venue freshness timestamps
- thin-liquidity flags
- resolution timing mismatch detection
- spread anomaly thresholds
- read-only status dashboard concepts

These patterns must be converted into internal non-executable contracts before any future runtime work.

## What Is Rejected

Rejected:

- automated trading bot runtime
- Express service runtime
- Axios polling against live venues
- Polymarket CLOB client
- wallet/private-key configuration
- proxy wallet configuration
- `ethers`
- `dotenv`
- order client initialization
- cooldown-controlled order placement
- any operational action named as a buy

## Safe Internal Mapping

Allowed internal mapping:

- `PolymarketPrices` / `KalshiPrices` concept -> `CrossVenuePriceSnapshot`
- venue status concept -> `VenueResolutionState`
- spread or late-resolution concept -> `CrossVenueArbitrageObservation`
- observation risk flags -> `RiskReviewInput`

Forbidden mapping:

- bot action -> order
- spread anomaly -> execution permission
- late-resolution observation -> venue order
- venue private key -> platform config
- wallet state -> research contract

## Required Safety Boundary

Every cross-venue observation must remain:

- local-only in unit tests
- public-data-only
- network-disabled in CI
- credential-free
- non-executable
- unable to create `OrderIntent`
- unable to create `ApprovedOrder`
- unable to approve risk
- unable to approve execution

## Non-Goals

- no repository clone
- no dependency installation
- no TypeScript runtime
- no venue API calls
- no keys
- no wallet
- no order client
- no trading
- no production use
