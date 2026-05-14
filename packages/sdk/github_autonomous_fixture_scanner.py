from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .github_autonomous_maintenance import (
    AutonomousCredentialBlocked,
    AutonomousMaintenanceDryRunPipeline,
    EvidenceRecord,
    _reject_credential_like_values,
)


class FixtureScannerError(Exception):
    """Raised when local fixture-driven scanning cannot proceed safely."""


@dataclass(frozen=True)
class WorkflowCheckFixture:
    name: str
    conclusion: str
    summary: str


@dataclass(frozen=True)
class WorkflowRunFixture:
    repository: str
    workflow_name: str
    event: str
    head_branch: str
    checks: tuple[WorkflowCheckFixture, ...]

    @property
    def failed_check_summaries(self) -> tuple[str, ...]:
        return tuple(
            f"{check.name}: {check.summary}"
            for check in self.checks
            if check.conclusion == "failure"
        )


class LocalWorkflowFixtureScanner:
    """Read local workflow fixtures and convert failures into dry-run evidence."""

    def load(self, path: Path | str) -> WorkflowRunFixture:
        fixture_path = Path(path)
        if not fixture_path.is_file():
            raise FixtureScannerError(f"workflow fixture not found: {fixture_path}")

        with fixture_path.open(encoding="utf-8") as fixture_file:
            payload = json.load(fixture_file)

        return self._parse(payload)

    def scan(self, paths: Iterable[Path | str]) -> list[WorkflowRunFixture]:
        return [self.load(path) for path in paths]

    def _parse(self, payload: dict[str, Any]) -> WorkflowRunFixture:
        required = ("repository", "workflow_name", "event", "head_branch", "checks")
        missing = [field for field in required if field not in payload]
        if missing:
            raise FixtureScannerError(f"workflow fixture missing required fields: {', '.join(missing)}")

        values = (
            str(payload["repository"]),
            str(payload["workflow_name"]),
            str(payload["event"]),
            str(payload["head_branch"]),
        )
        _reject_credential_like_values(values)

        checks = []
        for raw_check in payload["checks"]:
            check = WorkflowCheckFixture(
                name=str(raw_check["name"]),
                conclusion=str(raw_check["conclusion"]),
                summary=str(raw_check["summary"]),
            )
            _reject_credential_like_values((check.name, check.conclusion, check.summary))
            checks.append(check)

        return WorkflowRunFixture(
            repository=str(payload["repository"]),
            workflow_name=str(payload["workflow_name"]),
            event=str(payload["event"]),
            head_branch=str(payload["head_branch"]),
            checks=tuple(checks),
        )


class FixtureDrivenAutonomousMaintenanceScanner:
    """Run the dry-run maintenance pipeline from local workflow fixtures only."""

    def __init__(
        self,
        fixture_scanner: LocalWorkflowFixtureScanner | None = None,
        pipeline: AutonomousMaintenanceDryRunPipeline | None = None,
    ) -> None:
        self.fixture_scanner = fixture_scanner or LocalWorkflowFixtureScanner()
        self.pipeline = pipeline or AutonomousMaintenanceDryRunPipeline()

    def run(self, fixture_paths: Iterable[Path | str]) -> list[EvidenceRecord]:
        evidence_records: list[EvidenceRecord] = []

        for workflow_run in self.fixture_scanner.scan(fixture_paths):
            failed_checks = workflow_run.failed_check_summaries
            if not failed_checks:
                continue
            evidence_records.extend(self.pipeline.run([workflow_run.repository], failed_checks))

        return evidence_records


__all__ = [
    "AutonomousCredentialBlocked",
    "FixtureDrivenAutonomousMaintenanceScanner",
    "FixtureScannerError",
    "LocalWorkflowFixtureScanner",
    "WorkflowCheckFixture",
    "WorkflowRunFixture",
]
