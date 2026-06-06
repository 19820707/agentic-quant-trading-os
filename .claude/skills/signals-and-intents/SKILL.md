---
name: signals-and-intents
description: Use when turning a SignalCandidate into a normalized signal (signal-engine) or an OrderIntent (order-intent-service). A SignalCandidate is NOT an OrderIntent; an OrderIntent is NEVER executable and never sent to a broker. Sizing and approval belong to the Risk Gateway.
---

# SignalCandidate → signal → non-executable OrderIntent

> Bound by [`AGENTS.md`](../../../AGENTS.md). The signal-engine normalizes; the
> order-intent-service creates **non-executable** OrderIntents.

## When to use
Working in `signal-engine` or `order-intent-service`.

## Procedure
1. **Signal:** normalize a `SignalCandidate` / probability estimate into a signal
   (direction + strength). Conservative: below a confidence floor or within a
   deadband ⇒ FLAT. Preserve `signal_candidate_id` (identity chain). Do NOT size
   for execution.
2. **Intent:** map direction → side; FLAT ⇒ no intent. Set a **proposed** quantity
   (the Risk Gateway resizes). The OrderIntent is **non-executable** and must never
   be set executable or sent to a broker. Preserve the chain id.
3. **Distinctions:** a `SignalCandidate` is **not** an `OrderIntent`; only the Risk
   Gateway turns an intent into an `ApprovedOrder`.
4. **Hand to the Risk Gateway** — the sole pre-trade authority.

## Non-negotiables
- A signal is not an order; an OrderIntent is not executable and is never sent out.
- The signal/agentic layers never execute; only the Risk Gateway authorises.

## Definition of done
- Mapping + conservative-flat + non-executable + lineage tests green; checks green.
