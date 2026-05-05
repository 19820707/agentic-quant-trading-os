# Runbook Template

## Purpose

What operational situation does this runbook handle?

## Scope

In scope:

- 

Out of scope:

- live broker actions unless explicitly approved
- credential handling unless explicitly approved
- bypassing the Risk Gateway

## Signals

- Health:
- Readiness:
- Logs:
- Metrics:
- Traces:
- Audit events:

## Safe First Response

When uncertain, pause, reject, reduce or require manual approval.

## Procedure

1. Confirm service and environment.
2. Check health and readiness.
3. Check recent audit events.
4. Identify impact.
5. Apply only documented safe action.
6. Record outcome.

## Escalation

Escalate if:

- Risk Gateway state is unclear.
- Audit trail is missing.
- Credential exposure is suspected.
- Kill switch state is unknown.
- Reconciliation diverges.

## Rollback

Describe the rollback path, owner and validation.

## Evidence

Record:

- time
- actor
- service
- environment
- trace_id or correlation_id where relevant
- decision
- result

