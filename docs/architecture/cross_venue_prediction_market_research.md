# Cross-Venue Prediction Market Research

## Purpose

This document defines a safe cross-venue research pattern inspired by Polymarket/Kalshi arbitrage projects.

It does not approve installing external bots, calling venue APIs, using credentials, creating wallets, submitting orders, approving risk or enabling live trading.

## Safe Research Boundary

Allowed outputs:

- `VenueResolutionState`
- `CrossVenuePriceSnapshot`
- `CrossVenueArbitrageObservation`
- `SignalCandidate`
- `RiskReviewInput`

Forbidden outputs:

- executable orders
- `OrderIntent`
- `ApprovedOrder`
- wallet actions
- broker or exchange requests
- venue private endpoint requests
- risk approvals
- execution approvals

## Useful Patterns

Safe patterns that can be modeled internally:

- normalize public venue prices to cents
- preserve per-venue fetch timestamp
- preserve venue status such as open, closed, settled or unknown
- detect stale venue data
- detect thin liquidity
- detect cross-venue spread anomalies
- detect resolution timing mismatches
- require manual review when venue mapping is uncertain

## Rejected Runtime Patterns

Rejected patterns:

- private key configuration
- proxy wallet configuration
- Polymarket CLOB order clients
- Kalshi authenticated account access
- automatic polling against live venue APIs
- direct transition from spread observation to order placement
- cooldown-based order submission
- any endpoint that mutates venue, wallet or account state

## Required Flow

Cross-venue observations may inform research only.

Any later execution path must pass through:

1. `SignalCandidate`
2. separately approved order-intent service
3. deterministic-risk-gateway
4. `ApprovedOrder`
5. execution-engine only

Backtest or research success does not approve live execution.

## Risk Flags

Recommended risk flags:

- `cross_venue_resolution_mismatch`
- `stale_venue_data`
- `thin_liquidity`
- `late_resolution_arbitrage_claim`
- `venue_mapping_uncertain`
- `requires_manual_review`
- `deterministic_risk_gateway_required`

## Non-Goals

- no external bot installation
- no dependency installation
- no venue API runtime
- no private endpoints
- no credentials
- no wallet access
- no order submission
- no live trading
- no production enablement
