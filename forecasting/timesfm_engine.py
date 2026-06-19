from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
import importlib
from pathlib import Path
from typing import Protocol, runtime_checkable

from packages.domain.base import (
    SerializableModel,
    deterministic_id,
    require_aware_datetime,
    require_decimal,
    require_non_empty,
    require_positive,
)


class TimesFMError(ValueError):
    """Base error for the isolated TimesFM forecasting boundary."""


class TimesFMFeatureDisabled(TimesFMError):
    """Raised when TimesFM runtime has not been explicitly enabled."""


class TimesFMDependencyUnavailable(TimesFMError):
    """Raised when the optional official TimesFM package is unavailable."""


class TimesFMCheckpointUnavailable(TimesFMError):
    """Raised when no approved local or explicitly remote checkpoint is available."""


@dataclass(frozen=True)
class TimesFMConfig:
    enabled: bool = False
    package_version: str = "2.0.1"
    model_id: str = "google/timesfm-2.5-200m-pytorch"
    local_checkpoint_path: Path | None = None
    allow_remote_checkpoint_download: bool = False
    max_context: int = 1024
    max_horizon: int = 256
    normalize_inputs: bool = True
    use_continuous_quantile_head: bool = True
    force_flip_invariance: bool = True
    infer_is_positive: bool = True
    fix_quantile_crossing: bool = True

    def __post_init__(self) -> None:
        require_non_empty(self.package_version, "package_version")
        require_non_empty(self.model_id, "model_id")
        if not isinstance(self.max_context, int) or self.max_context < 2 or self.max_context > 16384:
            raise TimesFMError("max_context must be an integer between 2 and 16384")
        if not isinstance(self.max_horizon, int) or self.max_horizon < 1 or self.max_horizon > 1000:
            raise TimesFMError("max_horizon must be an integer between 1 and 1000")
        if self.local_checkpoint_path is not None and not isinstance(self.local_checkpoint_path, Path):
            raise TimesFMError("local_checkpoint_path must be pathlib.Path")


@dataclass(frozen=True)
class TimeSeriesForecastRequest(SerializableModel):
    forecast_request_id: str
    series_id: str
    model_id: str
    created_at: datetime
    observed_at: datetime
    context_start: datetime
    context_end: datetime
    frequency_seconds: int
    context_values: tuple[Decimal, ...]
    horizon: int
    trace_id: str
    correlation_id: str
    point_in_time_enforced: bool = True
    network_allowed: bool = False
    credentials_allowed: bool = False
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        require_non_empty(self.forecast_request_id, "forecast_request_id")
        require_non_empty(self.series_id, "series_id")
        require_non_empty(self.model_id, "model_id")
        require_non_empty(self.trace_id, "trace_id")
        require_non_empty(self.correlation_id, "correlation_id")
        require_aware_datetime(self.created_at, "created_at")
        require_aware_datetime(self.observed_at, "observed_at")
        require_aware_datetime(self.context_start, "context_start")
        require_aware_datetime(self.context_end, "context_end")
        if self.context_start > self.context_end:
            raise TimesFMError("context_start must not be after context_end")
        if self.context_end > self.observed_at:
            raise TimesFMError("context_end must not be after observed_at")
        if not isinstance(self.frequency_seconds, int) or self.frequency_seconds <= 0:
            raise TimesFMError("frequency_seconds must be a positive integer")
        if len(self.context_values) < 2:
            raise TimesFMError("at least two context values are required")
        for index, value in enumerate(self.context_values):
            require_decimal(value, f"context_values[{index}]")
        expected_span = self.frequency_seconds * (len(self.context_values) - 1)
        actual_span = int((self.context_end - self.context_start).total_seconds())
        if actual_span != expected_span:
            raise TimesFMError("context timestamps must match value count and frequency")
        if not isinstance(self.horizon, int) or self.horizon <= 0:
            raise TimesFMError("horizon must be a positive integer")
        if not self.point_in_time_enforced:
            raise TimesFMError("point-in-time enforcement is mandatory")
        if self.network_allowed or self.credentials_allowed or self.execution_allowed:
            raise TimesFMError("forecast requests cannot enable network, credentials or execution")


@dataclass(frozen=True)
class TimeSeriesForecastResult(SerializableModel):
    forecast_result_id: str
    forecast_request_id: str
    series_id: str
    model_id: str
    model_package_version: str
    generated_at: datetime
    horizon: int
    point_forecast: tuple[Decimal, ...]
    quantile_forecasts: dict[str, tuple[Decimal, ...]] = field(default_factory=dict)
    backend: str = "timesfm"
    local_only: bool = True
    network_used: bool = False
    credentials_used: bool = False
    signal_created: bool = False
    order_intent_allowed: bool = False
    execution_allowed: bool = False

    def __post_init__(self) -> None:
        require_non_empty(self.forecast_result_id, "forecast_result_id")
        require_non_empty(self.forecast_request_id, "forecast_request_id")
        require_non_empty(self.series_id, "series_id")
        require_non_empty(self.model_id, "model_id")
        require_non_empty(self.model_package_version, "model_package_version")
        require_non_empty(self.backend, "backend")
        require_aware_datetime(self.generated_at, "generated_at")
        if not isinstance(self.horizon, int) or self.horizon <= 0:
            raise TimesFMError("horizon must be a positive integer")
        if len(self.point_forecast) != self.horizon:
            raise TimesFMError("point forecast length must equal horizon")
        for index, value in enumerate(self.point_forecast):
            require_decimal(value, f"point_forecast[{index}]")
        for quantile, values in self.quantile_forecasts.items():
            require_non_empty(quantile, "quantile")
            if len(values) != self.horizon:
                raise TimesFMError(f"quantile {quantile} length must equal horizon")
            for index, value in enumerate(values):
                require_decimal(value, f"{quantile}[{index}]")
        if not self.local_only:
            raise TimesFMError("forecast result must remain local_only")
        if (
            self.network_used
            or self.credentials_used
            or self.signal_created
            or self.order_intent_allowed
            or self.execution_allowed
        ):
            raise TimesFMError("forecast result cannot claim network, credentials, signals or execution")


@runtime_checkable
class ForecastBackend(Protocol):
    name: str

    def forecast(
        self,
        values: tuple[Decimal, ...],
        *,
        horizon: int,
    ) -> tuple[tuple[Decimal, ...], dict[str, tuple[Decimal, ...]]]:
        ...


class DeterministicForecastBackend:
    """Deterministic local baseline used for tests and integration dry-runs."""

    name = "deterministic_local_drift"

    def forecast(
        self,
        values: tuple[Decimal, ...],
        *,
        horizon: int,
    ) -> tuple[tuple[Decimal, ...], dict[str, tuple[Decimal, ...]]]:
        drift = values[-1] - values[-2]
        points = tuple(values[-1] + drift * Decimal(step) for step in range(1, horizon + 1))
        lower = tuple(point * Decimal("0.99") for point in points)
        upper = tuple(point * Decimal("1.01") for point in points)
        return points, {"p10": lower, "p90": upper}


class _OfficialTimesFMBackend:
    name = "timesfm_2p5_200m_torch"

    def __init__(self, model: object) -> None:
        self._model = model

    def forecast(
        self,
        values: tuple[Decimal, ...],
        *,
        horizon: int,
    ) -> tuple[tuple[Decimal, ...], dict[str, tuple[Decimal, ...]]]:
        point_output, quantile_output = self._model.forecast(
            horizon=horizon,
            inputs=[[float(value) for value in values]],
        )
        point_row = _first_row(point_output)
        point_forecast = tuple(Decimal(str(value)) for value in point_row)
        quantiles: dict[str, tuple[Decimal, ...]] = {}
        if quantile_output is not None:
            quantile_cube = _to_list(quantile_output)
            first_series = quantile_cube[0]
            labels = ("mean", "p10", "p20", "p30", "p40", "p50", "p60", "p70", "p80", "p90")
            for index, label in enumerate(labels):
                if label == "mean":
                    continue
                values_for_quantile = tuple(Decimal(str(step[index])) for step in first_series)
                quantiles[label] = values_for_quantile
        return point_forecast, quantiles


class TimesFMForecastEngine:
    """Isolated numeric forecasting engine. It cannot create trading objects."""

    def __init__(self, config: TimesFMConfig, backend: ForecastBackend) -> None:
        if not config.enabled:
            raise TimesFMFeatureDisabled("TimesFM forecasting is disabled")
        if not isinstance(backend, ForecastBackend):
            raise TimesFMError("backend must implement ForecastBackend")
        self.config = config
        self.backend = backend

    def forecast(
        self,
        request: TimeSeriesForecastRequest,
        *,
        generated_at: datetime,
    ) -> TimeSeriesForecastResult:
        require_aware_datetime(generated_at, "generated_at")
        if request.model_id != self.config.model_id:
            raise TimesFMError("forecast request model_id does not match engine configuration")
        if len(request.context_values) > self.config.max_context:
            raise TimesFMError("forecast context exceeds configured max_context")
        if request.horizon > self.config.max_horizon:
            raise TimesFMError("forecast horizon exceeds configured max_horizon")
        points, quantiles = self.backend.forecast(request.context_values, horizon=request.horizon)
        return TimeSeriesForecastResult(
            forecast_result_id=deterministic_id(
                "tsfr",
                request.forecast_request_id,
                self.config.model_id,
                generated_at.isoformat(),
            ),
            forecast_request_id=request.forecast_request_id,
            series_id=request.series_id,
            model_id=self.config.model_id,
            model_package_version=self.config.package_version,
            generated_at=generated_at,
            horizon=request.horizon,
            point_forecast=points,
            quantile_forecasts=quantiles,
            backend=self.backend.name,
        )


def create_timesfm_engine(config: TimesFMConfig) -> TimesFMForecastEngine:
    """Create the official TimesFM backend only after explicit enablement."""

    if not config.enabled:
        raise TimesFMFeatureDisabled("TimesFM forecasting is disabled")
    source: str
    if config.local_checkpoint_path is not None:
        checkpoint = config.local_checkpoint_path.resolve()
        if not checkpoint.exists():
            raise TimesFMCheckpointUnavailable(f"local checkpoint does not exist: {checkpoint}")
        source = str(checkpoint)
    elif config.allow_remote_checkpoint_download:
        source = config.model_id
    else:
        raise TimesFMCheckpointUnavailable(
            "no local checkpoint configured and remote checkpoint download is disabled"
        )

    try:
        timesfm = importlib.import_module("timesfm")
    except ModuleNotFoundError as exc:
        raise TimesFMDependencyUnavailable(
            'optional dependency unavailable; install with python -m pip install -e ".[timesfm]"'
        ) from exc

    model_class = getattr(timesfm, "TimesFM_2p5_200M_torch", None)
    forecast_config_class = getattr(timesfm, "ForecastConfig", None)
    if model_class is None or forecast_config_class is None:
        raise TimesFMDependencyUnavailable("installed timesfm package does not expose the 2.5 PyTorch API")

    model = model_class.from_pretrained(source)
    model.compile(
        forecast_config_class(
            max_context=config.max_context,
            max_horizon=config.max_horizon,
            normalize_inputs=config.normalize_inputs,
            use_continuous_quantile_head=config.use_continuous_quantile_head,
            force_flip_invariance=config.force_flip_invariance,
            infer_is_positive=config.infer_is_positive,
            fix_quantile_crossing=config.fix_quantile_crossing,
        )
    )
    return TimesFMForecastEngine(config, _OfficialTimesFMBackend(model))


def _to_list(value: object):
    if hasattr(value, "tolist"):
        return value.tolist()
    return value


def _first_row(value: object):
    rows = _to_list(value)
    return rows[0]
