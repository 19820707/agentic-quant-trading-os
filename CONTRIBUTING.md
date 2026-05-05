# Contributing

Contributions must preserve the platform's critical properties: auditability, modularity, deterministic risk control, governed AI usage, and reproducibility.

Read `AGENTS.md` before making changes. It is the authoritative operating manual for automated and AI-assisted contributors.

## Workflow

1. Understand the affected service, contract, risk surface, and documentation.
2. Keep the change small, reviewable, and auditable.
3. Add or update tests for behavioral changes.
4. Update documentation for architecture, security, configuration, data, model, or operational changes.
5. Run the most relevant checks available.
6. Report assumptions, validation results, and residual risk.

## Scaffold Rules

- Keep placeholder services safe.
- Do not add broker integrations unless explicitly requested.
- Do not add credentials or realistic credential examples.
- Do not install dependencies as part of scaffold-only work.
- Do not create direct paths from agentic, model, signal, backtest or dashboard components to brokers or exchanges.
- Run `python scripts/scaffold_audit.py` after scaffold or boundary changes.
- Update `docs/architecture/engineering_discipline.md` when quality gates change.

## Review Expectations

Review should focus on:

- Correctness and reproducibility.
- Risk and execution safety.
- Service boundary integrity.
- Security and secret handling.
- Test coverage for the changed behavior.
- Audit evidence and observability.
- Documentation accuracy.

No contribution should claim production readiness unless the promotion gates in `docs/architecture/promotion_gates.md` have passed.
