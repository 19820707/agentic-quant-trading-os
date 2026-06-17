from __future__ import annotations

import json
from collections import deque
from collections.abc import Iterable, Iterator
from datetime import datetime, timedelta, timezone
from pathlib import Path

from packages.domain import OHLCVCandle, OrderBookSnapshot, Symbol, Venue

from .errors import MarketDataConnectionError, MarketDataReplayError, MarketDataSubscriptionError
from .interfaces import MarketDataEvent
from .normalization import event_to_record, normalize_event
from .resilience import AdapterHealth, AdapterHealthState, HeartbeatMonitor, ReconnectPolicy


class BaseLocalMarketDataAdapter:
    def __init__(
        self,
        *,
        reconnect_policy: ReconnectPolicy | None = None,
        stale_after: timedelta = timedelta(seconds=30),
    ) -> None:
        self.connected = False
        self.subscriptions: set[tuple[str, str]] = set()
        self.reconnect_policy = reconnect_policy or ReconnectPolicy()
        self.heartbeat = HeartbeatMonitor(stale_after=stale_after)
        self.last_error: str = ""

    def connect(self) -> None:
        self.connected = True
        self.last_error = ""

    def disconnect(self) -> None:
        self.connected = False

    def reconnect(self) -> None:
        self.disconnect()
        self.connect()

    def subscribe(self, symbol: Symbol, venue: Venue) -> None:
        self._require_connected()
        self.subscriptions.add((symbol.value, venue.value))

    def unsubscribe(self, symbol: Symbol, venue: Venue) -> None:
        self._require_connected()
        key = (symbol.value, venue.value)
        if key not in self.subscriptions:
            raise MarketDataSubscriptionError(f"subscription does not exist: {symbol.value}@{venue.value}")
        self.subscriptions.remove(key)

    def health(self) -> AdapterHealth:
        stale = self.heartbeat.is_stale()
        if not self.connected:
            state = AdapterHealthState.DISCONNECTED
        elif stale:
            state = AdapterHealthState.STALE
        else:
            state = AdapterHealthState.CONNECTED
        return AdapterHealth(
            state=state,
            checked_at=datetime.now(timezone.utc),
            connected=self.connected,
            stale=stale,
            subscriptions=tuple(f"{symbol}@{venue}" for symbol, venue in sorted(self.subscriptions)),
            last_event_at=self.heartbeat.last_event_at,
            message=self.last_error,
        )

    def _require_connected(self) -> None:
        if not self.connected:
            raise MarketDataConnectionError("market data adapter is not connected")

    def _is_subscribed(self, event: MarketDataEvent) -> bool:
        return (event.symbol.value, event.venue.value) in self.subscriptions


class MockMarketDataAdapter(BaseLocalMarketDataAdapter):
    def __init__(self, events: Iterable[MarketDataEvent], **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._events = tuple(events)
        self._queue: deque[MarketDataEvent] = deque(self._events)

    def get_historical_candles(
        self,
        symbol: Symbol,
        venue: Venue,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> tuple[OHLCVCandle, ...]:
        self._require_connected()
        candles = tuple(
            event for event in self._events
            if isinstance(event, OHLCVCandle)
            and event.symbol == symbol
            and event.venue == venue
            and (start is None or event.timestamp >= start)
            and (end is None or event.timestamp <= end)
        )
        return candles if limit is None else candles[:limit]

    def get_order_book_snapshot(self, symbol: Symbol, venue: Venue) -> OrderBookSnapshot:
        self._require_connected()
        matches = tuple(
            event for event in self._events
            if isinstance(event, OrderBookSnapshot) and event.symbol == symbol and event.venue == venue
        )
        if not matches:
            raise MarketDataReplayError(f"no order book snapshot for {symbol.value}@{venue.value}")
        return matches[-1]

    def stream_events(self) -> Iterator[MarketDataEvent]:
        self._require_connected()
        while self._queue:
            event = self._queue.popleft()
            if self.subscriptions and not self._is_subscribed(event):
                continue
            self.heartbeat.mark_event()
            yield event

    def reset(self) -> None:
        self._queue = deque(self._events)


class ReplayMarketDataAdapter(MockMarketDataAdapter):
    def __init__(self, path: Path, **kwargs: object) -> None:
        self.path = path
        super().__init__(self._load_events(path), **kwargs)

    @staticmethod
    def _load_events(path: Path) -> tuple[MarketDataEvent, ...]:
        if not path.exists():
            raise MarketDataReplayError(f"replay file does not exist: {path}")
        events: list[MarketDataEvent] = []
        with path.open(encoding="utf-8") as source:
            for line_number, line in enumerate(source, start=1):
                if not line.strip():
                    continue
                try:
                    events.append(normalize_event(json.loads(line)))
                except Exception as exc:
                    raise MarketDataReplayError(f"invalid replay event at line {line_number}: {exc}") from exc
        return tuple(events)


def write_replay_file(path: Path, events: Iterable[MarketDataEvent]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        for event in events:
            output.write(json.dumps(event_to_record(event), sort_keys=True))
            output.write("\n")
