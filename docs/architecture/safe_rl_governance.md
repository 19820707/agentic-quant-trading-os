# Safe RL Governance

## Purpose

Safe RL governance defines how future reinforcement-learning or policy-learning research may be described without enabling policy execution.

This document adopts safety-layer, constraint-first and recovery-policy concepts from trusted RL research while keeping all behavior contract-only.

## Policy Boundary

An RL policy may only propose research actions. It must not:

- create executable orders
- create `ApprovedOrder`
- approve risk
- approve execution
- access credentials
- call private endpoints
- bypass deterministic-risk-gateway
- mutate portfolio state

## Required Safety Layer

Every future RL policy must declare:

- allowed action space
- forbidden action space
- deterministic constraints
- safety layer requirement
- deterministic-risk-gateway requirement
- audit requirement
- fail-closed behavior

## Constraint Categories

Required constraint categories include:

- notional limit
- position limit
- exposure limit
- drawdown limit
- stale data block
- liquidity limit
- slippage limit
- kill-switch block
- credential access block
- risk-gateway bypass block

## Recovery Policy

Recovery decisions are governance records, not executable instructions.

Allowed recovery decision values:

- `FREEZE_POLICY`
- `REDUCE_EXPOSURE_SIMULATED`
- `REQUIRE_MANUAL_REVIEW`
- `REVERT_TO_BASELINE`
- `PAPER_ONLY`

## Zero-Violation Target

The project target is zero unauthorized execution:

- zero risk-gateway bypass
- zero credential access
- zero private endpoint use
- zero raw policy execution
- zero unapproved order

## Runtime Boundary

This document does not approve RL frameworks, training loops, simulators, policy checkpoints, multi-agent RL runtime, live policy execution, broker access, credentials, risk approval, execution approval or production deployment.
