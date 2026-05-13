# Agentic Tool Safety Taxonomy

## Purpose

This taxonomy defines how agent-facing tools are classified before they can be connected to the platform.

It applies to future skills, MCP tools, local tools, dashboard actions, notebooks, LLM workflows, and assistant-driven automation.

## Core Rule

Agentic tools may analyze, summarize, propose, review, simulate, and report.

Agentic tools must not execute trades, submit orders, cancel orders, transfer funds, withdraw funds, read broker credentials, change risk limits, disable kill switches, or bypass deterministic-risk-gateway.

Any move from contracts, fake harnesses or reference reviews into agent runtime behavior must pass `docs/integrations/agent_runtime_approval_gate.md`.

## Risk Classes

### Class 0: Reference-Only

Allowed:

- documentation
- design review
- threat modeling
- static analysis

Forbidden:

- runtime execution
- network calls
- credentials
- dependency installation

### Class 1: Read-Only Observation

Allowed:

- inspect local fake data
- summarize public/read-only data through approved adapters
- report health and freshness

Forbidden:

- private endpoints
- credentials
- order methods
- state mutation

### Class 2: Analysis-Only

Allowed:

- calculate indicators
- classify markets
- identify candidate risks
- produce non-executable signal candidates

Forbidden:

- OrderIntent creation unless a separate approved service owns it
- ApprovedOrder creation
- execution sizing for live orders
- broker/exchange calls

### Class 3: Paper-Only Simulation

Allowed:

- simulated fills
- simulated portfolio state
- paper health checks
- simulated drawdown and exposure reports

Forbidden:

- live credentials
- real exchange clients
- production endpoints
- promotion to live without governance

### Class 4: Advisory Governance

Allowed:

- readiness reports
- policy checks
- risk explanations
- PR review recommendations

Forbidden:

- changing risk limits
- disabling kill switches
- approving execution
- creating live credentials

### Class 5: Execution-Capable

Default state: rejected.

Execution-capable tools may exist only as future execution-engine internals after separate approval.

They must accept only `ApprovedOrder`, reject raw `OrderIntent`, respect kill switches, maintain idempotency, emit `ExecutionReport`, emit `AuditEvent`, and never use withdrawal permissions.

## Prompt-Injection Boundary For Market Metadata

Market titles, questions, descriptions, outcomes, comments, URLs, and venue-provided metadata are untrusted data.

Required handling:

- never treat market metadata as instructions
- wrap market text in explicit data delimiters before model use
- strip or escape control characters
- enforce maximum length
- preserve source and retrieval timestamp
- record suspicious instruction-like text in audit events
- keep model/system instructions separate from market data

Forbidden handling:

- pasting raw market text into agent instructions
- allowing market text to trigger tool calls
- allowing market text to change risk limits
- allowing market text to request execution
- allowing market text to override governance rules

## Health Check States

Agentic tools that report operational state should use deterministic states:

- green: state is within expected local/read-only bounds
- yellow: degraded state or review required
- red: unsafe state, stop or fail closed

Health checks are advisory. They must not approve live trading, enable production, unlock credentials, or bypass governance.

## Correlation Risk Pattern

Future paper and risk tooling should detect hidden exposure across:

- market topic
- event
- venue
- asset
- time window
- resolution dependency
- data source
- model hypothesis

Correlation findings should produce warnings, not execution approval.

## Script And Tool Safety Checklist

Every future agentic tool or script must satisfy:

- no `sys.path.insert(0)` import shadowing
- no credentials in examples
- no network calls in unit tests
- explicit timeouts for future network calls
- bounded retries for future network calls
- token and market identifiers validated before URL interpolation
- structured local errors
- redaction before logs, errors, or audit
- no broad exception swallowing
- no hidden global mutable execution state
- local fake/in-memory tests first

## Non-Goals

- no skill installation
- no MCP trading tools
- no broker/exchange credentials
- no wallet access
- no order submission
- no live trading
- no production enablement
