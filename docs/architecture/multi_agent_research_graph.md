# Multi-Agent Research Graph

## Purpose

This document defines a safe internal graph pattern for multi-agent market research.

It is inspired by external multi-agent prediction-market analysis systems, but it does not approve external dependencies, LLM provider SDKs, runtime graph frameworks, network calls, credentials, trading logic, or execution.

## Boundary

The graph may produce:

- analyst reports
- debate transcripts
- research manager summaries
- probability estimates
- signal candidates
- risk-review inputs
- audit events

The graph must not produce:

- executable orders
- ApprovedOrder
- broker or exchange calls
- wallet actions
- private endpoint calls
- execution approval
- risk approval
- live trading decisions

## Graph Phases

### Phase 1: Analyst Reports

Analysts operate independently and produce bounded reports.

Required roles:

- event analyst
- odds analyst
- information analyst
- sentiment analyst

Each report should include:

- report_type
- subject
- evidence_summary
- source_refs
- data_timestamp
- confidence
- caveats
- trace_id
- correlation_id

Analyst reports are evidence artifacts. They are not recommendations.

### Phase 2: YES / NO Debate

The debate phase forces competing arguments before synthesis.

Required outputs:

- yes_thesis
- no_thesis
- disagreements
- shared_evidence
- unresolved_questions
- research_manager_summary

The debate phase must not directly emit trade commands, order intents, or risk approvals.

### Phase 3: Signal Candidate Formatting

The signal processor converts research into a structured non-executable candidate.

Allowed fields:

- signal
- estimated_probability
- market_price
- edge
- confidence
- rationale
- risk_flags
- evidence_refs
- trace_id
- correlation_id

Required behavior:

- reject malformed model output
- reject execution-like language
- preserve uncertainty
- emit structured errors
- fail closed under ambiguity

### Phase 4: Advisory Risk Review

The advisory risk review may produce risk flags and review notes.

Review perspectives:

- aggressive
- conservative
- neutral
- risk_reviewer

Allowed outputs:

- risk_flags
- uncertainty_notes
- liquidity_notes
- stale_data_notes
- model_risk_notes
- governance_notes

Forbidden outputs:

- APPROVE
- ApprovedOrder
- execution permission
- risk-limit override
- kill-switch disablement

The deterministic-risk-gateway remains the only future pre-trade authority.

## Memory And Retrieval

Local memory may support:

- similar prior markets
- hypothesis records
- calibration notes
- postmortems
- prior debate summaries

Initial implementation must use fake/local data only.

Memory must not store:

- broker credentials
- exchange credentials
- wallet keys
- private account state
- live order identifiers
- secrets

## LLM Provider Boundary

Future provider integrations require separate approval.

Until approved:

- use model stubs only
- do not install provider SDKs
- do not read environment variables
- do not require API keys
- do not call network
- do not stream real provider output into tests

Any future provider boundary must include:

- timeout policy
- retry policy
- redaction
- structured errors
- audit events
- prompt-injection controls
- cost and latency metrics

## Market Metadata Handling

Market metadata is untrusted input.

The graph must:

- delimit market text as data
- sanitize control characters
- enforce maximum length
- preserve source timestamps
- prevent market text from becoming instructions
- detect instruction-like payloads
- keep system/developer prompts separate from retrieved market content

## Non-Goals

- no LangGraph runtime
- no LangChain runtime
- no provider SDKs
- no Polymarket API runtime
- no WebSocket runtime
- no NewsAPI runtime
- no credentials
- no trading commands
- no live execution
- no production deployment

