# Fake Offline Materialization Review

## Purpose

FakeOfflineMaterializationReview defines the evidence required before any future local-only fake feature materialization work can be considered.

This document does not approve real materialization, a real feature store, online serving, model training, backtesting, market data ingestion, signal creation, order intent creation, risk approval, execution approval, network access, credentials or production use.

## Current State

The current state remains fail-closed:

- fake offline materialization is not enabled;
- real feature store runtime is not implemented;
- online serving is not enabled;
- model training is not approved;
- backtesting is not approved;
- market data ingestion is not approved;
- signal creation is not approved;
- order intent creation is not approved;
- risk approval is not granted;
- execution is not allowed;
- network access is not allowed;
- credentials are not allowed;
- production use is not allowed.

## Required Evidence

Any later PR proposing fake offline materialization must reference:

- FeatureStoreApprovalGate;
- DatasetLineageRecord;
- LeakageReviewReport;
- FeatureViewContract;
- point-in-time join plan;
- rollback plan;
- human review record.

The review contract stores stable IDs only. It does not import runtime code, perform joins, load data, write features or start background jobs.

## Point-In-Time Controls

The point-in-time join plan must define:

- the as-of timestamp field;
- the event timestamp field;
- join keys;
- future-data blocking;
- late-arrival handling;
- clock-skew handling.

These controls are metadata requirements. They do not approve materialization or backtesting.

## Boundary

Allowed now:

- local contract validation;
- static fixture validation;
- documentation of required evidence;
- explicit rejected readiness decision.

Forbidden now:

- real feature store runtime;
- offline or online materialization jobs;
- external reads;
- mutable source data;
- training jobs;
- backtest jobs;
- signal or order creation;
- risk approval;
- execution;
- network;
- credentials.

## Non-Goals

- no Feast, Feathr, Featureform or hosted feature store integration;
- no pandas, polars, DuckDB or batch compute runtime;
- no data ingestion;
- no model training;
- no backtesting;
- no paper trading;
- no broker or exchange integration;
- no production enablement.
