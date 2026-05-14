import copy
import unittest

from scripts import data_lineage_leakage_audit


class DataLineageLeakageAuditTests(unittest.TestCase):
    def setUp(self):
        self.dataset_lineage = data_lineage_leakage_audit.load_json(
            data_lineage_leakage_audit.DATASET_LINEAGE_FIXTURE
        )
        self.leakage_review = data_lineage_leakage_audit.load_json(
            data_lineage_leakage_audit.LEAKAGE_REVIEW_FIXTURE
        )

    def test_static_audit_passes_for_valid_fixtures(self):
        result = data_lineage_leakage_audit.audit_data_lineage_leakage()

        self.assertEqual(len(result.checked_files), 2)
        self.assertEqual(
            data_lineage_leakage_audit.REQUIRED_LEAKAGE_CHECKS,
            result.checked_leakage_checks,
        )

    def test_identity_mismatch_is_rejected(self):
        leakage_review = copy.deepcopy(self.leakage_review)
        leakage_review["dataset_id"] = "dataset_other"

        with self.assertRaises(data_lineage_leakage_audit.DataLineageLeakageAuditError):
            data_lineage_leakage_audit.audit_identity_links(self.dataset_lineage, leakage_review)

    def test_future_event_time_after_cutoff_is_rejected(self):
        dataset_lineage = copy.deepcopy(self.dataset_lineage)
        dataset_lineage["temporal_bounds"]["max_event_time_at"] = "2026-01-01T00:00:01Z"

        with self.assertRaises(data_lineage_leakage_audit.DataLineageLeakageAuditError):
            data_lineage_leakage_audit.audit_temporal_semantics(
                dataset_lineage,
                self.leakage_review,
            )

    def test_disabled_as_of_join_is_rejected(self):
        dataset_lineage = copy.deepcopy(self.dataset_lineage)
        dataset_lineage["point_in_time_controls"]["as_of_join_required"] = False

        with self.assertRaises(data_lineage_leakage_audit.DataLineageLeakageAuditError):
            data_lineage_leakage_audit.audit_point_in_time_controls(dataset_lineage)

    def test_missing_required_leakage_check_is_rejected(self):
        leakage_review = copy.deepcopy(self.leakage_review)
        leakage_review["checks"] = [
            check
            for check in leakage_review["checks"]
            if check["check_name"] != "target_leakage"
        ]

        with self.assertRaises(data_lineage_leakage_audit.DataLineageLeakageAuditError):
            data_lineage_leakage_audit.audit_leakage_review(leakage_review)

    def test_training_approval_is_rejected(self):
        leakage_review = copy.deepcopy(self.leakage_review)
        leakage_review["approved_for_model_training"] = True

        with self.assertRaises(data_lineage_leakage_audit.DataLineageLeakageAuditError):
            data_lineage_leakage_audit.audit_leakage_review(leakage_review)

    def test_module_does_not_import_network_or_subprocess_tools(self):
        source = data_lineage_leakage_audit.__loader__.get_source(
            data_lineage_leakage_audit.__name__
        )

        self.assertIsNotNone(source)
        assert source is not None
        self.assertNotIn("requests", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("socket", source)


if __name__ == "__main__":
    unittest.main()
