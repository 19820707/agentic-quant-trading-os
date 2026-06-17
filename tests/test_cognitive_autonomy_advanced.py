import unittest
from decimal import Decimal

from packages.sdk.cognitive_autonomy import (
    AgentJudgment,
    CognitiveAutonomyError,
    CognitiveHealth,
    ForecastObservation,
    HealingActionType,
)
from packages.sdk.cognitive_autonomy_advanced import (
    AdvancedCognitiveAutonomyEngine,
    NeuralActivationSnapshot,
    build_default_advanced_cognitive_autonomy_engine,
)


class AdvancedCognitiveAutonomyTests(unittest.TestCase):
    def setUp(self):
        self.engine = AdvancedCognitiveAutonomyEngine()

    def test_neural_stability_diagnostics_detect_saturation_drift_and_uncertainty(self):
        snapshot = NeuralActivationSnapshot(
            snapshot_id="snapshot_001",
            activations=(Decimal("0.99"), Decimal("0.01"), Decimal("0.98"), Decimal("0.02")),
            baseline=(Decimal("0.50"), Decimal("0.50"), Decimal("0.50"), Decimal("0.50")),
            uncertainty=Decimal("0.20"),
        )

        diagnostics = self.engine.neural_stability_diagnostics(snapshot)

        self.assertEqual(diagnostics.sample_count, 4)
        self.assertEqual(diagnostics.saturation_ratio, Decimal("1.000000"))
        self.assertGreater(diagnostics.drift, Decimal("0.40"))
        self.assertEqual(diagnostics.health, CognitiveHealth.BLOCKED)

    def test_reliability_diagram_builds_deterministic_calibration_buckets(self):
        observations = (
            ForecastObservation("f01", Decimal("0.05"), False),
            ForecastObservation("f02", Decimal("0.15"), False),
            ForecastObservation("f03", Decimal("0.25"), False),
            ForecastObservation("f04", Decimal("0.35"), True),
            ForecastObservation("f05", Decimal("0.45"), True),
            ForecastObservation("f06", Decimal("0.55"), False),
            ForecastObservation("f07", Decimal("0.65"), True),
            ForecastObservation("f08", Decimal("0.75"), True),
            ForecastObservation("f09", Decimal("0.85"), True),
            ForecastObservation("f10", Decimal("0.95"), True),
        )

        diagram = self.engine.reliability_diagram(observations, bucket_count=5)

        self.assertEqual(diagram.bucket_count, 5)
        self.assertEqual(diagram.sample_count, 10)
        self.assertEqual(len(diagram.buckets), 5)
        self.assertEqual(sum(bucket.forecast_count for bucket in diagram.buckets), 10)
        self.assertGreaterEqual(diagram.expected_calibration_error, Decimal("0"))
        self.assertIn(diagram.health, {CognitiveHealth.STABLE, CognitiveHealth.WATCH, CognitiveHealth.DEGRADED})

    def test_collective_intelligence_flags_evidence_concentration_and_dissent(self):
        diagnostics = self.engine.collective_intelligence_diagnostics(
            (
                AgentJudgment("agent_a", "hypothesis_001", Decimal("0.90"), Decimal("0.90"), Decimal("10")),
                AgentJudgment("agent_b", "hypothesis_001", Decimal("0.20"), Decimal("0.60"), Decimal("1")),
                AgentJudgment("agent_c", "hypothesis_001", Decimal("0.25"), Decimal("0.60"), Decimal("1")),
            )
        )

        self.assertEqual(diagnostics.participant_count, 3)
        self.assertGreater(diagnostics.evidence_concentration, Decimal("0.50"))
        self.assertGreater(diagnostics.dissent_ratio, Decimal("0"))
        self.assertIn(diagnostics.health, {CognitiveHealth.DEGRADED, CognitiveHealth.BLOCKED})

    def test_physics_diagnostics_detects_stress_energy_without_runtime_actions(self):
        calm = self.engine.physics_diagnostics(
            (
                Decimal("100.0"),
                Decimal("100.1"),
                Decimal("100.2"),
                Decimal("100.3"),
                Decimal("100.4"),
            )
        )
        stressed = self.engine.physics_diagnostics(
            (
                Decimal("100"),
                Decimal("130"),
                Decimal("70"),
                Decimal("140"),
                Decimal("60"),
            )
        )

        self.assertEqual(calm.health, CognitiveHealth.STABLE)
        self.assertIn(stressed.health, {CognitiveHealth.DEGRADED, CognitiveHealth.BLOCKED})
        self.assertGreater(stressed.kinetic_energy, calm.kinetic_energy)

    def test_advanced_analyze_produces_fail_closed_self_healing_plan(self):
        judgments = (
            AgentJudgment("agent_a", "hypothesis_001", Decimal("0.95"), Decimal("0.90")),
            AgentJudgment("agent_b", "hypothesis_001", Decimal("0.05"), Decimal("0.90")),
            AgentJudgment("agent_c", "hypothesis_001", Decimal("0.10"), Decimal("0.80")),
        )
        observations = tuple(
            ForecastObservation(f"f{index:02d}", Decimal("0.90"), False)
            for index in range(1, 11)
        )
        prices = (
            Decimal("100"),
            Decimal("130"),
            Decimal("70"),
            Decimal("140"),
            Decimal("60"),
            Decimal("150"),
            Decimal("55"),
            Decimal("145"),
            Decimal("65"),
            Decimal("135"),
        )
        snapshot = NeuralActivationSnapshot(
            snapshot_id="snapshot_002",
            activations=(Decimal("0.99"), Decimal("0.01"), Decimal("0.98"), Decimal("0.02")),
            baseline=(Decimal("0.50"), Decimal("0.50"), Decimal("0.50"), Decimal("0.50")),
            uncertainty=Decimal("0.75"),
        )

        report = self.engine.analyze(
            judgments=judgments,
            observations=observations,
            prices=prices,
            neural_snapshot=snapshot,
        )

        action_types = {action.action_type for action in report.self_healing_plan.actions}

        self.assertEqual(report.health, CognitiveHealth.BLOCKED)
        self.assertIn(HealingActionType.PAUSE_AUTONOMY, action_types)
        self.assertIn(HealingActionType.RECALIBRATE_MODEL, action_types)
        self.assertIn("human_approval_record", report.self_healing_plan.evidence_required)
        self.assertFalse(report.autonomy_allowed)
        self.assertFalse(report.runtime_change_allowed)
        self.assertFalse(report.trading_allowed)
        self.assertFalse(report.network_allowed)
        self.assertFalse(report.credentials_allowed)
        self.assertFalse(report.self_healing_plan.remediation_allowed)
        self.assertFalse(report.self_healing_plan.runtime_change_allowed)

    def test_scientific_validity_requires_falsifiable_probabilities(self):
        with self.assertRaises(CognitiveAutonomyError):
            self.engine.scientific_validity_report(
                judgments=(AgentJudgment("agent_a", "hypothesis_001", Decimal("0.50"), Decimal("0.90")),),
                observations=(),
                prices=(Decimal("100"), Decimal("101"), Decimal("102")),
            )

        report = self.engine.scientific_validity_report(
            judgments=(
                AgentJudgment("agent_a", "hypothesis_001", Decimal("0.50"), Decimal("0.90")),
                AgentJudgment("agent_b", "hypothesis_001", Decimal("0.55"), Decimal("0.90")),
                AgentJudgment("agent_c", "hypothesis_001", Decimal("0.60"), Decimal("0.90")),
            ),
            observations=tuple(
                ForecastObservation(f"f{index:02d}", Decimal("1.00"), True)
                for index in range(1, 11)
            ),
            prices=tuple(Decimal("100") + Decimal(index) for index in range(10)),
        )

        self.assertFalse(report.falsifiable)
        self.assertEqual(report.health, CognitiveHealth.BLOCKED)

    def test_invalid_neural_snapshot_fails_closed(self):
        with self.assertRaises(CognitiveAutonomyError):
            NeuralActivationSnapshot("snapshot_bad", (), uncertainty=Decimal("0"))

        with self.assertRaises(CognitiveAutonomyError):
            NeuralActivationSnapshot(
                "snapshot_bad",
                (Decimal("0.5"), Decimal("0.6")),
                baseline=(Decimal("0.5"),),
            )

        with self.assertRaises(CognitiveAutonomyError):
            NeuralActivationSnapshot("snapshot_bad", (Decimal("1.1"),))

    def test_factory_builds_local_advanced_engine(self):
        engine = build_default_advanced_cognitive_autonomy_engine()

        self.assertIsInstance(engine, AdvancedCognitiveAutonomyEngine)

    def test_advanced_cognitive_module_exposes_no_operational_methods(self):
        import packages.sdk.cognitive_autonomy_advanced as advanced

        forbidden_names = {
            "submit_order",
            "cancel_order",
            "withdraw",
            "transfer",
            "auto_merge",
            "write_to_main",
            "place_trade",
            "broker_client",
        }

        self.assertTrue(forbidden_names.isdisjoint(dir(advanced)))


if __name__ == "__main__":
    unittest.main()
