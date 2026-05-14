# Data Lineage and Leakage Policy

## Purpose

This policy defines the minimum governance controls for datasets used by future feature engineering, model training, validation, backtesting and paper-research workflows.

The current repository remains a safe scaffold. These contracts document dataset provenance and leakage review only. They do not enable ingestion, market-data access, feature-engine runtime, model training, backtesting, broker/exchange integration, credentials, networking or trading.

## Required Contracts

Every dataset proposed for modeling or backtesting must eventually have both records:

1. `DatasetLineageRecord`
2. `LeakageReviewReport`

A lineage record describes where the dataset came from, what temporal range it covers, which source systems were used, and which point-in-time controls are required.

A leakage review report documents whether the dataset has been reviewed for look-ahead bias, future-label contamination, target leakage, train/test overlap, survivorship bias, late-arriving data and timestamp alignment.

## Non-Executable Boundary

These contracts are governance artifacts only.

They must not:

- fetch market data;
- call external APIs;
- read secrets;
- require broker, exchange, wallet, PMXT, Synthesis, OpenBB, CCXT or vendor credentials;
- compute features;
- train models;
- run backtests;
- approve model use;
- approve live use;
- create `SignalCandidate`, `OrderIntent`, `RiskDecision`, `ApprovedOrder` or `ExecutionReport`;
- bypass deterministic-risk-gateway.

## Point-in-Time Rules

Datasets intended for financial modeling must preserve point-in-time correctness.

Minimum rules:

- `as_of_join_required` must be true.
- `future_data_excluded` must be true.
- training, validation and test windows must preserve temporal order.
- split overlap must be disallowed unless a later approved methodology explicitly defines safe purging.
- feature availability must be tracked before runtime use.
- label horizons must be declared before runtime use.
- late-arriving data must be excluded, quarantined or manually reviewed.
- transformations must not use future information.

## Leakage Review Rules

A leakage review must consider at least:

- point-in-time joins;
- future label exclusion;
- target leakage;
- look-ahead features;
- survivorship bias;
- train/test overlap;
- timestamp alignment;
- late data arrival;
- feature availability;
- duplicate event contamination;
- manual override risk.

In this scaffold phase, `LeakageReviewReport` is deliberately fail-safe:

- `approved_for_model_training` must be false;
- `approved_for_backtest` must be false;
- `approved_for_live_use` must be false.

Future approval semantics require a separate PR with governance review, runtime controls and audit logging.

## Safe Implementation Sequence

1. Define lineage and leakage contracts.
2. Add valid fixtures using static paper-only data.
3. Add contract tests and CI coverage.
4. Add a dependency/SBOM baseline before runtime data tooling.
5. Add a read-only data adapter interface.
6. Add source-specific data quarantine and license review.
7. Add feature-engine contracts.
8. Add model-training contracts.
9. Add paper backtest contracts.
10. Only later consider runtime implementations.

## Prohibited in This Phase

- real market data;
- OpenBB;
- CCXT;
- QuestDB;
- Polymarket/Kalshi/PMXT/Synthesis clients;
- crawlers;
- network calls;
- credentials;
- feature-engine runtime;
- model training;
- backtest execution;
- trading logic;
- risk approval;
- execution approval.

## Audit Expectations

Every future runtime PR touching data or modeling must explain:

- source systems;
- license and entitlement constraints;
- timestamp semantics;
- as-of availability;
- late-arrival handling;
- split methodology;
- label horizon;
- feature availability;
- leakage tests;
- rollback plan;
- owner/reviewer.
