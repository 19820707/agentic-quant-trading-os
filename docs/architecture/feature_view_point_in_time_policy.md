# Feature View Point-In-Time Policy

## Purpose

Feature view contracts describe feature definitions and safe joins without
materializing features or approving model training, backtesting, production use,
risk decisions or execution.

## Required Links

Every feature view must link to:

- `DatasetLineageRecord`
- `LeakageReviewReport`

Every point-in-time join plan must link to:

- left dataset identity
- left dataset lineage record
- right feature view contract
- leakage review report

## Feature Requirements

Each feature must define:

- feature name
- data type
- source field
- availability lag
- maximum staleness
- point-in-time safety flag

Features are invalid for training or backtesting until their availability lag
and staleness assumptions are reviewed.

## Join Requirements

Join plans must use backward as-of semantics:

```text
feature.available_timestamp <= event.event_timestamp
```

The join must preserve temporal order, match entity keys, disallow future data
joins, require leakage review and remain non-executable.

## Forbidden Defaults

The following must remain false:

- `materialization_allowed`
- `model_training_approval_allowed`
- `backtest_approval_allowed`
- `network_allowed`
- `credentials_allowed`
- `production_approval_allowed`
- `execution_allowed`

## Current Status

Feature view contracts are metadata-only. They do not implement Feast, Feathr,
Featureform, Spark, DuckDB, Pandas, SQL, batch materialization, online serving,
network calls, credentials or production feature serving.
