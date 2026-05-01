# ml-automation-snowflake

Snowflake development and ML automation. SQL authoring, Snowpark pipelines, Snowpark ML training, model registry, and Streamlit in Snowflake deployment. Requires spark-core installed.

This is one of 14 Claude Code plugins in the [Blend Spark Harness](https://github.com/BLEND360). Work is tracked in Jira project [PM3](https://blend360.atlassian.net/jira/core/projects/PM3/board) — filter by label `plugin:snowflake`.

When invoked from CI/CD, you (Claude) act as an independent reviewer. You do not have the conversation context of whoever wrote the diff. Use this file plus `.claude/rules/` to ground your reasoning.

## Plugin layout

```
ml-automation-snowflake/
├── AGENTS.md                  # Routing table — public API
├── README.md
├── .cortex-plugin/
│   └── plugin.json            # Plugin manifest
├── agents/                    # Agent definitions
├── commands/                  # Slash commands
├── skills/                    # Skills (one dir per skill)
├── hooks/                     # Lifecycle hooks
├── templates/                 # Reusable scaffolding
├── .claude/                   # Claude Code config (rules, commands)
├── .github/                   # CI/CD workflows, PR template, CODEOWNERS
├── schemas/finding.schema.json
└── scripts/                   # CI helpers (claude_review, post_findings, validate_plugin)
```

Treat the manifest, AGENTS.md, and the agents/commands/skills directories as the **plugin's public API**. Changes there are higher-risk than changes inside a single skill body.

## Routing — agents and skills in this plugin

### Available agents

| Agent | When to use |
|---|---|
| `snowflake-data-engineer` | User wants to write SQL, design tables, build Snowpark pipelines, create stages/streams/tasks, or optimize queries |
| `snowflake-ml-engineer` | User wants to train a model in Snowpark ML, use FORECAST or ANOMALY_DETECTION, or register a model in the Snowflake Model Registry |
| `snowflake-reviewer` | User wants SQL quality review, cost optimization, or Snowflake best practices feedback |
| `snowflake-deployer` | User wants to deploy to Model Registry, create Streamlit in Snowflake, or build a stored procedure |
| `snowflake-connector` | User wants to set up a Snowflake connection, load data, or configure credentials |

### Available skills

| Skill | Trigger |
|---|---|
| `/snowflake-connect` | "connect to Snowflake", "set up Snowflake connection", "test my Snowflake credentials" |
| `/snowflake-coldstart` | "full Snowflake ML workflow", "end to end on my Snowflake table", "snowflake coldstart" |
| `/snowflake-sql` | "write SQL for Snowflake", "natural language to SQL", "generate a Snowflake query" |
| `/snowflake-pipeline` | "build a Snowpark pipeline", "transform data with Snowpark", "create a data pipeline in Snowflake" |
| `/snowflake-train` | "train a model on Snowflake data", "use Snowpark ML", "forecast with Snowflake", "anomaly detection in Snowflake" |
| `/snowflake-deploy` | "deploy to Snowflake Model Registry", "create Streamlit in Snowflake", "deploy as stored procedure" |
| `/snowflake-migrate` | "migrate pandas code to Snowpark", "convert sklearn to Snowpark ML", "port this to Snowflake" |
| `/snowflake-status` | "show Snowflake resources", "list my Snowflake models", "check warehouse usage" |

(See `AGENTS.md` for the canonical routing table; this section is a reminder for CI-invoked Claude.)

## Severity criteria (review prompt)

When you produce a code review, classify each finding into one severity. **Report only** BUG / SECURITY / CORRECTNESS / BREAKING / CRITICAL. Skip the rest — they erode trust in the bot.

| Severity | When to flag | Examples |
|---|---|---|
| **CRITICAL** | Production breakage, data loss, security exposure | Unguarded `eval`/`exec`, leaked secret, parallelism in benchmark harness |
| **BUG** | Code does not do what it claims | Off-by-one, wrong comparison operator, swallowed exception, comment contradicts code |
| **SECURITY** | Vulnerability or unsafe pattern | SQL/command injection, weak crypto, credentials in code |
| **CORRECTNESS** | Subtle incorrect behavior | Float `==`, mutable default arg, race condition, missing random seed |
| **BREAKING** | Public-API contract change | Removed agent, renamed command, plugin manifest schema change without migration |

**Do NOT flag** (skip silently): style/lint, missing docstrings on private functions, subjective preferences, "consider adding tests" without a specific case, micro-optimizations.

## Few-shot examples for ambiguous cases

**`try/except: pass` is sometimes the right answer.**

```python
# CORRECT — best-effort cache cleanup
try:
    cache.cleanup_expired()
except Exception:
    pass  # cleanup failure must not block the request
```
→ Do not flag. Comment makes intent clear.

```python
# WRONG — swallows errors that should bubble
try:
    response = api.call(payload); process(response)
except Exception:
    pass  # ???
```
→ Flag as BUG.

**Mutable default argument.** `def f(xs=[])` → flag CORRECTNESS. `def f(xs=None)` with `if xs is None: xs = []` → fine.

**Float equality.** `if score == 0.95` → flag CORRECTNESS, use `math.isclose`.

## Test fixtures and conventions

- Tests live in `tests/` (or alongside code as `test_*.py`).
- Pytest fixtures in `conftest.py` at repo root. Check it before inventing new ones.
- **Mock LLM/API calls** — never hit real services in unit tests. Integration tests are gated behind `INTEGRATION=1`.
- Coverage floor: 70%. Configured in `pyproject.toml`.

## Output format (CI invocations only)

When invoked with `--output-format json --json-schema schemas/finding.schema.json`, return findings as a JSON array. The schema is enforced by tool_use; do not return prose.

For interactive (non-CI) use, prose is fine.

## Working with Claude Code

- Project-scoped slash commands live in `.claude/commands/` (e.g., `/review`). Personal commands stay in `~/.claude/commands/`.
- Skills with `context: fork` run in a sub-agent and don't pollute main context.
- See `.claude/rules/` for path-scoped conventions (`python.md` for `*.py`, `testing.md` for tests, `plugin.md` for plugin layout).

## Jira / GitHub conventions

- Branch names: `PM3-<ticket>-<slug>` (required — CI rejects PRs without a `PM3-N` reference).
- Smart commits: `PM3-12 #in-progress`, `PM3-12 #done`, `PM3-12 #time 2h`. See `CONTRIBUTING.md`.
- PR template at `.github/pull_request_template.md` — required Jira link.
