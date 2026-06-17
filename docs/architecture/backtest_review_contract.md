# Backtest Review Contract

## Purpose

BacktestReviewContract defines the evidence required before any future local deterministic backtest runtime can be considered.

This document does not approve a backtest engine, strategy execution, market data ingestion, paper mode, portfolio mutation, order intent creation, risk approval, execution approval, broker or exchange access, network access, credentials or production use.

## Current State

The current state remains contract-only and fail-closed:

- backtest runtime is not enabled;
- strategy execution is not enabled;
- market data ingestion is not enabled;
- paper mode is not enabled;
- portfolio mutation is not enabled;
- order intent creation is not enabled;
- risk approval is not granted;
- execution is not allowed;
- broker and exchange access are not allowed;
- network access is not allowed;
- credentials are not allowed;
- production use is not allowed.

## Required Evidence

Before future backtest work can be reviewed, the platform must provide:

- DatasetLineageRecord;
- LeakageReviewReport;
- FeatureStoreApprovalGate;
- FakeOfflineMaterializationReview;
- point-in-time replay plan;
- fee model plan;
- slippage model plan;
- overfitting review plan;
- rollback plan;
- human review record.

The contract stores evidence references and required checks. It does not run a strategy, load market data or produce performance claims.

## Required Modeling Assumptions

Any later backtest runtime proposal must document:

- fee model;
- slippage model;
- latency model;
- spread model;
- fill model;
- survivorship-bias review;
- lookahead-bias review.

## Required Result Checks

Any later result contract must include:

- deterministic replay evidence;
- sample-size review;
- out-of-sample split;
- walk-forward plan;
- fee sensitivity;
- slippage sensitivity;
- drawdown review;
- tail-risk review;
- turnover review;
- benchmark comparison.

## Boundary

Allowed now:

- contract validation;
- fixture validation;
- documentation of required evidence;
- rejected readiness decision.

Forbidden now:

- backtest runtime;
- strategy execution;
- market data ingestion;
- paper trading runtime;
- portfolio mutation;
- SignalCandidate creation;
- OrderIntent creation;
- RiskDecision approval;
- ApprovedOrder creation;
- ExecutionReport creation;
- broker or exchange access;
- network;
- credentials;
- production use.

## Non-Goals

- no pandas, polars, DuckDB or distributed compute runtime;
- no historical data loader;
- no event loop;
- no strategy runtime;
- no fee, slippage or fill implementation;
- no performance metrics engine;
- no paper trading;
- no broker or exchange integration.
