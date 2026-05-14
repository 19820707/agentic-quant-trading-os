import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs" / "architecture" / "capability_maturity_matrix.md"
FIXTURE = ROOT / "tests" / "fixtures" / "contracts" / "governance" / "capability_manifest.valid.json"
SCAFFOLD_AUDIT = ROOT / "scripts" / "scaffold_audit.py"

FORBIDDEN_STATES = (
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
)


class RuntimeCapabilityForbiddenStateTests(unittest.TestCase):
    def test_forbidden_states_are_documented_and_manifested(self):
        matrix_text = MATRIX.read_text(encoding="utf-8")
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

        for state in FORBIDDEN_STATES:
            with self.subTest(state=state):
                self.assertIn(state, matrix_text)
                self.assertIn(state, fixture["forbidden_global_states"])

    def test_scaffold_audit_checks_capability_governance(self):
        text = SCAFFOLD_AUDIT.read_text(encoding="utf-8")

        self.assertIn("check_capability_governance", text)
        self.assertIn("capability_manifest.valid.json", text)
        self.assertIn("capability_maturity_matrix.md", text)

    def test_no_forbidden_state_is_documented_as_enabled(self):
        searchable_paths = [
            MATRIX,
            ROOT / "docs" / "architecture" / "promotion_gates.md",
            ROOT / "docs" / "architecture" / "service_boundaries.md",
            ROOT / "README.md",
        ]

        enabled_patterns = [
            f"{state}: true"
            for state in FORBIDDEN_STATES
        ] + [
            f"{state}=true"
            for state in FORBIDDEN_STATES
        ]

        for path in searchable_paths:
            text = path.read_text(encoding="utf-8")
            for pattern in enabled_patterns:
                with self.subTest(path=path.name, pattern=pattern):
                    self.assertNotIn(pattern, text)


if __name__ == "__main__":
    unittest.main()
