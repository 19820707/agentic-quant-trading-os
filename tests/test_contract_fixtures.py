import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "contracts"

FIXTURES = {
    "order_intent.valid.json": ("trading", "order_intent"),
    "risk_decision.valid.json": ("trading", "risk_decision"),
    "approved_order.valid.json": ("trading", "approved_order"),
    "execution_report.valid.json": ("trading", "execution_report"),
    "audit_event.valid.json": ("audit", "audit_event"),
    "dataset_lineage_record.valid.json": ("features", "dataset_lineage_record"),
    "leakage_review_report.valid.json": ("features", "leakage_review_report"),
    "research_dossier.valid.json": ("research", "research_dossier"),
    "probability_estimate.valid.json": ("research", "probability_estimate"),
    "hypothesis_record.valid.json": ("research", "hypothesis_record"),
    "analyst_report.valid.json": ("research", "analyst_report"),
    "debate_transcript.valid.json": ("research", "debate_transcript"),
    "signal_candidate.valid.json": ("research", "signal_candidate"),
    "risk_review_input.valid.json": ("research", "risk_review_input"),
}

FORBIDDEN_KEYS = {
    "api_key",
    "password",
    "private_key",
    "broker_secret",
    "exchange_secret",
    "access_token",
    "refresh_token",
}


class ContractFixtureTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def test_all_contract_fixtures_validate(self):
        for fixture_name, (domain, schema_name) in FIXTURES.items():
            with self.subTest(fixture=fixture_name):
                payload = self._load_fixture(fixture_name)
                result = self.validator.validate(domain, schema_name, payload)
                self.assertTrue(result.valid, result.errors)

    def test_fixtures_are_paper_only_where_execution_context_exists(self):
        for fixture_name in FIXTURES:
            with self.subTest(fixture=fixture_name):
                payload = self._load_fixture(fixture_name)
                if "venue" in payload:
                    self.assertEqual(payload["venue"], "paper")
                if "execution_mode" in payload:
                    self.assertEqual(payload["execution_mode"], "PAPER")

    def test_fixtures_do_not_include_credentials_or_live_markers(self):
        for fixture_name in FIXTURES:
            with self.subTest(fixture=fixture_name):
                payload_text = (FIXTURE_ROOT / fixture_name).read_text(encoding="utf-8").lower()
                for forbidden_key in FORBIDDEN_KEYS:
                    self.assertNotIn(forbidden_key, payload_text)
                self.assertNotIn("live", payload_text)

    def test_fixtures_share_lifecycle_correlation_id(self):
        correlation_ids = {
            self._load_fixture(fixture_name)["correlation_id"]
            for fixture_name in FIXTURES
        }

        self.assertEqual(
            correlation_ids,
            {
                "corr_feature_contracts_001",
                "corr_fixture_lifecycle_001",
                "corr_research_contracts_001",
            },
        )

    def test_research_fixtures_are_non_executable(self):
        for fixture_name, (domain, _) in FIXTURES.items():
            if domain != "research":
                continue
            with self.subTest(fixture=fixture_name):
                payload = self._load_fixture(fixture_name)
                if "execution_allowed" in payload:
                    self.assertFalse(payload["execution_allowed"])
                if "order_intent_allowed" in payload:
                    self.assertFalse(payload["order_intent_allowed"])
                if "risk_approval_allowed" in payload:
                    self.assertFalse(payload["risk_approval_allowed"])
                if "model_training_approval_allowed" in payload:
                    self.assertFalse(payload["model_training_approval_allowed"])
                if "production_approval_allowed" in payload:
                    self.assertFalse(payload["production_approval_allowed"])

    def _load_fixture(self, fixture_name):
        with (FIXTURE_ROOT / fixture_name).open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)


if __name__ == "__main__":
    unittest.main()
