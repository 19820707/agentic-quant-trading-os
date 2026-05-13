# SXai Prediction Market Arbitrage Lifecycle Reference Review

## Purpose

This review extracts additional safe research patterns from `SXai-lab/prediction-market-arbitrage`.

It does not approve installing, cloning, vendoring, importing, running, or adapting the repository runtime.

Repository reviewed:

- https://github.com/SXai-lab/prediction-market-arbitrage

## Current Decision

sxai_prediction_market_arbitrage_lifecycle_reviewed: true
reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
npm_runtime_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
private_endpoints_allowed: false
trading_methods_allowed: false
polymarket_clob_allowed: false
wallet_runtime_allowed: false
settlement_allowed: false
hedge_execution_allowed: false

Initial classification: reference-only lifecycle and simulation policy source.

## Reusable Patterns

### Market Discovery Record

The repository discovers short-window prediction markets before strategy evaluation.

Safe adaptation:

- record the asset symbol
- record a synthetic or manually reviewed market slug
- record round start and end timestamps
- record stale-data boundaries
- keep network, credentials and execution disabled

### Price Snapshot Record

The repository reasons over YES/NO ask prices and recent movement.

Safe adaptation:

- capture synthetic YES and NO ask prices
- capture spread and rough liquidity hints
- capture source lag
- keep the snapshot as research data, not as a runtime adapter

### Simulation History Record

The repository records activity for review and simulation.

Safe adaptation:

- preserve a decision path
- record a simulated outcome
- record simulated PnL
- keep the record simulation-only and non-executable

### Configuration Policy

The repository exposes configurable thresholds and timing controls.

Safe adaptation:

- define local threshold policy
- enforce conservative polling and observation windows
- keep secret material, network, runtime, production and execution disabled

## Non-Reusable Components

Do not reuse directly:

- TypeScript or npm runtime
- CLOB client runtime
- wallet or proxy-wallet workflows
- signature workflows
- credential environment workflow
- production flag workflow
- order placement
- redeem or settlement workflow
- live endpoint polling
- hedge execution workflow

## Required Internal Boundary

Any future implementation inspired by this repository must:

- remain contract-first
- use synthetic fixtures first
- avoid network calls in unit tests
- avoid credentials and environment reads
- avoid wallet, signature or settlement material
- treat discovery and price data as stale unless explicitly timestamped
- preserve trace_id and correlation_id
- emit non-executable research records only
- preserve deterministic-risk-gateway authority

## Safe Adaptation Targets

This project may safely define:

- prediction market discovery records
- prediction market price snapshots
- arbitrage simulation history records
- arbitrage configuration policy records
- local research runbooks

## Rejected Adaptation Targets

Rejected:

- direct dependency on the external repository
- vendoring source code
- npm runtime adoption
- live CLOB calls
- private endpoint calls
- wallet operations
- settlement operations
- hedge execution
- production mode
- model or agent authority to place trades

## Recommended Next Step

Review lifecycle and simulation policy contracts before adding any runtime adapter or external dependency.
