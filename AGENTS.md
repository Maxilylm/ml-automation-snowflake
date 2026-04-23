# spark-snowflake — Cortex Code Extension

Snowflake development and ML automation. SQL authoring, Snowpark pipelines, Snowpark ML training, model registry, and Streamlit in Snowflake deployment. Requires spark-core installed.

## Connection

Uses `~/.snowflake/connections.toml` for authentication — the same file Cortex Code CLI uses natively. No additional setup needed when running inside Cortex Code. If no connection is active, prefer the interactive `/connections` UI or `cortex connections list` / `cortex connections set` commands over manually editing the TOML file.

## Cortex Code Native Tools — Prefer These When Available

When running inside Cortex Code, these native tools should be preferred over the plugin's local Python helpers. The plugin's `snowflake_utils.py` remains a fallback for Claude Code or environments without Cortex Code tools.

| Task | Prefer (Cortex Code native) | Fallback (plugin helper) |
|---|---|---|
| Run any SQL | `sql_execute` tool | `snowflake_utils.execute_query()` |
| Profile a table (columns, types, PKs, row count, sample) | `#DB.SCHEMA.TABLE` syntax in prompt | `snowflake_utils.get_snowflake_metadata()` + manual SELECT |
| Discover databases/schemas/tables by description | `cortex search object "<query>"` | `SHOW DATABASES` / `SHOW TABLES` loops |
| Generate SQL from natural language | Cortex Analyst (`cortex analyst query`) when a semantic model exists | Manual LLM SQL generation |
| Discover business-layer views | `cortex semantic-views discover` / `describe` / `search` | None — new capability |
| Connection setup UI | `/connections` interactive command | Manual `connections.toml` editing |

Agents and skills in this plugin should check for Cortex Code context (e.g., the presence of `sql_execute` as an available tool) and route accordingly. The plugin's approval flow, report bus integration, and spark-core workflow hooks remain authoritative regardless of which tool runs the actual SQL.

## Conflict Resolution — Built-in Skill Overlap

Cortex Code ships with built-in skills that overlap with this plugin's skills. When the plugin is installed, prefer these rules:

| User intent | Prefer | Instead of |
|---|---|---|
| Write/run/debug SQL in a spark-core project | `$snowflake-sql` | built-in `sql-author` |
| Deploy Streamlit **in Snowflake** (`CREATE STREAMLIT`) | `$snowflake-deploy --target streamlit` | built-in `developing-with-streamlit` |
| Train models **inside** Snowflake warehouse (Snowpark ML, FORECAST, ANOMALY_DETECTION) | `$snowflake-train` | built-in `machine-learning` |
| Snowpark in spark-core-orchestrated workflows | `$snowflake-connect` / `$snowflake-pipeline` | built-in `snowpark-python` |

Rule of thumb: if the user's task touches the spark report bus, a spark-core workflow, or requires the plugin's approval/reflection gates, use the plugin skill. For standalone Snowflake work outside a spark project, the built-in skill is appropriate.

## Available Agents

| Agent | When to use |
|---|---|
| `snowflake-data-engineer` | User wants to write SQL, design tables, build Snowpark pipelines, create stages/streams/tasks, or optimize queries |
| `snowflake-ml-engineer` | User wants to train a model in Snowpark ML, use FORECAST or ANOMALY_DETECTION, or register a model in the Snowflake Model Registry |
| `snowflake-reviewer` | User wants SQL quality review, cost optimization, or Snowflake best practices feedback |
| `snowflake-deployer` | User wants to deploy to Model Registry, create Streamlit in Snowflake, or build a stored procedure |
| `snowflake-connector` | User wants to set up a Snowflake connection, load data, or configure credentials |

## Available Skills

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

## Routing

- SQL development, table design, Snowpark transformations → `snowflake-data-engineer`
- Model training, FORECAST, ANOMALY_DETECTION, Model Registry → `snowflake-ml-engineer`
- SQL review, cost, performance → `snowflake-reviewer`
- Streamlit in Snowflake, stored procedures, deployment → `snowflake-deployer`
- Connection setup, data loading → `snowflake-connector`
- Fallback → spark-core orchestrator

## Cortex Code Orchestration

Claude Code agents in this plugin declare `hooks_into: after-init | before-deploy | after-evaluation` frontmatter to auto-fire at spark-core workflow stages. **Cortex Code has no equivalent plugin-lifecycle hook system.** When running a spark-core workflow (`$team-coldstart`, `$snowflake-coldstart`) inside Cortex Code, the orchestrator should spawn these agents as subagents at the appropriate stages:

- **`after-init`** (data discovered) → spawn `snowflake-data-engineer` via the Task tool to profile tables and generate DDL
- **`after-evaluation`** (metrics computed) → spawn `snowflake-reviewer` to validate SQL quality and cost
- **`before-deploy`** (deployment preparing) → spawn `snowflake-ml-engineer` to offer Snowflake-native deployment options

For native Cortex Code team coordination, use `team_create` + `task_create` + `task_claim` or the `ctx-workflow` skill. The report bus (`save_agent_report` → `.claude/reports/` or `.cortex/reports/`) remains the cross-agent communication mechanism in both environments.

## Semantic Views and Cortex Analyst

Before writing raw SQL against a table, check whether a curated semantic view exists:

```
cortex semantic-views discover
cortex semantic-views search "<domain-keywords>"
cortex semantic-views describe <view_name>
```

If a semantic view exists for the domain, prefer `cortex analyst query "<question>"` over raw SQL generation — it produces business-aligned queries with explanations and follow-ups. Fall back to raw SQL only for DDL, one-off analytical queries, or when no semantic model covers the data.

## Hooks Reference

The plugin's `hooks/hooks.json` defines Cortex Code lifecycle hooks:

- **`SessionStart`** — auto-detects Snowflake indicators in the project and injects context
- **`Stop`** — writes a session summary to the report bus for spark-core workflow pickup

These are Cortex Code event-based hooks (`PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, etc.), distinct from the Claude Code `hooks_into` frontmatter on individual agents.
