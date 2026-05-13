# Prediction Market Copy-Trade Research Runbook

## Purpose

This runbook defines the local-only research process for prediction-market copy-trade analysis.

It does not approve runtime market access, external API calls, credentials, wallet operations, order submission, trade mirroring, risk approval, execution approval or production use.

## Required Sequence

1. Create or load a synthetic `CopyTradeTargetObservation`.
2. Record only manually reviewed or synthetic public target context.
3. Create an `ObservedTraderActivity` record with explicit timestamps.
4. Reject stale activity before any simulation.
5. Apply `CopyTradePolicy` with execution disabled.
6. Create a `CopyTradeSimulationRecord` only for local hypothetical replay.
7. Create or update a `TraderReliabilityProfile`.
8. Create a `CopyTradeRiskReviewInput` for advisory review only.
9. Stop at research output.

## Hard Stops

Research must stop if:

- target identity requires runtime resolution
- observed activity lacks timestamp or sequence
- activity is stale
- wallet, signature, account or credential material is required
- any step asks to mirror, place, cancel or manage trades
- any step treats another actor's activity as risk or execution approval

## Configuration Discipline

Configuration is research policy only.

Allowed:

- polling interval policy
- activity limit policy
- simulated size multiplier
- simulated notional cap
- trades-only filtering

Forbidden:

- credential material
- wallet enablement
- network enablement
- production enablement
- execution enablement
- automatic trade mirroring

## Output Boundary

The output may be:

- target observation metadata
- observed activity records
- simulation records
- reliability profiles
- advisory risk review inputs

The output must not be:

- executable orders
- order intents
- approved orders
- wallet operations
- account operations
- mirrored trades
- risk approval
- execution approval
