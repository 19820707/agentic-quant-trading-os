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
- `AgentOrchestrationPlan`: non-runtime supervised agent coordination plan
- `AgentRoleAssignment`: bounded agent responsibility record
- `AgentHandoffRecord`: redacted supervised handoff record
- `AgentConsensusRecord`: advisory-only consensus record
- `SwarmTopologyPolicy`: disabled swarm topology policy
- `AgentFederationPolicy`: cross-machine and remote-agent boundary policy
- `AgentMemoryPolicy`: local redacted memory policy
- `MCPToolRegistrationPolicy`: disabled MCP tool registration policy
- `BackgroundWorkerPolicy`: disabled background worker policy
- `AgentCostBudgetPolicy`: fail-closed cost budget policy
- `PromptInjectionReview`: defensive prompt safety review
- `InvestmentScenarioInput`: educational scenario assumptions
- `InvestmentScenarioProjection`: deterministic projection output
- `InvestorProfileAllocation`: educational profile allocation buckets
- `LongHorizonScenarioSet`: multi-horizon scenario comparison
- `AssumptionSensitivityReport`: sensitivity across static assumptions
- `FinancialEducationDisclaimer`: non-advisory simulation boundary

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
- agent orchestration governance
- swarm and federation policy
- memory and MCP registration policy
- prompt injection findings
- educational investment assumptions
- long-horizon projections
- sensitivity observations
- educational disclaimer state

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
- autonomous agent execution
- MCP runtime activation
- federation
- background automation
- personalized financial advice
- trade recommendations

## Execution Boundary

`SignalCandidate` is not an `OrderIntent`.

`RiskReviewInput` is not a `RiskDecision`.

No research contract can approve risk, approve execution, submit orders, cancel orders, transfer funds or withdraw funds.

Agent orchestration contracts cannot launch swarms, register MCP tools, federate agents, activate memory systems, schedule workers, access credentials, approve risk or approve execution. They only describe governance records and fail-closed policy.

Investment scenario contracts cannot recommend assets, create signals, create order intents, approve risk or approve execution. They only describe educational local assumptions and projections.

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

