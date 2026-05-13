# SXai Prediction Market Copytrade Reference Review

## Purpose

This review identifies safe research patterns from `SXai-lab/prediction-market-copytrade`.

It does not approve installing, cloning, vendoring, importing, running, or adapting the repository runtime.

Repository reviewed:

- https://github.com/SXai-lab/prediction-market-copytrade

## Current Decision

sxai_prediction_market_copytrade_reference_reviewed: true
reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
npm_runtime_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
private_endpoints_allowed: false
trading_methods_allowed: false
copy_execution_allowed: false
wallet_runtime_allowed: false
target_resolution_runtime_allowed: false

Initial classification: reference-only copy-trade observation and simulation source.

## Reusable Patterns

### Target Observation

The repository monitors a target trader identity before considering activity.

Safe adaptation:

- record a synthetic or manually reviewed target label
- record a public identifier as research context
- mark the record as observation-only
- keep network, credentials and execution disabled

### Observed Trader Activity

The repository reasons over recent target activity.

Safe adaptation:

- normalize activity type
- preserve observed timestamp and sequence
- record market reference, side, price and size
- set a stale-data boundary
- never transform activity into an execution command

### Copy Trade Policy

The repository exposes polling, activity limits, size multiplier and maximum size controls.

Safe adaptation:

- define local policy thresholds
- keep copy execution disabled
- keep wallet, credentials, network, production and execution disabled

### Copy Trade Simulation

The repository's copy-trade idea can be used only for hypothetical research replay.

Safe adaptation:

- record simulated size and notional
- record whether a cap was applied
- record blocked-by-policy or stale-activity outcomes
- keep the record simulation-only

### Trader Reliability Profile

Observed targets should be scored before any research uses them.

Safe adaptation:

- record sample count
- record win-rate estimate
- record drawdown estimate
- record recency score
- record data-quality flags
- disallow copy authority, risk approval and execution

### Copy Trade Risk Review Input

Copying another actor introduces concentration, latency, liquidity and copycat risk.

Safe adaptation:

- record advisory risk flags
- require deterministic-risk-gateway for any future path
- disallow risk approval and execution

## Non-Reusable Components

Do not reuse directly:

- TypeScript or npm runtime
- target username or address resolver runtime
- account activity polling runtime
- wallet or funder workflows
- signature workflows
- credential environment workflow
- copy-trade executor
- real account client
- order placement workflow
- production mode workflow

## Required Internal Boundary

Any future implementation inspired by this repository must:

- remain contract-first
- use synthetic fixtures first
- avoid network calls in unit tests
- avoid credentials and environment reads
- avoid wallet, signature or account runtime material
- treat observed activity as stale unless explicitly timestamped
- preserve trace_id and correlation_id
- emit non-executable research records only
- preserve deterministic-risk-gateway authority

## Safe Adaptation Targets

This project may safely define:

- copy-trade target observation contracts
- observed trader activity contracts
- copy-trade policy contracts
- copy-trade simulation contracts
- trader reliability profile contracts
- copy-trade risk review input contracts
- local research runbooks

## Rejected Adaptation Targets

Rejected:

- direct dependency on the external repository
- vendoring source code
- npm runtime adoption
- live account polling
- private endpoint calls
- wallet operations
- copy-trade execution
- production mode
- model or agent authority to mirror trades

## Recommended Next Step

Review copy-trade observation contracts before considering any adapter design or external dependency.
