# External Adapter Safety Policy

## 1. Purpose

External repositories are integrated through governed adapters. No external code is trusted by default, and no external project enters the core system directly.

The adapter boundary protects the critical system by forcing each integration through documented review, internal contracts, local tests and CI gates before implementation.

This policy applies to:

- market data adapters
- feature store adapters
- model monitoring adapters
- observability adapters
- security adapters
- paper trading adapters
- future execution adapters

## 2. Integration Lifecycle

Every external integration must follow this lifecycle:

1. Catalog the external project.
2. Review license, security posture and maintenance status.
3. Define the internal contract or interface.
4. Create the adapter interface.
5. Write local tests.
6. Add CI coverage.
7. Implement read-only first where possible.
8. Promote only after review.

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

## 4. Market Data Adapter Rules

Market data adapters are read-only only.

They may fetch:

- OHLCV bars
- trades
- order book snapshots
- funding rates
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

## 5. Paper Trading Adapter Rules

Paper trading adapters provide simulated execution only.

They must follow these rules:

- no live broker credentials
- no real order submission
- clear separation from execution-engine
- cannot promote to live trading
- cannot bypass deterministic-risk-gateway

## 6. Future Execution Adapter Rules

Future execution adapters may exist only inside execution-engine.

They must:

- accept only ApprovedOrder
- reject raw OrderIntent
- respect kill switch state
- enforce idempotency
- emit ExecutionReport
- emit AuditEvent
- never use withdrawal permissions
- never bypass deterministic-risk-gateway

## 7. MCP / Agentic Adapter Rules

MCP tools and agentic adapters must follow these rules:

- MCP tools cannot access broker credentials
- MCP tools cannot execute trades
- MCP tools cannot change risk limits
- MCP tools may only analyze, summarize, propose or report
- agentic adapters cannot approve execution
- agentic adapters cannot bypass deterministic-risk-gateway

## 8. Prohibited Names and Behaviors

Future non-execution adapters must not expose methods named:

- buy
- sell
- order
- create_order
- submit_order
- cancel_order
- withdraw
- transfer
- execute
- place_order

Future non-execution adapters must not implement order submission, order cancellation, fund movement, execution approval, risk approval or live trading behavior.

## 9. Required Review Checklist

Before any external adapter is merged, reviewers must confirm:

- safety boundary documented
- tests local-only
- credentials absent
- network behavior explicit
- no dangerous methods
- redaction used for errors
- CI passes
- AGENTS.md followed
