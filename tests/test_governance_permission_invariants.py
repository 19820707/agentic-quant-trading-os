"""Cross-fixture governance invariants on the explicit permission flags.

The platform encodes safety as boolean permission flags on contracts. Individual
contract tests assert their own flags; this meta-test asserts two cross-cutting
invariants UNIFORMLY across every valid fixture (present and future), so a new
fixture can never silently grant a forbidden capability (fail-closed):

  1. Eight capabilities are NEVER granted anywhere (broker credentials, credentials,
     trading, trading changes, auto-merge, apply-to-main, direct-main-write,
     risk-approval).
  2. Execution authorization (`execution_allowed = True`) appears ONLY on the
     `ApprovedOrder` — the sole object the Risk Gateway clears for execution. Any
     other fixture granting it is a violation.

Pure stdlib, deterministic. Scans tests/fixtures/contracts/*.valid.json recursively.
"""

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "contracts"

# Never True in any governed fixture.
UNIVERSALLY_FORBIDDEN = (
    "broker_credentials_allowed",
    "credentials_allowed",
    "trading_allowed",
    "trading_changes_allowed",
    "auto_merge_allowed",
    "apply_to_main_allowed",
    "direct_main_write_allowed",
    "risk_approval_allowed",
)
# `execution_allowed = True` is legitimate ONLY here (the Risk Gateway's output).
EXECUTION_ALLOWED_FIXTURES = {"approved_order"}


def _walk(obj, path, hits):
    """Collect (key, value, json_path) for every permission-flag key encountered."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            here = f"{path}.{key}"
            if key in UNIVERSALLY_FORBIDDEN or key == "execution_allowed":
                hits.append((key, value, here))
            _walk(value, here, hits)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            _walk(value, f"{path}[{i}]", hits)


class GovernancePermissionInvariantTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = sorted(FIXTURES.glob("*.valid.json"))
        self.assertTrue(self.fixtures, f"no fixtures under {FIXTURES}")
        self.by_fixture = {p: _collect(p) for p in self.fixtures}

    def test_universally_forbidden_capabilities_are_false_everywhere(self):
        offenders = []
        for path, hits in self.by_fixture.items():
            for key, value, jpath in hits:
                if key in UNIVERSALLY_FORBIDDEN and value is not False:
                    offenders.append(f"{path.name}:{jpath} = {value!r}")
        self.assertEqual(offenders, [], "forbidden capability granted:\n  " + "\n  ".join(offenders))

    def test_execution_authorization_only_on_approved_order(self):
        offenders = []
        for path, hits in self.by_fixture.items():
            stem = path.name.split(".")[0]
            for key, value, jpath in hits:
                if key == "execution_allowed" and value is True and stem not in EXECUTION_ALLOWED_FIXTURES:
                    offenders.append(f"{path.name}:{jpath} = True")
        self.assertEqual(
            offenders, [],
            "execution_allowed=True outside the ApprovedOrder:\n  " + "\n  ".join(offenders))

    def test_invariant_is_not_vacuous(self):
        seen = {key for hits in self.by_fixture.values() for key, _, _ in hits}
        self.assertTrue(seen, "no fixture declares any permission flag — invariant is vacuous")


def _collect(path):
    hits = []
    _walk(json.loads(path.read_text(encoding="utf-8")), path.name, hits)
    return hits


if __name__ == "__main__":
    unittest.main()
