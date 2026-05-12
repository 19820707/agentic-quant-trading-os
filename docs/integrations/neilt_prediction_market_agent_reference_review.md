# neilt93 Prediction Market Agent Reference Review

## Purpose

This document records what can be safely reused from
`https://github.com/neilt93/Prediction-Market-Agent` as reference architecture.

The repository is not approved as a dependency, runtime, adapter, service or
execution path. No code is copied, vendored or cloned into this project.

## Current Decision

reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
kalshi_runtime_allowed: false
polymarket_runtime_allowed: false
llm_runtime_allowed: false
lightgbm_runtime_allowed: false
database_runtime_allowed: false
network_access_allowed: false
credentials_allowed: false
trading_methods_allowed: false
production_enabled: false

## Useful Reference Patterns

- Forecasting pipeline separation: market context, rule parsing, evidence,
  forecasting, calibration and postmortem.
- Evidence records with retrieval time and point-in-time boundaries.
- Rule parsing records that capture entity, threshold, resolution logic and
  ambiguity.
- Calibration records that separate raw probability, calibrated probability,
  confidence, edge and uncertainty.
- Postmortem records for resolved predictions with scoring and error taxonomy.
- Feature snapshots that preserve data-as-of and availability timestamps.

## Rejected Runtime Patterns

- Live Kalshi trading.
- Polymarket CLOB clients.
- Venue API clients.
- Order placement.
- Position management.
- Credential configuration.
- Database, Redis, worker and server runtime.
- Local LLM serving runtime.
- LightGBM or diffusion runtime dependencies.
- Any direct path from forecast output to execution.

## Safe Adaptation

The safe adaptation is contract-first:

- `ForecastEvidenceItem`
- `MarketRuleParse`
- `ForecastCalibrationRecord`
- `ForecastPostmortem`
- `ForecastFeatureSnapshot`

These contracts are local-only, non-executable and do not approve risk or
execution.

## Required Future Review

Any future runtime use would require a separate external adapter review,
dependency review, security review, deterministic-risk-gateway review and
explicit approval. Until then this project only reuses the concepts as local
schemas, fixtures and tests.
