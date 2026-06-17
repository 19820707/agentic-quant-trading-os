from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI
except ModuleNotFoundError:  # pragma: no cover - exercised in GitHub Actions without runtime deps.
    FastAPI = None  # type: ignore[assignment]

from adapters import ExecutionAdapterConfig, FailClosedExecutionAdapter
from observability import (
    EvidenceJournalReference,
    LocalEvidenceJournal,
    LocalObservabilitySink,
    evaluate_evidence_quality_gate,
    summarize_loop_evidence,
)
from packages.domain import CorrelationId
from packages.domain.base import require_aware_datetime


class ControlPlaneError(ValueError):
    """Raised when control-plane state would become unsafe."""


class ControlPlaneRole(str, Enum):
    ADMIN = "admin"
    TRADER = "trader"
    OBSERVER = "observer"
    SERVICE = "service"


@dataclass(frozen=True)
class LocalRoute:
    path: str
    method: str
    endpoint_name: str


class LocalControlPlaneApp:
    """Tiny route registry used when FastAPI is not installed in minimal CI."""

    def __init__(self, *, title: str, version: str) -> None:
        self.title = title
        self.version = version
        self.routes: list[LocalRoute] = []

    def get(self, path: str):
        return self._register("GET", path)

    def post(self, path: str):
        return self._register("POST", path)

    def _register(self, method: str, path: str):
        def decorator(endpoint):
            self.routes.append(LocalRoute(path=path, method=method, endpoint_name=endpoint.__name__))
            return endpoint

        return decorator


@dataclass
class ControlPlaneState:
    started_at: datetime
    kill_switch_active: bool = True
    live_trading_enabled: bool = False
    paper_trading_enabled: bool = False
    backtesting_enabled: bool = True
    network_allowed: bool = False
    credentials_allowed: bool = False
    auth_placeholder_enabled: bool = True
    evidence_journal_path: Path | None = None
    evidence_journal_id: str = "control-plane-evidence-journal"
    roles: tuple[ControlPlaneRole, ...] = (
        ControlPlaneRole.ADMIN,
        ControlPlaneRole.TRADER,
        ControlPlaneRole.OBSERVER,
        ControlPlaneRole.SERVICE,
    )
    observability: LocalObservabilitySink = field(default_factory=LocalObservabilitySink)

    def __post_init__(self) -> None:
        require_aware_datetime(self.started_at, "started_at")
        if self.live_trading_enabled:
            raise ControlPlaneError("live trading must be disabled in control-plane scaffold")
        if self.network_allowed:
            raise ControlPlaneError("control plane must not allow network access to external services")
        if self.credentials_allowed:
            raise ControlPlaneError("control plane must not allow credentials")
        if self.evidence_journal_path is not None and self.evidence_journal_path.suffix != ".jsonl":
            raise ControlPlaneError("evidence journal path must use .jsonl suffix")

    def activate_kill_switch(self) -> dict[str, Any]:
        self.kill_switch_active = True
        return {"kill_switch_active": True, "status": "activated"}

    def request_kill_switch_deactivation(self) -> dict[str, Any]:
        self.kill_switch_active = True
        return {
            "kill_switch_active": True,
            "status": "blocked",
            "reason": "kill switch deactivation requires a future explicit approval gate",
        }


def default_control_plane_state() -> ControlPlaneState:
    return ControlPlaneState(started_at=datetime.now(timezone.utc))


def health_payload(state: ControlPlaneState) -> dict[str, Any]:
    return {
        "status": "ok",
        "component": "control-plane",
        "started_at": state.started_at.isoformat(),
        "live_trading_enabled": False,
        "network_allowed": False,
        "credentials_allowed": False,
    }


def readiness_payload(state: ControlPlaneState) -> dict[str, Any]:
    return {
        "ready": True,
        "mode": "local_control_plane_only",
        "kill_switch_active": state.kill_switch_active,
        "paper_trading_enabled": state.paper_trading_enabled,
        "backtesting_enabled": state.backtesting_enabled,
        "execution_adapter": "fail_closed",
    }


def system_status_payload(state: ControlPlaneState) -> dict[str, Any]:
    return {
        "runtime": {
            "live_trading_enabled": False,
            "network_allowed": False,
            "credentials_allowed": False,
            "production_enabled": False,
        },
        "gates": {
            "deterministic_risk_gateway_required": True,
            "direct_signal_to_exchange_allowed": False,
            "llm_to_broker_allowed": False,
            "paper_trading_requires_risk": True,
        },
        "capabilities": {
            "backtesting_local": state.backtesting_enabled,
            "paper_trading_local": state.paper_trading_enabled,
            "execution_adapter": "fail_closed",
            "observability_local": True,
        },
    }


def risk_status_payload(state: ControlPlaneState) -> dict[str, Any]:
    return {
        "risk_gateway_required": True,
        "kill_switch_active": state.kill_switch_active,
        "risk_decision_authority": "deterministic-risk-gateway",
        "execution_without_risk_allowed": False,
    }


def execution_status_payload() -> dict[str, Any]:
    adapter = FailClosedExecutionAdapter(ExecutionAdapterConfig(adapter_name="control-plane", enabled=True))
    health = adapter.health()
    return {
        "adapter_name": health.adapter_name,
        "state": health.state.value,
        "message": health.message,
        "live_trading_enabled": False,
        "network_allowed": False,
        "credentials_allowed": False,
    }


def audit_events_payload(state: ControlPlaneState, correlation_id: str | None = None) -> dict[str, Any]:
    events = state.observability.audit_events
    if correlation_id is not None:
        corr = CorrelationId(correlation_id)
        events = tuple(event for event in events if event.correlation_id == corr)
    return {
        "count": len(events),
        "events": [event.to_dict() for event in events],
    }


def metrics_payload(state: ControlPlaneState) -> dict[str, Any]:
    snapshot = state.observability.metrics_snapshot()
    return {
        "captured_at": snapshot.captured_at.isoformat(),
        "counters": {key: str(value) for key, value in snapshot.counters.items()},
        "gauges": {key: str(value) for key, value in snapshot.gauges.items()},
    }


def evidence_verification_payload(
    state: ControlPlaneState,
    *,
    checked_at: datetime | None = None,
) -> dict[str, Any]:
    timestamp = checked_at or datetime.now(timezone.utc)
    if state.evidence_journal_path is None:
        return {
            "configured": False,
            "journal_id": state.evidence_journal_id,
            "checked_at": timestamp.isoformat(),
            "valid": True,
            "entry_count": 0,
            "last_entry_hash": None,
            "violations": [],
            "mode": "local_only_no_persistence_configured",
            "network_allowed": False,
            "credentials_allowed": False,
            "external_services_used": False,
        }

    journal = LocalEvidenceJournal(state.evidence_journal_path, journal_id=state.evidence_journal_id)
    verification = journal.verify(checked_at=timestamp)
    return {
        "configured": True,
        "journal_id": verification.journal_id,
        "checked_at": verification.checked_at.isoformat(),
        "valid": verification.valid,
        "entry_count": verification.entry_count,
        "last_entry_hash": verification.last_entry_hash,
        "violations": list(verification.violations),
        "mode": "local_only_configured_journal",
        "network_allowed": False,
        "credentials_allowed": False,
        "external_services_used": False,
    }


def evidence_summary_payload(
    state: ControlPlaneState,
    *,
    checked_at: datetime | None = None,
) -> dict[str, Any]:
    timestamp = checked_at or datetime.now(timezone.utc)
    references = ()
    if state.evidence_journal_path is not None:
        references = (
            EvidenceJournalReference(
                path=state.evidence_journal_path,
                journal_id=state.evidence_journal_id,
            ),
        )
    summary = summarize_loop_evidence(references, checked_at=timestamp)
    payload = summary.to_dict()
    payload["mode"] = "local_only_evidence_summary"
    payload["configured"] = state.evidence_journal_path is not None
    return payload


def evidence_quality_gate_payload(
    state: ControlPlaneState,
    *,
    checked_at: datetime | None = None,
) -> dict[str, Any]:
    timestamp = checked_at or datetime.now(timezone.utc)
    references = ()
    if state.evidence_journal_path is not None:
        references = (
            EvidenceJournalReference(
                path=state.evidence_journal_path,
                journal_id=state.evidence_journal_id,
            ),
        )
    summary = summarize_loop_evidence(references, checked_at=timestamp)
    gate = evaluate_evidence_quality_gate(summary)
    payload = gate.to_dict()
    payload["checked_at"] = timestamp.isoformat()
    payload["configured"] = state.evidence_journal_path is not None
    payload["mode"] = "local_only_evidence_quality_gate"
    payload["summary"] = summary.to_dict()
    return payload


def create_control_plane_app(state: ControlPlaneState | None = None) -> Any:
    control_state = state or default_control_plane_state()
    if FastAPI is None:
        app = LocalControlPlaneApp(title="Agentic Quant Trading OS Control Plane", version="0.0.0")
    else:
        app = FastAPI(title="Agentic Quant Trading OS Control Plane", version="0.0.0")

    @app.get("/health")
    def health() -> dict[str, Any]:
        return health_payload(control_state)

    @app.get("/ready")
    def ready() -> dict[str, Any]:
        return readiness_payload(control_state)

    @app.get("/status")
    def status() -> dict[str, Any]:
        return system_status_payload(control_state)

    @app.get("/risk/status")
    def risk_status() -> dict[str, Any]:
        return risk_status_payload(control_state)

    @app.post("/risk/kill-switch/activate")
    def activate_kill_switch() -> dict[str, Any]:
        return control_state.activate_kill_switch()

    @app.post("/risk/kill-switch/deactivate")
    def deactivate_kill_switch() -> dict[str, Any]:
        return control_state.request_kill_switch_deactivation()

    @app.get("/execution/status")
    def execution_status() -> dict[str, Any]:
        return execution_status_payload()

    @app.get("/audit/events")
    def audit_events(correlation_id: str | None = None) -> dict[str, Any]:
        return audit_events_payload(control_state, correlation_id)

    @app.get("/observability/metrics")
    def metrics() -> dict[str, Any]:
        return metrics_payload(control_state)

    @app.get("/observability/evidence/verify")
    def verify_evidence() -> dict[str, Any]:
        return evidence_verification_payload(control_state)

    @app.get("/observability/evidence/summary")
    def summarize_evidence() -> dict[str, Any]:
        return evidence_summary_payload(control_state)

    @app.get("/observability/evidence/gate")
    def evidence_gate() -> dict[str, Any]:
        return evidence_quality_gate_payload(control_state)

    @app.get("/auth/placeholder")
    def auth_placeholder() -> dict[str, Any]:
        return {
            "auth_placeholder_enabled": control_state.auth_placeholder_enabled,
            "roles": [role.value for role in control_state.roles],
            "jwt_or_oauth2_ready": True,
            "enforcement": "not_enabled_in_local_scaffold",
        }

    return app
