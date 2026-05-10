# External Projects Catalog

This catalog documents external projects, tools and libraries considered for future integration.

## Rules

- External projects are reference-only unless explicitly approved.
- Do not clone, vendor, install or add submodules by default.
- Review license, security, maintenance and production suitability before integration.
- FIX engines belong only inside execution-engine adapters.
- Backtesting tools cannot promote strategies directly to live trading.
- MCP tools must never receive broker credentials.
- Prediction-market trading bots require an intake audit, source quarantine plan, dependency/SBOM review, and explicit risk approval before any runtime installation.
- Repositories with order execution, wallet signing, private-key handling, copy trading, autonomous arbitrage, or live exchange/API credentials must remain disabled until deterministic-risk-gateway and execution-engine controls exist.

## Active Intake Audits

- [Prediction Market Repository Intake Audit](../security/prediction_market_repo_intake_audit.md)

## Candidate Record Template

- Name:
- Purpose:
- Source:
- License:
- Maintenance status:
- Security notes:
- Integration pattern:
- Risk boundary:
- Approval status:
