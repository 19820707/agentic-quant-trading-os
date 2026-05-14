import inspect
import unittest

from packages.sdk.github_autonomous_maintenance import (
    AuditLog,
    AutonomousCredentialBlocked,
    AutonomousMaintenanceDryRunPipeline,
    AutonomousWriteBlocked,
    BranchCommitPRBot,
    EvidenceIndex,
    FindingEngine,
    GitHubRepositoryDiscovery,
    MultiRepoMonitor,
    PRReviewerAgent,
    PatchPlanner,
    PolicyEngine,
    RepositoryRef,
    RiskClassifier,
    RollbackEngine,
    SandboxPatchRunner,
    ScheduledScanner,
    TestRunner,
    WebhookReceiver,
)


class GitHubAutonomousMaintenanceDryRunTests(unittest.TestCase):
    def test_all_control_plane_blocks_are_present(self):
        blocks = (
            GitHubRepositoryDiscovery,
            MultiRepoMonitor,
            WebhookReceiver,
            ScheduledScanner,
            FindingEngine,
            PatchPlanner,
            RiskClassifier,
            PolicyEngine,
            SandboxPatchRunner,
            TestRunner,
            BranchCommitPRBot,
            PRReviewerAgent,
            EvidenceIndex,
            RollbackEngine,
            AuditLog,
        )

        for block in blocks:
            with self.subTest(block=block.__name__):
                self.assertTrue(inspect.isclass(block))

    def test_repository_discovery_is_local_and_rejects_credential_like_values(self):
        discovery = GitHubRepositoryDiscovery()

        repositories = discovery.discover(["19820707/agentic-quant-trading-os"])

        self.assertEqual(repositories[0].full_name, "19820707/agentic-quant-trading-os")
        with self.assertRaises(AutonomousCredentialBlocked):
            discovery.discover(["owner/token-leak"])

    def test_monitor_and_scanner_create_dry_run_requests_only(self):
        repository = RepositoryRef("19820707/agentic-quant-trading-os")
        monitor = MultiRepoMonitor()
        scheduler = ScheduledScanner()

        requests = monitor.build_scan_requests([repository])
        scheduled = scheduler.schedule_dry_run(repository)

        self.assertTrue(requests[0].dry_run)
        self.assertEqual(scheduled.trigger, "scheduled_dry_run")
        self.assertTrue(scheduled.dry_run)

    def test_webhook_receiver_is_dry_run_record_only(self):
        event = WebhookReceiver().receive_dry_run("pull_request", "19820707/agentic-quant-trading-os", "delivery-001")

        self.assertEqual(event.event_type, "pull_request")
        self.assertEqual(event.repository, "19820707/agentic-quant-trading-os")
        self.assertEqual(event.delivery_id, "delivery-001")

    def test_finding_risk_plan_policy_pipeline_fails_closed(self):
        repository = RepositoryRef("19820707/agentic-quant-trading-os")
        scan_request = ScheduledScanner().schedule_dry_run(repository)
        finding = FindingEngine().derive_findings(scan_request, ["contract tests failed"])[0]
        risk_class = RiskClassifier().classify(finding)
        patch_plan = PatchPlanner().plan(finding, risk_class)
        decision = PolicyEngine().decide(finding, patch_plan)

        self.assertEqual(risk_class, "medium")
        self.assertFalse(patch_plan.branch_creation_allowed)
        self.assertFalse(patch_plan.commit_allowed)
        self.assertFalse(patch_plan.pull_request_allowed)
        self.assertFalse(patch_plan.auto_merge_allowed)
        self.assertEqual(decision.decision, "REQUIRE_HUMAN_REVIEW")
        self.assertFalse(decision.repository_write_allowed)
        self.assertFalse(decision.branch_creation_allowed)
        self.assertFalse(decision.pull_request_allowed)
        self.assertFalse(decision.auto_merge_allowed)

    def test_high_risk_finding_is_blocked(self):
        repository = RepositoryRef("19820707/agentic-quant-trading-os")
        scan_request = ScheduledScanner().schedule_dry_run(repository)
        finding = FindingEngine().derive_findings(scan_request, ["execution credential path changed"])[0]
        risk_class = RiskClassifier().classify(finding)
        patch_plan = PatchPlanner().plan(finding, risk_class)
        decision = PolicyEngine().decide(finding, patch_plan)

        self.assertEqual(risk_class, "high")
        self.assertEqual(decision.decision, "BLOCK")
        self.assertEqual(decision.allowed_next_action, "none")

    def test_sandbox_runner_rejects_write_enabled_plan(self):
        repository = RepositoryRef("19820707/agentic-quant-trading-os")
        scan_request = ScheduledScanner().schedule_dry_run(repository)
        finding = FindingEngine().derive_findings(scan_request, ["contract tests failed"])[0]
        patch_plan = PatchPlanner().plan(finding, "medium")
        unsafe_plan = patch_plan.__class__(
            patch_plan_id=patch_plan.patch_plan_id,
            finding_id=patch_plan.finding_id,
            risk_class=patch_plan.risk_class,
            planned_files=patch_plan.planned_files,
            planned_tests=patch_plan.planned_tests,
            rollback_plan=patch_plan.rollback_plan,
            branch_creation_allowed=True,
        )

        with self.assertRaises(AutonomousWriteBlocked):
            SandboxPatchRunner().run(unsafe_plan)

    def test_test_runner_is_plan_only_and_does_not_execute_commands(self):
        results = TestRunner().plan_only(["python -m unittest discover -s tests"])

        self.assertTrue(results[0].passed)
        self.assertIn("not executed", results[0].evidence)

    def test_branch_commit_pr_bot_is_disabled(self):
        with self.assertRaises(AutonomousWriteBlocked):
            BranchCommitPRBot().create_branch_commit_or_pr()

    def test_reviewer_evidence_rollback_and_audit_are_local_records(self):
        repository = RepositoryRef("19820707/agentic-quant-trading-os")
        scan_request = ScheduledScanner().schedule_dry_run(repository)
        finding = FindingEngine().derive_findings(scan_request, ["contract tests failed"])[0]
        patch_plan = PatchPlanner().plan(finding, "medium")
        decision = PolicyEngine().decide(finding, patch_plan)
        test_results = TestRunner().plan_only(patch_plan.planned_tests)
        review = PRReviewerAgent().review(finding, "medium")
        evidence = EvidenceIndex().build(repository, finding, patch_plan, decision, test_results)
        rollback = RollbackEngine().plan(patch_plan)
        audit = AuditLog()
        audit.record("dry-run audit event")

        self.assertTrue(review.human_review_required)
        self.assertFalse(evidence.repository_write_performed)
        self.assertFalse(evidence.auto_merge_performed)
        self.assertIn("discard dry-run", rollback)
        self.assertEqual(audit.events, ["dry-run audit event"])

    def test_full_pipeline_produces_evidence_without_writes(self):
        pipeline = AutonomousMaintenanceDryRunPipeline()

        records = pipeline.run(["19820707/agentic-quant-trading-os"], ["contract tests failed"])

        self.assertEqual(len(records), 1)
        self.assertFalse(records[0].repository_write_performed)
        self.assertFalse(records[0].auto_merge_performed)
        self.assertTrue(pipeline.audit_log.events)

    def test_module_does_not_import_network_or_github_clients(self):
        import packages.sdk.github_autonomous_maintenance as module

        module_names = set(module.__dict__)
        forbidden = {"requests", "urllib", "httpx", "socket", "subprocess", "github", "octokit"}

        self.assertTrue(forbidden.isdisjoint(module_names))


if __name__ == "__main__":
    unittest.main()
