# GitHub Autonomous Maintenance Reference Review

## Purpose

This review maps public GitHub automation projects and official GitHub patterns
to safe internal architecture for an autonomous maintenance control plane.

It does not approve installing, cloning, vendoring or activating any external
automation runtime.

## References Reviewed

| Reference | URL | Useful Pattern | Current Use |
| --- | --- | --- | --- |
| Dependabot Core | https://github.com/dependabot/dependabot-core | dependency scan to automated PR | reference only |
| GitHub Copilot coding agent docs | https://docs.github.com/en/copilot/using-github-copilot/coding-agent/about-assigning-tasks-to-copilot | task to branch to PR workflow | reference only |
| PR-Agent | https://github.com/The-PR-Agent/pr-agent | PR review summaries and suggestions | reference only |
| Probot | https://github.com/probot/probot | GitHub App and webhook app framework | reference only |
| Octokit | https://github.com/octokit/octokit.js | GitHub API, App and webhook SDK | reference only |
| Semgrep | https://github.com/semgrep/semgrep | static finding engine | reference only |
| Trivy | https://github.com/aquasecurity/trivy | filesystem, dependency, secret and SBOM scanning | reference only |
| Actions Runner Controller | https://github.com/actions/actions-runner-controller | isolated runner scaling | reference only |

## Decision State

github_autonomous_references_reviewed: true
reference_only: true
dependency_allowed: false
github_app_allowed: false
webhook_receiver_allowed: false
scheduled_scanner_allowed: false
repository_write_allowed: false
auto_pr_allowed: false
auto_merge_allowed: false
llm_runtime_allowed: false
network_access_allowed: false
credentials_allowed: false
production_enabled: false

## What Can Be Reused

- Dependabot-style monitored finding to pull request lifecycle
- Copilot-style task, branch, commit and draft pull request traceability
- PR-Agent-style reviewer summaries, risk sections and test impact notes
- Probot/Octokit-style GitHub App separation from repository code
- Semgrep/CodeQL/Trivy-style finding records with severity and evidence
- GitHub Actions-style sandboxed validation before PR publication

## What Must Not Be Reused Yet

- external GitHub App runtime
- webhook server
- repository write token
- autonomous patch execution
- automatic pull request creation
- automatic merge
- LLM reviewer runtime
- external SaaS tokens
- privileged self-hosted runner

## Required Internal Contracts

Before any runtime is considered, this repository must define:

- `repository_monitor_policy`
- `maintenance_finding_record`
- `patch_plan_record`
- `autonomous_change_policy_decision`
- `maintenance_evidence_record`

## Next Gate

The next safe step is contract-only validation of the control-plane payloads.
No runtime automation should be implemented until those contracts are reviewed.

