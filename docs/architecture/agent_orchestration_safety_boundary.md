# Agent Orchestration Safety Boundary

## Purpose

This document defines the safety boundary for future agent orchestration work.

It does not approve agent runtime, MCP runtime, swarm runtime, federation, memory databases, background workers, network access, credentials, trading, risk approval, execution approval or production use.

## Allowed Governance Records

Allowed records:

- agent orchestration plans
- agent role assignments
- agent handoff records
- agent consensus records
- swarm topology policies
- federation policies
- memory policies
- MCP tool registration policies
- background worker policies
- cost budget policies
- prompt injection reviews

## Forbidden Runtime Authority

Forbidden authority:

- autonomous agent execution
- automatic MCP registration
- background task scheduling
- cross-machine federation
- remote agents
- external memory systems
- browser automation
- market data plugin runtime
- neural trading runtime
- credential access
- broker or exchange access
- trading decisions
- risk approval
- execution approval

## Default State

Every agentic capability starts disabled.

Default flags:

- network access: false
- credentials: false
- autonomous execution: false
- federation: false
- memory runtime: false
- MCP runtime: false
- trading: false
- production: false

## Escalation Rule

Any future move from documentation/contracts to runtime requires a separate approval PR, security review, dependency review, no-secrets review, no-network unit tests and deterministic-risk-gateway boundary review.

Agent orchestration records may coordinate research only. They must never directly create orders, approve risk, approve execution or access broker or exchange systems.
