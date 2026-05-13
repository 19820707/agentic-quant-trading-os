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
- `PredictionMarketToolkitAssessment`: external toolkit capability and default-state assessment
- `StrategyPatternClassification`: non-executable strategy pattern classification
- `IntegrationReadinessAssessment`: external integration readiness and risk scoring
- `MarketMakingResearchPolicy`: disabled market-making research policy
- `LiquidityQualityObservation`: local liquidity quality research observation
- `SpreadRiskEstimate`: spread and slippage risk estimate

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
- external toolkit governance
- strategy classifications
- liquidity quality
- spread risk

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
- quote publication
- inventory rebalancing

## Execution Boundary

`SignalCandidate` is not an `OrderIntent`.

`RiskReviewInput` is not a `RiskDecision`.

No research contract can approve risk, approve execution, submit orders, cancel orders, transfer funds or withdraw funds.

Prediction-market governance contracts cannot install toolkits, enable runtime adapters, publish quotes, rebalance inventory, approve risk or approve execution. They only classify and score external tools, strategy patterns, liquidity quality and spread risk.

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

