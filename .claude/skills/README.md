# Project Skills — Agentic Quant Trading OS

Project-level skills (`.claude/skills/<name>/SKILL.md`) encoding the recurring
competencies of this platform, **aligned to its real contracts, identity chain and
tooling**. Every skill is bound by the root [`AGENTS.md`](../../AGENTS.md): AI
proposes, models predict, the Risk Gateway decides, execution executes, audit
proves, human governance supervises. No live trading, no broker, no credentials.

## Real identity chain (preserve end-to-end)

```
research_dossier_id → hypothesis_id → analyst_report_id → debate_transcript_id
   → probability_estimate_id → signal_candidate_id → risk_review_input_id
order_intent_id → risk_decision_id → approved_order_id → execution_order_id
   → fill_id → audit_id        (+ trace_id, correlation_id, schema_version)
```

Lifecycle: `ResearchDossier → ProbabilityEstimate → SignalCandidate → RiskReviewInput`
then `OrderIntent → RiskDecision → ApprovedOrder → ExecutionReport → AuditEvent`.
**Research contracts are non-executable. `SignalCandidate` is not `OrderIntent`;
`RiskReviewInput` is not `RiskDecision`.**

## Implementation / QA / Operations skills

| Skill | Use it when you need to… |
|-------|---------------------------|
| [`add-governed-service`](add-governed-service/SKILL.md) | add/change a service within its boundary |
| [`contract-first`](contract-first/SKILL.md) | define/change a payload (`ContractValidator`/`SchemaRegistry`) |
| [`feature-pipeline`](feature-pipeline/SKILL.md) | point-in-time features, leakage audit, feature-store approval gate |
| [`model-predictions`](model-predictions/SKILL.md) | predictions/probability estimates only (no orders) |
| [`model-monitoring`](model-monitoring/SKILL.md) | drift → risk-reducing alerts |
| [`signals-and-intents`](signals-and-intents/SKILL.md) | signal candidate → non-executable OrderIntent → Risk Gateway |
| [`risk-gateway-check`](risk-gateway-check/SKILL.md) | a deterministic pre-trade check (final authority) |
| [`execution-control-plane`](execution-control-plane/SKILL.md) | fail-closed execution (ApprovedOrder-only, no live connector) |
| [`backtest-and-paper`](backtest-and-paper/SKILL.md) | backtest/paper with risk replay (paper-only) |
| [`portfolio-and-reporting`](portfolio-and-reporting/SKILL.md) | positions/P&L + read-only reports |
| [`audit-and-trace`](audit-and-trace/SKILL.md) | audit events + identity-chain reconstruction |
| [`security-and-secret-audit`](security-and-secret-audit/SKILL.md) | secret-artifact audit + redaction; fail-closed |
| [`incident-response`](incident-response/SKILL.md) | tripped guard / red check — stabilise first |
| [`dependency-review`](dependency-review/SKILL.md) | review before adding any dep / external project / MCP / FIX |
| [`release-readiness`](release-readiness/SKILL.md) | readiness review (never a live approval) |
| [`run-checks`](run-checks/SKILL.md) | verify a change with the real tooling |

## Governance skills (separate category)

The **agent-governing** skills — `research-and-debate`,
`agentic-self-programming-governance`, `agent-orchestration-and-swarm`,
`mcp-tool-governance` — live in their own category so the governance/assurance
layers (SC-01 Architect Prime, SC-02 Safety Oracle, Failure Intelligence Layer,
Runtime Assurance Layer) can apply policy to them without mixing with
implementation/QA/ops. They are delivered on the **`governance-skills`** branch
(formalised: pipelines, 9-stage self-programming flow, fail-closed swarm modes,
MCP untrusted-by-default), to be integrated as a separate, reviewed step.

**Golden rule:** if a step would touch secrets, place a live order, bypass the Risk
Gateway, or weaken a check — STOP. Those are human-only or forbidden. Skills describe
how to work here; they grant no new authority.
