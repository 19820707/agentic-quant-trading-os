# Prediction Market Research Safety Boundary

## Purpose

This document consolidates the safety boundary for prediction-market research contracts.

It does not approve external SDKs, runtime adapters, network access, credentials, private endpoints, wallet access, account access, order publication, risk approval, execution approval or production use.

## Allowed Research Outputs

Allowed outputs:

- toolkit assessments
- strategy pattern classifications
- integration readiness assessments
- liquidity observations
- spread risk estimates
- local simulation summaries
- audit notes
- advisory risk inputs

## Forbidden Outputs

Forbidden outputs:

- executable orders
- order intents
- approved orders
- account operations
- private endpoint payloads
- wallet operations
- quote publication
- risk approval
- execution approval
- production enablement

## Required Gates

Before any future runtime design, the project must have:

- external adapter review
- dependency review
- security review
- contract mapping
- fake/in-memory tests
- no-network unit tests
- credential-boundary tests
- deterministic-risk-gateway boundary review

## Governance Contracts

The governance contract layer includes:

- `PredictionMarketToolkitAssessment`
- `StrategyPatternClassification`
- `IntegrationReadinessAssessment`
- `MarketMakingResearchPolicy`
- `LiquidityQualityObservation`
- `SpreadRiskEstimate`

These contracts are non-executable and cannot approve runtime behavior.

## Escalation Rule

Research records may inform future analysis, but they must not directly feed broker, exchange, wallet, account, quote-publication or execution paths.

Any future executable path must pass through separately approved services and deterministic-risk-gateway.
