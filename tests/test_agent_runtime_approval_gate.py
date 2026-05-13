import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "docs" / "integrations" / "agent_runtime_approval_gate.md"
TAXONOMY = ROOT / "docs" / "architecture" / "agentic_tool_safety_taxonomy.md"
PROMOTION_GATES = ROOT / "docs" / "architecture" / "promotion_gates.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


class AgentRuntimeApprovalGateTests(unittest.TestCase):
    def test_runtime_gate_keeps_every_runtime_flag_disabled(self) -> None:
        text = GATE.read_text(encoding="utf-8")

        required_flags = (
            "agent_runtime_approved: false",
            "mcp_runtime_allowed: false",
            "tool_execution_allowed: false",
            "background_worker_allowed: false",
            "federation_allowed: false",
            "external_memory_allowed: false",
            "network_access_allowed: false",
            "credentials_allowed: false",
            "broker_access_allowed: false",
            "exchange_access_allowed: false",
            "trading_methods_allowed: false",
            "risk_approval_allowed: false",
            "execution_approval_allowed: false",
            "production_use_allowed: false",
        )

        for flag in required_flags:
            with self.subTest(flag=flag):
                self.assertIn(flag, text)

    def test_runtime_gate_requires_evidence_before_enablement(self) -> None:
        text = GATE.read_text(encoding="utf-8").lower()

        required_evidence = (
            "architecture review",
            "security review",
            "platform reliability review",
            "deterministic-risk-gateway boundary review",
            "prompt injection threat model",
            "tool capability matrix",
            "least privilege policy",
            "credential exposure review",
            "no-network unit tests",
            "fake/in-memory harness tests",
            "redaction tests",
            "rollback plan",
            "operator runbook",
            "secret and artifact audit pass",
        )

        for evidence in required_evidence:
            with self.subTest(evidence=evidence):
                self.assertIn(evidence, text)

    def test_runtime_gate_forbids_sensitive_runtime_capabilities(self) -> None:
        text = GATE.read_text(encoding="utf-8").lower()

        forbidden_items = (
            "running mcp servers",
            "registering real tools",
            "enabling background schedules",
            "enabling browser automation",
            "enabling federation",
            "enabling external memory databases",
            "reading environment credentials",
            "using broker credentials",
            "using exchange credentials",
            "calling broker or exchange apis",
            "submitting orders",
            "cancelling orders",
            "transferring funds",
            "withdrawing funds",
            "changing risk limits",
            "disabling kill switches",
            "approving risk",
            "approving execution",
            "production deployment",
        )

        for item in forbidden_items:
            with self.subTest(item=item):
                self.assertIn(item, text)

    def test_runtime_gate_requires_fail_closed_runtime_controls(self) -> None:
        text = GATE.read_text(encoding="utf-8").lower()

        controls = (
            "default disabled feature flag",
            "explicit approval-state check",
            "explicit capability allowlist",
            "explicit capability denylist",
            "network disabled by default",
            "credentials unavailable to agents",
            "structured local errors",
            "secret redaction",
            "audit events for configuration changes",
            "trace_id and correlation_id propagation",
            "deterministic-risk-gateway boundary enforcement",
            "kill-switch compatibility",
            "rollback procedure",
        )

        for control in controls:
            with self.subTest(control=control):
                self.assertIn(control, text)

    def test_related_governance_docs_link_the_gate(self) -> None:
        taxonomy = TAXONOMY.read_text(encoding="utf-8")
        promotion = PROMOTION_GATES.read_text(encoding="utf-8")

        self.assertIn("docs/integrations/agent_runtime_approval_gate.md", taxonomy)
        self.assertIn("docs/integrations/agent_runtime_approval_gate.md", promotion)

    def test_ci_runs_agent_runtime_approval_gate_tests(self) -> None:
        text = CI_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("test_agent_runtime_approval_gate.py", text)


if __name__ == "__main__":
    unittest.main()
