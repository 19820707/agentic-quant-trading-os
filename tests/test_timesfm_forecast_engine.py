from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import sys
from tempfile import TemporaryDirectory
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from forecasting import (
    DeterministicForecastBackend,
    TimeSeriesForecastRequest,
    TimesFMCheckpointUnavailable,
    TimesFMConfig,
    TimesFMFeatureDisabled,
    TimesFMForecastEngine,
    create_timesfm_engine,
)
from packages.contracts import ContractValidator


NOW = datetime(2026, 6, 19, 12, 3, tzinfo=timezone.utc)


class TimesFMForecastEngineTests(unittest.TestCase):
    def test_deterministic_backend_produces_numeric_forecast_only(self) -> None:
        engine = TimesFMForecastEngine(
            TimesFMConfig(enabled=True, max_context=32, max_horizon=8),
            DeterministicForecastBackend(),
        )

        result = engine.forecast(self._request(), generated_at=NOW + timedelta(seconds=1))

        self.assertEqual(result.point_forecast, (Decimal("104"), Decimal("105"), Decimal("106")))
        self.assertEqual(result.quantile_forecasts["p10"], (Decimal("102.96"), Decimal("103.95"), Decimal("104.94")))
        self.assertFalse(result.signal_created)
        self.assertFalse(result.order_intent_allowed)
        self.assertFalse(result.execution_allowed)
        self.assertFalse(result.network_used)
        self.assertFalse(result.credentials_used)

    def test_request_requires_point_in_time_regular_context(self) -> None:
        with self.assertRaises(ValueError):
            self._request(context_end=NOW + timedelta(minutes=1))

        with self.assertRaises(ValueError):
            self._request(context_start=NOW - timedelta(minutes=2))

        with self.assertRaises(ValueError):
            self._request(network_allowed=True)

    def test_engine_enforces_context_and_horizon_limits(self) -> None:
        engine = TimesFMForecastEngine(
            TimesFMConfig(enabled=True, max_context=3, max_horizon=2),
            DeterministicForecastBackend(),
        )

        with self.assertRaises(ValueError):
            engine.forecast(self._request(), generated_at=NOW)

    def test_factory_is_disabled_and_checkpoint_closed_by_default(self) -> None:
        with self.assertRaises(TimesFMFeatureDisabled):
            create_timesfm_engine(TimesFMConfig())

        with self.assertRaises(TimesFMCheckpointUnavailable):
            create_timesfm_engine(TimesFMConfig(enabled=True))

        with TemporaryDirectory() as directory:
            missing = Path(directory) / "missing-checkpoint"
            with self.assertRaises(TimesFMCheckpointUnavailable):
                create_timesfm_engine(TimesFMConfig(enabled=True, local_checkpoint_path=missing))

    def test_factory_uses_official_timesfm_2p5_api_with_local_checkpoint(self) -> None:
        compiled_configs: list[dict[str, object]] = []

        class FakeForecastConfig:
            def __init__(self, **kwargs: object) -> None:
                compiled_configs.append(kwargs)

        class FakeModel:
            def compile(self, config: object) -> None:
                self.config = config

            def forecast(self, *, horizon: int, inputs: list[list[float]]):
                points = [[104.0, 105.0, 106.0]]
                quantiles = [
                    [
                        [104.0, 102.96, 103.0, 103.2, 103.5, 104.0, 104.4, 104.7, 105.0, 105.04],
                        [105.0, 103.95, 104.0, 104.2, 104.5, 105.0, 105.4, 105.7, 106.0, 106.05],
                        [106.0, 104.94, 105.0, 105.2, 105.5, 106.0, 106.4, 106.7, 107.0, 107.06],
                    ]
                ]
                self.last_horizon = horizon
                self.last_inputs = inputs
                return points, quantiles

        class FakeModelClass:
            @staticmethod
            def from_pretrained(source: str) -> FakeModel:
                self.assertTrue(Path(source).exists())
                return FakeModel()

        class FakeTimesFMModule:
            TimesFM_2p5_200M_torch = FakeModelClass
            ForecastConfig = FakeForecastConfig

        with TemporaryDirectory() as directory:
            checkpoint = Path(directory) / "timesfm-checkpoint"
            checkpoint.mkdir()
            config = TimesFMConfig(enabled=True, local_checkpoint_path=checkpoint, max_context=32, max_horizon=8)
            with patch("forecasting.timesfm_engine.importlib.import_module", return_value=FakeTimesFMModule()):
                engine = create_timesfm_engine(config)
                result = engine.forecast(self._request(), generated_at=NOW + timedelta(seconds=1))

        self.assertEqual(result.backend, "timesfm_2p5_200m_torch")
        self.assertEqual(result.point_forecast, (Decimal("104.0"), Decimal("105.0"), Decimal("106.0")))
        self.assertEqual(result.quantile_forecasts["p10"][0], Decimal("102.96"))
        self.assertEqual(compiled_configs[0]["max_context"], 32)
        self.assertEqual(compiled_configs[0]["max_horizon"], 8)

    def test_packaging_declares_pinned_optional_timesfm_extra(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with (root / "pyproject.toml").open("rb") as pyproject_file:
            pyproject = tomllib.load(pyproject_file)

        self.assertEqual(
            pyproject["project"]["optional-dependencies"]["timesfm"],
            ["timesfm[torch]==2.0.1"],
        )
        self.assertIn("forecasting*", pyproject["tool"]["setuptools"]["packages"]["find"]["include"])

    def test_importing_forecasting_does_not_import_timesfm(self) -> None:
        self.assertNotIn("timesfm", sys.modules)

    def test_contract_fixtures_validate(self) -> None:
        validator = ContractValidator()
        request_payload = {
            "schema_version": "0.1.0",
            "trace_id": "trace_timesfm_test",
            "correlation_id": "corr_timesfm_test",
            "forecast_request_id": "tsfreq_test_001",
            "series_id": "paper_btc_usdt_close_1m",
            "model_id": "google/timesfm-2.5-200m-pytorch",
            "created_at": NOW.isoformat(),
            "observed_at": NOW.isoformat(),
            "context_start": (NOW - timedelta(minutes=3)).isoformat(),
            "context_end": NOW.isoformat(),
            "frequency_seconds": 60,
            "context_values": [100, 101, 102, 103],
            "horizon": 3,
            "point_in_time_enforced": True,
            "network_allowed": False,
            "credentials_allowed": False,
            "execution_allowed": False,
        }

        result = validator.validate("ml", "time_series_forecast_request", request_payload)

        self.assertTrue(result.valid, result.errors)

    def test_module_exposes_no_execution_methods(self) -> None:
        import forecasting.timesfm_engine as module

        forbidden = {
            "buy",
            "sell",
            "order",
            "submit_order",
            "cancel_order",
            "edit_order",
            "withdraw",
            "transfer",
            "execute",
            "create_order",
        }

        self.assertTrue(forbidden.isdisjoint(dir(module)))

    def _request(self, **overrides: object) -> TimeSeriesForecastRequest:
        values = {
            "forecast_request_id": "tsfreq_test_001",
            "series_id": "paper_btc_usdt_close_1m",
            "model_id": "google/timesfm-2.5-200m-pytorch",
            "created_at": NOW,
            "observed_at": NOW,
            "context_start": NOW - timedelta(minutes=3),
            "context_end": NOW,
            "frequency_seconds": 60,
            "context_values": (Decimal("100"), Decimal("101"), Decimal("102"), Decimal("103")),
            "horizon": 3,
            "trace_id": "trace_timesfm_test",
            "correlation_id": "corr_timesfm_test",
        }
        values.update(overrides)
        return TimeSeriesForecastRequest(**values)


if __name__ == "__main__":
    unittest.main()
