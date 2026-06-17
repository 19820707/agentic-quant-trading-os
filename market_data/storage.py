from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .interfaces import MarketDataEvent, MarketDataWriter
from .normalization import event_to_record


class InMemoryMarketDataWriter:
    def __init__(self) -> None:
        self.events: list[MarketDataEvent] = []

    def write_event(self, event: MarketDataEvent) -> None:
        self.events.append(event)

    def write_many(self, events: Iterable[MarketDataEvent]) -> None:
        for event in events:
            self.write_event(event)


class JsonLinesMarketDataWriter:
    def __init__(self, path: Path):
        self.path = path

    def write_event(self, event: MarketDataEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as output:
            output.write(json.dumps(event_to_record(event), sort_keys=True))
            output.write("\n")

    def write_many(self, events: Iterable[MarketDataEvent]) -> None:
        for event in events:
            self.write_event(event)


def ensure_writer(writer: MarketDataWriter) -> MarketDataWriter:
    return writer
