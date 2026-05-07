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

## Local development environment

Placeholder apps import **FastAPI**. Editors and type checkers need those packages in the active Python environment (they are not trading or broker integrations).

1. Create a virtual environment (from the repository root):

   ```bash
   python -m venv .venv
   ```

2. Activate it (Windows PowerShell):

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   On macOS/Linux:

   ```bash
   source .venv/bin/activate
   ```

3. Install scaffold **dev** dependencies (editable install of `packages/` plus dev extras):

   ```bash
   pip install -e ".[dev]"
   ```

   If editable install is not available in your environment, use the flat list instead:

   ```bash
   pip install -r requirements.txt
   ```

4. In Cursor or VS Code, choose the interpreter: **Python: Select Interpreter** → `.venv` (or `python` from that venv).

This does not start servers, call the network, or add broker credentials. To run a placeholder locally if needed: `uvicorn` against a specific `app` module is optional and not required for tests.

## Safe Checks

Run the scaffold auditor with:

```bash
python scripts/scaffold_audit.py
```

The auditor checks expected placeholder structure and scans for prohibited implementation markers. It does not call external services.

## CI Quality Gates

Pull requests and pushes to `main` run CI quality gates for scaffold audit, contract tests and adapter interface tests.

CI must not use secrets, perform live trading, call broker/exchange APIs or run network-dependent trading integrations.
