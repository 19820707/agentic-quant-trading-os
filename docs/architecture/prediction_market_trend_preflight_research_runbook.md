# Prediction Market Trend and Preflight Research Runbook

## Purpose

This runbook defines the local-only research process for prediction-market trend, imbalance, preflight and simulation-history analysis.

It does not approve runtime market access, external API calls, credentials, account operations, order submission, position switching, settlement, hedge execution, risk approval, execution approval or production use.

## Required Sequence

1. Create or load a synthetic `OrderBookImbalanceObservation`.
2. Convert imbalance context into `TrendStateObservation`.
3. If trend changes, create `TrendFlipObservation`.
4. Apply `PreflightSafetyReview`.
5. Apply `SimulationModePolicy`.
6. Record simulation-only PnL in `ArbitragePnLSimulationSummary`.
7. Record audit context in `StrategyHistoryEvent`.
8. Stop at research output.

## Hard Stops

Research must stop if:

- trend data requires runtime market access
- imbalance input has no timestamp
- preflight review requires account or balance checks
- any credential, signer, account, RPC or settlement material is required
- any step asks to place, cancel, switch, settle or hedge
- any step treats trend state as execution approval

## Configuration Discipline

Allowed:

- depth-level policy
- trend threshold policy
- simulation-only PnL estimates
- local strategy history events

Forbidden:

- credential material
- account enablement
- network enablement
- production enablement
- order placement
- position switching
- settlement
- execution enablement

## Output Boundary

The output may be:

- imbalance observations
- trend state observations
- trend flip observations
- preflight review records
- simulation mode policy records
- PnL simulation summaries
- strategy history events

The output must not be:

- executable orders
- order intents
- approved orders
- account operations
- settlement operations
- hedge operations
- risk approval
- execution approval
