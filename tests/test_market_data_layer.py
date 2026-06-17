import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from market_data import (
    AdapterHealthState,
    InMemoryMarketDataWriter,
    MarketDataConnectionError,
    MarketDataNormalizationError,
    MarketDataReplayError,
    MarketDataSubscriptionError,
    MockMarketDataAdapter,
    ReplayMarketDataAdapter,
    normalize_event,
    write_replay_file,
)
from market_data.resilience import HeartbeatMonitor, ReconnectPolicy
from packages.domain import (
    OHLCVCandle,
    OrderBookLevel,
    OrderBookSnapshot,
    Symbol,
    Ticker,
    Trade,
    Venue,
)


NOW = datetime(2026, 5, 15, 14, 0, tzinfo=timezone.utc)
SYMBOL = Symbol("BTC/USDT")
VENUE = Venue("paper")


def fixture_events():
    return (
        OHLCVCandle(
            symbol=SYMBOL,
            venue=VENUE,
            timestamp=NOW,
            open=Decimal("100.00"),
            high=Decimal("110.00"),
            low=Decimal("95.00"),
            close=Decimal("105.00"),
            volume=Decimal("10.5"),
        ),
        Trade(
            trade_id="trade_fixture_001",
            symbol=SYMBOL,
            venue=VENUE,
            timestamp=NOW + timedelta(seconds=1),
            price=Decimal("105.25"),
            quantity=Decimal("0.25"),
            side="buy",
        ),
        OrderBookSnapshot(
            symbol=SYMBOL,
            venue=VENUE,
            timestamp=NOW + timedelta(seconds=2),
            bids=(OrderBookLevel(price=Decimal("105.00"), quantity=Decimal("1.0")),),
            asks=(OrderBookLevel(price=Decimal("105.50"), quantity=Decimal("1.5")),),
        ),
    )


class MarketDataLayerTests(unittest.TestCase):
    def test_subscription_lifecycle_requires_connection(self):
        adapter = MockMarketDataAdapter(fixture_events())

        with self.assertRaises(MarketDataConnectionError):
            adapter.subscribe(SYMBOL, VENUE)

        adapter.connect()
        adapter.subscribe(SYMBOL, VENUE)
        self.assertEqual(adapter.health().subscriptions, ("BTC/USDT@paper",))

        adapter.unsubscribe(SYMBOL, VENUE)
        self.assertEqual(adapter.health().subscriptions, ())

        with self.assertRaises(MarketDataSubscriptionError):
            adapter.unsubscribe(SYMBOL, VENUE)

    def test_mock_event_generation_is_deterministic_and_normalized(self):
        adapter = MockMarketDataAdapter(fixture_events())
        adapter.connect()
        adapter.subscribe(SYMBOL, VENUE)

        first_pass = tuple(adapter.stream_events())
        adapter.reset()
        second_pass = tuple(adapter.stream_events())

        self.assertEqual(first_pass, second_pass)
        self.assertIsInstance(first_pass[0], OHLCVCandle)
        self.assertIsInstance(first_pass[1], Trade)
        self.assertIsInstance(first_pass[2], OrderBookSnapshot)

    def test_historical_candles_and_order_book_snapshot(self):
        adapter = MockMarketDataAdapter(fixture_events())
        adapter.connect()

        candles = adapter.get_historical_candles(SYMBOL, VENUE, limit=1)
        snapshot = adapter.get_order_book_snapshot(SYMBOL, VENUE)

        self.assertEqual(len(candles), 1)
        self.assertEqual(candles[0].close, Decimal("105.00"))
        self.assertEqual(snapshot.bids[0].price, Decimal("105.00"))

    def test_replay_adapter_is_deterministic_from_local_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            replay_path = Path(temp_dir) / "market-data-replay.records"
            write_replay_file(replay_path, fixture_events())

            first = ReplayMarketDataAdapter(replay_path)
            second = ReplayMarketDataAdapter(replay_path)
            first.connect()
            second.connect()

            self.assertEqual(tuple(first.stream_events()), tuple(second.stream_events()))

    def test_replay_adapter_reports_invalid_local_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            replay_path = Path(temp_dir) / "bad-replay.records"
            replay_path.write_text('{"event_type": "trade"}\n', encoding="utf-8")

            with self.assertRaises(MarketDataReplayError):
                ReplayMarketDataAdapter(replay_path)

    def test_stale_data_detection_and_reconnect_behavior(self):
        adapter = MockMarketDataAdapter(fixture_events(), stale_after=timedelta(seconds=1))

        self.assertEqual(adapter.health().state, AdapterHealthState.DISCONNECTED)
        adapter.connect()
        self.assertEqual(adapter.health().state, AdapterHealthState.STALE)

        tuple(adapter.stream_events())
        self.assertFalse(adapter.health().stale)

        adapter.disconnect()
        self.assertEqual(adapter.health().state, AdapterHealthState.DISCONNECTED)
        adapter.reconnect()
        self.assertTrue(adapter.connected)

    def test_heartbeat_monitor_marks_old_data_as_stale(self):
        monitor = HeartbeatMonitor(stale_after=timedelta(seconds=5))
        monitor.mark_event(NOW)

        self.assertFalse(monitor.is_stale(NOW + timedelta(seconds=5)))
        self.assertTrue(monitor.is_stale(NOW + timedelta(seconds=6)))

    def test_reconnect_policy_is_bounded(self):
        policy = ReconnectPolicy(max_attempts=3, base_delay_seconds=0.5, max_delay_seconds=1.0)

        self.assertEqual(policy.delay_for_attempt(1), 0.5)
        self.assertEqual(policy.delay_for_attempt(3), 1.0)

    def test_normalization_from_exchange_like_payload(self):
        event = normalize_event(
            {
                "event_type": "ticker",
                "symbol": "BTC/USDT",
                "venue": "paper",
                "payload": {
                    "timestamp": "2026-05-15T14:00:00+00:00",
                    "bid": "100.01",
                    "ask": "100.02",
                    "last": "100.015",
                },
            }
        )

        self.assertIsInstance(event, Ticker)
        self.assertEqual(event.bid, Decimal("100.01"))

    def test_normalization_rejects_float_financial_values(self):
        with self.assertRaises(MarketDataNormalizationError):
            normalize_event(
                {
                    "event_type": "trade",
                    "symbol": "BTC/USDT",
                    "venue": "paper",
                    "payload": {
                        "timestamp": "2026-05-15T14:00:00+00:00",
                        "price": 100.01,
                        "quantity": "1.0",
                    },
                }
            )

    def test_storage_hook_writes_to_memory(self):
        writer = InMemoryMarketDataWriter()
        writer.write_many(fixture_events())

        self.assertEqual(len(writer.events), 3)
        self.assertIsInstance(writer.events[0], OHLCVCandle)

    def test_adapter_exposes_no_execution_methods(self):
        adapter = MockMarketDataAdapter(fixture_events())
        forbidden_names = {
            "buy",
            "sell",
            "order",
            "submit_order",
            "cancel_order",
            "edit_order",
            "withdraw",
            "transfer",
            "execute",
        }

        self.assertTrue(forbidden_names.isdisjoint(dir(adapter)))


if __name__ == "__main__":
    unittest.main()
