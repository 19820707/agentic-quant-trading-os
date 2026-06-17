from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


class AdapterHealthState(str, Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTED = "CONNECTED"
    STALE = "STALE"
    RATE_LIMITED = "RATE_LIMITED"
    ERROR = "ERROR"


@dataclass(frozen=True)
class ReconnectPolicy:
    max_attempts: int = 3
    base_delay_seconds: float = 0.1
    max_delay_seconds: float = 1.0

    def delay_for_attempt(self, attempt: int) -> float:
        if attempt < 1:
            raise ValueError("attempt must be positive")
        return min(self.base_delay_seconds * (2 ** (attempt - 1)), self.max_delay_seconds)


@dataclass(frozen=True)
class RateLimitPolicy:
    max_requests: int
    per_seconds: int

    def __post_init__(self) -> None:
        if self.max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if self.per_seconds <= 0:
            raise ValueError("per_seconds must be positive")


@dataclass(frozen=True)
class AdapterHealth:
    state: AdapterHealthState
    checked_at: datetime
    connected: bool
    stale: bool
    subscriptions: tuple[str, ...]
    last_event_at: datetime | None = None
    message: str = ""


class HeartbeatMonitor:
    def __init__(self, stale_after: timedelta = timedelta(seconds=30)):
        if stale_after.total_seconds() <= 0:
            raise ValueError("stale_after must be positive")
        self.stale_after = stale_after
        self.last_event_at: datetime | None = None

    def mark_event(self, timestamp: datetime | None = None) -> None:
        self.last_event_at = timestamp or datetime.now(timezone.utc)

    def is_stale(self, now: datetime | None = None) -> bool:
        if self.last_event_at is None:
            return True
        current = now or datetime.now(timezone.utc)
        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)
        return current - self.last_event_at > self.stale_after
