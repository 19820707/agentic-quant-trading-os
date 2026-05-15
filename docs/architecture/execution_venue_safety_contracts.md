# Execution Venue Safety Contracts

This project can borrow useful operating patterns from LEAN, professional broker APIs, paper-trading platforms and connector-heavy systems without enabling broker connectivity.

The current implementation is contract-only. It does not install broker SDKs, open exchange clients, submit orders, read credentials or enable production trading.

## Purpose

The execution venue safety contracts define the minimum control plane that must exist before any broker, exchange or paper execution work can be promoted.

They capture four boundaries:

- `ExecutionVenueCapability`: what a venue adapter is allowed and forbidden to do.
- `BrokerAdapterSafetyPolicy`: safety rules for any future broker or exchange adapter.
- `PaperTradingSession`: explicit assumptions for local paper-mode sessions.
- `StrategyRuntimeApprovalGate`: promotion state for a strategy before it can leave research.

## Design Rules

The contracts preserve the platform rule:

```text
AI proposes.
Models predict.
Risk Gateway decides.
Execution Engine executes.
Audit proves.
Human governance supervises.
```

No model, signal, dashboard, notebook, agent or backtest may talk directly to a broker or exchange.

## Borrowed Patterns

The following mature platform patterns are useful:

- event-driven lifecycle separation from LEAN-style engines;
- order lifecycle state tracking from professional broker APIs;
- paper-mode separation from platforms such as Alpaca;
- connector capability mapping from Hummingbot-like systems;
- operational dashboards and pause/resume concepts from commercial bot platforms.

This repository only adopts the governance contracts. It does not copy external repositories or integrate their runtime code.

## Current Allowed State

- static fixtures;
- fake/in-memory adapters;
- read-only contract review;
- paper-mode contract definition;
- fail-closed strategy runtime gates.

## Current Forbidden State

- broker credentials;
- exchange credentials;
- private endpoints;
- direct model-to-broker paths;
- direct dashboard-to-broker paths;
- direct agent-to-broker paths;
- raw `OrderIntent` execution;
- order submission;
- order cancellation;
- transfer;
- withdrawal;
- position mutation;
- production trading.

## Promotion Requirements

Before any future venue or broker adapter may advance, a separate reviewed PR must prove:

- venue capability is documented;
- broker adapter safety policy exists;
- strategy runtime gate remains fail-closed by default;
- paper session assumptions are explicit;
- deterministic risk gateway is mandatory;
- `ApprovedOrder` is the only acceptable pre-execution input;
- `ExecutionReport` and `AuditEvent` are required;
- idempotency and kill switch requirements are documented;
- no credentials are introduced;
- no network tests are introduced.

## Non-Goals

This document does not approve:

- real broker integration;
- real exchange integration;
- live market connectivity;
- order execution;
- dependency installation;
- secrets or credentials;
- production deployment.
