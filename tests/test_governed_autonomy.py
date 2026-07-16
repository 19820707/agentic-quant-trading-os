from __future__ import annotations

from datetime import datetime, timezone
import unittest

from packages.contracts import ContractValidator
from packages.sdk import (
    AutonomyActionState,
    AutonomyPermission,
    build_default_governed_autonomy_planner,
)
from packages.sdk.autonomous_sprint_manager import (
    CapabilityState,
    MissionCandidate,
    MissionType,
    ProductModel,
    build_default_sprint_manager,
)

NOW = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


class GovernedAutonomyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sprint_manager = build_default_sprint_manager()
        self.planner = build_default_governed_autonomy_planner()
        self.product_model = ProductModel(
            product_goal="Build governed autonomy for safe engineering work",
            strategic_themes=("governance", "security", "reliability"),
        )

    def test_low_risk_docs_mission_can_prepare_draft_pr_only(self) -> None:
        plan = self._build_plan(
            "sprint_safe_docs",
            (
                _mission(
                    "mission_docs",
                    "Governance docs",
                    "Update governance documentation",
                    ("docs/architecture/governed_autonomy.md",),
                    mission_type=MissionType.DOCUMENTATION,
                ),
            ),
            capacity_points=2,
        )

        self.assertEqual(plan.ready_count, 1)
        work_order = plan.work_orders[0]
        self.assertEqual(work_order.state, AutonomyActionState.READY_FOR_PR_PREPARATION)
        self.assertIn(AutonomyPermission.MODIFY_FILES_IN_BRANCH, work_order.permitted_actions)
        self.assertIn(AutonomyPermission.PREPARE_DRAFT_PR, work_order.permitted_actions)
        self.assertFalse(work_order.human_review_required)
        self.assertFalse(plan.direct_main_write_allowed)
        self.assertFalse(plan.auto_merge_allowed)

    def test_sdk_mission_requires_human_review_before_preparation(self) -> None:
        plan = self._build_plan(
            "sprint_sdk_review",
            (
                _mission(
                    "mission_sdk",
                    "Governed autonomy planner",
                    "Refine local SDK governance",
                    ("packages/sdk/governed_autonomy.py",),
                ),
            ),
            capacity_points=3,
        )

        self.assertEqual(plan.human_review_count, 1)
        work_order = plan.work_orders[0]
        self.assertEqual(work_order.state, AutonomyActionState.HUMAN_REVIEW_REQUIRED)
        self.assertIn(AutonomyPermission.REQUEST_HUMAN_REVIEW, work_order.permitted_actions)
        self.assertNotIn(AutonomyPermission.MODIFY_FILES_IN_BRANCH, work_order.permitted_actions)
        self.assertIn("sdk_unit_tests", work_order.required_evidence)

    def test_critical_execution_mission_is_blocked_and_cannot_modify_files(self) -> None:
        plan = self._build_plan(
            "sprint_blocked",
            (
                _mission(
                    "mission_execution",
                    "Execution adapter",
                    "Add submit_order path",
                    ("services/execution-engine/app/main.py",),
                ),
            ),
            capacity_points=3,
        )

        self.assertEqual(plan.blocked_count, 1)
        work_order = plan.work_orders[0]
        self.assertEqual(work_order.state, AutonomyActionState.BLOCKED)
        self.assertIn(AutonomyPermission.REQUEST_HUMAN_REVIEW, work_order.permitted_actions)
        self.assertNotIn(AutonomyPermission.MODIFY_FILES_IN_BRANCH, work_order.permitted_actions)
        self.assertIn("blocked_scope_record", work_order.required_evidence)
        self.assertFalse(work_order.execution_allowed)

    def test_deferred_work_is_planning_only(self) -> None:
        plan = self._build_plan(
            "sprint_deferred",
            (
                _mission("mission_a", "Docs A", "docs", ("docs/a.md",), mission_type=MissionType.DOCUMENTATION, complexity_score=2),
                _mission("mission_b", "Docs B", "docs", ("docs/b.md",), mission_type=MissionType.DOCUMENTATION, complexity_score=2),
            ),
            capacity_points=2,
        )
        deferred = [item for item in plan.work_orders if item.state is AutonomyActionState.DEFERRED]

        self.assertEqual(len(deferred), 1)
        self.assertEqual(deferred[0].permitted_actions, (AutonomyPermission.PLAN, AutonomyPermission.RECORD_EVIDENCE))

    def test_plan_payload_validates_and_never_grants_critical_authority(self) -> None:
        plan = self._build_plan(
            "sprint_contract",
            (
                _mission(
                    "mission_docs",
                    "Governance docs",
                    "Update governance docs",
                    ("docs/architecture/governed_autonomy.md",),
                    mission_type=MissionType.DOCUMENTATION,
                ),
            ),
            capabilities=(CapabilityState("governance", "contract", enabled=True),),
            capacity_points=2,
        )
        payload = plan.to_contract_payload(
            trace_id="trace_governed_autonomy_001",
            correlation_id="corr_governed_autonomy_001",
        )

        validation = ContractValidator().validate("governance", "governed_autonomy_plan", payload)

        self.assertTrue(validation.valid, validation.errors)
        for field in (
            "direct_main_write_allowed",
            "auto_merge_allowed",
            "network_allowed",
            "credentials_allowed",
            "risk_approval_allowed",
            "execution_allowed",
        ):
            self.assertFalse(payload[field])

    def test_planner_exposes_no_execution_methods(self) -> None:
        forbidden = {
            "buy",
            "sell",
            "order",
            "submit_order",
            "cancel_order",
            "edit_order",
            "withdraw",
            "transfer",
            "execute",
            "create_order",
            "auto_merge",
            "write_to_main",
        }

        self.assertTrue(forbidden.isdisjoint(dir(self.planner)))

    def _build_plan(
        self,
        sprint_id: str,
        missions: tuple[MissionCandidate, ...],
        *,
        capacity_points: int,
        capabilities: tuple[CapabilityState, ...] = (),
    ):
        sprint = self.sprint_manager.plan_sprint(
            sprint_id=sprint_id,
            product_model=self.product_model,
            capabilities=capabilities,
            missions=missions,
            capacity_points=capacity_points,
        )
        return self.planner.build_plan(sprint_plan=sprint, created_at=NOW)


def _mission(
    mission_id: str,
    title: str,
    summary: str,
    target_files: tuple[str, ...],
    *,
    mission_type: MissionType = MissionType.TESTING,
    complexity_score: int = 1,
) -> MissionCandidate:
    return MissionCandidate(
        mission_id=mission_id,
        title=title,
        mission_type=mission_type,
        summary=summary,
        target_files=target_files,
        expected_tests=("python -m unittest discover -s tests",),
        value_score=7,
        urgency_score=6,
        complexity_score=complexity_score,
        risk_score=1,
    )


if __name__ == "__main__":
    unittest.main()
