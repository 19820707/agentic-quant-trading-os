import unittest

from packages.sdk.autonomous_sprint_manager import CapabilityState, ProductModel
from packages.sdk.cognitive_autonomy import AgentJudgment, ForecastObservation
from packages.sdk.deep_learning_loop_planner import (
    DeepLearningCapability,
    DeepLearningLoopPlanner,
    DeepLearningLoopPlannerError,
    DeepLearningLoopRequest,
    build_default_deep_learning_loop_planner,
)
from packages.sdk.loop_engineering import (
    LoopDecision,
    LoopIterationInput,
    LoopSignal,
    LoopSignalCategory,
    build_default_loop_engineering_engine,
)

from datetime import datetime, timezone
from decimal import Decimal


NOW = datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)


class DeepLearningLoopPlannerTests(unittest.TestCase):
    def setUp(self):
        self.planner = DeepLearningLoopPlanner()

    def test_generates_full_deep_learning_governance_mission_set(self):
        plan = self.planner.generate_missions(
            DeepLearningLoopRequest(
                request_id="dl_loop_001",
                objective="Create governed deep learning scaffold missions",
            )
        )

        mission_ids = {mission.mission_id for mission in plan.generated_missions}

        self.assertEqual(len(plan.generated_missions), len(tuple(DeepLearningCapability)))
        self.assertIn("dl_dataset_lineage_contract", mission_ids)
        self.assertIn("dl_leakage_review_contract", mission_ids)
        self.assertIn("dl_model_card_contract", mission_ids)
        self.assertIn("dl_deployment_approval_gate", mission_ids)
        self.assertEqual(plan.omitted_capabilities, ())
        self.assertFalse(plan.training_runtime_allowed)
        self.assertFalse(plan.model_serving_runtime_allowed)
        self.assertFalse(plan.network_allowed)
        self.assertFalse(plan.credentials_allowed)
        self.assertFalse(plan.trading_signals_allowed)
        self.assertFalse(plan.order_intent_allowed)
        self.assertFalse(plan.risk_approval_allowed)
        self.assertFalse(plan.execution_allowed)

    def test_respects_max_missions_limit_and_reports_omitted_capabilities(self):
        plan = self.planner.generate_missions(
            DeepLearningLoopRequest(
                request_id="dl_loop_002",
                objective="Create only the first planning slice",
                max_missions=3,
            )
        )

        self.assertEqual(len(plan.generated_missions), 3)
        self.assertGreater(len(plan.omitted_capabilities), 0)
        self.assertEqual(plan.generated_missions[0].mission_id, "dl_dataset_lineage_contract")

    def test_dangerous_runtime_flags_fail_closed(self):
        cases = (
            {"allow_training_runtime": True},
            {"allow_model_serving_runtime": True},
            {"allow_network": True},
            {"allow_credentials": True},
            {"allow_trading_signals": True},
        )
        for flags in cases:
            with self.subTest(flags=flags):
                with self.assertRaises(DeepLearningLoopPlannerError):
                    DeepLearningLoopRequest(
                        request_id="dl_loop_bad",
                        objective="unsafe request",
                        **flags,
                    )

    def test_generated_missions_can_feed_loop_engineering_sprint_plan(self):
        plan = self.planner.generate_missions(
            DeepLearningLoopRequest(
                request_id="dl_loop_003",
                objective="Feed loop engineering",
                max_missions=4,
            )
        )
        engine = build_default_loop_engineering_engine()

        report = engine.run_iteration(
            LoopIterationInput(
                loop_id="deep_learning_loop",
                iteration_id="iter_001",
                generated_at=NOW,
                product_model=ProductModel(
                    product_goal="Build governed deep learning scaffold",
                    strategic_themes=("deep learning", "governance", "lineage", "calibration"),
                ),
                capabilities=(CapabilityState("deep_learning_governance", "scaffold", enabled=True),),
                missions=plan.generated_missions,
                signals=(
                    LoopSignal(
                        "sig_dl_governance",
                        LoopSignalCategory.ARCHITECTURE,
                        1,
                        "deep learning governance missions generated",
                        evidence_refs=("planner:dl_loop_003",),
                    ),
                ),
                judgments=(
                    AgentJudgment("agent_a", "hypothesis_dl_loop", Decimal("0.60"), Decimal("0.90")),
                    AgentJudgment("agent_b", "hypothesis_dl_loop", Decimal("0.62"), Decimal("0.90")),
                    AgentJudgment("agent_c", "hypothesis_dl_loop", Decimal("0.61"), Decimal("0.90")),
                ),
                observations=(
                    ForecastObservation("f1", Decimal("0.80"), True),
                    ForecastObservation("f2", Decimal("0.80"), True),
                    ForecastObservation("f3", Decimal("0.20"), False),
                    ForecastObservation("f4", Decimal("0.20"), False),
                    ForecastObservation("f5", Decimal("0.80"), True),
                ),
                prices=(Decimal("100"), Decimal("101"), Decimal("102"), Decimal("103"), Decimal("104")),
                capacity_points=6,
            )
        )

        self.assertIn(report.decision, {LoopDecision.CONTINUE, LoopDecision.REDUCE_SCOPE})
        self.assertGreaterEqual(len(report.sprint_plan.selected), 1)
        self.assertFalse(report.trading_allowed)
        self.assertFalse(report.execution_allowed)
        self.assertFalse(report.network_allowed)
        self.assertFalse(report.credentials_allowed)

    def test_summary_is_deterministic_and_non_operational(self):
        plan = self.planner.generate_missions(
            DeepLearningLoopRequest(
                request_id="dl_loop_004",
                objective="Summarize deep learning plan",
                max_missions=2,
            )
        )
        payload = plan.to_summary()

        self.assertEqual(payload["request_id"], "dl_loop_004")
        self.assertEqual(len(payload["generated_missions"]), 2)
        self.assertFalse(payload["training_runtime_allowed"])
        self.assertFalse(payload["network_allowed"])
        self.assertFalse(payload["credentials_allowed"])
        self.assertFalse(payload["trading_signals_allowed"])
        self.assertFalse(payload["execution_allowed"])

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(DeepLearningLoopPlannerError):
            DeepLearningLoopRequest(request_id="", objective="bad")

        with self.assertRaises(DeepLearningLoopPlannerError):
            DeepLearningLoopRequest(request_id="dl", objective="", max_missions=1)

        with self.assertRaises(DeepLearningLoopPlannerError):
            DeepLearningLoopRequest(request_id="dl", objective="bad", max_missions=0)

    def test_factory_returns_planner(self):
        self.assertIsInstance(build_default_deep_learning_loop_planner(), DeepLearningLoopPlanner)

    def test_module_exposes_no_operational_methods(self):
        import packages.sdk.deep_learning_loop_planner as deep_learning_loop_planner

        forbidden_names = {
            "submit_order",
            "cancel_order",
            "withdraw",
            "transfer",
            "auto_merge",
            "write_to_main",
            "execute",
            "fit",
            "predict_live",
        }

        self.assertTrue(forbidden_names.isdisjoint(dir(deep_learning_loop_planner)))


if __name__ == "__main__":
    unittest.main()
