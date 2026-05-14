# Critical Control Loop Mapping

## Purpose

This document maps the Apollo-style autonomous-system loop into this trading platform without adopting Apollo runtime code.

The goal is to preserve a safety-critical separation between observation, prediction, planning, deterministic control and execution.

## Reference Loop

```text
Autonomous driving reference:
Perception -> Prediction -> Planning -> Control -> Vehicle

Trading platform mapping:
Market observations -> Forecasts -> Signal and intent planning -> Deterministic risk control -> Execution boundary
```

## Trading Control Loop

| Reference stage | Trading stage | Allowed output | Forbidden output |
| --- | --- | --- | --- |
| Perception | Market data and research observation | validated observations, lineage, quality flags | trading decision |
| Prediction | Forecasting and regime estimation | probability estimates, confidence, uncertainty | order intent, risk decision |
| Planning | Signal and intent planning | signal candidate, draft order intent | execution approval |
| Control | Deterministic risk gateway | reject, resize, require review, future approved order | risk bypass |
| Actuation | Execution engine boundary | future execution report after approval | direct model or agent execution |
| Monitor | Observability and audit | metrics, alerts, audit events | hidden state mutation |
| Replay | Scenario and incident replay | reproducible evidence | production permission |

## Non-Negotiable Separation

- Prediction cannot approve risk.
- Signal generation cannot execute.
- OrderIntent is not executable.
- Deterministic-risk-gateway remains the final pre-trade authority.
- Execution engine must reject raw signals and raw order intents.
- Agentic tools, dashboards and notebooks cannot call brokers or exchanges.
- Backtest and replay evidence cannot grant production permission.

## Scenario Discipline

Future scenario contracts should classify conditions before behavior changes:

- stale market data
- high volatility
- low liquidity
- model drift
- news shock
- market halt
- funding dislocation
- correlation break
- drawdown breach
- kill-switch condition

## Guardian Discipline

Guardian-style policies should remain deterministic and auditable:

- stale data guardian
- drift guardian
- liquidity guardian
- exposure guardian
- kill-switch guardian
- audit guardian

## Replay Discipline

Any future promotion toward paper or production-adjacent behavior requires replayable evidence:

- input snapshot
- contract payloads
- risk decision
- audit event chain
- expected failure behavior
- rollback path

## Runtime Boundary

This document does not approve Apollo runtime, Cyber RT, vehicle-control logic, real market-data runtime, broker integration, credentials, network calls, trading execution or production enablement.
