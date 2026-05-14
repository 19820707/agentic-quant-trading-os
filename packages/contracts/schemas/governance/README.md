# Governance Schemas

Governance schemas define approval, promotion, agent task and evidence contracts.

Future schemas must preserve approval state, evidence references, human sign-off and rollback metadata.

Current schemas:

- `agent_task_spec.schema.json`: proposed LLM-assisted engineering task with no runtime authority.
- `agent_patch_plan.schema.json`: proposed patch plan with tests and rollback, still pull-request-only.
- `agent_risk_assessment.schema.json`: deterministic policy classification with direct main writes, auto-merge, credentials, network, trading, risk approval and execution disabled.
- `sandbox_execution_report.schema.json`: isolated execution evidence that still grants no runtime authority.
- `test_evidence_report.schema.json`: deterministic validation evidence that still requires human review.
- `rollback_plan.schema.json`: rollback strategy contract with automated and production rollback disabled.

