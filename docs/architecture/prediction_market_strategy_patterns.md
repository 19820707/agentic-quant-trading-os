# Prediction Market Strategy Patterns

## Purpose

This document defines safe internal strategy pattern contracts inspired by external prediction-market trading toolkits.

The platform uses these patterns for research classification, feature planning and risk review only. They do not approve strategy runtime, venue access, credentials, wallet access, order creation, risk approval or execution.

## Safe Pattern Layer

Allowed:

- catalog strategy ideas
- document required observations
- record advisory risk guards
- compute read-only features from local fixtures
- produce non-executable signal candidates
- produce advisory risk-review inputs

Forbidden:

- executable bots
- wallet mirroring
- venue account access
- automatic entry or exit
- market making runtime
- live order book polling in unit tests
- direct execution from signal or feature output

## Pattern Catalog

Supported research categories:

- copy activity research
- short-window price research
- cross-venue research
- momentum research
- spread research
- sports market research
- resolution research
- orderbook imbalance research
- market making research
- on-chain activity research

Every pattern must preserve uncertainty, stale-data risk and manual review requirements.

## Risk Guard Concepts

Risk guard profiles may describe:

- circuit breaker thresholds
- event window lengths
- cooldown lengths
- depth guard thresholds
- dry-run requirements

They are not `RiskDecision` records and cannot approve execution.

## Feature Concepts

Read-only feature contracts may include:

- liquidity depth score
- order book imbalance score
- public wallet activity observation

These features may inform `SignalCandidate` or `RiskReviewInput`, but they must not create `OrderIntent` or `ApprovedOrder`.

## Non-Goals

- no trading runtime
- no external toolkit runtime
- no venue API calls
- no credentials
- no wallet keys
- no account state
- no order placement
- no production enablement
