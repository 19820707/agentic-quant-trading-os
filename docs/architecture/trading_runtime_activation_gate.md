# Trading Runtime Activation Gate

`TradingRuntimeActivationGate` is a contract-first control-plane guard for any future transition from scaffold/research-only work toward backtesting, paper trading, controlled live trading or production operation.

The current state is fail-closed.

## Current Decision

- Backtest runtime is not enabled.
- Paper trading runtime is not enabled.
- Live trading is not enabled.
- Production is not enabled.
- Market data ingestion is not enabled.
- Webhook ingestion is not enabled.
- Signal ingestion is not enabled.
- Broker SDKs are not enabled.
- Exchange SDKs are not enabled.
- Network access is not enabled.
- Credentials are not enabled.
- Order submission is not enabled.
- Order cancellation is not enabled.
- Withdrawal and transfer are not enabled.
- Model training runtime is not enabled.
- Feature store runtime is not enabled.

## Mandatory Boundary

Every future execution path must preserve:

```text
SignalCandidate
  -> RiskReviewInput
  -> OrderIntent
  -> deterministic-risk-gateway
  -> ApprovedOrder
  -> execution-engine
  -> ExecutionReport
  -> AuditEvent
```

Forbidden direct paths:

- signal to broker or exchange;
- LLM to broker or exchange;
- model to broker or exchange;
- dashboard to broker or exchange;
- notebook to broker or exchange;
- agent to broker or exchange;
- backtest to broker or exchange.

## Required Evidence Before Runtime Promotion

Runtime promotion requires separate reviewed contracts or policies for:

- dataset lineage;
- leakage review;
- feature store gate;
- fake offline materialization review;
- backtest review;
- paper trading review;
- broker adapter safety policy;
- execution venue capability;
- credential vault policy;
- kill switch policy;
- audit event policy;
- human approval record.

## Non-Goals

This gate does not implement:

- exchange adapters;
- broker adapters;
- market data ingestion;
- WebSocket clients;
- backtest engine;
- paper trading engine;
- live trading;
- model training;
- feature store runtime;
- API control plane endpoints;
- credentials or secrets.
