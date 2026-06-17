import unittest
from decimal import Decimal

from packages.sdk.cognitive_autonomy import (
    AgentJudgment,
    CognitiveAutonomyEngine,
    CognitiveAutonomyError,
    CognitiveHealth,
    ForecastObservation,
    HealingActionType,
)


class CognitiveAutonomyTests(unittest.TestCase):
    def setUp(self):
        self.engine = CognitiveAutonomyEngine()

    def test_collective_consensus_weights_confidence_and_evidence(self):
        consensus = self.engine.collective_consensus(
            (
                AgentJudgment("agent_a", "hypothesis_001", Decimal("0.70"), Decimal("0.90"), Decimal("2")),
                AgentJudgment("agent_b", "hypothesis_001", Decimal("0.60"), Decimal("0.80"), Decimal("1")),
                AgentJudgment("agent_c", "hypothesis_001", Decimal("0.65"), Decimal("0.70"), Decimal("1")),
            )
        )

        self.assertEqual(consensus.hypothesis_id, "hypothesis_001")
        self.assertEqual(consensus.consensus_probability, Decimal("0.665152"))
        self.assertEqual(consensus.participant_count, 3)
        self.assertIn(consensus.health, {CognitiveHealth.STABLE, CognitiveHealth.WATCH})

    def test_collective_consensus_blocks_high_disagreement(self):
        consensus = self.engine.collective_consensus(
            (
                AgentJudgment("agent_a", "hypothesis_001", Decimal("0.95"), Decimal("0.90")),
                AgentJudgment("agent_b", "hypothesis_001", Decimal("0.05"), Decimal("0.90")),
            )
        )

        self.assertEqual(consensus.health, CognitiveHealth.BLOCKED)

    def test_calibration_report_measures_brier_and_error(self):
        report = self.engine.calibration_report(
            (
                ForecastObservation("f1", Decimal("0.80"), True),
                ForecastObservation("f2", Decimal("0.70"), True),
                ForecastObservation("f3", Decimal("0.20"), False),
                ForecastObservation("f4", Decimal("0.10"), False),
                ForecastObservation("f5", Decimal("0.60"), True),
            )
        )

        self.assertEqual(report.sample_count, 5)
        self.assertEqual(report.brier_score, Decimal("0.068000"))
        self.assertEqual(report.empirical_frequency, Decimal("0.600000"))
        self.assertEqual(report.calibration_error, Decimal("0.120000"))
        self.assertEqual(report.health, CognitiveHealth.WATCH)

    def test_fractal_diagnostics_classifies_trend_and_chop(self):
        trend = self.engine.fractal_diagnostics(
            (Decimal("100"), Decimal("101"), Decimal("102"), Decimal("103"), Decimal("104"))
        )
        chop = self.engine.fractal_diagnostics(
            (Decimal("100"), Decimal("101"), Decimal("100"), Decimal("101"), Decimal("100"))
        )

        self.assertEqual(trend.regime_label, "persistent_trend")
        self.assertEqual(chop.regime_label, "choppy_mean_reverting")
        self.assertGreater(chop.roughness, trend.roughness)

    def test_stability_diagnostics_detects_stress_energy(self):
        calm = self.engine.stability_diagnostics(
            (Decimal("100"), Decimal("100.1"), Decimal("100.2"), Decimal("100.3"))
        )
        stressed = self.engine.stability_diagnostics(
            (Decimal("100"), Decimal("120"), Decimal("80"), Decimal("130"))
        )

        self.assertEqual(calm.health, CognitiveHealth.STABLE)
        self.assertIn(stressed.health, {CognitiveHealth.DEGRADED, CognitiveHealth.BLOCKED})
        self.assertGreater(stressed.stress_energy, calm.stress_energy)

    def test_analyze_generates_self_healing_actions_and_never_enables_trading(self):
        report = self.engine.analyze(
            judgments=(
                AgentJudgment("agent_a", "hypothesis_001", Decimal("0.95"), Decimal("0.90")),
                AgentJudgment("agent_b", "hypothesis_001", Decimal("0.05"), Decimal("0.90")),
            ),
            observations=(
                ForecastObservation("f1", Decimal("0.90"), False),
                ForecastObservation("f2", Decimal("0.90"), False),
                ForecastObservation("f3", Decimal("0.90"), False),
                ForecastObservation("f4", Decimal("0.90"), False),
                ForecastObservation("f5", Decimal("0.90"), False),
            ),
            prices=(Decimal("100"), Decimal("120"), Decimal("80"), Decimal("130")),
        )

        action_types = {action.action_type for action in report.healing_actions}

        self.assertEqual(report.health, CognitiveHealth.BLOCKED)
        self.assertIn(HealingActionType.RECALIBRATE_MODEL, action_types)
        self.assertIn(HealingActionType.PAUSE_AUTONOMY, action_types)
        self.assertIn(HealingActionType.REQUIRE_HUMAN_REVIEW, action_types)
        self.assertFalse(report.autonomy_allowed)
        self.assertFalse(report.trading_allowed)
        self.assertFalse(report.network_allowed)
        self.assertFalse(report.credentials_allowed)

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(CognitiveAutonomyError):
            AgentJudgment("agent_a", "hypothesis_001", Decimal("1.1"), Decimal("0.9"))

        with self.assertRaises(CognitiveAutonomyError):
            self.engine.collective_consensus(())

        with self.assertRaises(CognitiveAutonomyError):
            self.engine.fractal_diagnostics((Decimal("100"), Decimal("101")))

    def test_cognitive_module_exposes_no_operational_methods(self):
        import packages.sdk.cognitive_autonomy as cognitive_autonomy

        forbidden_names = {
            "submit_order",
            "cancel_order",
            "withdraw",
            "transfer",
            "auto_merge",
            "write_to_main",
        }

        self.assertTrue(forbidden_names.isdisjoint(dir(cognitive_autonomy)))


if __name__ == "__main__":
    unittest.main()
