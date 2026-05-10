# Security Tooling Integration Policy

## Purpose

This policy defines how security, review and offensive-security tools may be integrated into this repository.

Security tooling is a safety layer, not a trading runtime. It must never receive broker credentials, exchange keys, withdrawal keys, production secrets or execution authority.

## Approved Baseline

CodeQL is approved as the first repository-native security scanner.

The CodeQL workflow is allowed to run in GitHub Actions on pull requests, pushes to `main` and a weekly schedule. It must use repository code only, must not require project secrets and must not call broker, exchange or trading APIs.

CodeQL is advisory until GitHub Code Scanning is enabled for the repository. The workflow may run analysis without blocking merges while SARIF upload support is unavailable. Promoting CodeQL to a hard merge gate requires a separate PR after repository-level Code Scanning support is enabled.

Local secret and artifact hygiene auditing is approved as a standard-library CI gate. It blocks real `.env` files, private-key material, token-like values, local databases, model checkpoints and generated data artifacts without calling external services.

## Tool Classes

| Tool category | Default state | Approval required | Secrets required | Runtime environment |
| --- | --- | --- | --- | --- |
| Production CI candidates | CodeQL and local hygiene audit enabled; others disabled | Yes for non-baseline tools | No by default | GitHub Actions |
| Advisory review candidates | Disabled | Yes | Possible; must be reviewed | Pull request review only |
| Research-only candidates | Disabled | Yes | No | Local research only |
| Isolated lab only | Disabled | Yes | No production secrets | Isolated authorized lab |
| Web3 only | Disabled | Yes | No | Web3/Solidity scope only |

### Production CI Candidates

These tools may be proposed for CI/CD after explicit review:

- GitHub CodeQL for semantic SAST and code scanning
- local standard-library secret and artifact hygiene auditing
- Snyk for dependency, container and IaC review
- SonarQube or SonarCloud for quality, bugs, security hotspots and code smells

Snyk and SonarQube are not approved by this policy. They require separate approval because they may require tokens, organization configuration, external services or GitHub App permissions.

### Advisory Review Candidates

These tools may assist humans but must not become final approvers:

- CodeRabbit AI
- LLM Council
- defensive bug-bounty prompt libraries

Advisory tools may summarize, review, propose or explain. They must not approve merges, change risk limits, access credentials, call brokers or trigger execution.

### Research-Only Candidates

These resources may be used for research and threat modeling only:

- OpenMythos-style experimental model architecture references
- agentic AI security catalogs
- general "awesome" tool lists

Research-only resources are not dependencies and must not be treated as production-ready tools.

### Isolated Lab Only

Offensive or dual-use tooling is allowed only in isolated, authorized lab environments:

- PentestGPT-style tools
- Xalgorix-style autonomous pentest tools
- HackCode-style hacking terminals

These tools must not run against third-party targets without written authorization. They must not connect to production, brokers, exchanges, wallets, banks, real secrets or trading infrastructure.

No offensive or autonomous security tool may run against external targets unless the scope is documented, authorized and isolated.

### Web3 Only

Aderyn or similar Solidity analyzers are relevant only if the project adds Solidity, DeFi or smart-contract scope through a separate approved PR.

## Universal Rules

- no broker credentials
- no exchange trade credentials
- no withdrawal keys
- no wallet keys
- no trading secrets
- no production market data entitlements
- no live execution infrastructure access
- no production secrets
- no live trading paths
- no order submission
- no private broker or exchange endpoints
- no bypass of deterministic-risk-gateway
- no autonomous remediation without review
- no external security service tokens without approval
- no GitHub App installation without approval
- no generated findings treated as final approval
- no model checkpoints committed to the repository
- no local databases or market-data entitlement dumps committed to the repository
- no real `.env` files committed to the repository

## Integration Gates

Before any new security tool is added, the PR must document:

- tool purpose
- tool class
- required permissions
- required secrets
- data sent outside GitHub
- failure mode
- CI impact
- false-positive handling
- rollback plan
- owner/reviewer

Tools requiring external accounts, paid services, organization settings, GitHub Apps or secrets must use a separate approval PR before implementation.

## Current Decisions

```yaml
codeql_enabled: true
codeql_hard_gate_enabled: false
codeql_requires_code_scanning_enabled: true
local_secret_artifact_audit_enabled: true
snyk_enabled: false
sonarqube_enabled: false
coderabbit_enabled: false
llm_council_enabled: false
offensive_lab_tools_enabled: false
web3_static_analysis_enabled: false
external_security_tokens_allowed: false
broker_credentials_allowed: false
trading_authority_allowed: false
```

## Non-Goals

- no Snyk token configuration
- no SonarQube token configuration
- no CodeRabbit GitHub App installation
- no LLM Council runtime integration
- no pentest agent installation
- no offensive scans
- no broker or exchange integration
- no live trading
