# agentic-quant-trading-os

Agentic Quant Trading OS is a critical, auditable, modular and governed AI-native quantitative trading platform scaffold for real assets.

This is not a trading bot. The current repository is a safe scaffold only.

## Operating Manual

Start with [AGENTS.md](AGENTS.md). It is the permanent operating manual for Codex and other automated agents working in this repository.

The repository is governed by these core rules:

- AI outputs are untrusted until validated.
- Risk, portfolio constraints, and execution authority remain deterministic.
- Trading-impacting behavior must be auditable and reproducible.
- Service boundaries must be explicit.
- Promotion toward production requires documented gates and review.
- No trading logic, broker integration, credentials or live trading code is present in this scaffold.

## Documentation Map

- [Architecture](ARCHITECTURE.md)
- [Security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)
- [Service Boundaries](docs/architecture/service_boundaries.md)
- [Integration Strategy](docs/architecture/integration_strategy.md)
- [Promotion Gates](docs/architecture/promotion_gates.md)
- [External Projects Catalog](docs/architecture/external_projects_catalog.md)
- [Engineering Discipline](docs/architecture/engineering_discipline.md)
- [Operational Readiness](docs/runbooks/operational_readiness.md)
- [Threat Model](security/threat_model.md)

## Initial Scaffold

The scaffold defines root documentation, service folders, contract schema folders, integration documentation and safe placeholder FastAPI apps.

Every service exposes only:

- `GET /health`
- `GET /ready`

These endpoints are static placeholders and do not perform external calls.

## Safe Checks

Run the scaffold auditor with:

```bash
python scripts/scaffold_audit.py
```

The auditor checks expected placeholder structure and scans for prohibited implementation markers. It does not call external services.

## Development Environment

For local interpreter setup, dependency expectations and editor troubleshooting, see [Development Environment](docs/onboarding/dev_environment.md).

## CI Quality Gates

Pull requests and pushes to `main` run CI quality gates for scaffold audit, contract tests and adapter interface tests.

CI must not use secrets, perform live trading, call broker/exchange APIs or run network-dependent trading integrations.

## Security Tooling

Active baseline:

- CodeQL security analysis for Python code scanning

Documented but not active:

- Snyk
- SonarQube
- CodeRabbit
- LLM Council
- PentestGPT
- Xalgorix
- HackCode
- Aderyn

Documented tools are not installed, enabled or approved for runtime use by default. Tools that require tokens, GitHub Apps, external accounts, offensive capability or Web3 scope require separate approval before installation or use.

CodeQL is currently advisory until GitHub Code Scanning is enabled for the repository. Promoting it to a hard merge gate requires a separate approval PR after repository-level support is available.

See [Security Tooling Integration Policy](docs/security/security_tooling_integration_policy.md).
