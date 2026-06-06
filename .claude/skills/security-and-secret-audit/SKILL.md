---
name: security-and-secret-audit
description: Use when reviewing or changing anything touching secrets, credentials, redaction, or the fail-closed posture. Run the secret-artifact audit; only the execution-engine may ever hold live broker credentials (never withdrawal). Secret rotation and go-live are human-only.
---

# Security & secret-artifact audit

> Bound by [`AGENTS.md`](../../../AGENTS.md). Secrets are never committed, logged,
> traced, exposed to agents/dashboards/prompts, or passed to model/MCP tools. Only
> the execution-engine may ever hold live broker credentials (never withdrawal).

## When to use
Any change near credentials, env access, connectors, redaction, logging, or trust
boundaries; or a periodic posture review.

## Procedure
1. **Run the audits:** `python scripts/secret_artifact_audit.py` (and
   `make scaffold-check`) — no hardcoded secrets, no credential env reads in service
   code, no network/broker imports in `app/`, safe placeholders only.
2. **Redaction:** ensure logs/traces/reports redact secret-like values; payloads
   carry secret **references** only, never values. Fixtures contain no real broker
   identifiers.
3. **Fail-closed:** unknown/missing inputs ⇒ safer behaviour; the execution-engine
   ships no live connector; LIVE arming needs a human approval record.
4. **If a real secret is found committed:** treat as compromised — flag for
   immediate human rotation/revocation. **Do not** rotate or touch live keys yourself.

## Non-negotiables
- Never read, print, log, move, or commit secrets; mask in reports (first 4 + last 3).
- Secret rotation and go-live are **human** actions, never an agent's.

## Definition of done
- `secret_artifact_audit` + scaffold-check clean; redaction verified; fail-closed
  preserved; checks green.
