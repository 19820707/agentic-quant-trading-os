# Local-First Agentic Quant Boundary

## Purpose

This document defines the local-first agent and tool boundary for research-stage work.

It does not approve agent runtime, MCP runtime, LLM provider runtime, exchange runtime, credentials, network access, shell access, file-write access, trading, risk approval, execution approval or production use.

## Allowed Records

Allowed records:

- agent skill definitions
- skill dependency declarations
- tool permission policies
- tool risk classifications
- tool call audit records
- loop guard policies
- hallucination review requirements

## Forbidden Authority

Forbidden authority:

- shell execution
- file writes
- network calls
- credential access
- broker or exchange access
- order creation
- risk approval
- execution approval
- autonomous deployment

## Default Policy

All skills and tools start disabled.

Any future activation requires:

- explicit review
- risk classification
- redaction review
- audit logging
- no credential exposure
- no direct path to broker, exchange, wallet or execution engine

## Loop Guard

Agentic loops must:

- cap repeated tool calls
- cap reasoning steps
- fail closed on repeated identical tool calls
- require hallucination review before final claims
- stop before any operational action

## Escalation Rule

Agent records may inform research and documentation.

They must not directly modify runtime systems, call networks, access credentials, create orders, approve risk or approve execution.
