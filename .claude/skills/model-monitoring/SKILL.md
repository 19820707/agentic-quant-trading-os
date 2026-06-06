---
name: model-monitoring
description: Use when working on model monitoring / drift detection. Degraded or unknown model health must REDUCE risk, never increase it (monotone). Monitoring alerts the Risk Gateway; it never executes or changes limits.
---

# Model monitoring (drift → risk-reducing alerts)

> Bound by [`AGENTS.md`](../../../AGENTS.md). Low confidence, drift, degraded or
> anomalous behaviour must reduce risk. Unknown health ⇒ conservative.

## When to use
Working in `model-monitoring-service`.

## Procedure
1. **Compare** live realised performance vs the drift baseline (mean/std) — a
   standardized shortfall.
2. **Classify** health: HEALTHY / DEGRADED / CRITICAL / **UNKNOWN** (insufficient
   data ⇒ UNKNOWN, treated conservatively).
3. **Map to a risk-REDUCING action only:** HEALTHY→none, UNKNOWN/DEGRADED→reduce,
   CRITICAL→halt. The action vocabulary has **no** risk-increasing value.
4. **Alert the Risk Gateway** (the Gateway decides; monitoring never changes limits
   or executes). Prove monotonicity: worse performance ⇒ same-or-stricter action.

## Non-negotiables
- Worse/unknown health ⇒ same-or-stricter action; monitoring NEVER loosens risk.
- It recommends; the Risk Gateway decides.

## Definition of done
- Classification + monotone-invariant + alert tests green; checks green.
