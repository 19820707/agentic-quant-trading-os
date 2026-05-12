# Haredoggy Prediction Market Toolkits Reference Review

## Purpose

This document reviews `haredoggy/Prediction-Markets-Trading-Bot-Toolkits` as a high-risk reference for prediction-market strategy patterns, risk guard concepts and operational UI ideas.

Repository: https://github.com/haredoggy/Prediction-Markets-Trading-Bot-Toolkits

This review does not approve cloning, installing, vendoring, importing, building, running or deploying the repository.

## Current Decision State

```text
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
rust_runtime_allowed: false
tokio_runtime_allowed: false
venue_client_allowed: false
polymarket_clob_allowed: false
kalshi_client_allowed: false
limitless_client_allowed: false
wallet_tracking_runtime_allowed: false
credential_configuration_allowed: false
network_access_allowed: false
trading_methods_allowed: false
production_enabled: false
```

## What Is Useful

Useful as reference only:

- strategy taxonomy
- venue-agnostic adapter layering
- dry-run-first workflow
- circuit breaker concept
- liquidity/depth guard concept
- rate-limit and cooldown concepts
- terminal operational status concepts
- order book imbalance as a read-only feature
- public wallet activity as an observation source

## Strategy Patterns To Preserve As Research

Preserve only as research pattern names:

- copy activity research
- short-window price research
- cross-venue research
- momentum research
- spread research
- sports market research
- resolution research
- orderbook imbalance research
- market making research
- on-chain activity research

These patterns must not become executable bots in this project.

## Runtime Patterns To Reject

Rejected:

- Rust trading runtime
- Tokio venue polling runtime
- Polymarket CLOB integration
- Kalshi integration
- Limitless integration
- private wallet configuration
- wallet mirroring
- automatic position replication
- two-sided quoting
- market making runtime
- automatic exit management
- sports click-to-execute flow
- on-chain transaction mirroring

## Safe Internal Mapping

Allowed internal mapping:

- strategy taxonomy -> `StrategyResearchPattern`
- circuit breaker and depth guard concepts -> `StrategyRiskGuardProfile`
- public depth analysis -> `LiquidityDepthCheck`
- order book imbalance concept -> `OrderbookImbalanceFeature`
- public wallet activity signal -> `WalletActivityObservation`

Forbidden mapping:

- strategy pattern -> executable bot
- wallet activity -> copied position
- imbalance feature -> venue request
- risk guard profile -> risk approval
- dry-run status -> live approval
- terminal UI control -> execution control

## Non-Goals

- no repository clone
- no dependency installation
- no Rust build
- no runtime venue adapter
- no network calls
- no credentials
- no wallet connection
- no order placement
- no execution engine integration
- no production enablement
