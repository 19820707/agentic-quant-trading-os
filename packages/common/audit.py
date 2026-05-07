"""Local structured AuditEvent builder.

This module builds redacted AuditEvent-like dictionaries for future audit sinks.
It does not persist events, publish messages, call network, import services,
interpret trading semantics, approve risk, approve execution, or access
credentials.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone
from typing import Final
from uuid import uuid4

from packages.common.security import redact_secrets

SCHEMA_VERSION: Final[str] = "0.1.0"

ALLOWED_OUTCOMES: Final[frozenset[str]] = frozenset(
    {"APPROVED", "REJECTED", "ERROR", "INFO", "WARN", "SKIPPED", "SUCCESS"}
)

ALLOWED_LIFECYCLE_ID_KEYS: Final[frozenset[str]] = frozenset(
    {
        "dataset_snapshot_id",
        "model_version",
        "prediction_id",
        "signal_id",
        "order_intent_id",
        "risk_decision_id",
        "approved_order_id",
        "execution_order_id",
        "execution_report_id",
        "fill_id",
        "portfolio_update_id",
        "policy_decision_id",
        "incident_id",
    }
)


class AuditEventBuildError(ValueError):
    """Raised when a structured audit event cannot be safely built."""


def _require_non_empty(name: str, value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AuditEventBuildError(f"{name} must be a non-empty string")
    return value


def _require_allowed(name: str, value: str, allowed: frozenset[str]) -> str:
    _require_non_empty(name, value)
    if value not in allowed:
        raise AuditEventBuildError(
            f"{name} must be one of {sorted(allowed)!r}; got {value!r}"
        )
    return value


def _timestamp(value: datetime | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat()
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _redact_optional_mapping(data: Mapping[str, object] | None) -> dict[str, object] | None:
    if data is None:
        return None
    redacted = redact_secrets(data)
    if not isinstance(redacted, dict):
        raise AuditEventBuildError("redacted mapping must remain a dictionary")
    return redacted


class AuditEventEmitter:
    """Local-only builder for redacted AuditEvent-like dictionaries."""

    def __init__(self, source_service: str, environment: str | None = None) -> None:
        self.source_service = _require_non_empty("source_service", source_service)
        self.environment = environment

    def build_event(
        self,
        *,
        trace_id: str,
        correlation_id: str,
        event_type: str,
        event_category: str,
        actor_type: str,
        actor_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        outcome: str,
        audit_id: str | None = None,
        reason: str | None = None,
        occurred_at: datetime | None = None,
        metadata: dict[str, object] | None = None,
        before: dict[str, object] | None = None,
        after: dict[str, object] | None = None,
        lifecycle_ids: dict[str, str] | None = None,
    ) -> dict[str, object]:
        """Build a redacted AuditEvent-like payload without side effects."""

        payload: dict[str, object] = {
            "schema_version": SCHEMA_VERSION,
            "trace_id": _require_non_empty("trace_id", trace_id),
            "correlation_id": _require_non_empty("correlation_id", correlation_id),
            "audit_id": audit_id or f"audit_{uuid4().hex}",
            "event_type": _require_non_empty("event_type", event_type),
            "event_category": _require_non_empty("event_category", event_category),
            "occurred_at": _timestamp(occurred_at),
            "actor_type": _require_non_empty("actor_type", actor_type),
            "actor_id": _require_non_empty("actor_id", actor_id),
            "action": _require_non_empty("action", action),
            "entity_type": _require_non_empty("entity_type", entity_type),
            "entity_id": _require_non_empty("entity_id", entity_id),
            "outcome": _require_allowed("outcome", outcome, ALLOWED_OUTCOMES),
            "append_only": True,
            "contains_secrets": False,
            "source_service": self.source_service,
            "redaction_applied": any(item is not None for item in (metadata, before, after)),
        }

        if self.environment is not None:
            payload["environment"] = self.environment

        if reason is not None:
            payload["reason"] = reason

        redacted_metadata = _redact_optional_mapping(metadata)
        redacted_before = _redact_optional_mapping(before)
        redacted_after = _redact_optional_mapping(after)

        if redacted_metadata is not None:
            payload["metadata"] = redacted_metadata
        if redacted_before is not None:
            payload["before"] = redacted_before
        if redacted_after is not None:
            payload["after"] = redacted_after

        if lifecycle_ids is not None:
            unknown = sorted(set(lifecycle_ids) - ALLOWED_LIFECYCLE_ID_KEYS)
            if unknown:
                raise AuditEventBuildError(f"unknown lifecycle ID keys: {', '.join(unknown)}")
            for key, value in lifecycle_ids.items():
                payload[key] = _require_non_empty(key, value)

        return payload
