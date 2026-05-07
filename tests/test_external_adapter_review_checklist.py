from pathlib import Path
import unittest


CHECKLIST_PATH = Path("docs/integrations/external_adapter_review_checklist.md")


def _checklist_text() -> str:
    return CHECKLIST_PATH.read_text(encoding="utf-8")


class ExternalAdapterReviewChecklistTests(unittest.TestCase):
    def test_required_sections_exist(self):
        text = _checklist_text()

        for section in (
            "## 1. Purpose",
            "## 2. Adapter Identity",
            "## 3. Safety Boundary",
            "## 4. Dependency Review",
            "## 5. Credential and Secret Review",
            "## 6. Network Behavior Review",
            "## 7. Contract Boundary Review",
            "## 8. Category-Specific Review",
            "## 9. Testing Requirements",
            "## 10. Approval Gates",
            "## 11. Final Decision",
        ):
            self.assertIn(section, text)

    def test_mentions_license_review(self):
        self.assertIn("license reviewed", _checklist_text().lower())

    def test_mentions_credential_and_secret_review(self):
        text = _checklist_text().lower()

        self.assertIn("credential and secret review", text)
        self.assertIn("no credentials committed", text)
        self.assertIn("redaction applied to errors", text)

    def test_mentions_no_withdrawal_permissions(self):
        self.assertIn("no withdrawal permissions", _checklist_text().lower())

    def test_mentions_no_network_calls_in_unit_tests(self):
        self.assertIn("no network calls in unit tests", _checklist_text().lower())

    def test_mentions_internal_contracts(self):
        text = _checklist_text().lower()

        self.assertIn("internal contract selected", text)
        self.assertIn("mapped to internal contracts", text)

    def test_mentions_point_in_time_correctness(self):
        self.assertIn("point-in-time correctness", _checklist_text().lower())

    def test_mentions_approved_order_only_future_execution(self):
        text = _checklist_text()

        self.assertIn("ApprovedOrder only", text)
        self.assertIn("reject raw OrderIntent", text)

    def test_mentions_mcp_tools_cannot_execute_trades(self):
        self.assertIn("cannot execute trades", _checklist_text().lower())

    def test_mentions_ci_quality_gates(self):
        self.assertIn("CI quality gates updated", _checklist_text())

    def test_mentions_final_decision_classifications(self):
        text = _checklist_text()

        for classification in (
            "rejected",
            "reference-only",
            "approved for research",
            "approved for paper",
            "approved for read-only production",
            "approved for controlled-live execution",
        ):
            self.assertIn(classification, text)

    def test_checklist_test_is_local_only(self):
        self.assertTrue(CHECKLIST_PATH.is_file())


if __name__ == "__main__":
    unittest.main()
