---
name: agent-orchestration-and-swarm
description: Use to define how multiple agents coordinate — role assignment, delegation, consensus, conflict resolution, federation, memory coordination, cost optimization, workload balancing, escalation. Fail-closed; unsafe consensus is blocked. Coordination only — no agent gains execution authority or broker credentials.
category: governance
---

# Agent orchestration & swarm

> Governance skill, bound by [`AGENTS.md`](../../../../AGENTS.md). Orchestration
> coordinates *proposers*; it grants no execution authority and bypasses nothing.

## Capabilities

```
capabilities:
  role_assignment
  delegation
  consensus
  conflict_resolution
  federation
  memory_coordination
  cost_optimization
  workload_balancing
  escalation_management
```

## Safety modes (mandatory)

```
fail_mode        = fail_closed     # any unsafe/unknown state halts, never escalates
unsafe_consensus = block           # consensus reached under unsafe conditions is blocked
```

## Contract mapping
`agent_orchestration_plan`, `agent_role_assignment`, `agent_consensus_record`,
`agent_handoff_record`, `agent_federation_policy`, `agent_cost_budget_policy`,
`agent_memory_policy`, `swarm_topology_policy`, `background_worker_policy` — each
contract-shaped with explicit bounds and lineage.

## Discipline
- Roles are research / analysis / review — never execution or approval.
- Bounds (cost, memory, fan-out, background work) are **fail-closed**: exceeding a
  bound halts. Consensus is invalid if any participant is in an unsafe state.
- Conflict resolution and escalation route to a human for critical decisions.

## Non-negotiables
- Coordination only; agents stay proposers. `fail_mode = fail_closed`;
  `unsafe_consensus = block`.
- No execution authority, no broker credentials, no Risk-Gateway bypass.

## Definition of done
- Policies contract-conformant with explicit bounds + fail-closed modes; no
  authority leakage; checks green.
