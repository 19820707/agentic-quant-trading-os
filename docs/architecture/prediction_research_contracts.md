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
- `PredictionMarketSignalClassification`: five-tier non-executable signal classification
- `EdgeComputationRecord`: calibrated probability versus market probability comparison
- `EnsembleProbabilityVote`: model-vote record and aggregation metadata
- `AdvisoryKellySizing`: capped sizing hint for research review only
- `SignalPipelineStatus`: local progress record for signal pipeline stages

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
- signal classification
- edge computation
- ensemble probability votes
- advisory Kelly sizing
- pipeline status

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

`PredictionMarketSignalClassification` is not an `OrderIntent`.

`AdvisoryKellySizing` is not a position size, risk approval or execution approval.

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
- no external LLM provider
- no Synthesis.trade runtime
- no wallet or order API
- no dashboard execution controls

