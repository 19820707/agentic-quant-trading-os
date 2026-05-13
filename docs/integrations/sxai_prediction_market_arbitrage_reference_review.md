# SXai Prediction Market Arbitrage Reference Review

## Purpose

This review identifies safe research patterns from `SXai-lab/prediction-market-arbitrage`.

It does not approve installing, cloning, vendoring, importing, running, or adapting the repository runtime.

Repository reviewed:

- https://github.com/SXai-lab/prediction-market-arbitrage

## Current Decision

sxai_prediction_market_arbitrage_reference_reviewed: true
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

Initial classification: reference-only arbitrage observation and simulation source.

## Reusable Design Patterns

### Two-Leg Arbitrage Observation

The useful pattern is measuring whether two complementary legs have a combined cost below a configured threshold.

Safe adaptation:

- record both leg labels and public prices
- compute combined cost and structural edge
- mark the record as observation-only
- keep production and execution approval disabled

### Sudden Move Observation

The useful pattern is detecting short-window price movement for later research.

Safe adaptation:

- record the observation window
- record the configured move threshold
- record the observed move
- never turn the trigger into an execution command

### Hedge Condition Plan

The conditional hedge idea is useful only as a research plan.

Safe adaptation:

- describe the first leg reference price
- describe the opposite leg maximum price
- describe the combined cost limit
- keep hedge execution disabled

### Market Round Lifecycle

Round timing is useful for avoiding stale or misclassified observations.

Safe adaptation:

- record round start and end timestamps
- record observation window timestamps
- record settlement status as research context
- avoid settlement actions or wallet workflows

### Arbitrage Simulation Run

Simulation summaries are useful for backtesting research assumptions.

Safe adaptation:

- record opportunity count
- record simulated action count
- record simulated PnL
- mark the run as simulation-only
- keep production approval and execution disabled

### Arbitrage Observation Audit

Research observations need audit review before any future strategy work.

Safe adaptation:

- link observation identifiers
- record audit findings
- record review status
- disallow order and wallet references

## Non-Reusable Components

Do not reuse directly:

- TypeScript or npm runtime
- Polymarket CLOB client runtime
- wallet or proxy-wallet workflow
- signature configuration
- API-key workflow
- order submission
- cancellation workflow
- redeem or settlement workflow
- authenticated endpoint workflow
- polling real APIs in CI
- hedge execution logic

## Required Internal Boundary

Any future implementation inspired by this repository must:

- be contract-first
- use local synthetic fixtures first
- avoid network calls in unit tests
- avoid credentials and environment reads
- avoid wallet, proxy-wallet or signature material
- treat observed market data as untrusted research input
- preserve trace_id and correlation_id
- emit non-executable research records only
- preserve deterministic-risk-gateway authority

## Safe Adaptation Targets

This project may safely define:

- two-leg arbitrage observation contracts
- sudden-move observation contracts
- hedge-condition planning contracts
- market-round lifecycle contracts
- arbitrage simulation contracts
- arbitrage observation audit contracts

## Rejected Adaptation Targets

Rejected:

- direct dependency on the external repository
- vendoring source code
- npm runtime adoption
- live Polymarket CLOB calls
- private endpoint calls
- wallet operations
- settlement operations
- hedge execution
- model or agent authority to place trades

## Recommended Next Step

Review the internal arbitrage observation contracts and keep future work limited to local fake data until a separate adapter review is approved.
