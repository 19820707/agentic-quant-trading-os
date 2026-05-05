# Security

This repository is security-sensitive because it may contain code and configuration for trading, data processing, model governance, broker integration, and operational controls.

The permanent agent rules in `AGENTS.md` apply to all security-relevant work.

The current scaffold contains no secrets, no broker credentials, no broker integrations and no live trading code.

## Security Principles

- Never commit secrets, tokens, credentials, private keys, broker credentials, account identifiers, or regulated sensitive data.
- Use least privilege for services, users, agents, and automation.
- Fail closed for authentication, authorization, risk, execution, and compliance uncertainty.
- Keep audit logs useful without leaking secrets.
- Treat AI output, external data, and third-party services as untrusted until validated.
- Review dependency additions for supply-chain, license, maintenance, and runtime risk.

## Sensitive Surfaces

Changes require extra care when they touch:

- Authentication or authorization.
- Secret management.
- Broker or venue connectivity.
- Order routing and execution.
- Risk limits and portfolio constraints.
- Data permissions and regulated datasets.
- CI/CD, deployment, promotion, or infrastructure.
- Logging, audit, monitoring, and incident handling.

## Vulnerability Handling

Do not disclose sensitive findings publicly before coordinated remediation. Record enough evidence for maintainers to reproduce the issue without exposing secrets or production data.

Security fixes should include tests or validation where practical and must document any residual risk.

## Placeholder Environment

`.env.example` must remain documentation-only. It must not contain real API keys, realistic credentials, account identifiers, broker tokens, exchange secrets or withdrawal permissions.

## Threat Model

See [Threat Model](security/threat_model.md) for scaffold-level assumptions, trust boundaries and prohibited credential paths.
