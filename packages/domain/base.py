from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import NAMESPACE_URL, uuid5


class DomainModelError(ValueError):
    """Raised when a domain model receives invalid data."""


def require_non_empty(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DomainModelError(f"{field_name} must be a non-empty string")
    return value.strip()


def require_decimal(value: Decimal, field_name: str) -> Decimal:
    if not isinstance(value, Decimal):
        raise DomainModelError(f"{field_name} must be Decimal")
    if not value.is_finite():
        raise DomainModelError(f"{field_name} must be finite")
    return value


def require_non_negative(value: Decimal, field_name: str) -> Decimal:
    value = require_decimal(value, field_name)
    if value < Decimal("0"):
        raise DomainModelError(f"{field_name} must be non-negative")
    return value


def require_positive(value: Decimal, field_name: str) -> Decimal:
    value = require_decimal(value, field_name)
    if value <= Decimal("0"):
        raise DomainModelError(f"{field_name} must be positive")
    return value


def require_ratio(value: Decimal, field_name: str) -> Decimal:
    value = require_decimal(value, field_name)
    if value < Decimal("0") or value > Decimal("1"):
        raise DomainModelError(f"{field_name} must be between 0 and 1")
    return value


def require_aware_datetime(value: datetime, field_name: str) -> datetime:
    if not isinstance(value, datetime):
        raise DomainModelError(f"{field_name} must be datetime")
    if value.tzinfo is None:
        raise DomainModelError(f"{field_name} must be timezone-aware")
    return value.astimezone(timezone.utc)


def deterministic_id(prefix: str, *parts: object) -> str:
    key = "|".join(str(part) for part in parts)
    return f"{prefix}_{uuid5(NAMESPACE_URL, key).hex}"


def parse_decimal(value: object, field_name: str) -> Decimal:
    if isinstance(value, float):
        raise DomainModelError(f"{field_name} must not be float")
    try:
        return Decimal(str(value))
    except Exception as exc:
        raise DomainModelError(f"{field_name} must be decimal-compatible") from exc


def parse_datetime(value: object, field_name: str) -> datetime:
    if not isinstance(value, str):
        raise DomainModelError(f"{field_name} must be an ISO datetime string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return require_aware_datetime(parsed, field_name)


def to_primitive(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return require_aware_datetime(value, "datetime").isoformat()
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {field.name: to_primitive(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple):
        return [to_primitive(item) for item in value]
    if isinstance(value, list):
        return [to_primitive(item) for item in value]
    if isinstance(value, dict):
        return {str(key): to_primitive(item) for key, item in value.items()}
    return value


class SerializableModel:
    def to_dict(self) -> dict[str, Any]:
        if not is_dataclass(self):
            raise DomainModelError("SerializableModel requires dataclass subclasses")
        return to_primitive(self)
