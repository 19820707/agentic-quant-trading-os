# Fake Offline Materialization Review

## Purpose

The fake offline materialization review contract defines the evidence required before any future local-only feature materialization simulation can be considered.

This document does not approve materialization jobs, real feature store runtime, online serving, model training, backtesting, signal generation, order intent creation, risk decisions, execution, network access, credentials, or production use.

## Scope

Allowed scope is limited to a reviewed plan for fake offline materialization using deterministic local fixtures in a future PR. The current contract is review-only and does not create data, mutate files, run jobs, or call services.

## Required Evidence

Every review must reference:

- a FeatureStoreApprovalGate record;
- a feature view contract ID;
- a dataset lineage record ID;
- a leakage review report ID;
- a point-in-time join plan ID;
- a rollback plan ID;
- a human review record ID.

## Required Checks

The review must prove the future fake materialization plan is:

- local-only;
- deterministic;
- point-in-time constrained;
- leakage-reviewed;
- reversible;
- isolated from model training and backtesting;
- isolated from risk and execution.

## Forbidden Capabilities

The review cannot approve:

- real feature store runtime;
- physical feature materialization;
- online serving;
- feature writes to a database;
- external data fetches;
- credentials;
- model training;
- backtest promotion;
- signal candidate creation;
- order intent creation;
- risk approval;
- execution;
- production use.

## Promotion Rule

The only possible next step after this contract is a separate PR for a fake local materialization harness. That future PR must still use fixtures or in-memory data only and must not introduce pandas, polars, DuckDB, network calls, credentials, runtime services, training, backtesting or trading paths unless separately approved.

## Non-Goals

- no materialization implementation;
- no feature store dependency;
- no feature store service;
- no database;
- no scheduler;
- no model training;
- no backtesting engine;
- no signal engine integration;
- no trading or execution.
