# Engineering Discipline

This document defines the engineering discipline expected for Agentic Quant Trading OS. `AGENTS.md` remains authoritative.

## Discipline Principles

- Preserve safety invariants before adding capability.
- Prefer explicit contracts over implicit coupling.
- Keep domain logic separate from adapters.
- Treat configuration as governed policy.
- Treat data, models and audit events as versioned assets.
- Make failure modes visible, bounded and testable.
- Do not claim production readiness without promotion evidence.

## Change Classification

Every change should be classified before implementation:

| Class | Examples | Required discipline |
| --- | --- | --- |
| Documentation | README, ADR, runbook | Consistency with `AGENTS.md` |
| Scaffold | Folders, placeholders, safe scripts | No external calls, no credentials, no trading logic |
| Contract | JSON Schema, lifecycle IDs | Schema tests and compatibility notes |
| Data | Features, manifests, snapshots | Point-in-time and leakage review |
| Model | Training, inference, registry | Drift, validation and promotion evidence |
| Risk | Limits, decisions, kill switches | Deterministic tests and replay tests |
| Execution | Order state, adapters, reconciliation | Explicit approval, idempotency and audit evidence |
| Security | Auth, secrets, permissions | Threat model and secret exposure tests |

## Required Design Notes

Before implementing non-trivial behavior, capture:

- Service owner and boundary.
- Inputs and outputs.
- Contract references.
- Failure modes.
- Audit events.
- Security assumptions.
- Test strategy.
- Rollback path.

Use templates where relevant:

- ADR: `docs/adr/TEMPLATE.md`
- Runbook: `docs/runbooks/TEMPLATE.md`
- Contract review: `docs/architecture/contract_review_template.md`
- Safety review: `security/safety_review_template.md`
- Phased execution: `docs/architecture/phased_execution_plan.md`

## Quality Gates

No meaningful change should merge without:

- Contract impact review.
- Security impact review.
- Audit impact review.
- Test impact review.
- Documentation impact review.
- Residual risk statement.

Risk, execution and security changes require stricter review and must fail closed when uncertain.

## Modern Discipline Additions

Use these controls for non-trivial future work:

- Define invariants before implementation.
- Prefer small PRs with one clear responsibility.
- Keep adapters replaceable and domain logic deterministic.
- Use typed boundaries and schema validation at service edges.
- Record assumptions in ADRs when they affect architecture, risk or security.
- Require rollback notes for behavior changes.
- Require migration notes for contract, config or data shape changes.
- Treat observability as part of the feature, not aftercare.
- Prefer boring, inspectable mechanisms over clever hidden automation.

## Review Checklist

Every review should ask:

- Does this preserve the allowed system flow?
- Can this bypass the Risk Gateway?
- Does this introduce hidden network access?
- Does this expose or imply credentials?
- Are contracts updated before cross-service behavior?
- Are failure modes explicit and safe?
- Are tests proportional to the risk?
- Is the documentation update relevant and non-duplicative?

## Definition of Done

A change is done only when:

- Scope stayed within the requested task.
- Relevant checks were run or explicitly skipped with reason.
- Files changed are summarized.
- Intentional non-work is stated.
- Remaining risk or next step is clear.

## Agent Discipline

Agents must keep changes small and evidence-oriented. If a requested change would weaken boundaries, hide risk, bypass governance or create live-capable behavior without explicit approval, the unsafe part must be refused.
