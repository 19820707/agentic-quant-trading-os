---
name: audit-and-trace
description: Use when emitting audit events or reconstructing the end-to-end identity chain. The audit log is append-only and tamper-evident; history must never be silently modified. Carries the full research→trading chain.
---

# Append-only audit & end-to-end trace

> Bound by [`AGENTS.md`](../../../AGENTS.md). Every critical event is auditable; the
> audit is append-only and tamper-evident; history must never be silently modified.

## When to use
Working in `observability-audit-service`; emitting `audit/audit_event`.

## Procedure
1. **Emit a contract-shaped `audit_event`** carrying the relevant identity ids from
   the full chain — `research_dossier_id`, `hypothesis_id`, `analyst_report_id`,
   `debate_transcript_id`, `probability_estimate_id`, `signal_candidate_id`,
   `risk_review_input_id`, `order_intent_id`, `risk_decision_id`, `approved_order_id`,
   `execution_order_id`, `fill_id` — plus `trace_id`/`correlation_id`/`schema_version`.
2. **Append only:** never add an update/delete API; reads return copies.
3. **Tamper-evidence:** a verify step must detect any modify/reorder/delete. Surface
   a failed verify as a critical incident (the `incident-response` skill).
4. **Trace:** reconstruct the chain from recorded events for end-to-end provenance.

## Non-negotiables
- Append-only; tamper must be detectable; the audit service has no trade authority.
- Audit is on the critical path for live — if it cannot record, live must not proceed.

## Definition of done
- Events contract-conformant with chain ids; tamper-evidence proven; checks green.
