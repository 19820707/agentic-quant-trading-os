import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_ROOT = ROOT / "packages" / "contracts" / "schemas" / "governance"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts"

EVIDENCE_CONTRACTS = {
    "sandbox_execution_report": "sandbox_execution_report.valid.json",
    "test_evidence_report": "test_evidence_report.valid.json",
    "rollback_plan": "rollback_plan.valid.json",
}

FALSE_FIELDS = (
    "auto_merge_allowed",
    "network_allowed",
    "credentials_allowed",
    "risk_approval_allowed",
    "execution_allowed",
)


class AgenticEvidenceContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()

    def test_evidence_schemas_are_closed(self):
        for name in EVIDENCE_CONTRACTS:
            with self.subTest(schema=name):
                schema = self._schema(name)
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["type"], "object")
                self.assertFalse(schema["additionalProperties"])
                self.assertTrue(schema["$id"].endswith(f"/schemas/governance/{name}.schema.json"))

    def test_evidence_fixtures_validate(self):
        for name in EVIDENCE_CONTRACTS:
            with self.subTest(schema=name):
                result = self.validator.validate("governance", name, self._fixture(name))
                self.assertTrue(result.valid, result.errors)

    def test_evidence_fixtures_do_not_grant_runtime_authority(self):
        for name in EVIDENCE_CONTRACTS:
            fixture = self._fixture(name)
            with self.subTest(schema=name):
                for field in FALSE_FIELDS:
                    self.assertFalse(fixture[field])
                if "requires_human_review" in fixture:
                    self.assertTrue(fixture["requires_human_review"])
                if "requires_human_approval" in fixture:
                    self.assertTrue(fixture["requires_human_approval"])

    def test_sandbox_report_forbids_network_and_credentials_observation(self):
        fixture = self._fixture("sandbox_execution_report")

        for field in ("network_observed", "credentials_observed"):
            changed = copy.deepcopy(fixture)
            changed[field] = True
            with self.subTest(field=field):
                result = self.validator.validate("governance", "sandbox_execution_report", changed)
                self.assertFalse(result.valid)

    def test_test_evidence_does_not_allow_auto_merge_even_when_tests_pass(self):
        fixture = self._fixture("test_evidence_report")
        fixture["auto_merge_allowed"] = True

        result = self.validator.validate("governance", "test_evidence_report", fixture)

        self.assertFalse(result.valid)

    def test_rollback_plan_does_not_allow_automated_or_production_rollback(self):
        for field in ("automated_rollback_allowed", "production_rollback_allowed"):
            fixture = self._fixture("rollback_plan")
            fixture[field] = True
            with self.subTest(field=field):
                result = self.validator.validate("governance", "rollback_plan", fixture)
                self.assertFalse(result.valid)

    def test_evidence_chain_uses_same_patch_plan_and_correlation_id(self):
        sandbox = self._fixture("sandbox_execution_report")
        tests = self._fixture("test_evidence_report")
        rollback = self._fixture("rollback_plan")

        self.assertEqual(sandbox["agent_patch_plan_id"], "app_docs_quality_gate_001")
        self.assertEqual(tests["agent_patch_plan_id"], sandbox["agent_patch_plan_id"])
        self.assertEqual(rollback["agent_patch_plan_id"], sandbox["agent_patch_plan_id"])
        self.assertEqual(
            {sandbox["correlation_id"], tests["correlation_id"], rollback["correlation_id"]},
            {"corr_agentic_governance_001"},
        )

    def _schema(self, name):
        with (SCHEMA_ROOT / f"{name}.schema.json").open(encoding="utf-8") as schema_file:
            return json.load(schema_file)

    def _fixture(self, name):
        fixture_name = EVIDENCE_CONTRACTS[name]
        with (FIXTURE_ROOT / fixture_name).open(encoding="utf-8") as fixture_file:
            return copy.deepcopy(json.load(fixture_file))


if __name__ == "__main__":
    unittest.main()
