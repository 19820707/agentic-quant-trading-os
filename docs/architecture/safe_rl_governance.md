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

## Policy Evaluation

Safe policy evaluation reports are evidence records, not promotion approvals.

Every report must preserve:

- policy identity and version
- evaluation dataset identity
- scenario set identity
- calibration and loss metrics
- drawdown and CVaR-style risk estimates
- uncertainty estimate and coverage
- zero unauthorized execution evidence
- zero credential access evidence
- zero deterministic-risk-gateway bypass evidence

Evaluation reports must keep `approved_for_promotion`, `network_allowed`,
`credentials_allowed`, `policy_execution_allowed`, `risk_approval_allowed`,
`execution_allowed` and `production_enabled` false.

## Scenario Stress Tests

Scenario stress reports document how a future policy behaved under synthetic
market regimes such as liquidity shock, volatility spike, crash, stale data or
spread widening.

Stress reports must remain local and synthetic. They must not call markets,
load real exchange clients, read credentials or produce executable actions.
Failure must be blocked and routed to manual review.

## Promotion Gate

Policy promotion gates block learned policies by default.

Promotion gates may list required evidence and required approvals, but they do
not approve dependencies, training runtimes, network access, credential access,
risk approval, execution approval, paper trading, live trading or production
deployment.

## Zero-Violation Target

The project target is zero unauthorized execution:

- zero risk-gateway bypass
- zero credential access
- zero private endpoint use
- zero raw policy execution
- zero unapproved order

## Runtime Boundary

This document does not approve RL frameworks, training loops, simulators, policy checkpoints, multi-agent RL runtime, live policy execution, broker access, credentials, risk approval, execution approval or production deployment.
