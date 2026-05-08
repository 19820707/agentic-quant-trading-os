"""Tests for MarketDataAdapterRegistry thread safety and name validation hardening."""

import threading
import unittest
from datetime import datetime, timezone

from packages.common import MarketDataHealth, MarketDataRequest, OrderBookSnapshot
from packages.sdk import (
    DuplicateMarketDataAdapterError,
    MarketDataAdapterRegistry,
    MarketDataAdapterRegistryError,
)

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


class _MinimalAdapter:
    def __init__(self, name: str = "minimal") -> None:
        self._name = name

    def adapter_name(self) -> str:
        return self._name

    def health(self) -> MarketDataHealth:
        return MarketDataHealth(adapter_name=self._name, status="OK", checked_at=NOW, stale=False)

    def fetch_ohlcv(self, r: MarketDataRequest) -> tuple:
        return ()

    def fetch_trades(self, r: MarketDataRequest) -> tuple:
        return ()

    def fetch_order_book(self, r: MarketDataRequest) -> OrderBookSnapshot:
        return OrderBookSnapshot(symbol=r.symbol, venue=r.venue, timestamp=NOW, bids=[], asks=[])

    def fetch_funding_rates(self, r: MarketDataRequest) -> tuple:
        return ()

    def fetch_market_calendar(self, r: MarketDataRequest) -> tuple:
        return ()

    def fetch_economic_calendar(self, r: MarketDataRequest) -> tuple:
        return ()

    def fetch_news(self, r: MarketDataRequest) -> tuple:
        return ()


class ThreadSafetyTests(unittest.TestCase):
    def test_concurrent_unique_registrations_all_succeed(self):
        registry = MarketDataAdapterRegistry()
        names = [f"adapter-{i:04d}" for i in range(50)]
        errors: list[Exception] = []

        def _register(name: str) -> None:
            try:
                registry.register(name, lambda n=name: _MinimalAdapter(n))
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=_register, args=(n,)) for n in names]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(errors), 0, f"unexpected errors: {errors}")
        registered = {info.name for info in registry.list_adapters()}
        self.assertEqual(registered, set(names))

    def test_concurrent_duplicate_registrations_raise_not_corrupt(self):
        registry = MarketDataAdapterRegistry()
        registry.register("shared", _MinimalAdapter)
        duplicate_errors: list[Exception] = []

        def _try_register() -> None:
            try:
                registry.register("shared", _MinimalAdapter)
            except DuplicateMarketDataAdapterError as exc:
                duplicate_errors.append(exc)

        threads = [threading.Thread(target=_try_register) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertGreaterEqual(len(duplicate_errors), 1)
        self.assertEqual(len(registry.list_adapters()), 1)

    def test_concurrent_reads_do_not_raise(self):
        registry = MarketDataAdapterRegistry()
        for i in range(5):
            registry.register(f"reader-{i}", _MinimalAdapter)

        exceptions: list[Exception] = []

        def _read() -> None:
            try:
                registry.list_adapters()
                registry.exists("reader-0")
                registry.get_info("reader-0")
            except Exception as exc:
                exceptions.append(exc)

        threads = [threading.Thread(target=_read) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(exceptions), 0)


class AdapterNameValidationTests(unittest.TestCase):
    def setUp(self):
        self.registry = MarketDataAdapterRegistry()

    def test_valid_names_accepted(self):
        for name in ("adapter", "my-adapter", "adapter-v2", "A", "adapter-registry"):
            with self.subTest(name=name):
                self.registry.register(name, _MinimalAdapter)
                self.assertTrue(self.registry.exists(name))

    def test_digit_leading_name_rejected(self):
        with self.assertRaises(MarketDataAdapterRegistryError):
            self.registry.register("123start", _MinimalAdapter)

    def test_name_with_space_rejected(self):
        with self.assertRaises(MarketDataAdapterRegistryError):
            self.registry.register("has space", _MinimalAdapter)

    def test_name_with_dot_rejected(self):
        with self.assertRaises(MarketDataAdapterRegistryError):
            self.registry.register("dot.name", _MinimalAdapter)

    def test_existing_invalid_names_still_rejected(self):
        for name in ("", "../fixture", "fixture/name", "fixture\\name"):
            with self.subTest(name=name):
                with self.assertRaises(MarketDataAdapterRegistryError):
                    self.registry.register(name, _MinimalAdapter)

    def test_ccxt_readonly_name_is_valid(self):
        from packages.sdk.market_data_adapter_registry import CCXT_READONLY_ADAPTER_NAME
        self.registry.register(CCXT_READONLY_ADAPTER_NAME, _MinimalAdapter)
        self.assertTrue(self.registry.exists(CCXT_READONLY_ADAPTER_NAME))


if __name__ == "__main__":
    unittest.main()
