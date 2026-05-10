# market-edge Reference Review

## Purpose

This review identifies which ideas from `datori/market-edge` can be reused safely as internal design patterns.

It does not approve installing, cloning, vendoring, importing, running, or adapting `market-edge` code.

Repository reviewed:

- https://github.com/datori/market-edge

## Current Decision

market_edge_reference_reviewed: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
polymarket_clob_allowed: false
live_executor_allowed: false
wallet_access_allowed: false
trading_methods_allowed: false

Initial classification: reference-only architecture source.

## Reusable Ideas

### Research / Strategy / Tactical Separation

The three-loop structure is useful as an internal design reference:

- research loop: collect dossiers, news, source material, and historical context
- strategy loop: screen and rank candidate markets
- tactical loop: perform deeper analysis and produce structured estimates

In this platform, those loops must terminate at research artifacts, predictions, candidate signals, or review records. They must not call broker, exchange, wallet, CLOB, order, or execution APIs.

### Multi-Pass Probability Estimation

The four-pass probability workflow is useful as a future AI research pattern:

- base-rate estimate
- evidence or Bayesian update
- adversarial review
- calibration adjustment

The safe internal equivalent should produce only a `ProbabilityEstimate`, `ModelForecast`, or `SignalCandidate`. It must not produce an `OrderIntent`, `ApprovedOrder`, execution decision, wallet action, or order request.

### Market Selection Thesis

The strategy thesis is useful because it treats market selection as a first-class risk control.

Reusable policy concepts:

- avoid highly efficient markets where model consensus is likely already priced in
- separate market categories by information structure
- track market volume and liquidity as edge-decay indicators
- require explicit reasoning when model probability diverges from market odds
- reject ambiguous resolution criteria as a governance risk

### Hypothesis Lifecycle

The hypothesis tracker concept is useful for governed research:

- proposed
- testing
- confirmed
- rejected
- retest required

This platform should preserve hypothesis history, confidence decay, test evidence, and reviewer decisions. A confirmed research hypothesis must not imply live-trading approval.

### Backtest And Calibration Evaluation

Reusable evaluation concepts:

- Brier score tracking
- stratified sampling by category and volume tier
- bootstrap confidence intervals
- paired model comparisons
- contamination checks for historical outcomes that may appear in model training data
- separation between research backtests and production decisions

### Observability Dashboard Concepts

The dashboard sections are useful as a reference for future observability:

- calibration
- evaluation
- hypotheses
- operations
- positions or simulated portfolio state
- cost and latency metrics

For this platform, dashboard views must remain observational. They must not expose direct trade, cancel, transfer, wallet, private endpoint, or risk-limit override controls.

## Non-Reusable Components

Do not reuse directly:

- Polymarket CLOB client
- live executor
- wallet or private-key configuration
- funder address configuration
- `.env` runtime key workflow
- Kelly sizing connected to execution
- autonomous agent run command
- dashboard or CLI paths that can trigger execution
- local live portfolio database semantics
- any code path that can place, cancel, modify, transfer, redeem, or settle orders

## Dependency Risk

Observed dependency concerns include:

- LLM provider SDK
- web-search provider SDK
- Polymarket CLOB client
- HTTP client libraries
- dashboard runtime dependencies
- Python version and package-manager assumptions that differ from this project

No dependency from `market-edge` should be added without a separate dependency review and explicit approval.

## Safe Internal Adaptation Targets

Future safe PRs may create project-native documentation or contracts for:

- prediction-market research pipeline design
- market-selection policy
- probability-estimate schema
- hypothesis lifecycle schema
- calibration and Brier-score evaluation plan
- observability dashboard requirements
- paper-only simulation review gates

Each future PR must be local-only and contract-first.

## Required Guardrails

Any future work inspired by `market-edge` must preserve these boundaries:

- no external repository clone
- no vendored code
- no dependency installation
- no provider API keys
- no wallet credentials
- no private endpoints
- no CLOB client
- no live executor
- no order submission
- no OrderIntent creation from research loops
- no ApprovedOrder creation
- no bypass of deterministic-risk-gateway
- no dashboard-to-execution path

## Recommended Next Step

Create a project-native prediction-market research pipeline document and tests. The pipeline should model safe research, probability estimation, hypothesis tracking, calibration, and observability boundaries without implementation code.

