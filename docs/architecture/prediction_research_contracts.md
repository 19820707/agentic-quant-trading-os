# Prediction Research Contracts

## Purpose

Prediction research contracts define the non-executable payloads produced by future research, multi-agent analysis, debate, calibration and advisory-risk workflows.

They are contract-first scaffolding only. They do not implement a graph runtime, LLM provider, network integration, prediction-market adapter, trading strategy, order intent service, risk gateway, execution engine or broker/exchange integration.

## Contracts

The `research` schema domain contains:

- `ResearchDossier`: source-bound research summary with uncertainty and prompt-injection review state
- `ProbabilityEstimate`: calibrated or research-derived probability estimate
- `HypothesisRecord`: governed research hypothesis lifecycle record
- `AnalystReport`: bounded report from event, odds, information or sentiment analysts
- `DebateTranscript`: YES/NO, advisory risk or governance debate record
- `SignalCandidate`: non-executable candidate signal
- `RiskReviewInput`: advisory input for later deterministic risk review
- `TieredResearchStage`: local tiered research stage metadata
- `MarketNewsRelevanceScore`: local market-news relevance scoring record
- `ResearchCadencePlan`: non-runtime cadence plan for research workflows
- `ModelLimitationRecord`: explicit model limitation and failure-mode record
- `DryRunEvaluationSummary`: paper-only dry-run evaluation summary

## Safety Boundary

These contracts may describe:

- research evidence
- probabilities
- confidence
- uncertainty
- risk flags
- debate summaries
- hypothesis state
- advisory notes
- tiered research planning
- market-news relevance scores
- research cadence plans
- model limitation records
- dry-run evaluation summaries

They must not contain:

- credentials
- private endpoint payloads
- wallet keys
- broker or exchange secrets
- executable orders
- `ApprovedOrder`
- live execution approval
- risk approval
- broker/exchange requests

## Execution Boundary

`SignalCandidate` is not an `OrderIntent`.

`RiskReviewInput` is not a `RiskDecision`.

`DryRunEvaluationSummary` is not live approval.

`ResearchCadencePlan` is not a scheduler.

No research contract can approve risk, approve execution, submit orders, cancel orders, transfer funds or withdraw funds.

Any future path from a research contract toward an order must pass through separately approved services and deterministic-risk-gateway.

## Testing Boundary

Current validation is local-only:

- JSON Schema fixtures
- contract registry tests
- contract validator tests
- non-executable safety assertions
- no network
- no credentials
- no LLM runtime
- no scheduler runtime
- no Polymarket CLOB runtime
- no wallet or notification runtime

