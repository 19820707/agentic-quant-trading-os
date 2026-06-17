# Configuration Architecture

## Purpose

The configuration layer defines safe typed settings for the platform scaffold. It separates local, test, paper, staging and production environments while keeping live trading disabled by default.

The current implementation is a local configuration boundary. It does not start services, connect to brokers, connect to exchanges, read credential values, submit orders, run strategies or approve execution.

## Module Boundary

Configuration code lives in `config/settings.py`.

The module models:

- environment;
- trading mode;
- database settings;
- Redis/cache settings;
- broker/exchange settings;
- observability settings;
- security settings.

The implementation uses Python dataclasses and enums to avoid adding a new dependency before the dependency governance layer is ready. A later PR may migrate this to Pydantic Settings after dependency review.

## Safe Defaults

Default state:

- environment: `local`;
- trading mode: `disabled`;
- live trading enabled: `false`;
- broker/exchange integration enabled: `false`;
- withdrawal permission: `false`;
- private endpoint permission: `false`;
- secrets manager enabled: `false`;
- kill switch enabled: `true`;
- agent execution authority: `false`.

These defaults are intentionally inert. They allow local contract and scaffold tests without creating a trading runtime.

## Runtime Validation

The configuration validator rejects unsafe states:

- live trading enabled without `trading_mode=live`;
- `trading_mode=live` without live trading enabled;
- backtest or paper mode with live trading enabled;
- withdrawal permission;
- agent execution authority;
- production with kill switch disabled;
- production live mode without RBAC;
- live mode without broker/exchange integration;
- live mode without a credential reference;
- live mode without secrets-manager controls;
- private endpoint access without RBAC.

## Credential Boundary

Configuration may contain a credential reference, not credential material.

Allowed:

- reference name for a future secrets manager entry;
- empty reference in non-live modes.

Forbidden:

- inline broker secrets;
- inline exchange secrets;
- wallet keys;
- withdrawal keys;
- tokens in repository files;
- values printed in logs or error messages.

## Mode Separation

Backtest, paper and live modes are mutually separated.

- Backtest mode must not enable live trading.
- Paper mode must not enable live trading.
- Live mode requires explicit live flag, broker/exchange integration flag, credential reference, secrets-manager controls, kill switch and production RBAC if running in production.

This module does not approve backtesting, paper trading or live trading. It only defines the validation boundary for later runtime work.

## Environment File

`.env.example` documents supported variable names with safe empty or false defaults. It must not contain real credentials or production values.

## Non-Goals

- no strategy runtime;
- no exchange adapter;
- no broker adapter;
- no market data ingestion;
- no paper exchange;
- no OMS runtime;
- no production deployment;
- no secrets manager implementation;
- no live trading enablement.
