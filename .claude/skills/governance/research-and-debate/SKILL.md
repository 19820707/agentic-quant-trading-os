---
name: research-and-debate
description: Use for the multi-agent research/debate layer — dossiers, hypotheses, adversarial analysis, debate, probability estimation, and a SignalCandidate that feeds (never bypasses) the Risk Gateway. Produces ONLY structured knowledge; non-executable; cannot trigger changes or approve actions.
category: governance
---

# Research & debate (knowledge only; non-executable)

> Governance skill, bound by [`AGENTS.md`](../../../../AGENTS.md). It produces
> structured **knowledge** — never orders, changes, or approvals.

## Formal definition

```
input:
  dossier

pipeline:
  evidence_collection
  hypothesis_generation
  adversarial_analysis
  debate
  probability_estimation
  uncertainty_analysis
  signal_generation

output:
  signal_candidate
  confidence
  evidence_graph
  unresolved_questions

constraints:
  non_executable          # produces knowledge, never actions
  cannot_trigger_changes
  cannot_approve_actions
```

## Contract mapping (preserve lineage at each step)
`research_dossier → hypothesis_record → analyst_report → debate_transcript →
probability_estimate → signal_candidate (+ risk_review_input)`, carrying
`research_dossier_id → … → risk_review_input_id` + `trace_id`/`correlation_id`/
`schema_version`.

## Discipline
- Probabilities, not certainties; record `confidence`, the `evidence_graph`, and
  `unresolved_questions`. Disagreement / low confidence **de-risks** downstream.
- A `SignalCandidate` is **not** an `OrderIntent`; a `RiskReviewInput` is **not** a
  `RiskDecision`. Hand off only via contracts; the Risk Gateway remains sole authority.

## Non-negotiables
- Non-executable: it informs; it never decides, changes, executes, or approves.

## Definition of done
- Contract-conformant research artifacts with full lineage; only structured
  knowledge produced; checks green.
