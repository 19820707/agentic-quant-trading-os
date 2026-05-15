# External Platform Landscape

This document classifies external research, broker, exchange, signal, bot and trading platforms by safe integration boundary.

This PR is documentation and policy only. All platforms are reference-only for now.

## Current-State Decision

All platforms listed here are reference-only for now.

- No runtime integration is approved.
- No dependency installation is approved.
- No broker, exchange or client SDK is approved.
- No credentials are allowed.
- No network access is allowed.
- No live trading is approved.
- No paper trading runtime is approved.
- No backtesting runtime is approved.
- No market data ingestion is approved.
- No webhook ingestion is approved.
- No signal ingestion is approved.
- No broker or exchange execution is approved.
- No autonomous order submission is approved.
- No LLM, agent, model, dashboard, notebook or research service may call broker or exchange APIs directly.
- Any future execution path must pass through deterministic-risk-gateway and may only send `ApprovedOrder` to a future execution-engine adapter.

Signal tools and execution tools are different classes of systems. Signal tools may only be considered as future sources for normalized `SignalCandidate` records. Execution tools may only be considered as future execution-engine adapters that accept `ApprovedOrder`, never raw alerts, model outputs or `OrderIntent`.

TradingView-style alerts must become `SignalCandidate` only. They must never trigger direct execution.

Broker APIs may only receive `ApprovedOrder` in the future, after separate approval gates. They must never receive direct calls from LLMs, models, agents, dashboards, notebooks, backtests or signal services.

## Categories

- `research_backtesting_engine`
- `execution_broker_api`
- `crypto_strategy_runtime`
- `signal_source`
- `commercial_bot_reference`
- `futures_trading_platform`
- `forex_cfd_platform`
- `ux_research_only`

## Platform Classification

| Platform | Category | Possible future use | Allowed current state | Prohibited current state | Required future gates before integration | Credential/network risk | Execution risk | Recommended integration boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QuantConnect / LEAN | `research_backtesting_engine` | Reference for research lifecycle, event-driven backtesting, portfolio simulation and backtest evidence design | Reference-only documentation | Installing LEAN, running backtests, ingesting market data, promoting backtests to paper/live trading | Dataset lineage, leakage review, feature store gate, backtest review, paper review, dependency/security review | Medium if real data feeds or cloud runtimes are used later | Medium if backtest output is treated as execution approval | Research/backtest evidence only; no execution path |
| Interactive Brokers API | `execution_broker_api` | Future institutional execution venue candidate | Reference-only documentation | Installing SDK, connecting to TWS/Gateway, reading accounts, submitting/canceling orders, credentials, network | Broker adapter safety policy, credential vault policy, kill switch, idempotency, `ApprovedOrder` input, `ExecutionReport`, audit event, human approval | High due to live broker credentials and account access | Critical due to real order execution and position mutation | Future execution-engine adapter only; accepts `ApprovedOrder` only |
| Alpaca API | `execution_broker_api` | Future paper-first broker adapter candidate | Reference-only documentation | Installing SDK, paper/live API calls, credentials, account reads, order submission, market data ingestion | Paper adapter gate, broker adapter safety policy, credential vault policy, sandbox review, `ApprovedOrder` input, audit event | High once API keys exist | High for live, medium for paper if promoted incorrectly | Future paper adapter first; live adapter requires separate gate |
| Hummingbot | `crypto_strategy_runtime` | Reference for connector capability mapping and isolated strategy sandbox design | Reference-only documentation | Installing runtime, exchange connectors, strategy execution, exchange keys, market making, arbitrage runtime | External runtime review, dependency/SBOM review, sandbox isolation, no-key paper mode, risk-gateway boundary, human approval | High due to exchange connectors and keys | Critical if strategy runtime reaches exchanges | Isolated sandbox candidate only; never central execution path |
| TradingView | `signal_source` | Future alert source for normalized signal intake | Reference-only documentation | Webhook runtime, signal ingestion, direct webhook-to-order, broker bridge, credentials | Signal intake contract, webhook safety policy, replay tests, prompt/input validation, `SignalCandidate` normalization, risk review | Medium if webhook endpoints and secrets are used later | High if alerts bypass risk gateway | Alert -> `SignalCandidate` only; never direct execution |
| NinjaTrader | `futures_trading_platform` | Future futures venue family reference and execution lifecycle reference | Reference-only documentation | Installing desktop/platform components, brokerage connection, strategy runtime, order routing | Futures venue gate, broker adapter safety policy, paper review, credential vault policy, execution-engine adapter approval | High due to broker connectivity | Critical for futures execution | Future venue-family adapter review only |
| TradeStation | `futures_trading_platform` | Future futures/equities venue family reference | Reference-only documentation | Installing SDK, broker connection, account reads, order routing, EasyLanguage strategy runtime | Venue gate, broker adapter safety policy, paper review, credential vault policy, execution-engine adapter approval | High due to brokerage access | Critical for live order execution | Future execution-engine adapter family only |
| MetaTrader 5 | `forex_cfd_platform` | Future forex/CFD venue family reference | Reference-only documentation | Installing terminal, Expert Advisors, broker credentials, account reads, order routing | Plugin/source review, forex/CFD venue gate, credential isolation, broker adapter safety policy, paper review | High due to broker credentials and EA/plugin ecosystem | Critical for live leveraged products | Deferred venue-family review only |
| cTrader | `forex_cfd_platform` | Future forex/CFD venue family reference | Reference-only documentation | Installing platform/API, cBots, broker credentials, account reads, order routing | Plugin/source review, forex/CFD venue gate, credential isolation, broker adapter safety policy, paper review | High due to broker credentials | Critical for live leveraged products | Deferred venue-family review only |
| 3Commas | `commercial_bot_reference` | UX, bot lifecycle and operator workflow reference | Reference-only documentation | Connecting exchange keys, copying bot runtime, signal bridges, smart trade execution | UX review only unless a separate external bot integration gate exists | High if exchange keys are used | Critical if bot controls exchange account | UX/reference only; no runtime dependency |
| Cryptohopper | `commercial_bot_reference` | UX and strategy-template reference | Reference-only documentation | Exchange key connection, automated bot runtime, signal-triggered execution | UX review only unless separately gated | High if exchange keys are used | Critical if bot controls exchange account | UX/reference only; no runtime dependency |
| Bitsgap | `commercial_bot_reference` | UX, grid/arbitrage workflow reference | Reference-only documentation | Exchange keys, bot execution, portfolio mutation | UX review only unless separately gated | High if exchange keys are used | Critical if bot controls exchange account | UX/reference only; no runtime dependency |
| Pionex | `commercial_bot_reference` | UX and exchange-bot product reference | Reference-only documentation | Using exchange/bot runtime, account funding, bot execution | UX review only unless separately gated | High if funds/accounts are used | Critical if bot controls exchange account | UX/reference only; no runtime dependency |
| Coinrule | `commercial_bot_reference` | Rule-builder and operator workflow reference | Reference-only documentation | Broker/exchange connection, live rules, webhook-to-order automation | Rule contract design, signal intake gate, risk review if ever considered | High if account connections are used | Critical if rules submit orders | UX/reference only; local rule contracts only |
| WunderTrading | `commercial_bot_reference` | Copy-trading, bot workflow and signal automation reference | Reference-only documentation | Exchange keys, copy trading, bot execution, signal-to-order automation | UX review only unless separately gated; copy-trading would require separate high-risk gate | High if exchange keys are used | Critical due to copy-trading/order automation | UX/reference only; no runtime dependency |
| TradeSanta | `commercial_bot_reference` | Bot workflow and operator UX reference | Reference-only documentation | Exchange keys, live bot runtime, DCA/grid execution | UX review only unless separately gated | High if exchange keys are used | Critical if bot controls exchange account | UX/reference only; no runtime dependency |
| TrendSpider | `ux_research_only` | Charting, scanning, alerting and research UX reference | Reference-only documentation | Alert ingestion, broker routing, automated trade execution, market data ingestion | Research UX review, signal intake contract if future alerts are considered | Medium if webhooks/data access are used later | High if alerts are wired to execution | UX/research reference only; future alerts become `SignalCandidate` only |

## Future Gate Requirements

Any future PR that proposes moving a platform beyond reference-only must include:

- external adapter review;
- dependency and license review;
- security and maintenance review;
- credential model review;
- network behavior review;
- deterministic-risk-gateway boundary review;
- no direct AI/model/dashboard/agent path review;
- contract mapping review;
- tests that require no real credentials;
- local-only CI behavior;
- rollback plan.

Execution-capable platforms also require:

- `ApprovedOrder`-only input;
- raw `OrderIntent` rejection;
- kill switch;
- idempotency key;
- `ExecutionReport`;
- audit event;
- no withdrawal permission;
- no transfer permission;
- no private endpoints until separately approved;
- human approval.

## Non-Goals

This document does not approve:

- runtime integration;
- dependency installation;
- SDK installation;
- Docker services;
- API clients;
- TradingView webhook runtime;
- Alpaca, IBKR, LEAN, Hummingbot, MetaTrader, cTrader, NinjaTrader, TradeStation or commercial bot SDKs;
- network calls;
- credentials or environment variables;
- trading logic;
- market data ingestion;
- backtest runtime;
- paper trading runtime;
- feature store runtime;
- model training;
- `SignalCandidate`, `OrderIntent`, `RiskDecision`, `ApprovedOrder` or `ExecutionReport` creation;
- execution approval;
- bypassing deterministic-risk-gateway.
