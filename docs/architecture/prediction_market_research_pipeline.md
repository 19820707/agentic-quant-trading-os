# Prediction Market Research Pipeline

## Purpose

This document defines a safe internal research pipeline inspired by external prediction-market research systems.

It is not a trading runtime. It does not approve external dependencies, exchange access, wallet access, broker credentials, private endpoints, order submission, or live execution.

## Boundary

The pipeline may produce:

- research dossiers
- market selection notes
- probability estimates
- model forecasts
- signal candidates
- calibration records
- hypothesis records
- audit events

The pipeline must not produce:

- executable orders
- OrderIntent without a separate approved order-intent service
- ApprovedOrder
- broker or exchange requests
- wallet transactions
- private endpoint calls
- risk approvals
- execution approvals

## Safe Loop Model

### Research Loop

Purpose:

- collect source material
- summarize relevant context
- record provenance
- identify uncertainty and missing evidence

Output:

- research dossier
- source list
- freshness timestamp
- confidence caveats

Forbidden:

- private endpoints
- credentials
- order or wallet operations
- direct trading recommendations

### Strategy Loop

Purpose:

- classify candidate markets
- evaluate category, liquidity, volume, horizon, and resolution clarity
- reject markets with poor governance or ambiguous resolution criteria
- rank candidates for deeper review

Output:

- candidate score
- market-selection rationale
- rejection reason where applicable

Forbidden:

- execution sizing
- broker/exchange calls
- wallet state reads
- bypass of deterministic-risk-gateway

### Tactical Analysis Loop

Purpose:

- run deeper probability analysis
- compare estimate against market-implied probability
- identify evidence for divergence
- produce a non-executable signal candidate

Output:

- probability estimate
- uncertainty interval
- evidence summary
- adversarial critique
- calibration adjustment
- signal candidate

Forbidden:

- order placement
- order cancellation
- transfer or withdrawal
- risk approval
- execution approval

## Probability Estimation Stages

Future model work should separate these stages:

1. Base rate
2. Evidence update
3. Adversarial review
4. Calibration adjustment

Every estimate should preserve:

- input data timestamp
- evidence timestamp
- model identity
- prompt or policy version where relevant
- trace_id
- correlation_id
- uncertainty and caveats
- redacted error context

## Market Selection Policy

Candidate markets should be evaluated by:

- market category
- volume tier
- liquidity
- time to resolution
- resolution clarity
- information freshness
- likelihood that public model consensus is already priced in
- data availability
- stale data risk
- legal, jurisdictional, or governance concerns

Markets should be rejected when:

- resolution criteria are ambiguous
- required data is stale or unavailable
- category is outside approved research scope
- analysis requires credentials or private endpoints
- expected behavior depends on direct execution
- confidence cannot be explained with auditable evidence

## Hypothesis Lifecycle

Research hypotheses should follow a governed lifecycle:

- proposed
- testing
- confirmed
- rejected
- retest required

Each hypothesis should track:

- owner
- creation timestamp
- evidence
- test plan
- confidence
- decay or review date
- decision history
- relationship to model or market category

Confirmed hypotheses may inform research configuration. They must not automatically approve live trading, risk changes, execution changes, or credential access.

## Calibration And Evaluation

Calibration workflows should support:

- Brier score tracking
- category-level calibration
- volume-tier calibration
- bootstrap confidence intervals
- paired model comparisons
- pre/post adversarial review comparison
- contamination checks for historical outcomes
- separation of backtest, paper, and live approval states

Backtest success is evidence, not approval. Paper trading remains mandatory before any future controlled-live path.

## Observability

The platform should emit or display:

- research dossier status
- candidate scoring status
- model forecast quality
- calibration history
- hypothesis lifecycle state
- stale-data indicators
- cost and latency metrics
- audit trail for research configuration changes

Observability surfaces must remain read-only unless a separate governance PR explicitly approves a controlled operational action. They must not expose trade, cancel, transfer, withdrawal, private endpoint, wallet, or kill-switch disable controls.

## Integration Rules

Any future implementation must:

- use internal contracts first
- use local fake/in-memory tests first
- avoid network calls in unit tests
- avoid credentials in tests and examples
- redact errors before reporting
- emit structured audit events where relevant
- preserve trace_id and correlation_id where relevant
- fail closed when data, model, or safety state is unclear

## Non-Goals

- no external repository integration
- no dependency installation
- no Polymarket, Kalshi, CLOB, wallet, or broker runtime
- no private endpoints
- no trading logic
- no order submission
- no execution engine integration
- no production deployment

