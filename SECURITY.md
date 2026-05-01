# Security policy

This plugin is part of the Blend Spark Harness — 14 Claude Code plugins for ML automation. Security issues are tracked via Jira project [PM3](https://blend360.atlassian.net/jira/core/projects/PM3/board) under the `security` label.

## Reporting a vulnerability

**Do not open a public GitHub issue for security problems.**

Email Maximo Lorenzo Losada at `maximo.lorenzolosada@blend360.com` with:

- A description of the issue and impact.
- Steps to reproduce or proof of concept.
- Affected plugin and version.
- Your contact for follow-up.

You will receive an acknowledgement within 2 business days.

## Triage SLA

| Severity | Examples | First response | Patch target |
|---|---|---|---|
| Critical | Remote code execution, secret exposure, data exfiltration | 1 business day | 7 calendar days |
| High | Privilege escalation, auth bypass, injection in user input paths | 2 business days | 14 calendar days |
| Medium | Information disclosure, weak crypto in non-secret paths | 5 business days | 30 calendar days |
| Low | Hardening recommendations, defense-in-depth | 10 business days | Best effort |

## What CI catches automatically

The `claude-review` job in `.github/workflows/claude-review.yml` flags `SECURITY` findings as build-failing on every PR. Categories include:

- SQL injection, command injection, path traversal
- Weak crypto (MD5/SHA1 for security purposes, hard-coded IVs/keys)
- Credentials in code
- Unguarded `eval` / `exec` / pickle deserialization

`validate-plugin-layout` separately catches structural drift in the public API (manifest, AGENTS.md, agent/skill definitions).

## What CI does NOT catch

- Vulnerabilities in third-party dependencies — Dependabot (`.github/dependabot.yml`) opens weekly PRs for minor and patch upgrades; security advisories are handled by GitHub's security alerts.
- Logic bugs in the model training or evaluation pipelines (these are CORRECTNESS findings, not SECURITY).
- Any issue introduced via supply-chain attacks on installed packages — keep an eye on Dependabot security advisories and upstream repository activity.

## Responsible disclosure

We follow coordinated disclosure: please give us a chance to patch before publishing details. We will credit reporters in release notes if requested.
