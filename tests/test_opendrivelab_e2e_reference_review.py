import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs" / "integrations" / "opendrivelab_e2e_autonomous_driving_reference_review.md"
GOVERNANCE = ROOT / "docs" / "architecture" / "model_evaluation_governance.md"
CI = ROOT / ".github" / "workflows" / "ci.yml"
PYPROJECT = ROOT / "pyproject.toml"


class OpenDriveLabE2EReferenceReviewTests(unittest.TestCase):
    def test_reference_review_keeps_repository_reference_only(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        required_flags = [
            "opendrivelab_e2e_reference_reviewed: true",
            "reference_only: true",
            "direct_dependency_allowed: false",
            "clone_allowed: false",
            "vendoring_allowed: false",
            "dataset_download_allowed: false",
            "benchmark_runtime_allowed: false",
            "simulator_runtime_allowed: false",
            "model_runtime_allowed: false",
            "end_to_end_execution_allowed: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "trading_methods_allowed: false",
            "production_enabled: false",
        ]

        for flag in required_flags:
            with self.subTest(flag=flag):
                self.assertIn(flag, text)

    def test_reference_review_documents_safe_patterns(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        for pattern in (
            "research taxonomy",
            "open-loop and closed-loop evaluation",
            "benchmark discipline",
            "dataset catalog discipline",
            "challenge and leaderboard pattern",
        ):
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)

    def test_reference_review_rejects_runtime_components(self):
        text = REVIEW.read_text(encoding="utf-8").lower()

        for component in (
            "autonomous-driving datasets",
            "dataset download scripts",
            "simulator runtimes",
            "benchmark execution frameworks",
            "model training code",
            "pretrained model artifacts",
            "multimodal sensor pipelines",
            "end-to-end control policies",
            "external leaderboard integrations",
        ):
            with self.subTest(component=component):
                self.assertIn(component, text)

    def test_model_evaluation_governance_defines_required_boundaries(self):
        text = GOVERNANCE.read_text(encoding="utf-8").lower()

        for phrase in (
            "open_loop",
            "closed_loop_simulated",
            "paper_only",
            "data leakage",
            "lookahead bias",
            "calibration drift",
            "evaluation results are evidence only",
            "cannot create `orderintent`",
            "deterministic-risk-gateway",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_pyproject_does_not_add_opendrivelab_runtime_dependencies(self):
        text = PYPROJECT.read_text(encoding="utf-8").lower()

        for forbidden in (
            "opendrivelab",
            "end-to-end-autonomous-driving",
            "carla",
            "nuplan",
            "nuscenes",
            "argoverse",
            "waymo",
            "uniad",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, text)

    def test_ci_runs_opendrivelab_reference_review_tests(self):
        text = CI.read_text(encoding="utf-8")
        self.assertIn("test_opendrivelab_e2e_reference_review.py", text)


if __name__ == "__main__":
    unittest.main()
