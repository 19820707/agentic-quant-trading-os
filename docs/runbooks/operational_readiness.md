# Operational Readiness Runbook

Current status: scaffold only. No service is production-ready or live-trading-ready.

## Purpose

This runbook defines the minimum operational readiness evidence expected before any future service becomes production-facing.

## Readiness Checklist

- Owner identified.
- Service boundary documented.
- Dependencies documented.
- Health and readiness checks defined.
- Configuration validated.
- Secrets model reviewed.
- Logs, metrics and traces defined.
- Alerts defined.
- Failure modes documented.
- Rollback procedure documented.
- Incident response path documented.
- Tests mapped to risk level.

## Service Readiness Levels

Use these levels to prevent premature production claims:

| Level | Meaning | Allowed use |
| --- | --- | --- |
| SRL-0 | Placeholder only | Documentation and scaffold checks |
| SRL-1 | Local deterministic behavior | Unit and contract tests |
| SRL-2 | Integrated non-live workflow | Integration and replay tests |
| SRL-3 | Paper-only workflow | Paper trading with isolated credentials or no credentials |
| SRL-4 | Controlled-live candidate | Requires all live gates and explicit approvals |

Current scaffold services are SRL-0.

## Minimum Operational Signals

Future production-facing services should expose:

- health state
- readiness state
- dependency state
- config version
- contract version
- build version
- error count
- latency distribution
- queue depth where relevant
- data freshness where relevant

These signals must not expose secrets or regulated data.

## Live-Capable Additional Checks

For any future live-capable path:

- Risk Gateway cannot be bypassed.
- Execution Engine accepts only `ApprovedOrder`.
- Kill switches are tested.
- Reconciliation is tested.
- Audit events are append-only.
- Broker credentials are isolated to approved execution-engine adapters.
- Manual rollback plan exists.
- Capital limits are explicitly approved.

## Default Incident Posture

When uncertain, pause, reject, reduce or require manual approval. Do not continue operating aggressively under unknown risk state.

## Stop And Escalate

Stop and require explicit human instruction if:

- Risk Gateway behavior is unclear.
- Audit events are missing.
- Credential isolation is uncertain.
- Kill switch state is unknown.
- Reconciliation diverges.
- Model health is unknown in a trading-impacting path.
