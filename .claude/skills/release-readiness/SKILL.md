---
name: release-readiness
description: Use to produce or update a readiness/architecture review consolidating platform state for human governance. Honest by construction — states what is proven, modelled, stubbed, and reserved for the human Live Gate. Never an approval to go live.
---

# Release readiness & governance review

> Bound by [`AGENTS.md`](../../../AGENTS.md). A readiness report consolidates state
> for review; it is NOT a live approval. Production is never implicit.

## When to use
Before a review milestone, or after meaningful change.

## Procedure
1. **Inventory honestly:** per-service status (implemented/tested vs placeholder),
   contracts, gates, checks. Verify the numbers (the `run-checks` skill).
2. **State the proven invariants** with evidence: Risk Gateway authority, no-look-
   ahead, monotone risk-reducing monitoring, tamper-evident audit, research-non-
   executable, backtest≠live, fail-closed execution, no secrets, agent-changes
   human-approved.
3. **Verdict by dimension** (architecture, governance, contracts, observability,
   security, test rigor) AND the two honest ones: **strategy edge — not established**;
   **live readiness — NOT APPROVED**.
4. **Caveats, no spin:** modelled (not market-validated) realism, any stubs, no live
   connector, research-only data. Negative findings are deliverables.
5. **Live Gate checklist:** the human-only steps (secret rotation, broker integration,
   approvals, capital limit, rollback). **The report does not constitute approval.**

## Non-negotiables
- Honest: never claim live readiness or a validated edge that isn't there.
- The report informs a human decision; it never grants live.

## Definition of done
- Readiness review refreshed with verified numbers + honest verdicts; checks green.
