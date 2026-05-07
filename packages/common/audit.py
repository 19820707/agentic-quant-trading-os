"""Local audit event emission interfaces.

This module prepares redacted AuditEvent-like payloads for future audit sinks.
It does not persist events, call network, import services, interpret trading
semantics, or access credentials.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from packages.common.security import redact_mapping


class AuditEventEmitterError(ValueError):
    """Raised when an audit event cannot be safely prepared."""


@dataclass(frozen=True)
class PreparedAuditEvent:
    """Redacted AuditEvent-like payload prepared for a future audit sink."""

    payload: dict[str, object]


class AuditEventEmitter(Protocol):
    """Protocol for local audit event emitters."""

    def emit(self, event: Mapping[str, object]) -> PreparedAuditEvent:
        """Prepare an audit event without persistence or network I/O."""


def prepare_audit_event(event: Mapping[str, object]) -> PreparedAuditEvent:
    """Return a redacted audit payload and enforce append-only safety flags."""

    if not isinstance(event, Mapping):
        raise AuditEventEmitterError("audit event must be a mapping")

    redacted = redact_mapping(event)

    if redacted.get("append_only") is not True:
        raise AuditEventEmitterError("audit event must be append_only")
    if redacted.get("contains_secrets") is not False:
        raise AuditEventEmitterError("audit event must declare contains_secrets false")

    return PreparedAuditEvent(payload=redacted)


class LocalRedactingAuditEventEmitter:
    """In-memory redacting emitter for tests and local composition only."""

    def emit(self, event: Mapping[str, object]) -> PreparedAuditEvent:
        return prepare_audit_event(event)
