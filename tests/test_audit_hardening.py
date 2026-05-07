"""Tests for AuditEventEmitter hardening: outcome validation, environment, constants."""

import unittest

from packages.common.audit import (
    ALLOWED_OUTCOMES,
    SCHEMA_VERSION,
    AuditEventBuildError,
    AuditEventEmitter,
)


def _emitter(**kwargs) -> AuditEventEmitter:
    return AuditEventEmitter(source_service=kwargs.pop("source_service", "test-service"), **kwargs)


def _base_event(emitter: AuditEventEmitter, **overrides) -> dict:
    defaults = dict(
        trace_id="trace-001",
        correlation_id="corr-001",
        event_type="LOCAL_TEST_EVENT",
        event_category="TEST",
        actor_type="AGENT",
        actor_id="agent-001",
        action="LOCAL_TEST_ACTION",
        entity_type="order_intent",
        entity_id="oi-001",
        outcome="INFO",
    )
    defaults.update(overrides)
    return emitter.build_event(**defaults)


class OutcomeValidationTests(unittest.TestCase):
    def test_all_allowed_outcomes_accepted(self):
        emitter = _emitter()
        for outcome in ALLOWED_OUTCOMES:
            event = _base_event(emitter, outcome=outcome)
            self.assertEqual(event["outcome"], outcome)

    def test_unknown_outcome_raises(self):
        emitter = _emitter()
        with self.assertRaises(AuditEventBuildError) as ctx:
            _base_event(emitter, outcome="UNKNOWN_OUTCOME")
        self.assertIn("outcome", str(ctx.exception).lower())

    def test_empty_outcome_raises(self):
        emitter = _emitter()
        with self.assertRaises(AuditEventBuildError):
            _base_event(emitter, outcome="")

    def test_lowercase_outcome_rejected(self):
        # Outcomes are case-sensitive: only uppercase is canonical.
        emitter = _emitter()
        with self.assertRaises(AuditEventBuildError):
            _base_event(emitter, outcome="info")

    def test_allowed_outcomes_is_frozenset(self):
        self.assertIsInstance(ALLOWED_OUTCOMES, frozenset)
        self.assertGreater(len(ALLOWED_OUTCOMES), 0)


class SchemaVersionTests(unittest.TestCase):
    def test_schema_version_constant_is_string(self):
        self.assertIsInstance(SCHEMA_VERSION, str)
        self.assertTrue(SCHEMA_VERSION)

    def test_event_schema_version_matches_constant(self):
        emitter = _emitter()
        event = _base_event(emitter)
        self.assertEqual(event["schema_version"], SCHEMA_VERSION)


class EnvironmentFieldTests(unittest.TestCase):
    def test_environment_absent_when_not_set(self):
        emitter = _emitter()
        event = _base_event(emitter)
        self.assertNotIn("environment", event)

    def test_environment_included_when_set(self):
        emitter = _emitter(environment="paper-test")
        event = _base_event(emitter)
        self.assertEqual(event["environment"], "paper-test")

    def test_environment_propagates_across_multiple_builds(self):
        emitter = _emitter(environment="staging")
        for _ in range(3):
            event = _base_event(emitter)
            self.assertEqual(event["environment"], "staging")

    def test_environment_does_not_override_other_fields(self):
        emitter = _emitter(environment="local")
        event = _base_event(emitter)
        self.assertIn("trace_id", event)
        self.assertIn("actor_id", event)
        self.assertEqual(event["contains_secrets"], False)


class InvariantsTests(unittest.TestCase):
    def test_append_only_always_true(self):
        emitter = _emitter()
        event = _base_event(emitter)
        self.assertIs(event["append_only"], True)

    def test_contains_secrets_always_false(self):
        emitter = _emitter()
        event = _base_event(emitter, metadata={"api_key": "example-secret"})
        self.assertIs(event["contains_secrets"], False)

    def test_metadata_with_secret_is_redacted_in_payload(self):
        from packages.common.security import REDACTED_VALUE
        emitter = _emitter()
        event = _base_event(emitter, metadata={"api_key": "example-secret", "venue": "paper"})
        self.assertEqual(event["metadata"]["api_key"], REDACTED_VALUE)
        self.assertEqual(event["metadata"]["venue"], "paper")

    def test_redaction_applied_true_when_metadata_present(self):
        emitter = _emitter()
        event = _base_event(emitter, metadata={"safe": "value"})
        self.assertIs(event["redaction_applied"], True)

    def test_redaction_applied_false_when_no_optional_fields(self):
        emitter = _emitter()
        event = _base_event(emitter)
        self.assertIs(event["redaction_applied"], False)

    def test_unknown_lifecycle_id_key_raises(self):
        emitter = _emitter()
        with self.assertRaises(AuditEventBuildError) as ctx:
            _base_event(emitter, lifecycle_ids={"unknown_custom_id": "val-001"})
        self.assertIn("unknown lifecycle ID keys", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
