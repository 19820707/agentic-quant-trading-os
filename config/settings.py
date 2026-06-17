from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping


class ConfigurationError(ValueError):
    """Raised when configuration would enable an unsafe runtime state."""


class Environment(str, Enum):
    LOCAL = "local"
    TEST = "test"
    PAPER = "paper"
    STAGING = "staging"
    PRODUCTION = "production"


class TradingMode(str, Enum):
    DISABLED = "disabled"
    BACKTEST = "backtest"
    PAPER = "paper"
    LIVE = "live"


def _env(environ: Mapping[str, str], *names: str, default: str = "") -> str:
    for name in names:
        value = environ.get(name)
        if value is not None:
            return value.strip()
    return default


def _bool(value: str, *, default: bool = False) -> bool:
    if value == "":
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ConfigurationError(f"invalid boolean value: {value!r}")


def _enum(enum_type: type[Enum], value: str, field_name: str) -> Enum:
    try:
        return enum_type(value.strip().lower())
    except ValueError as exc:
        allowed = ", ".join(item.value for item in enum_type)
        raise ConfigurationError(f"invalid {field_name}: {value!r}; expected one of: {allowed}") from exc


@dataclass(frozen=True)
class DatabaseSettings:
    primary_dsn: str = ""
    timeseries_dsn: str = ""
    object_store_uri: str = ""


@dataclass(frozen=True)
class CacheSettings:
    redis_url: str = ""
    cache_enabled: bool = False


@dataclass(frozen=True)
class BrokerExchangeSettings:
    integration_enabled: bool = False
    default_venue: str = ""
    credential_reference: str = ""
    allow_withdrawals: bool = False
    allow_private_endpoints: bool = False


@dataclass(frozen=True)
class ObservabilitySettings:
    json_logs_enabled: bool = True
    metrics_enabled: bool = False
    tracing_enabled: bool = False
    service_name: str = "agentic-quant-trading-os"


@dataclass(frozen=True)
class SecuritySettings:
    secrets_manager_enabled: bool = False
    require_credential_reference: bool = True
    kill_switch_enabled: bool = True
    rbac_enabled: bool = False
    allow_agent_execution: bool = False


@dataclass(frozen=True)
class AppSettings:
    environment: Environment = Environment.LOCAL
    trading_mode: TradingMode = TradingMode.DISABLED
    live_trading_enabled: bool = False
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    cache: CacheSettings = field(default_factory=CacheSettings)
    broker_exchange: BrokerExchangeSettings = field(default_factory=BrokerExchangeSettings)
    observability: ObservabilitySettings = field(default_factory=ObservabilitySettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)

    def validate(self) -> None:
        if self.live_trading_enabled and self.trading_mode is not TradingMode.LIVE:
            raise ConfigurationError("live_trading_enabled requires trading_mode=live")

        if self.trading_mode is TradingMode.LIVE and not self.live_trading_enabled:
            raise ConfigurationError("trading_mode=live requires live_trading_enabled=true")

        if self.trading_mode in {TradingMode.BACKTEST, TradingMode.PAPER} and self.live_trading_enabled:
            raise ConfigurationError("backtest and paper modes cannot enable live trading")

        if self.broker_exchange.allow_withdrawals:
            raise ConfigurationError("withdrawal permission is never allowed")

        if self.security.allow_agent_execution:
            raise ConfigurationError("agent execution authority is disabled by policy")

        if self.environment is Environment.PRODUCTION:
            self._validate_production()

        if self.live_trading_enabled:
            self._validate_live_trading()

    def _validate_production(self) -> None:
        if not self.security.kill_switch_enabled:
            raise ConfigurationError("production requires kill_switch_enabled=true")
        if self.trading_mode is TradingMode.LIVE and not self.security.rbac_enabled:
            raise ConfigurationError("production live mode requires rbac_enabled=true")

    def _validate_live_trading(self) -> None:
        if not self.broker_exchange.integration_enabled:
            raise ConfigurationError("live mode requires broker/exchange integration to be explicitly enabled")
        if not self.broker_exchange.credential_reference:
            raise ConfigurationError("live mode requires a credential reference, not inline secret values")
        if self.security.require_credential_reference and not self.security.secrets_manager_enabled:
            raise ConfigurationError("live mode requires secrets_manager_enabled=true")
        if self.broker_exchange.allow_private_endpoints and not self.security.rbac_enabled:
            raise ConfigurationError("private endpoint access requires rbac_enabled=true")


def load_settings(environ: Mapping[str, str] | None = None) -> AppSettings:
    source = os.environ if environ is None else environ

    settings = AppSettings(
        environment=_enum(
            Environment,
            _env(source, "AQTOS_ENVIRONMENT", "APP_ENV", default=Environment.LOCAL.value),
            "environment",
        ),
        trading_mode=_enum(
            TradingMode,
            _env(source, "AQTOS_TRADING_MODE", "TRADING_MODE", default=TradingMode.DISABLED.value),
            "trading_mode",
        ),
        live_trading_enabled=_bool(
            _env(source, "AQTOS_LIVE_TRADING_ENABLED", "LIVE_TRADING_ENABLED", default="false")
        ),
        database=DatabaseSettings(
            primary_dsn=_env(source, "AQTOS_DATABASE_DSN"),
            timeseries_dsn=_env(source, "AQTOS_TIMESERIES_DSN"),
            object_store_uri=_env(source, "AQTOS_OBJECT_STORE_URI"),
        ),
        cache=CacheSettings(
            redis_url=_env(source, "AQTOS_REDIS_URL"),
            cache_enabled=_bool(_env(source, "AQTOS_CACHE_ENABLED", default="false")),
        ),
        broker_exchange=BrokerExchangeSettings(
            integration_enabled=_bool(
                _env(source, "AQTOS_BROKER_INTEGRATION_ENABLED", "BROKER_INTEGRATION_ENABLED", default="false")
            ),
            default_venue=_env(source, "AQTOS_DEFAULT_VENUE"),
            credential_reference=_env(source, "AQTOS_BROKER_CREDENTIAL_REFERENCE"),
            allow_withdrawals=_bool(_env(source, "AQTOS_ALLOW_WITHDRAWALS", default="false")),
            allow_private_endpoints=_bool(_env(source, "AQTOS_ALLOW_PRIVATE_ENDPOINTS", default="false")),
        ),
        observability=ObservabilitySettings(
            json_logs_enabled=_bool(_env(source, "AQTOS_JSON_LOGS_ENABLED", default="true"), default=True),
            metrics_enabled=_bool(_env(source, "AQTOS_METRICS_ENABLED", default="false")),
            tracing_enabled=_bool(_env(source, "AQTOS_TRACING_ENABLED", default="false")),
            service_name=_env(source, "AQTOS_SERVICE_NAME", default="agentic-quant-trading-os"),
        ),
        security=SecuritySettings(
            secrets_manager_enabled=_bool(_env(source, "AQTOS_SECRETS_MANAGER_ENABLED", default="false")),
            require_credential_reference=_bool(
                _env(source, "AQTOS_REQUIRE_CREDENTIAL_REFERENCE", default="true"),
                default=True,
            ),
            kill_switch_enabled=_bool(_env(source, "AQTOS_KILL_SWITCH_ENABLED", default="true"), default=True),
            rbac_enabled=_bool(_env(source, "AQTOS_RBAC_ENABLED", default="false")),
            allow_agent_execution=_bool(_env(source, "AQTOS_ALLOW_AGENT_EXECUTION", default="false")),
        ),
    )
    settings.validate()
    return settings
