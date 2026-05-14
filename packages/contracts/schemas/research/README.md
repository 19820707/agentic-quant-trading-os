# Research Contracts

Prediction research contracts define non-executable payloads for research dossiers,
probability estimates, hypotheses, analyst reports, debate transcripts, signal
candidates, advisory risk review inputs and agent orchestration governance.

These contracts must not contain credentials, private endpoint data, broker or
exchange secrets, wallet keys, executable orders, `ApprovedOrder` payloads or
live trading authority.

Agent orchestration governance contracts may describe plans, roles, handoffs,
consensus, topology, federation, memory, MCP registration, workers, budgets and
prompt-injection review. They must not activate agent runtime, MCP runtime,
federation, background workers, credentials, trading or execution.

Multi-model review governance contracts may describe review plans, consensus
gates, adversarial debates, provider policy, phase gates, prompt preflight and
security review workflows. They must not call models, activate providers,
install plugins, start MCP servers, patch code automatically, merge PRs
automatically, access credentials, trade or execute.

