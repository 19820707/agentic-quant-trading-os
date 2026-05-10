# Trading-Agent-Polymarket Reference Review

## Purpose

This review identifies safe design patterns from `InjayTseng/Trading-Agent-Polymarket`.

It does not approve installing, cloning, vendoring, importing, running, or adapting the repository runtime.

Repository reviewed:

- https://github.com/InjayTseng/Trading-Agent-Polymarket

## Current Decision

trading_agent_polymarket_reference_reviewed: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
langgraph_allowed: false
langchain_allowed: false
llm_provider_sdk_allowed: false
polymarket_gamma_allowed: false
polymarket_websocket_allowed: false
newsapi_allowed: false
trading_decision_authority_allowed: false
kelly_sizing_for_execution_allowed: false

Initial classification: reference-only multi-agent research architecture source.

## Reusable Design Patterns

### Multi-Agent State Machine

The repository models prediction-market analysis as a graph with staged responsibilities:

- analyst team
- research debate
- signal or trading decision formatting
- risk debate
- structured output

The safe internal adaptation is a research graph that terminates at non-executable research records, probability estimates, signal candidates, and risk-review inputs.

### Specialized Analyst Team

Reusable analyst roles:

- event analyst: event definition, resolution criteria, timeline, ambiguity
- odds analyst: prices, liquidity, spread, order-book quality, market efficiency
- information analyst: news, related markets, external evidence
- sentiment analyst: public sentiment, expert/crowd divergence

These roles should produce bounded reports with source timestamps, confidence, caveats, and trace identifiers.

### YES / NO Research Debate

The YES/NO debate pattern is useful for reducing one-sided model reasoning.

Safe adaptation:

- YES researcher builds the strongest case for resolution
- NO researcher builds the strongest case against resolution
- research manager summarizes disagreement, evidence quality, and unresolved uncertainty

The debate must not produce an executable recommendation.

### Advisory Risk Debate

The aggressive, conservative, neutral, and judge pattern is useful only as advisory input.

Safe adaptation:

- aggressive reviewer identifies upside and thesis strength
- conservative reviewer identifies downside and failure modes
- neutral reviewer identifies balanced uncertainty
- risk reviewer produces advisory risk flags

This must never replace deterministic-risk-gateway. It may inform risk inputs, but cannot approve execution.

### Structured Signal Processor

Converting natural-language model output into structured records is useful.

Future safe records may include:

- signal: LONG, SHORT, FLAT, YES, NO, PASS, or abstain equivalent depending on contract
- estimated_probability
- market_price
- edge
- confidence
- rationale
- risk_flags
- evidence_refs
- trace_id
- correlation_id

The signal processor must reject malformed, overconfident, or execution-like outputs.

### Similar-Market Memory

The BM25-style memory pattern is useful as a local retrieval concept.

Safe adaptation:

- retrieve prior research dossiers
- retrieve hypothesis records
- retrieve calibration notes
- retrieve postmortem findings
- keep retrieval local/fake-first until separately approved

Memory must not contain secrets, credentials, private account data, or execution records with sensitive identifiers.

### LLM Provider Abstraction

The provider abstraction idea is useful, but external SDKs are not approved.

Safe adaptation:

- define an internal provider boundary
- keep providers disabled by default
- use fake/model-stub tests first
- require redaction, timeout, retry, and audit policies before any provider runtime

## Non-Reusable Components

Do not reuse directly:

- LangGraph runtime
- LangChain dependencies
- OpenAI, Google, Anthropic, XAI, OpenRouter, or other provider SDKs
- `python-dotenv`
- NewsAPI integration
- live Polymarket Gamma calls
- Polymarket WebSocket calls
- market URL ingestion that triggers live network lookups
- Kelly sizing connected to a trading decision
- BUY_YES or BUY_NO as operational commands
- code that treats model risk debate as approval

## Required Internal Boundary

Any future implementation inspired by this repository must:

- be contract-first
- use local fake/model-stub tests first
- avoid network calls in unit tests
- avoid credentials and environment reads
- treat market metadata as untrusted data
- emit structured non-executable outputs
- preserve trace_id and correlation_id
- fail closed on malformed model output
- preserve deterministic-risk-gateway authority

## Safe Adaptation Targets

Future project-native work may define:

- multi-agent research graph design
- analyst report contracts
- debate transcript contract
- signal candidate contract
- risk review input contract
- local memory/retrieval test harness
- LLM provider boundary documentation

## Rejected Adaptation Targets

Rejected:

- live graph execution against Polymarket
- provider SDK installation
- `.env` based API-key workflow
- trading decision authority
- Kelly sizing for live execution
- BUY/NO command path
- risk judge as execution approver
- WebSocket or Gamma runtime integration

## Recommended Next Step

Create internal contracts for multi-agent research outputs before implementing any graph runtime.

