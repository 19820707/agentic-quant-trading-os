# Prediction Market Repository Intake Audit

## Decision

Status: reference-only intake gate.

Do not clone, vendor, install, import, execute or run these repositories in the platform runtime until a separate approval PR completes dependency review, license review, secret handling review, deterministic risk integration design, and execution isolation design.

This project currently remains a safe scaffold. These repositories are useful as research inputs for market-data adapters, paper-trading workflows, prediction-market analytics, and future MCP/read-only tooling, but several include live trading, order submission, wallet/private-key handling, or autonomous execution paths.

## Intake Scope

| Repository | URL | Primary capability | Execution capability | Secrets/keys | Initial decision |
| --- | --- | --- | --- | --- | --- |
| datori/market-edge | https://github.com/datori/market-edge | LLM probability estimation, Polymarket scanning, paper/live portfolio logic | Live executor described | Anthropic, Tavily, Polymarket private key/funder | Research only; no install |
| mjunaidca/polymarket-skills | https://github.com/mjunaidca/polymarket-skills | Agent skills for scanner, analyzer, monitor, paper trading, strategy, live executor | Live executor skill exists | L2 wallet/private key for live | Skills may be studied; live executor disabled |
| InjayTseng/Trading-Agent-Polymarket | https://github.com/InjayTseng/Trading-Agent-Polymarket | LangGraph multi-agent analysis and risk debate | Analysis only per README | LLM provider keys | Candidate for advisory-only analysis design |
| pmxt-dev/pmxt-mcp | https://github.com/pmxt-dev/pmxt-mcp | MCP server for PMXT prediction-market API | Order tools exist | PMXT API key; potential trading credentials | Read-only MCP candidate only; order tools blocked |
| Composio-HQ/polymarket-kalshi-arbitrage-bot | https://github.com/Composio-HQ/polymarket-kalshi-arbitrage-bot | Polymarket/Kalshi arbitrage bot | Polymarket order placement when enabled | Polymarket private key/proxy wallet | High-risk; no install |
| haredoggy/Prediction-Markets-Trading-Bot-Toolkits | https://github.com/haredoggy/Prediction-Markets-Trading-Bot-Toolkits | Multi-venue prediction-market trading toolkit | Claims production trading bots | Wallet/API credentials likely | High-risk vendor-style toolkit; no install |
| neilt93/Prediction-Market-Agent | https://github.com/neilt93/Prediction-Market-Agent | Local-first prediction-market forecasting/trading agent | Insufficient README detail | Unknown pending deep audit | Hold pending file-level audit |
| lmhtq/polymarket-ai-agent | https://github.com/lmhtq/polymarket-ai-agent | Polymarket AI agent with paper/live executor | Live CLOB executor exists | GPTSAPI key, Polymarket private key | Research only; paper-mode patterns only |
| yigitcankzl/PolymarketSignalAgent | https://github.com/yigitcankzl/PolymarketSignalAgent | Signal engine, arbitrage, dashboard, Synthesis trading | Dashboard/API trading execution | Groq and Synthesis keys | High-risk; no install |
| SXai-lab/prediction-market-arbitrage | https://github.com/SXai-lab/prediction-market-arbitrage | Dump-and-hedge Polymarket arbitrage | Production CLOB order path | Private key, proxy wallet, CLOB credentials | High-risk; no install |
| SXai-lab/prediction-market-copytrade | https://github.com/SXai-lab/prediction-market-copytrade | Polymarket copy trading | Mirrors trades into user's wallet | Private key and Polymarket address | High-risk; no install |
| zkOSAI/polymarket-arbitrage-bot | https://github.com/zkOSAI/polymarket-arbitrage-bot | Polymarket arbitrage bot | Simulation/live order path | Wallet private key, proxy wallet, API credentials | High-risk; no install |

Duplicate input: `haredoggy/Prediction-Markets-Trading-Bot-Toolkits` appeared twice and is tracked once.

## Audit Observations

### datori/market-edge

The README describes an autonomous Polymarket agent using LLM probability estimation, market scanning, Kelly sizing, and trade execution or paper trading against a local portfolio. It requires Anthropic and Tavily API keys, and Polymarket private key plus funder address for live trading. The README also states research/paper-trading status and reports no confirmed out-of-sample edge.

Decision: do not install. Potential future use is limited to research notes, calibration methodology, backtest structuring, and paper-only design patterns after license/dependency review.

### mjunaidca/polymarket-skills

The README provides composable skills for scanning, analysis, monitoring, paper trading, strategy advice, and a live executor. It documents `py-clob-client` and `requests` dependencies, paper-first workflows, and a live executor requiring wallet credentials and human opt-in.

Decision: do not install globally. If used later, import only read-only scanner/analyzer/paper-trader skills into an isolated skills sandbox; exclude live executor.

### InjayTseng/Trading-Agent-Polymarket

The README describes a LangGraph state machine for prediction-market analysis with analyst, research debate, trader, and risk-manager phases. It currently states analysis-only/no order execution and relies on public Polymarket APIs plus LLM provider keys.

Decision: best low-runtime-risk candidate for advisory-only architecture reference. Still requires dependency and prompt-injection review before use.

### pmxt-dev/pmxt-mcp

The README describes an MCP server that exposes a unified prediction-market API. It includes read-only market tools and order-related tools such as build/create/submit/cancel order, and it forwards tool calls to hosted or local PMXT API over HTTP using `PMXT_API_KEY` or local sidecar.

Decision: read-only MCP candidate only. Do not expose order tools to agents. Do not provide broker, exchange, wallet, PMXT live API, or trading credentials.

### Composio-HQ/polymarket-kalshi-arbitrage-bot

The README describes a 15-minute Polymarket/Kalshi arbitrage bot using Express/TypeScript, Axios, `@polymarket/clob-client`, and `ethers`. It documents private key and proxy wallet variables and buy signals for Polymarket orders.

Decision: high risk. No install. The public README includes marketing claims and a Telegram sale/contact prompt; require strict source audit before any reference use.

### haredoggy/Prediction-Markets-Trading-Bot-Toolkits

The README describes a multi-venue trading toolkit with multiple claimed production-ready strategies, low-latency execution, copy trading, arbitrage, market making, and on-chain whale signals. It repeatedly points to external contact links.

Decision: high risk. Treat as vendor/marketing material and not as an installable dependency. No runtime use.

### neilt93/Prediction-Market-Agent

The README is minimal and describes a local-first forecasting/trading agent with uv, Docker Compose, migrations, and a FastAPI service.

Decision: hold. Requires file-level review of dependencies, Docker Compose services, migrations, API surface, secret handling, and execution paths.

### lmhtq/polymarket-ai-agent

The README describes an autonomous Polymarket AI agent with crawlers, LLM scoring, Kelly sizing, risk limits, dashboard, paper executor, and live CLOB executor. It explicitly reports a negative 25-day paper-trading result and defaults to `PM_DRY_RUN=1`.

Decision: research only. Useful for honest-results framing and paper-mode risk boundaries. Do not import executor code.

### yigitcankzl/PolymarketSignalAgent

The README describes live market/news/LLM/signal/arbitrage pipeline and one-click or automated trading through Synthesis.trade APIs. It requires Groq and Synthesis credentials.

Decision: high risk. Do not install. Future review may extract dashboard UX patterns only, not execution.

### SXai-lab/prediction-market-arbitrage

The README describes a TypeScript Polymarket 15-minute dump-and-hedge bot using official CLOB client, private keys, proxy wallet address, production mode, and optional redemption. It includes simulation mode and safety checklist.

Decision: high risk. No install. Can inform future simulation-mode and production-gate checklists only.

### SXai-lab/prediction-market-copytrade

The README describes a Polymarket copy-trading bot that monitors a target user and mirrors trades into the user's account using private key and Polymarket proxy/funder address.

Decision: high risk. No install. Copy-trading is explicitly trading-authority behavior and must remain outside scaffold.

### zkOSAI/polymarket-arbitrage-bot

The README describes a TypeScript Polymarket arbitrage bot for 15-minute markets with simulation/live mode, CLOB order execution, private-key signing, proxy wallet support, and possible settlement/redemption.

Decision: high risk. No install. Potential reference only for simulation/live-mode separation after source audit.

## Allowed Integration Pattern

Only the following is allowed by this intake PR:

1. Document repositories as candidates.
2. Preserve their URLs and initial audit posture.
3. Block direct runtime installation, vendoring, cloning, submodules, dependency changes, and execution wiring.
4. Require separate approval PRs for any future adapter, MCP tool, skill import, or paper-trading sandbox.

## Prohibited Until Separate Approval

- adding these repositories as git submodules
- vendoring source code from these repositories
- adding their package dependencies to `pyproject.toml`, `package.json`, lockfiles, Dockerfiles, or CI
- adding `.env` variables for their API keys or private keys
- enabling MCP order tools
- enabling live executor skills
- adding wallet, CLOB, PMXT, Synthesis, Kalshi, Polymarket, or broker credentials
- adding autonomous order execution
- adding copy trading
- adding market making
- adding settlement/redemption calls

## Future Safe Sequence

1. Merge security baseline.
2. Add dependency/SBOM baseline without external tokens.
3. Add an external repository quarantine/intake process.
4. For each candidate, open one PR with pinned source review, license review, dependency inventory, and prohibited-method scan.
5. Approve read-only market-data extraction only after deterministic risk and secret boundaries are tested.
6. Approve paper-trading sandbox only after audit logging and kill-switch controls exist.
7. Defer live execution until deterministic-risk-gateway, portfolio-service, execution-engine and governance-service enforce hard limits.
