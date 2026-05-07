"""Tests for security redaction hardening: depth guard, redact_for_log, public API."""

import json
import unittest

from packages.common.security import (
    DEFAULT_SENSITIVE_KEYS,
    MAX_REDACTION_DEPTH,
    REDACTED_VALUE,
    redact_for_log,
    redact_secrets,
    redact_value,
)


class DepthGuardTests(unittest.TestCase):
    def _build_nested(self, depth: int) -> dict:
        """Build a dict nested `depth` levels deep with a secret at the leaf."""
        node: dict = {"api_key": "example-secret"}
        for _ in range(depth):
            node = {"nested": node}
        return node

    def test_shallow_nesting_redacts_secret(self):
        payload = self._build_nested(3)
        redacted = redact_secrets(payload)
        leaf = redacted
        for _ in range(3):
            leaf = leaf["nested"]
        self.assertEqual(leaf["api_key"], REDACTED_VALUE)

    def test_depth_at_limit_cuts_subtree(self):
        # Structure: MAX_REDACTION_DEPTH wrappers + leaf dict with api_key.
        # The guard fires at depth == MAX_REDACTION_DEPTH, replacing the child
        # of the last fully-processed dict with REDACTED_VALUE.
        payload = self._build_nested(MAX_REDACTION_DEPTH)
        redacted = redact_secrets(payload)

        # Traverse MAX_REDACTION_DEPTH - 1 levels; the dict at that depth
        # must have its "nested" value replaced by the guard.
        node = redacted
        for _ in range(MAX_REDACTION_DEPTH - 1):
            self.assertIsInstance(node, dict, "expected dict at intermediate depth")
            node = node["nested"]

        self.assertIsInstance(node, dict)
        self.assertEqual(node["nested"], REDACTED_VALUE)

    def test_beyond_depth_limit_never_exposes_secret(self):
        payload = self._build_nested(MAX_REDACTION_DEPTH + 10)
        result = redact_secrets(payload)
        dumped = json.dumps(result, default=str)
        self.assertNotIn("example-secret", dumped)

    def test_wide_shallow_dict_fully_redacted(self):
        # Use canonical sensitive key names — only exact matches are redacted.
        sensitive_keys = sorted(DEFAULT_SENSITIVE_KEYS)[:10]
        payload = {key: f"secret-for-{key}" for key in sensitive_keys}
        redacted = redact_secrets(payload)
        for key, value in redacted.items():
            self.assertEqual(value, REDACTED_VALUE, f"key {key!r} was not redacted")

    def test_depth_guard_on_sequence(self):
        deep_list: list = ["secret"]
        for _ in range(MAX_REDACTION_DEPTH):
            deep_list = [deep_list]
        result = redact_value(deep_list)
        self.assertIsInstance(result, list)
        dumped = json.dumps(result, default=str)
        self.assertNotIn("secret", dumped)


class RedactForLogTests(unittest.TestCase):
    def test_returns_valid_json_string(self):
        payload = {"symbol": "BTC/USDT", "api_key": "example-key"}
        result = redact_for_log(payload)
        parsed = json.loads(result)
        self.assertEqual(parsed["api_key"], REDACTED_VALUE)
        self.assertEqual(parsed["symbol"], "BTC/USDT")

    def test_returns_string_type(self):
        result = redact_for_log({"ok": True})
        self.assertIsInstance(result, str)

    def test_safe_on_non_json_serialisable_scalar(self):
        from decimal import Decimal
        payload = {"price": Decimal("1.23"), "api_key": "example"}
        result = redact_for_log(payload)
        parsed = json.loads(result)
        self.assertEqual(parsed["api_key"], REDACTED_VALUE)

    def test_label_appears_on_failure_path(self):
        # Bomb raises in __str__ so json.dumps(default=str) propagates the error.
        class Bomb:
            def __str__(self) -> str:
                raise RuntimeError("serialisation-bomb")

        result = redact_for_log(Bomb(), label="order_intent")
        self.assertIn("order_intent", result)
        self.assertIn("redaction-failed", result)

    def test_empty_dict_returns_json_object(self):
        result = redact_for_log({})
        self.assertEqual(json.loads(result), {})

    def test_scalar_string_preserved_in_log(self):
        result = redact_for_log("safe diagnostic message")
        parsed = json.loads(result)
        self.assertEqual(parsed, "safe diagnostic message")

    def test_nested_secrets_redacted_in_log_output(self):
        payload = {"metadata": {"token": "example-token", "venue": "paper"}}
        result = redact_for_log(payload)
        parsed = json.loads(result)
        self.assertEqual(parsed["metadata"]["token"], REDACTED_VALUE)
        self.assertEqual(parsed["metadata"]["venue"], "paper")


class PublicApiTests(unittest.TestCase):
    def test_all_exports_importable(self):
        from packages.common import security
        for name in security.__all__:
            self.assertTrue(hasattr(security, name), f"__all__ entry {name!r} not found")

    def test_redacted_value_is_string(self):
        self.assertIsInstance(REDACTED_VALUE, str)

    def test_max_redaction_depth_is_positive_int(self):
        self.assertIsInstance(MAX_REDACTION_DEPTH, int)
        self.assertGreater(MAX_REDACTION_DEPTH, 0)


if __name__ == "__main__":
    unittest.main()
