# Polymarket Signal Agent Reference Review

## Purpose

This document records what can be safely reused from
`https://github.com/yigitcankzl/PolymarketSignalAgent` as reference
architecture.

The repository is not approved as a dependency, runtime, adapter, service,
dashboard, data source or execution path. No code is copied, vendored or cloned
into this project.

## Current Decision

reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
synthesis_runtime_allowed: false
groq_runtime_allowed: false
dashboard_runtime_allowed: false
wallet_runtime_allowed: false
network_access_allowed: false
credentials_allowed: false
trading_methods_allowed: false
production_enabled: false

## Useful Reference Patterns

- Five-tier signal classification: strong buy, buy, hold, sell and strong sell.
- Edge calculation as calibrated probability minus market probability.
- Confidence-aware signal thresholding.
- Multi-model ensemble vote capture and median aggregation.
- Advisory capped Kelly sizing for research review only.
- Pipeline stage status for fetch, research, analyze, calibrate, compare, size
  and signal.
- Cross-venue spread observation as non-executable market research.

## Rejected Runtime Patterns

- Synthesis.trade API runtime.
- Groq or other LLM provider runtime.
- Google News RSS runtime.
- Dashboard trade routes.
- One-click buy or sell controls.
- Wallet API access.
- Order API access.
- Private keys, API keys or credential configuration.
- Automatic arbitrage execution.
- Any direct path from signal output to orders.

## Safe Adaptation

The safe adaptation is contract-first:

- `PredictionMarketSignalClassification`
- `EdgeComputationRecord`
- `EnsembleProbabilityVote`
- `AdvisoryKellySizing`
- `SignalPipelineStatus`

These contracts are local-only, non-executable and do not approve risk or
execution.

## Required Future Review

Any future runtime use would require a separate external adapter review,
dependency review, security review, deterministic-risk-gateway review and
explicit approval. Until then this project only reuses the concepts as local
schemas, fixtures and tests.
