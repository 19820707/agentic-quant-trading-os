from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from .base import SerializableModel, parse_datetime, require_aware_datetime, require_non_empty


@dataclass(frozen=True)
class CorrelationId(SerializableModel):
    value: str

    def __post_init__(self) -> None:
        require_non_empty(self.value, "correlation_id")


@dataclass(frozen=True)
class CausationId(SerializableModel):
    value: str

    def __post_init__(self) -> None:
        require_non_empty(self.value, "causation_id")


class AuditEventType(str, Enum):
    CONFIG_VALIDATED = "CONFIG_VALIDATED"
    SIGNAL_CREATED = "SIGNAL_CREATED"
    ORDER_INTENT_CREATED = "ORDER_INTENT_CREATED"
    RISK_CHECKED = "RISK_CHECKED"
    ORDER_STATE_CHANGED = "ORDER_STATE_CHANGED"
    PORTFOLIO_SNAPSHOT_CREATED = "PORTFOLIO_SNAPSHOT_CREATED"
    SECURITY_POLICY_CHECKED = "SECURITY_POLICY_CHECKED"


@dataclass(frozen=True)
class AuditEvent(SerializableModel):
    audit_event_id: str
    event_type: AuditEventType
    occurred_at: datetime
    correlation_id: CorrelationId
    causation_id: CausationId | None
    actor: str
    subject: str
    outcome: str
    metadata: dict[str, str | int | bool | None] = field(default_factory=dict)

    def __post_init__(self) -> None:
        require_non_empty(self.audit_event_id, "audit_event_id")
        require_aware_datetime(self.occurred_at, "occurred_at")
        require_non_empty(self.actor, "actor")
        require_non_empty(self.subject, "subject")
        require_non_empty(self.outcome, "outcome")

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AuditEvent":
        causation = data.get("causation_id")
        return cls(
            audit_event_id=str(data["audit_event_id"]),
            event_type=AuditEventType(str(data["event_type"])),
            occurred_at=parse_datetime(data["occurred_at"], "occurred_at"),
            correlation_id=CorrelationId(str(data["correlation_id"]["value"])),
            causation_id=None if causation is None else CausationId(str(causation["value"])),
            actor=str(data["actor"]),
            subject=str(data["subject"]),
            outcome=str(data["outcome"]),
            metadata=dict(data.get("metadata", {})),
        )
