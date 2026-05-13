# Ruflo Reference Review

## Purpose

This review identifies safe governance patterns from `ruvnet/ruflo`.

It does not approve installing, cloning, vendoring, importing, running, or adapting the repository runtime.

Repository reviewed:

- https://github.com/ruvnet/ruflo

## Current Decision

ruflo_reference_reviewed: true
reference_only: true
direct_dependency_allowed: false
clone_allowed: false
vendoring_allowed: false
npm_runtime_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
trading_methods_allowed: false
mcp_runtime_allowed: false
swarm_runtime_allowed: false
federation_runtime_allowed: false
memory_runtime_allowed: false
background_worker_runtime_allowed: false
neural_trader_runtime_allowed: false
market_data_runtime_allowed: false

Initial classification: reference-only agent orchestration governance source.

## Reusable Patterns

### Agent Orchestration Governance

Ruflo emphasizes coordinated multi-agent workflows.

Safe adaptation:

- define orchestration plans
- define role assignments
- define handoff records
- define consensus records
- keep all records advisory and non-executable

### Swarm Topology Policy

Swarm topology is useful as a policy concept only.

Safe adaptation:

- define maximum agent count
- restrict topology to manual supervision
- disable federation
- disable autonomous loops
- disable network and execution

### Federation Boundary

Cross-machine agent federation is a high-risk boundary.

Safe adaptation:

- block remote agents by default
- block cross-machine coordination
- require explicit identity review
- disallow credentials and network access

### Agent Memory Governance

Agent memory is useful only after strict data classification.

Safe adaptation:

- restrict memory to redacted local audit records
- disallow secret storage
- disallow credential storage
- disallow external memory systems

### MCP Tool Registration Policy

MCP registration is useful as a governed interface, not as automatic runtime activation.

Safe adaptation:

- require explicit registration policy
- block tool registration by default
- block broker credentials
- block trading and execution

### Background Worker Policy

Background workers can create hidden automation risk.

Safe adaptation:

- block schedules by default
- block autonomous execution
- block network and credentials

### Cost Budget Policy

Agent budgets prevent runaway work.

Safe adaptation:

- cap tokens per task
- cap cost per task
- fail closed on budget breaches
- disallow autonomous spending

### Prompt Injection Review

Prompt-injection and tool-call defence are critical for agentic systems.

Safe adaptation:

- classify prompt risk
- require sanitization
- block tool calls where needed
- disallow credential exposure

## Non-Reusable Components

Do not reuse directly:

- npm or npx installation flows
- shell install scripts
- MCP server runtime
- plugin marketplace runtime
- swarm runtime
- federation runtime
- vector memory runtime
- RAG runtime
- background workers
- browser automation runtime
- neural trading runtime
- market data runtime
- hosted web UI or cloud workflow

## Required Internal Boundary

Any future implementation inspired by this repository must:

- remain contract-first
- use synthetic fixtures first
- avoid network calls in unit tests
- avoid credentials and environment reads
- avoid automatic tool registration
- avoid autonomous background execution
- preserve trace_id and correlation_id
- emit non-executable governance records only
- preserve deterministic-risk-gateway authority

## Safe Adaptation Targets

This project may safely define:

- agent orchestration plan contracts
- agent role assignment contracts
- agent handoff record contracts
- agent consensus record contracts
- swarm topology policy contracts
- agent federation policy contracts
- agent memory policy contracts
- MCP tool registration policy contracts
- background worker policy contracts
- agent cost budget policy contracts
- prompt injection review contracts

## Rejected Adaptation Targets

Rejected:

- direct dependency on the external repository
- vendoring source code
- runtime agent swarms
- MCP runtime activation
- cross-machine federation
- vector memory adoption
- background automation
- neural trading tools
- market data plugin runtime
- model or agent authority to trade

## Recommended Next Step

Review the orchestration governance contracts before considering any runtime agent framework.
