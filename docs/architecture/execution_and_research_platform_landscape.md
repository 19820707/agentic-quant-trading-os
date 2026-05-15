# Execution and Research Platform Landscape

This document classifies external trading, research, automation and bot platforms as future integration references.

It does not approve installing dependencies, cloning repositories, adding broker SDKs, opening network access, adding credentials, enabling live trading or promoting any runtime path.

## Classification Rule

External platforms may influence architecture, contracts and review gates. They must not bypass the deterministic risk gateway.

Allowed influence:

- research lifecycle design;
- backtest review design;
- paper-trading evidence design;
- connector capability classification;
- operator dashboard workflow references;
- execution report state modeling.

Forbidden influence:

- direct AI/model/dashboard/agent to broker or exchange;
- credentials in agents, dashboards, notebooks or tests;
- raw `OrderIntent` execution;
- live order submission;
- order cancellation;
- transfer or withdrawal;
- production enablement without explicit gates.

## Platform Classification

| Platform | Category | Project use | Recommended state | Integration boundary |
| --- | --- | --- | --- | --- |
| QuantConnect / LEAN | Research and backtesting engine | Reference for research lifecycle, backtest review, portfolio simulation and event-driven architecture | Research reference only | No runtime integration until lineage, leakage, feature, backtest and paper gates exist |
| Interactive Brokers API | Institutional broker execution API | Future controlled execution venue candidate | Blocked | `ApprovedOrder` -> execution-engine adapter -> `ExecutionReport`; never AI/model/dashboard direct |
| Alpaca | Developer-friendly paper/live broker API | Future paper adapter candidate before any live adapter | Blocked until adapter gates | Paper-only first; no credentials until credential vault policy and approval gate exist |
| Hummingbot | Crypto strategy/runtime and connector framework | Reference for connector capability mapping and isolated crypto strategy sandbox design | Isolated review candidate | No central runtime dependency; no exchange keys; no live connector activation |
| TradingView | Signal and alert source | Future webhook signal intake candidate | Contract-only first | Webhook -> intake contract -> `SignalCandidate` -> `RiskReviewInput`; never webhook-to-order |
| 3Commas | Commercial crypto bot platform | UX and workflow reference | Reference only | No runtime integration; no shared credentials |
| Bitsgap | Commercial crypto bot platform | UX and workflow reference | Reference only | No runtime integration; no shared credentials |
| Cryptohopper | Commercial crypto bot platform | UX and workflow reference | Reference only | No runtime integration; no shared credentials |
| Pionex | Exchange/bot product | UX and workflow reference | Reference only | No runtime integration; no shared credentials |
| Coinrule | Rule-based trading automation | Rule builder and operator UX reference | Reference only | Rules may inspire local contracts; no execution dependency |
| NinjaTrader | Futures/traditional trading automation | Future venue family reference | Deferred | Requires separate futures venue gate and adapter policy |
| TradeStation | Futures/equities automation | Future venue family reference | Deferred | Requires separate venue gate and adapter policy |
| MetaTrader 5 | Forex/CFD automation | Future venue family reference | Deferred | Requires plugin/source review and strict credential isolation |
| cTrader | Forex/CFD automation | Future venue family reference | Deferred | Requires plugin/source review and strict credential isolation |

## Required Sequence Before Any Real Integration

1. Dataset lineage and leakage review contracts.
2. Feature store approval gate.
3. Fake offline materialization review.
4. Feature view contracts.
5. Backtest review contract.
6. Paper trading review contract.
7. Signal intake contract.
8. Execution venue capability contract.
9. Broker adapter safety policy.
10. Fail-closed execution adapter interface.
11. Paper execution adapter.
12. Separate dependency/security/credential/runtime approval.

## External Platform Gates

Any future platform-specific PR must answer:

- What category is the platform in?
- Is it reference-only, contract-only, fake-runtime-only, paper-only or live-blocked?
- Does it require credentials?
- Does it call network?
- Does it expose private endpoints?
- Does it expose order submission, cancellation, transfer or withdrawal?
- Can it bypass deterministic-risk-gateway?
- Does it produce or consume `SignalCandidate`, `RiskReviewInput`, `ApprovedOrder` or `ExecutionReport`?
- What rollback exists?
- What evidence is required before promotion?

## Non-Goals

This document does not approve:

- installing QuantConnect/LEAN, IBKR, Alpaca, Hummingbot, TradingView integrations, MT5, cTrader, NinjaTrader, TradeStation or commercial bot platform SDKs;
- cloning external projects;
- copying external project source code;
- adding credentials;
- network tests;
- broker or exchange execution;
- production use.
