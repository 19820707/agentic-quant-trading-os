# External Projects Catalog

This catalog is a placeholder for documenting external projects, tools and libraries considered for future integration.

## Rules

- External projects are reference-only unless explicitly approved.
- Do not clone, vendor, install or add submodules by default.
- Review license, security, maintenance and production suitability before integration.
- FIX engines belong only inside execution-engine adapters.
- Backtesting tools cannot promote strategies directly to live trading.
- MCP tools must never receive broker credentials.
- Platform classification lives in `docs/architecture/execution_and_research_platform_landscape.md`.
- Broker/exchange APIs are blocked until a separate execution adapter safety gate approves a controlled scope.
- Commercial bot platforms are UX/reference-only by default and must not receive credentials.

## Current Platform Families

| Family | Examples | Default status |
| --- | --- | --- |
| Research/backtesting | QuantConnect / LEAN | Reference only |
| Broker execution APIs | Interactive Brokers API, Alpaca | Blocked |
| Crypto strategy runtimes | Hummingbot | Isolated review candidate |
| Signal sources | TradingView | Contract-only first |
| Commercial bot platforms | 3Commas, Bitsgap, Cryptohopper, Pionex, Coinrule | Reference only |
| Futures/traditional automation | NinjaTrader, TradeStation | Deferred |
| Forex/CFD automation | MetaTrader 5, cTrader | Deferred |

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

