# Prediction Market Repository Audit

## Purpose

This audit catalogs external prediction-market repositories before any integration decision.

It does not approve cloning, vendoring, installing, importing, running, or wiring any listed repository into the platform.

All candidates remain subject to the external adapter safety policy, the external adapter review checklist, deterministic-risk-gateway boundaries, and explicit human governance.

## Current Decision State

prediction_market_external_repos_cataloged: true
direct_installation_allowed: false
external_repo_cloning_allowed: false
vendoring_allowed: false
submodules_allowed: false
runtime_enabled: false
production_enabled: false
network_access_allowed: false
credentials_allowed: false
private_endpoints_allowed: false
trading_methods_allowed: false
broker_exchange_execution_allowed: false
mcp_trading_tools_allowed: false

## Global Findings

The reviewed repositories are relevant to prediction-market research, market data discovery, agent workflows, arbitrage, copy trading, MCP tools, and automated trading.

They also contain high-risk patterns for this project:

- live or automated trading claims
- Polymarket CLOB clients
- Kalshi or unified prediction-market APIs
- wallet/private-key requirements
- API-key or hosted-service requirements
- order submission, cancellation, copy-trading, arbitrage, or execution paths
- MCP tools that can expose order-related actions
- missing licenses in several repositories
- limited maintenance history for several young repositories

Because this platform is a critical financial system, none of these repositories may be installed or coupled directly. Any future use must be through a separate approved adapter or reference-only design process.

## Repository Decisions

| Repository | URL | Observed scope | License signal | Risk classification | Initial decision |
|---|---|---|---|---|---|
| datori/market-edge | https://github.com/datori/market-edge | LLM prediction-market agent, Polymarket CLOB, paper/live trading, Kelly sizing | No license detected | High | Reference-only, reject direct install |
| mjunaidca/polymarket-skills | https://github.com/mjunaidca/polymarket-skills | Agent skills for scanning, analysis, paper trading, live execution | No license detected | High | Reference-only, individual skill review required |
| InjayTseng/Trading-Agent-Polymarket | https://github.com/InjayTseng/Trading-Agent-Polymarket | Multi-agent Polymarket analysis framework | Apache-2.0 | Medium | Research-reference candidate only |
| pmxt-dev/pmxt-mcp | https://github.com/pmxt-dev/pmxt-mcp | MCP server for unified prediction-market API with read and order tools | MIT | High | MCP reference-only, no runtime connection |
| Composio-HQ/polymarket-kalshi-arbitrage-bot | https://github.com/Composio-HQ/polymarket-kalshi-arbitrage-bot | Polymarket/Kalshi arbitrage bot with CLOB, ethers, dotenv | No license detected | Critical | Reject direct install |
| haredoggy/Prediction-Markets-Trading-Bot-Toolkits | https://github.com/haredoggy/Prediction-Markets-Trading-Bot-Toolkits | Multi-venue prediction-market trading/copy-trading toolkit | MIT | Critical | Reject direct install |
| neilt93/Prediction-Market-Agent | https://github.com/neilt93/Prediction-Market-Agent | LLM forecasting and automated Kalshi trading | No license detected | Critical | Reject direct install |
| lmhtq/polymarket-ai-agent | https://github.com/lmhtq/polymarket-ai-agent | Autonomous Polymarket trading agent with CLOB executor | MIT | Critical | Reject direct install |
| yigitcankzl/PolymarketSignalAgent | https://github.com/yigitcankzl/PolymarketSignalAgent | Multi-LLM signal/arbitrage system with optional execution | No license detected | High | Reference-only, reject runtime |
| SXai-lab/prediction-market-arbitrage | https://github.com/SXai-lab/prediction-market-arbitrage | Polymarket arbitrage bot with production CLOB order flow | MIT | Critical | Reject direct install |
| SXai-lab/prediction-market-copytrade | https://github.com/SXai-lab/prediction-market-copytrade | Polymarket copy-trading bot requiring wallet credentials | No license detected | Critical | Reject direct install |
| zkOSAI/polymarket-arbitrage-bot | https://github.com/zkOSAI/polymarket-arbitrage-bot | Polymarket arbitrage bot with credential management and execution | No license detected | Critical | Reject direct install |

The duplicate haredoggy repository entry in the request was de-duplicated for this audit.

## Installation Decision

Do not install any listed repository at this stage.

Do not clone any listed repository into this project.

Do not add any listed repository as a dependency, Git submodule, vendored folder, MCP runtime, service, adapter, package, Docker service, workflow, or script target.

## Allowed Use For Now

Allowed:

- reference-only architecture review
- threat modeling
- license/security/maintenance review
- extraction of safe requirements into internal documents
- future read-only market-data adapter proposals
- future paper-only simulation proposals

Not allowed:

- runtime integration
- dependency installation
- hosted API use
- MCP tool activation
- private endpoints
- wallet or exchange credentials
- broker/exchange order submission
- copy-trading
- arbitrage execution
- live trading
- direct path from AI/agent/model/dashboard/notebook to broker, exchange, wallet, or hosted trading API

## Required Gate Before Any Future Candidate Work

Before any future PR may implement work based on one of these repositories, it must provide:

- completed external adapter review checklist
- license review
- dependency and transitive dependency review
- security and credential-boundary review
- maintenance and release history review
- explicit internal contract mapping
- local-only fake/in-memory tests
- no network calls in unit tests
- prohibited method denylist tests
- redaction for errors/logs/audit
- approval from engineering, security, risk architecture, platform reliability, and maintainer reviewers

## Safe Next Candidate Direction

The only safe technical direction from this audit is a future documentation-only PR for a prediction-market integration policy and read-only market-data candidate checklist.

Any future adapter must begin as read-only and fake-client-only. It must not create OrderIntent, ApprovedOrder, execution reports, broker orders, wallet transactions, or risk approvals.

