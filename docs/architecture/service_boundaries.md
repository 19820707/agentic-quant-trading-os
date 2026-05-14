# Service Boundaries

This document defines the expected ownership boundaries for the platform. `AGENTS.md` remains the authoritative operating manual for agent behavior.

## Boundary Rules

- Each service owns a clear domain responsibility.
- Services communicate through explicit APIs, events, schemas, or contract files.
- Shared mutable state across domains is not allowed.
- Deterministic enforcement services must not depend on nondeterministic AI output for final authority.
- Cross-boundary changes require contract updates, tests, and documentation.

## Expected Domains

| Domain | Primary responsibility | Must not own |
| --- | --- | --- |
| Data ingestion | Raw data intake, validation, lineage, quality | Trading decisions |
| Research/features | Feature creation, experiments, backtest inputs | Live execution |
| Model/signals | Forecasts, rankings, confidence metadata | Final risk or order authority |
| Strategy | Candidate actions and target exposures | Broker routing |
| Portfolio | Allocation and portfolio constraints | Broker state |
| Risk | Deterministic limits and approvals/rejections | Alpha generation |
| Execution | Orders, routing, fills, cancel/replace, broker state | Risk policy definition |
| Audit/compliance | Evidence, approvals, lineage, exceptions | Runtime risk enforcement |
| Operations | Health, metrics, alerts, runbooks | Strategy logic |

## Boundary Change Checklist

- Identify producer and consumer services.
- Update API, event, or schema contracts.
- Add contract tests.
- Define failure and timeout behavior.
- Preserve audit identifiers across the boundary.
- Update architecture documentation and operational notes.

## Critical Control Loop Boundary

The platform follows a safety-critical observation -> prediction -> planning -> control -> execution-boundary separation.

- Market data and research services may produce observations.
- Model services may produce forecasts, probabilities and confidence metadata.
- Signal and intent services may produce candidate signals or non-executable order intents.
- Deterministic-risk-gateway remains the final pre-trade control boundary.
- Execution-engine remains the only future boundary for approved execution.

No model, agent, dashboard, notebook, research service, backtest or signal service may bypass deterministic-risk-gateway or call a broker/exchange directly.

