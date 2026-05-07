# External Adapter Safety Policy

## 1. Purpose

External repositories are integrated through governed adapters. No external code is trusted by default, and no external project enters the core system directly.

The adapter boundary protects the critical system by forcing each integration through documented review, internal contracts, local tests and CI gates before implementation.

The reusable [External Adapter Review Checklist](../integrations/external_adapter_review_checklist.md) must be completed before implementing any external adapter.

This policy applies to:

- market data adapters
- feature store adapters
- model monitoring adapters
- observability adapters
- security adapters
- paper trading adapters
- future execution adapters
- MCP / agentic adapters

External integrations must never bypass internal contracts.

## 2. Integration Lifecycle

Every external integration must follow this lifecycle:

External project identified
-> catalog entry created
-> license/security/maintenance review
-> internal contract selected or created
-> adapter interface defined
-> local fake/in-memory tests
-> CI coverage
-> read-only implementation first where possible
-> review
-> promotion

## 3. Universal Adapter Rules

All adapters must follow these rules:

- no credentials by default
- no secrets in logs, errors, audit events or reports
- no network calls in unit tests
- no external repo vendoring
- no Git submodule without explicit approval
- no hidden side effects
- no global mutable unsafe state
- explicit failure modes
- structured errors
- redaction before reporting errors
- local-only tests by default
- no bypassing deterministic-risk-gateway
- no broker/exchange credentials outside approved execution-engine adapters

## 4. Market Data Adapter Rules

Market data adapters are read-only only.

They may fetch:

- OHLCV bars
- trades
- order book snapshots
- funding rates
- open interest
- news
- market calendars
- economic calendars

They must not:

- create OrderIntent
- create ApprovedOrder
- access trade credentials
- submit orders
- cancel orders
- modify orders
- withdraw funds
- transfer funds

## 5. Feature Store Adapter Rules

Feature store adapters must preserve point-in-time correctness.

They must:

- preserve event_timestamp
- preserve created_timestamp
- preserve available_timestamp
- prevent future data leakage into training datasets
- version dataset snapshots
- support leakage audit workflows
- avoid broker credentials

## 6. Model Monitoring Adapter Rules

Model monitoring adapters may report model health, but they are not execution controls.

They may:

- report drift
- report anomalies
- report degradation
- produce monitoring alerts
- inform Risk Gateway inputs

They must not:

- directly change execution state
- directly place orders
- override deterministic risk checks

## 7. Paper Trading Adapter Rules

Paper trading adapters provide simulated execution only.

They must follow these rules:

- no live broker credentials
- no real order submission
- clear separation from execution-engine
- cannot promote to live trading
- cannot promote strategy to live trading
- cannot bypass governance gates

## 8. Future Execution Adapter Rules

Future execution adapters may exist only inside execution-engine.

They must:

- accept only ApprovedOrder
- reject raw OrderIntent
- respect kill switch state
- enforce idempotency
- maintain order state machine
- emit ExecutionReport
- emit AuditEvent
- never use withdrawal permissions
- never bypass deterministic-risk-gateway

## 9. MCP / Agentic Adapter Rules

MCP tools and agentic adapters must follow these rules:

- MCP tools cannot access broker credentials
- MCP tools cannot execute trades
- MCP tools cannot submit orders
- MCP tools cannot change risk limits
- MCP tools cannot disable kill switches
- MCP tools may only analyze, summarize, propose or report
- agentic adapters cannot approve execution
- agentic adapters cannot bypass deterministic-risk-gateway

## 10. Prohibited Names and Behaviors

Future non-execution adapters must not expose methods named:

- buy
- sell
- order
- create_order
- submit_order
- cancel_order
- modify_order
- withdraw
- transfer
- execute
- place_order

Future non-execution adapters must not implement order submission, order cancellation, fund movement, execution approval, risk approval or live trading behavior.

These names are only allowed in future execution-engine adapters after explicit approval, and even then only behind ApprovedOrder flow.

## 11. Required Review Checklist

Before any external adapter is merged, reviewers must confirm:

- external adapter review checklist completed
- safety boundary documented
- tests local-only
- credentials absent
- network behavior explicit
- no dangerous methods
- redaction used for errors
- CI passes
- AGENTS.md followed
- no bypass of deterministic-risk-gateway
- no broker credentials outside execution-engine
- no live trading behavior

## 12. Failure Posture

Adapters must fail closed under uncertainty.

If adapter safety is unclear:

- reject unsafe adapter behavior
- prefer read-only behavior
- prefer paper-only behavior
- disable the adapter until the safety boundary is clear
