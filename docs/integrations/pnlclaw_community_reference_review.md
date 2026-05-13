# PnLClaw Community Reference Review

## Purpose

This review identifies safe architecture patterns from `YicunAI/Pnlclaw-community`.

It does not approve installing, cloning, vendoring, importing, running, or adapting the repository runtime.

Repository reviewed:

- https://github.com/YicunAI/Pnlclaw-community

## Current Decision

pnlclaw_community_reference_reviewed: true
reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
trading_methods_allowed: false
agent_runtime_allowed: false
mcp_runtime_allowed: false
llm_provider_runtime_allowed: false
exchange_runtime_allowed: false
paper_runtime_allowed: false
desktop_runtime_allowed: false

Initial classification: reference-only local-first agentic quant architecture source.

## Reusable Patterns

### Skill Registry

The layered skill registry concept is useful for governance.

Safe adaptation:

- catalog skill definitions
- record registry layer
- declare tool dependencies
- validate missing-tool behavior
- keep skills disabled by default

### Tool Policy

Per-tool risk policy is useful for blocking dangerous agent capabilities.

Safe adaptation:

- classify tool risk
- require manual approval for risky tools
- block shell, file writes, network, credentials, trading and execution by default
- audit proposed or blocked tool calls

### ReAct Loop Guard

The observe-think-act-reflect loop requires strict guardrails.

Safe adaptation:

- cap repeated tool calls
- cap reasoning steps
- fail closed on loops
- require hallucination review
- disallow autonomous actions

### Local-First Boundary

The local-first privacy posture is useful as a principle.

Safe adaptation:

- keep research data local
- keep sensitive material out of prompts and logs
- use redaction before audit or model context
- keep agent tools without ambient authority

## Non-Reusable Components

Do not reuse directly:

- desktop application runtime
- local API runtime
- agent runtime
- MCP runtime
- LLM provider runtime
- exchange websocket runtime
- strategy compiler runtime
- backtest or paper trading execution runtime
- exchange setup workflow
- deployment workflows

## Required Internal Boundary

Any future implementation inspired by this repository must:

- remain contract-first
- use synthetic fixtures first
- avoid network calls in unit tests
- avoid credentials and environment reads
- avoid ambient shell and file-write authority
- preserve trace_id and correlation_id
- emit non-executable research records only
- preserve deterministic-risk-gateway authority

## Safe Adaptation Targets

This project may safely define:

- agent skill definition contracts
- skill dependency declaration contracts
- agent tool permission policy contracts
- tool risk classification contracts
- tool call audit records
- agent loop guard contracts
- local-first agentic quant boundary documentation

## Rejected Adaptation Targets

Rejected:

- direct dependency on the external repository
- vendoring source code
- app/runtime adoption
- provider SDK adoption
- exchange runtime adoption
- MCP runtime activation
- paper or production deployment paths
- model or agent authority to trade

## Recommended Next Step

Review the local-first agent/tool contracts before considering any runtime agent framework.
