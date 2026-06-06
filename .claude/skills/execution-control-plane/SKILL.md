---
name: execution-control-plane
description: Use when working on the execution-engine. Accepts ONLY ApprovedOrder, idempotent, order state machine, kill-switch gated, no withdrawal, fail-closed LIVE (no live connector ships). Live arming is human-gated — never autonomous. No broker submission / credentials in the scaffold.
---

# Execution control plane (fail-closed)

> Bound by [`AGENTS.md`](../../../AGENTS.md). The execution-engine is the only
> service that may ever hold live broker credentials and the only one that executes
> — but ONLY an `ApprovedOrder`, never a raw `OrderIntent`. In the scaffold: **no
> broker submission, no live trading, no credentials, no live connector.**

## When to use
Working in `execution-engine`.

## Procedure
1. **Accept only ApprovedOrder** (reject raw OrderIntent / malformed / missing
   `trace_id`/`correlation_id`). Fail-closed.
2. **Idempotency** (key per order); **state machine** (SUBMITTED→ACK→PARTIAL_FILL→
   FILLED / REJECTED / CANCELLED → RECONCILED) with validated transitions.
3. **Kill-switch gate:** never execute when active. **No withdrawal** method.
4. **Connectors:** shadow (places nothing) + simulated (sandbox). **Ship NO live
   connector.** LIVE arming requires a **human approval record** + an
   operator-supplied real connector + confirmation — none ship here, by design.
5. **Emit** an `ExecutionReport` + audit events (the `audit-and-trace` skill); feed
   fills to the portfolio.

## Non-negotiables
- ApprovedOrder-only; no broker submission/credentials/live connector in scaffold.
- LIVE never auto; no withdrawal; never execute without trace/correlation ids.

## Definition of done
- ApprovedOrder-only + idempotency + state machine + fail-closed LIVE tests green;
  no shipped live connector; checks green.
