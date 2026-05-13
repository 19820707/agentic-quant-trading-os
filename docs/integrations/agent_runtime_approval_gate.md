# Agent Runtime Approval Gate

## Purpose

This gate controls any future move from agentic research contracts, reference reviews, or fake graph harnesses into agent runtime behavior.

This document does not approve runtime agents, MCP servers, tool execution, background workers, federation, external memory, network access, credentials, broker access, exchange access, trading, risk approval, execution approval or production use.

## Current Decision State

agent_runtime_approved: false
mcp_runtime_allowed: false
tool_execution_allowed: false
background_worker_allowed: false
federation_allowed: false
external_memory_allowed: false
network_access_allowed: false
credentials_allowed: false
broker_access_allowed: false
exchange_access_allowed: false
trading_methods_allowed: false
risk_approval_allowed: false
execution_approval_allowed: false
production_use_allowed: false

## Scope

This gate applies to:

- LLM agents
- analyst agents
- research graph agents
- MCP tools
- local skills
- browser automation
- background workers
- memory or retrieval services
- federated agent systems
- tool registries
- autonomous review loops

## Required Evidence Before Runtime Approval

Before any future PR may enable agent runtime behavior, it must provide:

- explicit architecture review
- security review
- platform reliability review
- deterministic-risk-gateway boundary review
- prompt injection threat model
- tool capability matrix
- least privilege policy
- credential exposure review
- no-network unit tests
- fake/in-memory harness tests
- redaction tests for logs, errors and audit events
- rollback plan
- operator runbook
- CI pass
- scaffold audit pass
- secret and artifact audit pass

## Allowed Future Change After Separate Approval

Only after a separate approval PR changes the decision state, a future implementation may be considered for:

- local fail-closed agent runtime scaffolding
- local fake tool registry
- local fake memory adapter
- local no-network orchestration tests
- local permission evaluation
- local capability denial tests

That future work must remain disabled by default and must not access live systems.

## Explicitly Forbidden Without Separate Approval

Forbidden:

- installing agent runtime frameworks
- running MCP servers
- registering real tools
- enabling background schedules
- enabling browser automation
- enabling federation
- enabling external memory databases
- reading environment credentials
- using broker credentials
- using exchange credentials
- calling broker or exchange APIs
- submitting orders
- cancelling orders
- transferring funds
- withdrawing funds
- changing risk limits
- disabling kill switches
- approving risk
- approving execution
- production deployment

## Runtime Controls Required Before Any Enablement

Any future runtime must include:

- default disabled feature flag
- explicit approval-state check
- explicit capability allowlist
- explicit capability denylist
- network disabled by default
- credentials unavailable to agents
- deterministic timeout policy
- bounded retry policy
- structured local errors
- secret redaction
- audit events for configuration changes
- trace_id and correlation_id propagation
- deterministic-risk-gateway boundary enforcement
- kill-switch compatibility
- rollback procedure

## Approval Record

| Role | Status | Approver | Date | Notes |
| --- | --- | --- | --- | --- |
| Security | Pending | TBD | TBD | Runtime threat model required |
| Risk architecture | Pending | TBD | TBD | Must preserve deterministic-risk-gateway authority |
| Platform reliability | Pending | TBD | TBD | Must include rollback and runbook |
| Maintainer | Pending | TBD | TBD | Must confirm scope and ownership |
| CI impact | Pending | TBD | TBD | Must remain local and deterministic |

## Decision

Current decision: rejected by default / not approved.

Agent runtime work remains contract-only and documentation-only until this gate is explicitly changed in a separate reviewed PR.

## Non-Goals

- no agent runtime implementation
- no MCP server implementation
- no tool execution
- no external memory runtime
- no federation runtime
- no browser automation runtime
- no credentials
- no network access
- no trading
- no production enablement
