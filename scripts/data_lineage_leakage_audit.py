"""Local semantic audit for dataset lineage and leakage fixtures.

This auditor is intentionally local-only. It validates static governance fixtures
and performs deterministic point-in-time consistency checks without network,
credentials, data ingestion, feature computation, model training, backtesting or
trading.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from packages.contracts import ContractValidator


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "contracts" / "data"
DATASET_LINEAGE_FIXTURE = FIXTURE_ROOT / "dataset_lineage_record.valid.json"
LEAKAGE_REVIEW_FIXTURE = FIXTURE_ROOT / "leakage_review_report.valid.json"

REQUIRED_LEAKAGE_CHECKS = {
    "point_in_time_join",
    "future_label_exclusion",
    "target_leakage",
    "lookahead_features",
    "survivorship_bias",
    "train_test_overlap",
    "timestamp_alignment",
    "late_data_arrival",
    "feature_availability",
    "duplicate_event_contamination",
    "manual_override_review",
}

FORBIDDEN_TEXT_MARKERS = {
    "api_key",
    "private_key",
    "password",
    "broker_secret",
    "exchange_secret",
    "access_token",
    "refresh_token",
    "wallet_private_key",
}


class DataLineageLeakageAuditError(AssertionError):
    """Raised when static data governance fixtures fail semantic audit."""


@dataclass(frozen=True)
class AuditResult:
    checked_files: tuple[Path, ...]
    checked_leakage_checks: frozenset[str]


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise DataLineageLeakageAuditError(f"fixture root must be object: {path}")
    return payload


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_contracts(dataset_lineage: dict[str, Any], leakage_review: dict[str, Any]) -> None:
    validator = ContractValidator()
    validations = (
        validator.validate("data", "dataset_lineage_record", dataset_lineage),
        validator.validate("data", "leakage_review_report", leakage_review),
    )
    errors = [error for result in validations for error in result.errors]
    if errors:
        raise DataLineageLeakageAuditError("; ".join(errors))


def audit_identity_links(dataset_lineage: dict[str, Any], leakage_review: dict[str, Any]) -> None:
    expected_pairs = (
        "trace_id",
        "correlation_id",
        "dataset_lineage_id",
        "dataset_id",
    )
    for field in expected_pairs:
        if dataset_lineage[field] != leakage_review[field]:
            raise DataLineageLeakageAuditError(f"mismatched {field}")

    if dataset_lineage.get("leakage_review_report_id") != leakage_review["leakage_review_report_id"]:
        raise DataLineageLeakageAuditError("lineage record must point to leakage review report")


def audit_temporal_semantics(dataset_lineage: dict[str, Any], leakage_review: dict[str, Any]) -> None:
    bounds = dataset_lineage["temporal_bounds"]
    observation_start = parse_utc(bounds["observation_start_at"])
    observation_end = parse_utc(bounds["observation_end_at"])
    max_event_time = parse_utc(bounds["max_event_time_at"])
    as_of_cutoff = parse_utc(bounds["as_of_cutoff_at"])
    label_start = parse_utc(bounds["label_start_at"])
    label_end = parse_utc(bounds["label_end_at"])
    lineage_created_at = parse_utc(dataset_lineage["created_at"])
    reviewed_at = parse_utc(leakage_review["reviewed_at"])

    if not observation_start < observation_end:
        raise DataLineageLeakageAuditError("observation_start_at must be before observation_end_at")
    if not max_event_time <= as_of_cutoff:
        raise DataLineageLeakageAuditError("max_event_time_at must not exceed as_of_cutoff_at")
    if not observation_end <= as_of_cutoff:
        raise DataLineageLeakageAuditError("observation_end_at must not exceed as_of_cutoff_at")
    if not as_of_cutoff <= label_start < label_end:
        raise DataLineageLeakageAuditError("label horizon must start at or after cutoff and end later")
    if not as_of_cutoff <= lineage_created_at <= reviewed_at:
        raise DataLineageLeakageAuditError("lineage and review timestamps must follow cutoff order")

    for source in dataset_lineage["source_systems"]:
        completed_at = parse_utc(source["ingestion_completed_at"])
        watermark = parse_utc(source["source_watermark_at"])
        if not watermark <= as_of_cutoff:
            raise DataLineageLeakageAuditError("source watermark must not exceed as-of cutoff")
        if not completed_at <= lineage_created_at:
            raise DataLineageLeakageAuditError("source ingestion must complete before lineage record creation")


def audit_point_in_time_controls(dataset_lineage: dict[str, Any]) -> None:
    controls = dataset_lineage["point_in_time_controls"]
    split_policy = dataset_lineage["split_policy"]

    required_true_controls = (
        "as_of_join_required",
        "future_data_excluded",
        "feature_availability_tracked",
        "label_horizon_declared",
    )
    for field in required_true_controls:
        if controls[field] is not True:
            raise DataLineageLeakageAuditError(f"{field} must be true")

    if split_policy["temporal_order_preserved"] is not True:
        raise DataLineageLeakageAuditError("temporal order must be preserved")
    if split_policy["overlap_allowed"] is not False:
        raise DataLineageLeakageAuditError("split overlap must be disallowed")

    for transformation in dataset_lineage["transformations"]:
        if transformation["uses_future_information"] is not False:
            raise DataLineageLeakageAuditError("transformations must not use future information")


def audit_leakage_review(leakage_review: dict[str, Any]) -> frozenset[str]:
    if leakage_review["approved_for_model_training"] is not False:
        raise DataLineageLeakageAuditError("leakage review must not approve model training")
    if leakage_review["approved_for_backtest"] is not False:
        raise DataLineageLeakageAuditError("leakage review must not approve backtesting")
    if leakage_review["approved_for_live_use"] is not False:
        raise DataLineageLeakageAuditError("leakage review must not approve live use")

    checks = {check["check_name"] for check in leakage_review["checks"]}
    missing = REQUIRED_LEAKAGE_CHECKS - checks
    if missing:
        raise DataLineageLeakageAuditError(f"missing leakage checks: {sorted(missing)}")

    failed_critical = [
        check["check_name"]
        for check in leakage_review["checks"]
        if check["result"] == "FAIL" and check["severity"] in {"HIGH", "CRITICAL"}
    ]
    if failed_critical and leakage_review["remediation_required"] is not True:
        raise DataLineageLeakageAuditError(
            f"critical failed checks require remediation: {failed_critical}"
        )

    return frozenset(checks)


def audit_forbidden_markers() -> None:
    for path in (DATASET_LINEAGE_FIXTURE, LEAKAGE_REVIEW_FIXTURE):
        text = path.read_text(encoding="utf-8").lower()
        for marker in FORBIDDEN_TEXT_MARKERS:
            if marker in text:
                raise DataLineageLeakageAuditError(f"forbidden marker {marker!r} found in {path}")


def audit_data_lineage_leakage() -> AuditResult:
    dataset_lineage = load_json(DATASET_LINEAGE_FIXTURE)
    leakage_review = load_json(LEAKAGE_REVIEW_FIXTURE)

    validate_contracts(dataset_lineage, leakage_review)
    audit_identity_links(dataset_lineage, leakage_review)
    audit_temporal_semantics(dataset_lineage, leakage_review)
    audit_point_in_time_controls(dataset_lineage)
    checked_leakage_checks = audit_leakage_review(leakage_review)
    audit_forbidden_markers()

    return AuditResult(
        checked_files=(DATASET_LINEAGE_FIXTURE, LEAKAGE_REVIEW_FIXTURE),
        checked_leakage_checks=checked_leakage_checks,
    )


def main() -> None:
    result = audit_data_lineage_leakage()
    print(
        "data lineage/leakage audit passed: "
        f"{len(result.checked_files)} fixtures, "
        f"{len(result.checked_leakage_checks)} leakage checks"
    )


if __name__ == "__main__":
    main()
