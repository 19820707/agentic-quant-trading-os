# Data Lineage And Leakage Policy

## Purpose

This policy defines the minimum evidence required before datasets, labels,
features, backtests or model training can be considered reliable.

It does not approve real market-data ingestion, feature-store runtime,
backtesting runtime, model training, network access, credentials, production
use, risk approval or execution.

## Required Lineage Evidence

Every dataset must preserve:

- dataset identifier and version
- event timestamp field
- created timestamp field
- available timestamp field
- label timestamp field
- positive label horizon
- dataset start and end timestamps
- source snapshot identifiers
- transformation identifiers
- feature availability lag
- temporal split policy

## Point-In-Time Rule

Feature availability must be evaluated using the timestamp at which the feature
was known, not the timestamp at which the event later settled.

Any dataset without `event_timestamp`, `created_timestamp`,
`available_timestamp` and `label_timestamp` must be blocked from model training
and backtesting.

## Leakage Review

The leakage review must cover:

- event timestamp presence
- created timestamp presence
- available timestamp presence
- label horizon validation
- future data join guard
- temporal train/validation split
- feature availability lag
- target leakage guard
- cross-sectional leakage guard
- survivorship bias review

Passing this review permits research evidence only. It does not approve model
training, backtesting, production use, risk decisions or execution.

## Required Defaults

All lineage and leakage contracts must keep these false:

- `model_training_approval_allowed`
- `backtest_approval_allowed`
- `production_approval_allowed`
- `network_allowed`
- `credentials_allowed`
- `execution_allowed`

## Promotion Boundary

Future promotion from research dataset to training dataset requires a separate
approval gate with human review, reproducibility evidence, leakage review,
data-retention policy, and rollback plan.

Until that gate exists, lineage and leakage records are audit evidence only.
