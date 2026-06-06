---
name: agent-orchestration-and-swarm
description: Use when defining how multiple agents coordinate — orchestration plans, role assignments, consensus, handoffs, federation, cost budgets, memory and swarm-topology policies. Coordination only; no agent gains execution authority or broker credentials.
---

# Agent orchestration & swarm policies

> Bound by [`AGENTS.md`](../../../AGENTS.md). Orchestration coordinates *proposers*.
> No orchestration grants execution authority, bypasses the Risk Gateway, or hands
> credentials to an agent.

## When to use
Working with the `research` policy contracts: `agent_orchestration_plan`,
`agent_role_assignment`, `agent_consensus_record`, `agent_handoff_record`,
`agent_federation_policy`, `agent_cost_budget_policy`, `agent_memory_policy`,
`swarm_topology_policy`, `background_worker_policy`.

## Procedure
1. **Plan + roles:** `agent_orchestration_plan` + `agent_role_assignment` define who
   does what; roles are research/analysis/review — never execution/approval.
2. **Consensus + handoff:** `agent_consensus_record` and `agent_handoff_record`
   preserve lineage and disagreement; low consensus de-risks downstream.
3. **Bounds (fail-closed):** `agent_cost_budget_policy` caps spend; `agent_memory_policy`
   bounds retention; `swarm_topology_policy` / `agent_federation_policy` bound fan-out;
   `background_worker_policy` bounds autonomous background work. Exceeding a bound
   halts, never escalates.
4. **No authority leakage:** an orchestrated agent never executes trades, approves
   risk/live, alters critical limits, disables kill switches, or receives broker
   credentials.

## Non-negotiables
- Coordination only; agents stay proposers. Bounds are fail-closed.
- No execution authority, no broker credentials, no Risk-Gateway bypass.

## Definition of done
- Policies are contract-conformant with explicit bounds; no authority leakage; checks green.
