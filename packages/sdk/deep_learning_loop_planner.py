from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from packages.sdk.autonomous_sprint_manager import MissionCandidate, MissionType


class DeepLearningLoopPlannerError(ValueError):
    """Raised when a deep-learning loop plan would cross a safety boundary."""


class DeepLearningCapability(str, Enum):
    DATASET_LINEAGE = "dataset_lineage"
    LEAKAGE_REVIEW = "leakage_review"
    FEATURE_MATERIALIZATION_REVIEW = "feature_materialization_review"
    MODEL_CARD_CONTRACT = "model_card_contract"
    TRAINING_RUN_CONTRACT = "training_run_contract"
    EVALUATION_REPORT = "evaluation_report"
    CALIBRATION_REPORT = "calibration_report"
    MONITORING_GATE = "monitoring_gate"
    DEPLOYMENT_APPROVAL_GATE = "deployment_approval_gate"


@dataclass(frozen=True)
class DeepLearningLoopRequest:
    request_id: str
    objective: str
    required_capabilities: tuple[DeepLearningCapability, ...] = tuple(DeepLearningCapability)
    max_missions: int = 12
    allow_training_runtime: bool = False
    allow_model_serving_runtime: bool = False
    allow_network: bool = False
    allow_credentials: bool = False
    allow_trading_signals: bool = False

    def __post_init__(self) -> None:
        _non_empty(self.request_id, "request_id")
        _non_empty(self.objective, "objective")
        if not self.required_capabilities:
            raise DeepLearningLoopPlannerError("required_capabilities must not be empty")
        if self.max_missions < 1 or self.max_missions > 50:
            raise DeepLearningLoopPlannerError("max_missions must be between 1 and 50")
        if self.allow_training_runtime:
            raise DeepLearningLoopPlannerError("training runtime is not approved by this planner")
        if self.allow_model_serving_runtime:
            raise DeepLearningLoopPlannerError("model serving runtime is not approved by this planner")
        if self.allow_network:
            raise DeepLearningLoopPlannerError("network access is not approved by this planner")
        if self.allow_credentials:
            raise DeepLearningLoopPlannerError("credentials are not approved by this planner")
        if self.allow_trading_signals:
            raise DeepLearningLoopPlannerError("trading signal production is not approved by this planner")


@dataclass(frozen=True)
class DeepLearningLoopPlan:
    request_id: str
    objective: str
    generated_missions: tuple[MissionCandidate, ...]
    omitted_capabilities: tuple[DeepLearningCapability, ...]
    safety_invariants: tuple[str, ...] = (
        "no training runtime",
        "no model serving runtime",
        "no network",
        "no credentials",
        "no trading signals",
        "no order intent creation",
        "no risk approval",
        "no execution approval",
    )
    training_runtime_allowed: bool = False
    model_serving_runtime_allowed: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False
    trading_signals_allowed: bool = False
    order_intent_allowed: bool = False
    risk_approval_allowed: bool = False
    execution_allowed: bool = False

    def to_summary(self) -> dict[str, object]:
        return {
            "request_id": self.request_id,
            "objective": self.objective,
            "generated_missions": [mission.mission_id for mission in self.generated_missions],
            "omitted_capabilities": [capability.value for capability in self.omitted_capabilities],
            "safety_invariants": list(self.safety_invariants),
            "training_runtime_allowed": self.training_runtime_allowed,
            "model_serving_runtime_allowed": self.model_serving_runtime_allowed,
            "network_allowed": self.network_allowed,
            "credentials_allowed": self.credentials_allowed,
            "trading_signals_allowed": self.trading_signals_allowed,
            "order_intent_allowed": self.order_intent_allowed,
            "risk_approval_allowed": self.risk_approval_allowed,
            "execution_allowed": self.execution_allowed,
        }


class DeepLearningLoopPlanner:
    """Generates contract-first deep-learning missions for Loop Engineering.

    The planner creates planning work only. It does not train models, import ML
    frameworks, read data, call network, read credentials, serve predictions,
    generate trading signals, approve risk, or approve execution.
    """

    def generate_missions(self, request: DeepLearningLoopRequest) -> DeepLearningLoopPlan:
        missions: list[MissionCandidate] = []
        omitted: list[DeepLearningCapability] = []
        for capability in request.required_capabilities:
            if len(missions) >= request.max_missions:
                omitted.append(capability)
                continue
            missions.append(_mission_for(capability))

        return DeepLearningLoopPlan(
            request_id=request.request_id,
            objective=request.objective,
            generated_missions=tuple(missions),
            omitted_capabilities=tuple(omitted),
        )


def build_default_deep_learning_loop_planner() -> DeepLearningLoopPlanner:
    return DeepLearningLoopPlanner()


def _mission_for(capability: DeepLearningCapability) -> MissionCandidate:
    definitions = {
        DeepLearningCapability.DATASET_LINEAGE: (
            "dl_dataset_lineage_contract",
            "Deep learning dataset lineage contract",
            MissionType.CONTRACT,
            "Define local-only dataset lineage requirements for future deep learning research.",
            (
                "packages/contracts/schemas/features/deep_learning_dataset_lineage.schema.json",
                "tests/test_deep_learning_dataset_lineage_contract.py",
                "docs/architecture/deep_learning_dataset_lineage.md",
            ),
            10,
            10,
            2,
        ),
        DeepLearningCapability.LEAKAGE_REVIEW: (
            "dl_leakage_review_contract",
            "Deep learning leakage review contract",
            MissionType.CONTRACT,
            "Define point-in-time and leakage review evidence before any future learning experiment.",
            (
                "packages/contracts/schemas/features/deep_learning_leakage_review.schema.json",
                "tests/test_deep_learning_leakage_review_contract.py",
                "docs/architecture/deep_learning_leakage_review.md",
            ),
            10,
            10,
            2,
        ),
        DeepLearningCapability.FEATURE_MATERIALIZATION_REVIEW: (
            "dl_feature_materialization_review",
            "Deep learning feature materialization review",
            MissionType.CONTRACT,
            "Define fake offline feature materialization review before future learning experiments.",
            (
                "packages/contracts/schemas/features/deep_learning_feature_materialization_review.schema.json",
                "tests/test_deep_learning_feature_materialization_review.py",
                "docs/architecture/deep_learning_feature_materialization_review.md",
            ),
            9,
            9,
            2,
        ),
        DeepLearningCapability.MODEL_CARD_CONTRACT: (
            "dl_model_card_contract",
            "Deep learning model card contract",
            MissionType.CONTRACT,
            "Define model card metadata, intended use, limitations and prohibited runtime use.",
            (
                "packages/contracts/schemas/models/deep_learning_model_card.schema.json",
                "tests/test_deep_learning_model_card_contract.py",
                "docs/architecture/deep_learning_model_card.md",
            ),
            9,
            8,
            2,
        ),
        DeepLearningCapability.TRAINING_RUN_CONTRACT: (
            "dl_training_run_contract",
            "Deep learning training run contract",
            MissionType.CONTRACT,
            "Define future offline training run metadata as a contract, without implementing training runtime.",
            (
                "packages/contracts/schemas/models/deep_learning_training_run.schema.json",
                "tests/test_deep_learning_training_run_contract.py",
                "docs/architecture/deep_learning_training_run.md",
            ),
            8,
            8,
            2,
        ),
        DeepLearningCapability.EVALUATION_REPORT: (
            "dl_evaluation_report_contract",
            "Deep learning evaluation report contract",
            MissionType.CONTRACT,
            "Define deterministic offline evaluation report fields and acceptance gates.",
            (
                "packages/contracts/schemas/models/deep_learning_evaluation_report.schema.json",
                "tests/test_deep_learning_evaluation_report_contract.py",
                "docs/architecture/deep_learning_evaluation_report.md",
            ),
            9,
            9,
            2,
        ),
        DeepLearningCapability.CALIBRATION_REPORT: (
            "dl_calibration_report_contract",
            "Deep learning calibration report contract",
            MissionType.CONTRACT,
            "Define calibration, reliability buckets and drift review requirements for future models.",
            (
                "packages/contracts/schemas/models/deep_learning_calibration_report.schema.json",
                "tests/test_deep_learning_calibration_report_contract.py",
                "docs/architecture/deep_learning_calibration_report.md",
            ),
            9,
            9,
            2,
        ),
        DeepLearningCapability.MONITORING_GATE: (
            "dl_model_monitoring_gate",
            "Deep learning model monitoring gate",
            MissionType.CONTRACT,
            "Define local monitoring gate requirements for drift, stale data, calibration and rollback.",
            (
                "packages/contracts/schemas/models/deep_learning_monitoring_gate.schema.json",
                "tests/test_deep_learning_monitoring_gate.py",
                "docs/architecture/deep_learning_monitoring_gate.md",
            ),
            8,
            8,
            2,
        ),
        DeepLearningCapability.DEPLOYMENT_APPROVAL_GATE: (
            "dl_deployment_approval_gate",
            "Deep learning deployment approval gate",
            MissionType.CONTRACT,
            "Define approval gate requirements before any future model can influence downstream services.",
            (
                "packages/contracts/schemas/models/deep_learning_deployment_gate.schema.json",
                "tests/test_deep_learning_deployment_gate.py",
                "docs/architecture/deep_learning_deployment_gate.md",
            ),
            8,
            8,
            2,
        ),
    }
    mission_id, title, mission_type, summary, target_files, value, urgency, complexity = definitions[capability]
    return MissionCandidate(
        mission_id=mission_id,
        title=title,
        mission_type=mission_type,
        summary=summary,
        target_files=target_files,
        expected_tests=("python -m unittest discover -s tests",),
        value_score=value,
        urgency_score=urgency,
        complexity_score=complexity,
        risk_score=2,
    )


def _non_empty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise DeepLearningLoopPlannerError(f"{field_name} must be a non-empty string")
