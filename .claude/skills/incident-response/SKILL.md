---
name: incident-response
description: Use when something is wrong — a tripped kill switch, a failed audit verify, a red check/gate, a prompt-injection hit, or anomalous agent behaviour. Stabilise first, fail closed, never auto-remediate destructively, escalate human-gated actions.
---

# Incident response (stabilise first, fail closed)

> Bound by [`AGENTS.md`](../../../AGENTS.md). Under uncertainty choose the safer
> option; production-impacting fixes need human approval.

## When to use
A kill switch is active, audit verify fails (tamper), a check/gate is red, a
prompt-injection is detected, or agent behaviour is anomalous.

## Procedure
1. **Stabilise:** confirm a safe state (default no-execution; LIVE disarmed; kill
   switch keeps execution halted). Do NOT re-arm or override to "restore flow".
2. **Diagnose with evidence:** error + file + line + failed invariant + blast radius.
   Distinguish evidence / inference / decision.
3. **Audit-first:** if audit verify fails, treat history as compromised — surface it,
   never "repair" the append-only log. Reconstruct the chain to scope impact.
4. **Fail closed:** unknown model health or stale data ⇒ reduce risk; never widen
   limits to keep trading.
5. **Escalate human-gated actions:** secret rotation, going/staying live, broker
   changes, destructive remediation, merging an agent patch to a critical surface —
   all **human** decisions. Record the incident (append-only).

## Non-negotiables
- Never auto-remediate destructively; never bypass the Risk Gateway to restore flow.
- Never touch secrets/live keys; never silently rewrite audit history.

## Definition of done
- System confirmed safe; honest diagnosis recorded; human-gated actions escalated,
  not taken.
