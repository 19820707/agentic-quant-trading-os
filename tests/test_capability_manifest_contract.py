import copy
import json
import unittest
from pathlib import Path

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "contracts" / "governance" / "capability_manifest.valid.json"

FORBIDDEN_STATES = {
    "LIVE_TRADING_ENABLED",
    "BROKER_PRIVATE_ENDPOINTS",
    "ORDER_SUBMISSION",
    "ORDER_CANCELLATION",
    "POSITION_MUTATION",
    "UNREVIEWED_AGENT_RUNTIME",
    "UNGATED_MEMORY_RUNTIME",
    "UNGATED_NETWORK_ACCESS",
    "UNGATED_CREDENTIAL_ACCESS",
    "BYPASS_DETERMINISTIC_RISK_GATEWAY",
}


class CapabilityManifestContractTests(unittest.TestCase):
    def setUp(self):
        self.validator = ContractValidator()
        self.fixture = self._fixture()

    def test_capability_manifest_fixture_validates(self):
        result = self.validator.validate("governance", "capability_manifest", self.fixture)

        self.assertTrue(result.valid, result.errors)

    def test_capability_manifest_defaults_runtime_to_disabled(self):
        defaults = self.fixture["runtime_defaults"]

        self.assertFalse(defaults["runtime_enabled"])
        self.assertFalse(defaults["production_enabled"])
        self.assertFalse(defaults["network_access_allowed"])
        self.assertFalse(defaults["credentials_allowed"])
        self.assertFalse(defaults["private_endpoints_allowed"])
        self.assertFalse(defaults["trading_methods_allowed"])
        self.assertFalse(defaults["risk_approval_allowed"])
        self.assertFalse(defaults["execution_approval_allowed"])

    def test_capability_manifest_tracks_forbidden_global_states(self):
        self.assertEqual(set(self.fixture["forbidden_global_states"]), FORBIDDEN_STATES)

    def test_capability_manifest_links_domains_to_tests_and_gates(self):
        domains = {capability["domain"]: capability for capability in self.fixture["capabilities"]}

        for domain in ("trading_contracts", "market_data_adapters", "agent_runtime", "execution_engine"):
            with self.subTest(domain=domain):
                capability = domains[domain]
                self.assertTrue(capability["required_tests"])
                self.assertTrue(capability["required_approval_gate"].endswith(".md"))
                self.assertTrue(capability["owner_boundary"])
                self.assertTrue(capability["forbidden_capability"])

    def test_capability_manifest_rejects_runtime_enabled_defaults(self):
        payload = copy.deepcopy(self.fixture)
        payload["runtime_defaults"]["runtime_enabled"] = True

        result = self.validator.validate("governance", "capability_manifest", payload)

        self.assertFalse(result.valid)

    def test_capability_manifest_rejects_unknown_maturity_state(self):
        payload = copy.deepcopy(self.fixture)
        payload["capabilities"][0]["current_status"] = "UNGATED_RUNTIME"

        result = self.validator.validate("governance", "capability_manifest", payload)

        self.assertFalse(result.valid)

    def _fixture(self):
        with FIXTURE.open(encoding="utf-8") as fixture_file:
            return json.load(fixture_file)


if __name__ == "__main__":
    unittest.main()
