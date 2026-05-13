# Prediction Market Toolkit Governance Catalog

## Purpose

This catalog defines how external prediction-market toolkits are assessed before any integration is considered.

It does not approve installing, cloning, vendoring, importing, running, or adapting external toolkit runtime code.

Reference source:

- https://github.com/haredoggy/Prediction-Markets-Trading-Bot-Toolkits

## Current Decision

prediction_market_toolkit_catalog_reviewed: true
reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
private_endpoints_allowed: false
trading_methods_allowed: false
toolkit_runtime_allowed: false
market_making_runtime_allowed: false
copy_trade_runtime_allowed: false
arbitrage_runtime_allowed: false

Initial classification: reference-only governance and capability-taxonomy source.

## Capability Categories

External toolkits may be cataloged into:

- data ingestion
- market discovery
- signal research
- arbitrage research
- copy-trade observation
- market-making research
- risk review
- simulation
- audit

Cataloging a capability does not approve dependency use or runtime use.

## Default States

Every external toolkit must start as one of:

- reference-only
- research-only
- fake-client-only
- paper candidate
- read-only candidate
- future execution candidate

The default for unreviewed prediction-market tooling is `reference-only`.

## Required Review Axes

Each toolkit assessment must record:

- license clarity
- maintenance state
- dependency and transitive dependency risk
- credential risk
- execution risk
- testability
- production readiness
- required approval gates

## Strategy Pattern Registry

Strategy patterns may be classified as research only:

- arbitrage
- trend following
- copy-trade observation
- market-making research
- liquidity-provision research
- event reaction
- spread monitoring

No strategy pattern classification can create order intent, approve risk or approve execution.

## Market-Making Boundary

Market-making research may describe:

- quoted spread targets
- inventory limits
- liquidity quality
- spread risk

Market-making research must not:

- rebalance inventory
- publish quotes
- access credentials
- call networks
- submit executable instructions

## Research-to-Execution Escalation Map

Any future progression must be explicit:

1. reference-only
2. research contracts
3. fake adapter
4. read-only adapter
5. paper trading
6. controlled execution

No step may be skipped. Deterministic-risk-gateway remains mandatory for any future pre-trade path.

## Rejected Adaptation Targets

Rejected:

- direct dependency on external toolkits
- vendoring external source code
- SDK installation
- market-making runtime
- arbitrage runtime
- copy-trade runtime
- account clients
- position clients
- private endpoint workflows
- wallet workflows
- quote or order publication
- agent authority to trade

## Recommended Next Step

Review the governance contracts and use them to triage future prediction-market repositories before any adapter design.
