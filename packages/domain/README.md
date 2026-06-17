# Domain Models

This package contains local strongly typed domain models for the trading platform scaffold.

Current state:

- pure Python dataclasses and enums;
- Decimal for price, quantity, money, exposure and PnL fields;
- timezone-aware datetime validation;
- deterministic IDs where useful;
- JSON-compatible serialization helpers;
- no broker SDKs;
- no exchange SDKs;
- no network calls;
- no credentials;
- no execution authority.

These models define in-process types only. They do not approve live trading, paper trading, backtesting, strategy runtime, risk approval or execution.
