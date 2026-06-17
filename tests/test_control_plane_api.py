from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from api import (
    ControlPlaneError,
    ControlPlaneState,
    create_control_plane_app,
    evidence_quality_gate_payload,
    evidence_verification_payload,
    evidence_summary_payload,
    execution_status_payload,
    health_payload,
    readiness_payload,
    risk_status_payload,
    system_status_payload,
)
from observability import EvidenceRecordType, LocalEvidenceJournal


NOW = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)


class ControlPlaneApiTests(unittest.TestCase):
    def test_state_rejects_live_network_and_credentials(self) -> None:
        for flag in ("live_trading_enabled", "network_allowed", "credentials_allowed"):
            with self.subTest(flag=flag):
                with self.assertRaises(ControlPlaneError):
                    ControlPlaneState(started_at=NOW, **{flag: True})

    def test_health_and_readiness_are_local_only(self) -> None:
        state = ControlPlaneState(started_at=NOW)

        health = health_payload(state)
        readiness = readiness_payload(state)

        self.assertEqual(health["status"], "ok")
        self.assertFalse(health["live_trading_enabled"])
        self.assertFalse(health["network_allowed"])
        self.assertFalse(health["credentials_allowed"])
        self.assertTrue(readiness["kill_switch_active"])
        self.assertEqual(readiness["execution_adapter"], "fail_closed")

    def test_system_status_blocks_direct_execution_paths(self) -> None:
        state = ControlPlaneState(started_at=NOW)

        status = system_status_payload(state)

        self.assertFalse(status["runtime"]["live_trading_enabled"])
        self.assertFalse(status["gates"]["direct_signal_to_exchange_allowed"])
        self.assertFalse(status["gates"]["llm_to_broker_allowed"])
        self.assertTrue(status["gates"]["deterministic_risk_gateway_required"])

    def test_kill_switch_deactivation_is_blocked(self) -> None:
        state = ControlPlaneState(started_at=NOW)

        blocked = state.request_kill_switch_deactivation()

        self.assertTrue(blocked["kill_switch_active"])
        self.assertEqual(blocked["status"], "blocked")
        self.assertTrue(state.kill_switch_active)

    def test_risk_and_execution_status_are_fail_closed(self) -> None:
        state = ControlPlaneState(started_at=NOW)

        risk = risk_status_payload(state)
        execution = execution_status_payload()

        self.assertTrue(risk["risk_gateway_required"])
        self.assertFalse(risk["execution_without_risk_allowed"])
        self.assertEqual(execution["state"], "PAPER_ONLY")
        self.assertFalse(execution["live_trading_enabled"])
        self.assertFalse(execution["network_allowed"])
        self.assertFalse(execution["credentials_allowed"])

    def test_create_app_registers_expected_routes(self) -> None:
        app = create_control_plane_app(ControlPlaneState(started_at=NOW))
        paths = {route.path for route in app.routes}

        for expected in {
            "/health",
            "/ready",
            "/status",
            "/risk/status",
            "/risk/kill-switch/activate",
            "/risk/kill-switch/deactivate",
            "/execution/status",
            "/audit/events",
            "/observability/metrics",
            "/observability/evidence/verify",
            "/observability/evidence/summary",
            "/observability/evidence/gate",
            "/auth/placeholder",
        }:
            self.assertIn(expected, paths)

    def test_evidence_verification_endpoint_is_local_and_optional(self) -> None:
        state = ControlPlaneState(started_at=NOW)

        payload = evidence_verification_payload(state, checked_at=NOW)

        self.assertFalse(payload["configured"])
        self.assertTrue(payload["valid"])
        self.assertEqual(payload["entry_count"], 0)
        self.assertFalse(payload["network_allowed"])
        self.assertFalse(payload["credentials_allowed"])
        self.assertFalse(payload["external_services_used"])

    def test_evidence_verification_reads_configured_local_journal_only(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "control-plane.jsonl"
            journal = LocalEvidenceJournal(path, journal_id="control-plane-evidence-journal")
            journal.append(
                EvidenceRecordType.GENERIC_EVIDENCE,
                {"component": "control-plane", "safe": True},
                occurred_at=NOW,
            )
            state = ControlPlaneState(started_at=NOW, evidence_journal_path=path)

            payload = evidence_verification_payload(state, checked_at=NOW)

            self.assertTrue(payload["configured"])
            self.assertTrue(payload["valid"])
            self.assertEqual(payload["entry_count"], 1)
            self.assertEqual(payload["violations"], [])
            self.assertFalse(payload["network_allowed"])
            self.assertFalse(payload["credentials_allowed"])

    def test_evidence_journal_path_must_be_jsonl(self) -> None:
        with self.assertRaises(ControlPlaneError):
            ControlPlaneState(started_at=NOW, evidence_journal_path=Path("not-json.txt"))

    def test_evidence_summary_endpoint_reports_integrity_and_coverage(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "control-plane.jsonl"
            journal = LocalEvidenceJournal(path, journal_id="control-plane-evidence-journal")
            journal.append(
                EvidenceRecordType.LOOP_RUN_REPORT,
                {"decision": "continue"},
                occurred_at=NOW,
            )
            state = ControlPlaneState(started_at=NOW, evidence_journal_path=path)

            payload = evidence_summary_payload(state, checked_at=NOW)

            self.assertTrue(payload["configured"])
            self.assertEqual(payload["integrity_score"], "1.000000")
            self.assertEqual(payload["coverage_score"], "1.000000")
            self.assertEqual(payload["record_type_counts"]["LOOP_RUN_REPORT"], 1)
            self.assertFalse(payload["network_allowed"])
            self.assertFalse(payload["credentials_allowed"])
            self.assertFalse(payload["external_services_used"])

    def test_evidence_quality_gate_endpoint_blocks_without_evidence(self) -> None:
        state = ControlPlaneState(started_at=NOW)

        payload = evidence_quality_gate_payload(state, checked_at=NOW)

        self.assertFalse(payload["configured"])
        self.assertEqual(payload["decision"], "block")
        self.assertFalse(payload["promotion_allowed"])
        self.assertIn("no_evidence_entries", payload["reasons"])
        self.assertFalse(payload["network_allowed"])
        self.assertFalse(payload["credentials_allowed"])

    def test_evidence_quality_gate_endpoint_passes_complete_local_journal(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "control-plane.jsonl"
            journal = LocalEvidenceJournal(path, journal_id="control-plane-evidence-journal")
            journal.append(
                EvidenceRecordType.LOOP_RUN_REPORT,
                {"decision": "continue"},
                occurred_at=NOW,
            )
            state = ControlPlaneState(started_at=NOW, evidence_journal_path=path)

            payload = evidence_quality_gate_payload(state, checked_at=NOW)

            self.assertTrue(payload["configured"])
            self.assertEqual(payload["decision"], "pass")
            self.assertTrue(payload["promotion_allowed"])
            self.assertEqual(payload["summary"]["coverage_score"], "1.000000")
            self.assertFalse(payload["network_allowed"])
            self.assertFalse(payload["credentials_allowed"])


if __name__ == "__main__":
    unittest.main()
