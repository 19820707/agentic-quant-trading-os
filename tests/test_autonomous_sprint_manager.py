import unittest

from packages.sdk.autonomous_sprint_manager import (
    AutonomousSprintManager,
    CapabilityState,
    MissionCandidate,
    MissionStatus,
    MissionType,
    ProductModel,
    SprintManagerError,
)


class AutonomousSprintManagerTests(unittest.TestCase):
    def setUp(self):
        self.manager = AutonomousSprintManager()
        self.product_model = ProductModel(
            product_goal="Build a governed AI-native trading platform scaffold",
            strategic_themes=("risk", "market data", "portfolio", "governance"),
        )

    def test_selects_high_value_safe_missions_within_capacity(self):
        plan = self.manager.plan_sprint(
            sprint_id="sprint_001",
            product_model=self.product_model,
            capabilities=(),
            missions=(
                self._mission(
                    mission_id="mission_portfolio",
                    title="Portfolio accounting hardening",
                    summary="Improve portfolio local accounting tests",
                    target_files=("tests/test_portfolio_accounting.py",),
                    value_score=9,
                    urgency_score=8,
                    complexity_score=2,
                ),
                self._mission(
                    mission_id="mission_docs",
                    title="Documentation cleanup",
                    summary="Update architecture docs",
                    target_files=("docs/architecture/readme.md",),
                    value_score=3,
                    urgency_score=2,
                    complexity_score=1,
                    mission_type=MissionType.DOCUMENTATION,
                ),
            ),
            capacity_points=3,
        )

        self.assertEqual([item.mission_id for item in plan.selected], ["mission_portfolio", "mission_docs"])
        self.assertEqual(plan.blocked, ())
        self.assertIn("no credentials", plan.safety_invariants)

    def test_defers_when_capacity_is_exhausted(self):
        plan = self.manager.plan_sprint(
            sprint_id="sprint_002",
            product_model=self.product_model,
            capabilities=(),
            missions=(
                self._mission("mission_a", "Risk evaluator", "risk engine hardening", ("tests/test_risk_evaluator.py",), complexity_score=3),
                self._mission("mission_b", "Market data replay", "market data replay", ("tests/test_market_data_layer.py",), complexity_score=3),
            ),
            capacity_points=3,
        )

        self.assertEqual(len(plan.selected), 1)
        self.assertEqual(len(plan.deferred), 1)
        self.assertEqual(plan.deferred[0].status, MissionStatus.DEFERRED)

    def test_blocks_forbidden_live_trading_mission(self):
        plan = self.manager.plan_sprint(
            sprint_id="sprint_003",
            product_model=self.product_model,
            capabilities=(),
            missions=(
                self._mission(
                    "mission_live",
                    "Enable live trading",
                    "Add live trading with broker credentials",
                    ("services/execution-engine/app/main.py",),
                    complexity_score=1,
                ),
            ),
            capacity_points=5,
        )

        self.assertEqual(plan.selected, ())
        self.assertEqual(plan.blocked[0].status, MissionStatus.BLOCKED)
        self.assertTrue(any("forbidden capability" in item for item in plan.blocked[0].rationale))

    def test_blocks_missing_dependency_capability(self):
        plan = self.manager.plan_sprint(
            sprint_id="sprint_004",
            product_model=self.product_model,
            capabilities=(CapabilityState("risk_gate", "scaffold", enabled=False),),
            missions=(
                self._mission(
                    "mission_dep",
                    "Paper review contract",
                    "paper governance contract",
                    ("packages/contracts/schemas/paper/paper_review.schema.json",),
                    dependencies=("risk_gate",),
                ),
            ),
            capacity_points=5,
        )

        self.assertIn("dependency not enabled: risk_gate", plan.blocked[0].rationale)

    def test_blocks_critical_policy_findings_from_agent_policy_engine(self):
        plan = self.manager.plan_sprint(
            sprint_id="sprint_005",
            product_model=self.product_model,
            capabilities=(),
            missions=(
                self._mission(
                    "mission_critical",
                    "Execution adapter",
                    "submit_order path",
                    ("packages/sdk/execution_adapter.py",),
                ),
            ),
            capacity_points=5,
        )

        self.assertEqual(plan.blocked[0].risk_assessment.policy_decision.value, "block")
        self.assertTrue(any("critical" in item for item in plan.blocked[0].rationale))

    def test_summary_is_deterministic_and_non_operational(self):
        plan = self.manager.plan_sprint(
            sprint_id="sprint_006",
            product_model=self.product_model,
            capabilities=(),
            missions=(
                self._mission(
                    "mission_docs",
                    "Docs",
                    "governance docs",
                    ("docs/governance.md",),
                    mission_type=MissionType.DOCUMENTATION,
                    complexity_score=1,
                ),
            ),
            capacity_points=1,
        )

        self.assertEqual(
            plan.to_summary(),
            {
                "sprint_id": "sprint_006",
                "product_goal": "Build a governed AI-native trading platform scaffold",
                "selected": ["mission_docs"],
                "blocked": [],
                "deferred": [],
                "capacity_points": 1,
                "safety_invariants": [
                    "no direct main writes",
                    "no auto merge",
                    "no credentials",
                    "no network execution",
                    "no live trading",
                    "no risk approval",
                    "no execution approval",
                ],
            },
        )

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(SprintManagerError):
            self.manager.plan_sprint(
                sprint_id="",
                product_model=self.product_model,
                capabilities=(),
                missions=(self._mission("mission_docs", "Docs", "docs", ("docs/a.md",)),),
                capacity_points=1,
            )

        with self.assertRaises(SprintManagerError):
            self._mission("bad_score", "Bad", "bad", ("docs/a.md",), value_score=11)

    def test_sprint_manager_exposes_no_execution_methods(self):
        import packages.sdk.autonomous_sprint_manager as sprint_manager

        forbidden_names = {
            "submit_order",
            "cancel_order",
            "withdraw",
            "transfer",
            "execute",
            "auto_merge",
            "write_to_main",
        }

        self.assertTrue(forbidden_names.isdisjoint(dir(sprint_manager)))

    def _mission(
        self,
        mission_id: str,
        title: str,
        summary: str,
        target_files: tuple[str, ...],
        *,
        mission_type: MissionType = MissionType.TESTING,
        dependencies: tuple[str, ...] = (),
        value_score: int = 5,
        urgency_score: int = 5,
        complexity_score: int = 2,
        risk_score: int = 1,
    ) -> MissionCandidate:
        return MissionCandidate(
            mission_id=mission_id,
            title=title,
            mission_type=mission_type,
            summary=summary,
            target_files=target_files,
            expected_tests=("python -m unittest discover -s tests",),
            dependencies=dependencies,
            value_score=value_score,
            urgency_score=urgency_score,
            complexity_score=complexity_score,
            risk_score=risk_score,
        )


if __name__ == "__main__":
    unittest.main()
