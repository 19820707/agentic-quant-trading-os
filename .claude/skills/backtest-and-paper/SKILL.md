---
name: backtest-and-paper
description: Use when backtesting or paper-trading a strategy. Enforces no look-ahead, transaction costs + slippage + spread, risk-gateway replay (the real Gateway adjudicates every order), and that approval promotes to PAPER only — never live.
---

# Backtest / paper (research-only; paper-only promotion)

> Bound by [`AGENTS.md`](../../../AGENTS.md). Backtest realism + risk replay;
> **backtest approval never grants live — it promotes to paper only.** Paper is an
> isolated sandbox; fills are always simulated.

## When to use
Working in `backtesting-engine` or `paper-trading-engine`.

## Procedure
1. **Backtest:** no look-ahead (decisions use only past data; fills on the next bar);
   costs always on (fee + slippage + half-spread, adverse); **risk-gateway replay**
   — inject the real Risk Gateway; it adjudicates every order with evolving state;
   honour RESIZE/REJECT.
2. **Paper-readiness report:** `live_ready` is always False; require costs/slippage/
   spread enabled + risk replay passed + execution quality acceptable.
3. **Backtest gate** → promotes to **paper only**.
4. **Paper:** accept **only ApprovedOrder** (reject raw OrderIntent), idempotent,
   paper fills always simulated; the paper gate ties monitoring-clean + divergence
   vs backtest → live *candidate* only (the human Live Gate is separate).

## Non-negotiables
- No look-ahead; costs always applied; every order through the Risk Gateway.
- **Backtest/paper never grant live**; `live_ready` is structurally False.
- Public/no-auth data only; no broker, no credentials.

## Definition of done
- Honest stats + paper-readiness report; gate decisions contract-conformant; checks green.
