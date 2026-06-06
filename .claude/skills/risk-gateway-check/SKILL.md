---
name: risk-gateway-check
description: Use when adding or changing a deterministic pre-trade check in the deterministic-risk-gateway. It is the final pre-trade authority (APPROVE/REJECT/RESIZE/CANCEL_ALL/REQUIRE_MANUAL_APPROVAL). A RiskReviewInput is NOT a RiskDecision. Deterministic, fail-closed.
---

# Deterministic Risk Gateway check (final authority)

> Bound by [`AGENTS.md`](../../../AGENTS.md). The Risk Gateway is the **final
> pre-trade authority**; it emits the only executable object (`ApprovedOrder`). A
> `RiskReviewInput` (research) is **not** a `RiskDecision`.

## When to use
Working in `deterministic-risk-gateway`.

## Procedure
1. **Inputs are passed in, never read.** No clock, no I/O, no randomness —
   determinism is mandatory.
2. **Order, fail-closed:** kill switches → intent sanity (OrderIntent must be
   non-executable) → market-data integrity (stale ⇒ REJECT) → session/window →
   model health → size limits → manual-approval threshold.
3. **Size limits ⇒ RESIZE down only.** Compute binding headroom in notional terms,
   take the minimum, and floor the quantity so a resize can never exceed a limit.
4. **Unknown ⇒ safer:** missing/ambiguous data ⇒ REJECT or REQUIRE_MANUAL_APPROVAL,
   never a silent APPROVE.
5. **Emit** a `RiskDecision`; only on APPROVE/RESIZE emit an `ApprovedOrder`
   (contract-conformant). Deterministic tests for every verdict + the guard +
   same-inputs-same-output + resize-never-exceeds-limit.

## Non-negotiables
- The Gateway never creates alpha, accesses broker keys, or submits orders.
- ApprovedOrder only on APPROVE/RESIZE (fail-closed otherwise). Deterministic tests.

## Definition of done
- New check + deterministic tests; contract-conformant output; checks green.
