from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SCHEMA_ROOT = Path(__file__).resolve().parent / "schemas"


@dataclass(frozen=True)
class SchemaRegistryEntry:
    domain: str
    name: str
    path: Path
    title: str


SCHEMA_REGISTRY: dict[tuple[str, str], SchemaRegistryEntry] = {
    ("audit", "audit_event"): SchemaRegistryEntry(
        domain="audit",
        name="audit_event",
        path=SCHEMA_ROOT / "audit" / "audit_event.schema.json",
        title="AuditEvent",
    ),
    ("trading", "approved_order"): SchemaRegistryEntry(
        domain="trading",
        name="approved_order",
        path=SCHEMA_ROOT / "trading" / "approved_order.schema.json",
        title="ApprovedOrder",
    ),
    ("trading", "execution_report"): SchemaRegistryEntry(
        domain="trading",
        name="execution_report",
        path=SCHEMA_ROOT / "trading" / "execution_report.schema.json",
        title="ExecutionReport",
    ),
    ("trading", "order_intent"): SchemaRegistryEntry(
        domain="trading",
        name="order_intent",
        path=SCHEMA_ROOT / "trading" / "order_intent.schema.json",
        title="OrderIntent",
    ),
    ("trading", "risk_decision"): SchemaRegistryEntry(
        domain="trading",
        name="risk_decision",
        path=SCHEMA_ROOT / "trading" / "risk_decision.schema.json",
        title="RiskDecision",
    ),
}


def list_schemas() -> tuple[SchemaRegistryEntry, ...]:
    return tuple(SCHEMA_REGISTRY[key] for key in sorted(SCHEMA_REGISTRY))


def get_schema_entry(domain: str, name: str) -> SchemaRegistryEntry:
    schema_name = name.removesuffix(".schema.json")
    key = (domain, schema_name)
    try:
        return SCHEMA_REGISTRY[key]
    except KeyError as exc:
        raise KeyError(f"schema is not registered: {domain}/{name}") from exc
