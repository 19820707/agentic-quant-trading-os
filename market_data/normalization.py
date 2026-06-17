from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from packages.domain import (
    FundingRate,
    OHLCVCandle,
    OpenInterest,
    OrderBookDelta,
    OrderBookLevel,
    OrderBookSnapshot,
    Symbol,
    Ticker,
    Trade,
    Venue,
)
from packages.domain.base import DomainModelError, deterministic_id, parse_decimal

from .errors import MarketDataNormalizationError
from .interfaces import MarketDataEvent


def parse_timestamp(value: object) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, int):
        parsed = datetime.fromtimestamp(value / 1000, tz=timezone.utc)
    elif isinstance(value, str):
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    else:
        raise MarketDataNormalizationError("timestamp must be datetime, ISO string or millisecond integer")

    if parsed.tzinfo is None:
        raise MarketDataNormalizationError("timestamp must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def normalize_trade(raw: dict[str, Any], *, symbol: Symbol, venue: Venue) -> Trade:
    timestamp = parse_timestamp(raw["timestamp"])
    return Trade(
        trade_id=str(raw.get("trade_id") or deterministic_id("trade", symbol.value, venue.value, timestamp.isoformat(), raw["price"], raw["quantity"])),
        symbol=symbol,
        venue=venue,
        timestamp=timestamp,
        price=parse_decimal(raw["price"], "price"),
        quantity=parse_decimal(raw["quantity"], "quantity"),
        side=None if raw.get("side") is None else str(raw["side"]),
    )


def normalize_ticker(raw: dict[str, Any], *, symbol: Symbol, venue: Venue) -> Ticker:
    return Ticker(
        symbol=symbol,
        venue=venue,
        timestamp=parse_timestamp(raw["timestamp"]),
        bid=parse_decimal(raw["bid"], "bid"),
        ask=parse_decimal(raw["ask"], "ask"),
        last=parse_decimal(raw["last"], "last"),
    )


def normalize_ohlcv(raw: dict[str, Any], *, symbol: Symbol, venue: Venue) -> OHLCVCandle:
    return OHLCVCandle(
        symbol=symbol,
        venue=venue,
        timestamp=parse_timestamp(raw["timestamp"]),
        open=parse_decimal(raw["open"], "open"),
        high=parse_decimal(raw["high"], "high"),
        low=parse_decimal(raw["low"], "low"),
        close=parse_decimal(raw["close"], "close"),
        volume=parse_decimal(raw["volume"], "volume"),
    )


def normalize_order_book_snapshot(raw: dict[str, Any], *, symbol: Symbol, venue: Venue) -> OrderBookSnapshot:
    return OrderBookSnapshot(
        symbol=symbol,
        venue=venue,
        timestamp=parse_timestamp(raw["timestamp"]),
        bids=tuple(_level(item) for item in raw.get("bids", ())),
        asks=tuple(_level(item) for item in raw.get("asks", ())),
    )


def normalize_order_book_delta(raw: dict[str, Any], *, symbol: Symbol, venue: Venue) -> OrderBookDelta:
    return OrderBookDelta(
        symbol=symbol,
        venue=venue,
        timestamp=parse_timestamp(raw["timestamp"]),
        sequence=int(raw["sequence"]),
        bid_updates=tuple(_level(item) for item in raw.get("bid_updates", ())),
        ask_updates=tuple(_level(item) for item in raw.get("ask_updates", ())),
    )


def normalize_funding_rate(raw: dict[str, Any], *, symbol: Symbol, venue: Venue) -> FundingRate:
    return FundingRate(
        symbol=symbol,
        venue=venue,
        timestamp=parse_timestamp(raw["timestamp"]),
        funding_rate=parse_decimal(raw["funding_rate"], "funding_rate"),
    )


def normalize_open_interest(raw: dict[str, Any], *, symbol: Symbol, venue: Venue) -> OpenInterest:
    notional = raw.get("notional")
    return OpenInterest(
        symbol=symbol,
        venue=venue,
        timestamp=parse_timestamp(raw["timestamp"]),
        quantity=parse_decimal(raw["quantity"], "quantity"),
        notional=None if notional is None else parse_decimal(notional, "notional"),
    )


def normalize_event(raw: dict[str, Any]) -> MarketDataEvent:
    try:
        event_type = str(raw["event_type"])
        symbol = Symbol(str(raw["symbol"]))
        venue = Venue(str(raw["venue"]))
        payload = raw["payload"]
        if not isinstance(payload, dict):
            raise MarketDataNormalizationError("payload must be an object")
        if event_type == "trade":
            return normalize_trade(payload, symbol=symbol, venue=venue)
        if event_type == "ticker":
            return normalize_ticker(payload, symbol=symbol, venue=venue)
        if event_type == "ohlcv":
            return normalize_ohlcv(payload, symbol=symbol, venue=venue)
        if event_type == "order_book_snapshot":
            return normalize_order_book_snapshot(payload, symbol=symbol, venue=venue)
        if event_type == "order_book_delta":
            return normalize_order_book_delta(payload, symbol=symbol, venue=venue)
        if event_type == "funding_rate":
            return normalize_funding_rate(payload, symbol=symbol, venue=venue)
        if event_type == "open_interest":
            return normalize_open_interest(payload, symbol=symbol, venue=venue)
    except KeyError as exc:
        raise MarketDataNormalizationError(f"missing raw event field: {exc.args[0]}") from exc
    except (DomainModelError, ValueError, TypeError) as exc:
        raise MarketDataNormalizationError(str(exc)) from exc

    raise MarketDataNormalizationError(f"unsupported event_type: {event_type}")


def event_type_for(event: MarketDataEvent) -> str:
    if isinstance(event, Trade):
        return "trade"
    if isinstance(event, Ticker):
        return "ticker"
    if isinstance(event, OHLCVCandle):
        return "ohlcv"
    if isinstance(event, OrderBookSnapshot):
        return "order_book_snapshot"
    if isinstance(event, OrderBookDelta):
        return "order_book_delta"
    if isinstance(event, FundingRate):
        return "funding_rate"
    if isinstance(event, OpenInterest):
        return "open_interest"
    raise MarketDataNormalizationError(f"unsupported domain event: {type(event).__name__}")


def event_to_record(event: MarketDataEvent) -> dict[str, object]:
    return {
        "event_type": event_type_for(event),
        "symbol": event.symbol.value,
        "venue": event.venue.value,
        "payload": event.to_dict(),
    }


def _level(item: object) -> OrderBookLevel:
    if isinstance(item, dict):
        return OrderBookLevel(price=parse_decimal(item["price"], "price"), quantity=parse_decimal(item["quantity"], "quantity"))
    if not isinstance(item, (list, tuple)) or len(item) < 2:
        raise MarketDataNormalizationError("order book level must be [price, quantity]")
    return OrderBookLevel(price=parse_decimal(item[0], "price"), quantity=parse_decimal(item[1], "quantity"))
