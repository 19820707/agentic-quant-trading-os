from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any

from packages.domain import AuditEvent, CorrelationId
from packages.domain.base import deterministic_id, require_aware_datetime, require_decimal, require_non_empty, require_non_negative


class ObservabilityError(ValueError):
    """Raised when local observability input violates scaffold constraints."""


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class MetricKind(str, Enum):
    COUNTER = "COUNTER"
    GAUGE = "GAUGE"


SENSITIVE_ATTRIBUTE_MARKERS = (
    "credential",
    "key",
    "password",
    "private",
    "secret",
    "token",
)

PROHIBITED_OBSERVABILITY_METHOD_NAMES = frozenset(
    {
        "buy",
        "sell",
        "order",
        "submit_order",
        "cancel_order",
        "edit_order",
        "withdraw",
        "transfer",
        "execute",
        "send",
        "post",
        "publish_external",
    }
)


@dataclass(frozen=True)
class StructuredLogRecord:
    log_id: str
    occurred_at: datetime
    level: LogLevel
    component: str
    message: str
    correlation_id: CorrelationId
    attributes: dict[str, str | int | Decimal | bool | None] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_non_empty(self.log_id, "log_id")
        require_aware_datetime(self.occurred_at, "occurred_at")
        require_non_empty(self.component, "component")
        require_non_empty(self.message, "message")
        object.__setattr__(self, "attributes", sanitize_attributes(self.attributes))


@dataclass(frozen=True)
class MetricPoint:
    name: str
    kind: MetricKind
    value: Decimal
    observed_at: datetime
    tags: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_non_empty(self.name, "metric_name")
        require_decimal(self.value, "metric_value")
        require_aware_datetime(self.observed_at, "observed_at")
        if any(_is_sensitive_key(key) or _is_sensitive_key(value) for key, value in self.tags.items()):
            raise ObservabilityError("metric tags must not contain sensitive identifiers")


@dataclass(frozen=True)
class MetricsSnapshot:
    captured_at: datetime
    counters: dict[str, Decimal]
    gauges: dict[str, Decimal]

    def __post_init__(self) -> None:
        require_aware_datetime(self.captured_at, "captured_at")


@dataclass(frozen=True)
class TraceReport:
    correlation_id: CorrelationId
    generated_at: datetime
    audit_event_count: int
    log_count: int
    actors: tuple[str, ...]
    subjects: tuple[str, ...]
    outcomes: tuple[str, ...]
    first_event_at: datetime | None
    last_event_at: datetime | None
    missing_causation_count: int
    causal_edges: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        require_aware_datetime(self.generated_at, "generated_at")
        if self.audit_event_count < 0 or self.log_count < 0 or self.missing_causation_count < 0:
            raise ObservabilityError("trace counts must be non-negative")


class LocalObservabilitySink:
    """In-memory observability sink for local scaffold execution.

    This sink does not open sockets, write files, export telemetry, call network
    endpoints, read credentials, or approve any trading operation.
    """

    def __init__(self) -> None:
        _assert_no_prohibited_surface(self)
        self._audit_events: list[AuditEvent] = []
        self._logs: list[StructuredLogRecord] = []
        self._counters: dict[str, Decimal] = {}
        self._gauges: dict[str, Decimal] = {}
        self._metric_points: list[MetricPoint] = []

    @property
    def audit_events(self) -> tuple[AuditEvent, ...]:
        return tuple(sorted(self._audit_events, key=lambda event: (event.occurred_at, event.audit_event_id)))

    @property
    def logs(self) -> tuple[StructuredLogRecord, ...]:
        return tuple(sorted(self._logs, key=lambda record: (record.occurred_at, record.log_id)))

    @property
    def metric_points(self) -> tuple[MetricPoint, ...]:
        return tuple(self._metric_points)

    def record_audit_event(self, event: AuditEvent) -> None:
        self._audit_events.append(event)
        self.increment_counter(
            "audit_events_total",
            tags={"actor": event.actor, "event_type": event.event_type.value, "outcome": event.outcome},
            observed_at=event.occurred_at,
        )

    def log(
        self,
        *,
        level: LogLevel,
        component: str,
        message: str,
        correlation_id: CorrelationId,
        occurred_at: datetime | None = None,
        attributes: dict[str, str | int | Decimal | bool | None] | None = None,
    ) -> StructuredLogRecord:
        timestamp = occurred_at or datetime.now(timezone.utc)
        record = StructuredLogRecord(
            log_id=deterministic_id("log", correlation_id.value, component, message, timestamp.isoformat()),
            occurred_at=timestamp,
            level=level,
            component=component,
            message=message,
            correlation_id=correlation_id,
            attributes=attributes or {},
        )
        self._logs.append(record)
        self.increment_counter(
            "logs_total",
            tags={"component": component, "level": level.value},
            observed_at=timestamp,
        )
        return record

    def increment_counter(
        self,
        name: str,
        *,
        amount: Decimal = Decimal("1"),
        observed_at: datetime | None = None,
        tags: dict[str, str] | None = None,
    ) -> MetricPoint:
        require_non_negative(amount, "counter_amount")
        timestamp = observed_at or datetime.now(timezone.utc)
        metric_key = _metric_key(name, tags or {})
        new_value = self._counters.get(metric_key, Decimal("0")) + amount
        self._counters[metric_key] = new_value
        point = MetricPoint(name=metric_key, kind=MetricKind.COUNTER, value=new_value, observed_at=timestamp, tags=tags or {})
        self._metric_points.append(point)
        return point

    def set_gauge(
        self,
        name: str,
        value: Decimal,
        *,
        observed_at: datetime | None = None,
        tags: dict[str, str] | None = None,
    ) -> MetricPoint:
        require_decimal(value, "gauge_value")
        timestamp = observed_at or datetime.now(timezone.utc)
        metric_key = _metric_key(name, tags or {})
        self._gauges[metric_key] = value
        point = MetricPoint(name=metric_key, kind=MetricKind.GAUGE, value=value, observed_at=timestamp, tags=tags or {})
        self._metric_points.append(point)
        return point

    def record_backtest_metrics(
        self,
        *,
        backtest_id: str,
        correlation_id: CorrelationId,
        observed_at: datetime,
        metrics: Any,
    ) -> None:
        require_non_empty(backtest_id, "backtest_id")
        for name in (
            "events_seen",
            "signals_emitted",
            "order_intents_created",
            "risk_checks",
            "paper_fills",
        ):
            self.set_gauge(
                f"backtest_{name}",
                Decimal(str(getattr(metrics, name))),
                observed_at=observed_at,
                tags={"backtest_id": backtest_id, "correlation_id": correlation_id.value},
            )
        self.set_gauge(
            "backtest_total_pnl",
            Decimal(str(getattr(metrics, "total_pnl"))),
            observed_at=observed_at,
            tags={"backtest_id": backtest_id, "correlation_id": correlation_id.value},
        )

    def metrics_snapshot(self, *, captured_at: datetime | None = None) -> MetricsSnapshot:
        return MetricsSnapshot(
            captured_at=captured_at or datetime.now(timezone.utc),
            counters=dict(sorted(self._counters.items())),
            gauges=dict(sorted(self._gauges.items())),
        )

    def trace_report(self, correlation_id: CorrelationId, *, generated_at: datetime | None = None) -> TraceReport:
        events = tuple(event for event in self.audit_events if event.correlation_id == correlation_id)
        logs = tuple(log for log in self.logs if log.correlation_id == correlation_id)
        causal_edges = tuple(
            (event.causation_id.value, event.audit_event_id)
            for event in events
            if event.causation_id is not None
        )
        missing_causation_count = sum(1 for event in events if event.causation_id is None)
        return TraceReport(
            correlation_id=correlation_id,
            generated_at=generated_at or datetime.now(timezone.utc),
            audit_event_count=len(events),
            log_count=len(logs),
            actors=tuple(sorted({event.actor for event in events})),
            subjects=tuple(event.subject for event in events),
            outcomes=tuple(event.outcome for event in events),
            first_event_at=events[0].occurred_at if events else None,
            last_event_at=events[-1].occurred_at if events else None,
            missing_causation_count=missing_causation_count,
            causal_edges=causal_edges,
        )


def sanitize_attributes(attributes: dict[str, str | int | Decimal | bool | None]) -> dict[str, str | int | Decimal | bool | None]:
    sanitized: dict[str, str | int | Decimal | bool | None] = {}
    for key, value in attributes.items():
        if _is_sensitive_key(key):
            sanitized[str(key)] = "[REDACTED]"
        else:
            sanitized[str(key)] = value
    return sanitized


def _is_sensitive_key(value: str) -> bool:
    lowered = str(value).lower()
    return any(marker in lowered for marker in SENSITIVE_ATTRIBUTE_MARKERS)


def _metric_key(name: str, tags: dict[str, str]) -> str:
    require_non_empty(name, "metric_name")
    if not tags:
        return name
    rendered_tags = ",".join(f"{key}={tags[key]}" for key in sorted(tags))
    return f"{name}{{{rendered_tags}}}"


def _assert_no_prohibited_surface(target: object) -> None:
    exposed = set(dir(target))
    prohibited = sorted(exposed.intersection(PROHIBITED_OBSERVABILITY_METHOD_NAMES))
    if prohibited:
        raise ObservabilityError(f"observability sink exposes prohibited methods: {', '.join(prohibited)}")
