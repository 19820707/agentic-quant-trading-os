# Configuration

Typed, fail-closed configuration for the platform scaffold.

Current state:

- local/test/paper/staging/production environments are modeled;
- backtest/paper/live trading modes are modeled;
- live trading is disabled by default;
- live mode requires explicit runtime gates;
- production live mode requires a credential reference and secrets-manager controls;
- no secret values should be stored in configuration files.

See `docs/architecture/configuration.md` for policy details.
