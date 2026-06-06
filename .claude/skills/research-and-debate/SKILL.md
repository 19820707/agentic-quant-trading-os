---
name: research-and-debate
description: Use when working on the multi-agent research/debate layer — research dossiers, hypotheses, analyst reports, debate transcripts, probability estimates, and the SignalCandidate / RiskReviewInput that feed (but never bypass) the Risk Gateway. Research outputs are non-executable.
---

# Research & debate (proposes — never executes)

> Bound by [`AGENTS.md`](../../../AGENTS.md). The research layer produces **evidence
> and probabilities**, not orders. Research contracts are **non-executable**.

## When to use
Working with the `research` contract domain:
`research_dossier`, `hypothesis_record`, `analyst_report`, `debate_transcript`,
`probability_estimate`, `signal_candidate`, `risk_review_input`.

## Procedure
1. **Flow (preserve lineage at each step):**
   `ResearchDossier → Hypothesis → AnalystReport → DebateTranscript →
   ProbabilityEstimate → SignalCandidate → RiskReviewInput`. Carry
   `research_dossier_id → … → risk_review_input_id` + `trace_id`/`correlation_id`/
   `schema_version`.
2. **Probabilities, not certainties:** estimates are probabilistic and auditable;
   low confidence / disagreement must reduce downstream risk, not increase it.
3. **Hard distinctions:** a `SignalCandidate` is **not** an `OrderIntent`; a
   `RiskReviewInput` is **not** a `RiskDecision`. Research never creates orders,
   never sizes for execution, never approves risk.
4. **Hand-off** to the trading lifecycle only via the documented contracts; the
   Risk Gateway remains the sole pre-trade authority.

## Non-negotiables
- Research outputs are non-executable; they inform, they never decide or execute.
- Disagreement/low-confidence is recorded and **de-risks** downstream.

## Definition of done
- Contract-conformant research artifacts with full lineage; distinctions preserved;
  checks green.
