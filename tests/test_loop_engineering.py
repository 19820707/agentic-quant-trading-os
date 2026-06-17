from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from observability import EvidenceRecordType, LocalEvidenceJournal
from packages.sdk.autonomous_sprint_manager import CapabilityState, MissionCandidate, MissionType, ProductModel
from packages.sdk.cognitive_autonomy import AgentJudgment, ForecastObservation
from packages.sdk.cognitive_autonomy_advanced import NeuralActivationSnapshot
from packages.sdk.persistence_discipline import PersistenceIteration
from packages.sdk.loop_engineering import (
    LoopDecision,
    LoopEngineeringError,
    LoopIterationInput,
    LoopPhase,
    LoopSignal,
    LoopSignalCategory,
    build_default_loop_engineering_engine,
    run_loop_iteration_with_evidence,
)


NOW = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)


def product_model() -> ProductModel:
    return ProductModel(
        product_goal="Build a governed autonomous trading platform scaffold",
        strategic_themes=("risk", "governance", "observability", "reliability"),
    )


def mission(
    mission_id: str = "mission_observability",
    *,
    target_files: tuple[str, ...] = ("docs/architecture/observability.md",),
    complexity_score: int = 1,
    summary: str = "observability governance docs",
) -> MissionCandidate:
    return MissionCandidate(
        mission_id=mission_id,
        title="Observability hardening",
        mission_type=MissionType.DOCUMENTATION,
        summary=summary,
        target_files=target_files,
        expected_tests=("python -m unittest discover -s tests",),
        value_score=8,
        urgency_score=6,
        complexity_score=complexity_score,
    )


def stable_judgments() -> tuple[AgentJudgment, ...]:
    return (
        AgentJudgment("agent_a", "hypothesis_loop", Decimal("0.60"), Decimal("0.90")),
        AgentJudgment("agent_b", "hypothesis_loop", Decimal("0.62"), Decimal("0.90")),
        AgentJudgment("agent_c", "hypothesis_loop", Decimal("0.61"), Decimal("0.90")),
    )


def stable_observations() -> tuple[ForecastObservation, ...]:
    return (
        ForecastObservation("f1", Decimal("0.80"), True),
        ForecastObservation("f2", Decimal("0.80"), True),
        ForecastObservation("f3", Decimal("0.20"), False),
        ForecastObservation("f4", Decimal("0.20"), False),
        ForecastObservation("f5", Decimal("0.80"), True),
    )


def stable_prices() -> tuple[Decimal, ...]:
    return (Decimal("100"), Decimal("101"), Decimal("102"), Decimal("103"), Decimal("104"))


def loop_input(
    *,
    signals: tuple[LoopSignal, ...],
    missions: tuple[MissionCandidate, ...] = (mission(),),
    capacity_points: int = 3,
    judgments: tuple[AgentJudgment, ...] = stable_judgments(),
    observations: tuple[ForecastObservation, ...] = stable_observations(),
    prices: tuple[Decimal, ...] = stable_prices(),
    neural_snapshot: NeuralActivationSnapshot | None = None,
    persistence_iterations: tuple[PersistenceIteration, ...] = (),
) -> LoopIterationInput:
    return LoopIterationInput(
        loop_id="loop_engineering",
        iteration_id="iter_001",
        generated_at=NOW,
        product_model=product_model(),
        capabilities=(CapabilityState("observability", "scaffold", enabled=True),),
        missions=missions,
        signals=signals,
        judgments=judgments,
        observations=observations,
        prices=prices,
        capacity_points=capacity_points,
        neural_snapshot=neural_snapshot,
        persistence_iterations=persistence_iterations,
    )


class LoopEngineeringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = build_default_loop_engineering_engine()

    def test_safe_loop_can_continue_but_never_enables_operations(self) -> None:
        report = self.engine.run_iteration(
            loop_input(
                signals=(
                    LoopSignal(
                        "sig_ci_green",
                        LoopSignalCategory.CI,
                        1,
                        "all checks green",
                        evidence_refs=("ci:green",),
                    ),
                )
            )
        )

        self.assertEqual(report.decision, LoopDecision.CONTINUE)
        self.assertEqual(report.phases_completed[-1], LoopPhase.REVIEW)
        self.assertEqual(report.sprint_plan.selected[0].mission_id, "mission_observability")
        self.assertFalse(report.patch_allowed)
        self.assertFalse(report.direct_main_write_allowed)
        self.assertFalse(report.auto_merge_allowed)
        self.assertFalse(report.trading_allowed)
        self.assertFalse(report.risk_approval_allowed)
        self.assertFalse(report.execution_allowed)
        self.assertFalse(report.network_allowed)
        self.assertFalse(report.credentials_allowed)

    def test_missing_evidence_reduces_scope(self) -> None:
        report = self.engine.run_iteration(
            loop_input(
                signals=(
                    LoopSignal("sig_ci_unknown", LoopSignalCategory.CI, 2, "ci status missing"),
                )
            )
        )

        self.assertEqual(report.decision, LoopDecision.REDUCE_SCOPE)
        self.assertIn("missing_signal_evidence_reduce_scope", report.rationale)

    def test_trading_boundary_signal_requires_human_review_and_extra_evidence(self) -> None:
        report = self.engine.run_iteration(
            loop_input(
                signals=(
                    LoopSignal(
                        "sig_boundary",
                        LoopSignalCategory.TRADING_BOUNDARY,
                        2,
                        "execution boundary touched",
                        evidence_refs=("review:boundary",),
                    ),
                )
            )
        )

        self.assertEqual(report.decision, LoopDecision.REQUIRE_HUMAN_REVIEW)
        self.assertIn("deterministic_risk_gateway_review", report.required_evidence)
        self.assertIn("human_approval_record", report.required_evidence)

    def test_severity_five_signal_blocks_loop(self) -> None:
        report = self.engine.run_iteration(
            loop_input(
                signals=(
                    LoopSignal(
                        "sig_critical",
                        LoopSignalCategory.SECURITY,
                        5,
                        "critical safety signal",
                        evidence_refs=("security:critical",),
                    ),
                )
            )
        )

        self.assertEqual(report.decision, LoopDecision.BLOCK)
        self.assertIn("security_policy_review", report.required_evidence)

    def test_capacity_pressure_reduces_scope(self) -> None:
        report = self.engine.run_iteration(
            loop_input(
                signals=(LoopSignal("sig_ci_green", LoopSignalCategory.CI, 1, "green", evidence_refs=("ci",)),),
                missions=(
                    mission("mission_a", complexity_score=3),
                    mission("mission_b", complexity_score=3),
                ),
                capacity_points=3,
            )
        )

        self.assertEqual(report.decision, LoopDecision.REDUCE_SCOPE)
        self.assertTrue(report.sprint_plan.deferred)

    def test_evidence_payload_is_deterministic_and_non_operational(self) -> None:
        report = self.engine.run_iteration(
            loop_input(
                signals=(
                    LoopSignal("sig_ci_green", LoopSignalCategory.CI, 1, "green", evidence_refs=("ci",)),
                )
            )
        )
        payload = report.to_evidence_payload()

        self.assertEqual(payload["decision"], "continue")
        self.assertEqual(payload["selected_missions"], ["mission_observability"])
        self.assertIsNone(payload["advanced_cognitive_health"])
        self.assertEqual(payload["advanced_self_healing_evidence_required"], [])
        self.assertIsNone(payload["persistence_decision"])
        self.assertIsNone(payload["persistence_score"])
        self.assertFalse(payload["patch_allowed"])
        self.assertFalse(payload["execution_allowed"])
        self.assertFalse(payload["credentials_allowed"])

    def test_advanced_cognitive_diagnostics_can_block_loop_decision(self) -> None:
        report = self.engine.run_iteration(
            loop_input(
                signals=(
                    LoopSignal(
                        "sig_ci_green",
                        LoopSignalCategory.CI,
                        1,
                        "ci is green but cognition is unstable",
                        evidence_refs=("ci:green",),
                    ),
                ),
                neural_snapshot=NeuralActivationSnapshot(
                    snapshot_id="snapshot_loop_unstable",
                    activations=(Decimal("0.99"), Decimal("0.01"), Decimal("0.98"), Decimal("0.02")),
                    baseline=(Decimal("0.50"), Decimal("0.50"), Decimal("0.50"), Decimal("0.50")),
                    uncertainty=Decimal("0.80"),
                ),
            )
        )
        payload = report.to_evidence_payload()

        self.assertEqual(report.decision, LoopDecision.BLOCK)
        self.assertIsNotNone(report.advanced_cognitive_report)
        self.assertIn("advanced_cognitive_health_blocked", report.rationale)
        self.assertIn("human_approval_record", report.required_evidence)
        self.assertEqual(payload["advanced_cognitive_health"], "blocked")
        self.assertIn("rollback_plan", payload["advanced_self_healing_evidence_required"])
        self.assertFalse(payload["patch_allowed"])
        self.assertFalse(payload["execution_allowed"])
        self.assertFalse(payload["network_allowed"])
        self.assertFalse(payload["credentials_allowed"])

    def test_persistence_discipline_blocks_loop_after_repeated_blockers(self) -> None:
        report = self.engine.run_iteration(
            loop_input(
                signals=(
                    LoopSignal(
                        "sig_ci_green",
                        LoopSignalCategory.CI,
                        1,
                        "current signal is green but recent loop history is blocked",
                        evidence_refs=("ci:green",),
                    ),
                ),
                persistence_iterations=(
                    PersistenceIteration("iter_001", False, False, ("ci:failed",), blockers=("ci_failure",)),
                    PersistenceIteration("iter_002", False, False, ("audit:failed",), blockers=("audit_failure",)),
                    PersistenceIteration("iter_003", False, False, ("ci:failed",), blockers=("same_failure",)),
                ),
            )
        )
        payload = report.to_evidence_payload()

        self.assertEqual(report.decision, LoopDecision.BLOCK)
        self.assertIsNotNone(report.persistence_report)
        self.assertIn("persistence_discipline_blocked", report.rationale)
        self.assertIn("evidence_quality_gate", report.required_evidence)
        self.assertEqual(payload["persistence_decision"], "block")
        self.assertFalse(payload["patch_allowed"])
        self.assertFalse(payload["execution_allowed"])
        self.assertFalse(payload["network_allowed"])
        self.assertFalse(payload["credentials_allowed"])

    def test_persistence_progress_streak_is_recorded_without_granting_permissions(self) -> None:
        report = self.engine.run_iteration(
            loop_input(
                signals=(
                    LoopSignal("sig_ci_green", LoopSignalCategory.CI, 1, "green", evidence_refs=("ci",)),
                ),
                persistence_iterations=(
                    PersistenceIteration("iter_001", True, True, ("ci:green",)),
                    PersistenceIteration("iter_002", True, True, ("audit:green",)),
                ),
            )
        )
        payload = report.to_evidence_payload()

        self.assertEqual(report.decision, LoopDecision.CONTINUE)
        self.assertEqual(payload["persistence_decision"], "continue")
        self.assertEqual(payload["persistence_score"], "1.000000")
        self.assertIn("keep_evidence_gate_required", payload["persistence_required_actions"])
        self.assertFalse(payload["patch_allowed"])
        self.assertFalse(payload["execution_allowed"])

    def test_loop_report_appends_to_tamper_evident_journal(self) -> None:
        with TemporaryDirectory() as directory:
            journal = LocalEvidenceJournal(Path(directory) / "loop.jsonl")
            report = self.engine.run_iteration(
                loop_input(
                    signals=(
                        LoopSignal("sig_ci_green", LoopSignalCategory.CI, 1, "green", evidence_refs=("ci",)),
                    )
                )
            )

            entry = report.append_to_evidence_journal(journal)
            verification = journal.verify(checked_at=NOW)

            self.assertEqual(entry.record_type, EvidenceRecordType.LOOP_RUN_REPORT)
            self.assertEqual(entry.payload["decision"], "continue")
            self.assertFalse(entry.payload["execution_allowed"])
            self.assertTrue(verification.valid)
            self.assertEqual(verification.entry_count, 1)

    def test_run_loop_iteration_with_evidence_helper(self) -> None:
        with TemporaryDirectory() as directory:
            report, entry = run_loop_iteration_with_evidence(
                engine=self.engine,
                input_data=loop_input(
                    signals=(
                        LoopSignal("sig_ci_green", LoopSignalCategory.CI, 1, "green", evidence_refs=("ci",)),
                    )
                ),
                journal_path=Path(directory) / "loop.jsonl",
            )

            self.assertEqual(report.decision, LoopDecision.CONTINUE)
            self.assertEqual(entry.record_type, EvidenceRecordType.LOOP_RUN_REPORT)

    def test_invalid_loop_inputs_fail_closed(self) -> None:
        with self.assertRaises(LoopEngineeringError):
            LoopSignal("bad", LoopSignalCategory.CI, 6, "invalid")

        with self.assertRaises(LoopEngineeringError):
            loop_input(signals=())

        with self.assertRaises(LoopEngineeringError):
            LoopIterationInput(
                loop_id="loop",
                iteration_id="iter",
                generated_at=datetime(2026, 6, 16, 12, 0),
                product_model=product_model(),
                capabilities=(),
                missions=(mission(),),
                signals=(LoopSignal("sig", LoopSignalCategory.CI, 1, "ok", evidence_refs=("ci",)),),
                judgments=stable_judgments(),
                observations=stable_observations(),
                prices=stable_prices(),
                capacity_points=1,
            )

    def test_loop_engineering_module_exposes_no_operational_methods(self) -> None:
        import packages.sdk.loop_engineering as loop_engineering

        forbidden_names = {
            "submit_order",
            "cancel_order",
            "withdraw",
            "transfer",
            "auto_merge",
            "write_to_main",
            "execute",
        }

        self.assertTrue(forbidden_names.isdisjoint(dir(loop_engineering)))


if __name__ == "__main__":
    unittest.main()
