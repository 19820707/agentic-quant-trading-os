---
name: portfolio-and-reporting
description: Use when tracking positions/exposure/P&L from fills (portfolio-service) or generating reports from audited data (reporting-engine). Read/aggregate only — never places orders, never executes, never touches credentials.
---

# Portfolio tracking & reporting (read-only)

> Bound by [`AGENTS.md`](../../../AGENTS.md). The portfolio-service tracks state from
> fills; the reporting-engine summarises audited data. Neither places orders,
> executes, nor accesses credentials.

## When to use
Working in `portfolio-service` or `reporting-engine`.

## Procedure
1. **Portfolio:** maintain signed positions with average cost, realized P&L on
   reductions/flips, and gross/net exposure + unrealized P&L + equity at given marks.
   Handle long, short, and flips correctly. Validate fills.
2. **Reporting:** performance report (equity/return/P&L/exposure/positions) and an
   audit-integrity report over the tamper-evident audit (verify() result, counts,
   chain). Read-only — never an action.
3. **Source of truth:** fills from execution/paper reports; integrity from the audit.
   Surface a failed audit verify() as a critical signal.

## Non-negotiables
- Read/aggregate only; never place orders, change risk, or execute.
- No credentials; deterministic, no I/O.

## Definition of done
- P&L (long/short/flip) + exposure + report + audit-integrity tests green; checks green.
