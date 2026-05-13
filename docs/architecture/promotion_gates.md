# Promotion Gates

Promotion gates define how code, configuration, models, strategies, and operational changes move from development toward production. `AGENTS.md` is the authoritative manual for agent conduct.

## Promotion States

- Development: implementation or research in progress.
- Reviewed: code or document review completed.
- Tested: relevant automated checks passed.
- Simulated: behavior validated in controlled simulation where applicable.
- Paper: behavior validated with paper trading or non-capital environment where applicable.
- Approved: accountable review completed for risk, security, architecture, and operations.
- Production: live-capital impact allowed under explicit operating policy.

## Required Gates

Production-impacting changes must pass applicable gates:

- Code review.
- Automated test review.
- Contract test review for service-boundary changes.
- Architecture review for cross-service or platform-level changes.
- Security review for sensitive surfaces.
- Data quality and lineage validation.
- Backtest reproducibility review for strategy/model changes.
- Simulation review for trading workflows.
- Paper-trading review before live trading.
- Risk sign-off for limits, exposures, execution, and capital impact.
- Operational readiness review.
- Rollback and incident plan.

Agent runtime changes must also pass `docs/integrations/agent_runtime_approval_gate.md` before any runtime agent, MCP server, tool execution, background worker, federation, external memory, credential access or network access is enabled.

## Evidence Expectations

Promotion evidence should identify:

- Code version.
- Configuration version.
- Data snapshot or lineage.
- Model artifact and prompt version where applicable.
- Test results.
- Known limitations.
- Approval owner.
- Rollback path.

No agent may describe a change as production-ready unless the relevant gates have passed and evidence is available.

