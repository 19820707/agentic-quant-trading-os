# Prediction Market Arbitrage Research Runbook

## Purpose

This runbook defines the local-only research process for prediction-market arbitrage analysis.

It does not approve runtime market access, external API calls, credentials, wallet operations, order submission, settlement, hedge execution, risk approval, execution approval or production use.

## Required Sequence

1. Create or load a synthetic `PredictionMarketDiscoveryRecord`.
2. Confirm the round is inside the observation window.
3. Confirm the discovery record is not stale.
4. Create a synthetic `PredictionMarketPriceSnapshot`.
5. Review spread, rough liquidity hint and source lag.
6. Record any research decision path in `ArbitrageSimulationHistoryRecord`.
7. Apply `ArbitrageConfigurationPolicy` before comparing thresholds.
8. Stop at research output.

## Hard Stops

Research must stop if:

- discovery data is stale
- the observation window is closed
- price snapshots are missing timestamps
- spread or liquidity quality is unknown and the research method requires quality
- any credential, wallet, signature, private endpoint or production flag is required
- any step asks to place, cancel, settle or hedge

## Configuration Discipline

Configuration is research policy only.

Allowed:

- asset limits
- polling interval policy
- observation window policy
- movement threshold policy
- combined cost target policy

Forbidden:

- secret material
- network enablement
- runtime enablement
- production enablement
- execution enablement

## Output Boundary

The output may be:

- local discovery metadata
- local price snapshots
- simulation history
- configuration policy
- analyst notes
- audit findings

The output must not be:

- executable orders
- order intents
- approved orders
- wallet operations
- settlement operations
- hedge operations
- risk approval
- execution approval
