# APP Spec — What the product does and for whom

> Bound by [`AGENTS.md`](../../AGENTS.md). The product is the **governed pipeline and
> its auditability**, not any single strategy. Architecture-level by design — see
> `docs/architecture/` and `packages/contracts/` for the authoritative specifics.

## 1. One-sentence definition

**Agentic Quant Trading OS** is a critical, auditable, modular and governed
AI-native quantitative trading platform for real assets, where **AI is only an
intelligence layer** and deterministic risk controls + controlled execution retain
final authority. It is **not a trading bot**, **not** an autonomous trader, and
**not** a "get rich" product.

## 2. Core principle

```
AI proposes. Models predict. Risk Gateway decides.
Execution Engine executes. Audit proves. Human governance supervises.
```

## 3. Who it is for (personas & jobs-to-be-done)

| Persona | Primary job | What the product gives them |
|---------|-------------|------------------------------|
| **Quant Researcher** | turn an idea into validated, gated evidence | the research/debate layer (dossier → hypothesis → analyst report → debate → probability estimate → signal candidate), non-executable by construction |
| **Risk Officer** | guarantee no order escapes risk control | the Deterministic Risk Gateway as the single, final pre-trade authority; deterministic, testable limits |
| **Execution Engineer** | execute only what was approved, idempotently | the execution-engine that consumes only an `ApprovedOrder`; isolated credentials; no live connector by default |
| **Governance / Compliance** | prove every decision and approve promotions | the end-to-end identity chain, append-only audit, and staged gates with human approval for anything persistent or live |
| **Agentic-Systems Engineer** | let agents *propose* code safely | the agentic self-programming flow (task spec → risk assessment → patch → sandbox → tests → PR evidence → human approval → rollback) |
| **Platform / SRE** | run it reliably and fail closed | health/readiness, observability, kill switches, documented failure modes |

## 4. What it does (capabilities)

- **Research & debate:** multi-agent evidence, hypotheses, adversarial analysis and
  probability estimates — producing **knowledge**, never orders.
- **Risk authority:** the Risk Gateway adjudicates every intent (approve / reject /
  resize / cancel-all / require-manual) and emits the only executable object.
- **Backtest & paper:** realistic costs + risk-gateway replay; paper is an isolated,
  simulated sandbox. **Backtest/paper never grant live.**
- **Execution (gated):** only an `ApprovedOrder` is executed; idempotent, reconciled,
  fail-closed; live is human-armed.
- **Audit:** append-only, tamper-evident, reconstructable end-to-end.
- **Agentic governance:** agents propose code under a gated, human-approved,
  reversible flow; orchestration/swarm and MCP tools operate fail-closed with no
  execution authority and no broker credentials.

## 5. Explicit non-goals

- No autonomous live trading; no AI/agent/tool execution authority.
- No "alpha guaranteed" claims — research returns honest negatives.
- No withdrawal capability, ever.
- No bypass of the Risk Gateway by any component, internal or external.

## 6. Success criteria

The product succeeds when it can, *with evidence*:

1. Prove that **no order reaches a broker** except as an `ApprovedOrder` executed by
   the execution-engine.
2. **Trace any fill** back through approval, decision, intent, signal candidate,
   probability and research dossier.
3. **Reject false positives** before capital is risked (research → backtest → paper
   → live, gated).
4. **Fail closed** under uncertainty, model degradation, or component failure.
5. Let a new contributor **orient from the docs**, not from tribal memory.

## 7. The honest line

The durable asset is the **governance, auditability and fail-closed discipline** —
the ability to distinguish a robust signal from a flattering one and to keep
capability behind control — not any specific strategy. Going live is a deliberate
**human** decision, never an automatic consequence of a green pipeline.
