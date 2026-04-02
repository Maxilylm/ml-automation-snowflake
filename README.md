# spark-snowflake

Snowflake development and ML automation extension for [ml-automation](https://github.com/Maxilylm/ml-automation-core).

## Prerequisites

- [ml-automation](https://github.com/Maxilylm/ml-automation-core) core plugin (>= v1.8.0)
- Claude Code CLI
- Snowflake account (for connection)

## Installation

```bash
claude plugin add /path/to/spark-snowflake
```

## What's Included

### Agents

| Agent | Purpose | Hooks Into |
|---|---|---|
| `snowflake-data-engineer` | SQL development, pipelines, Snowpark | `after-init` |
| `snowflake-ml-engineer` | Snowpark ML, ML Functions, Model Registry | `before-deploy` |
| `snowflake-reviewer` | SQL quality, cost optimization, best practices | `after-evaluation` |
| `snowflake-deployer` | Model Registry, Streamlit in Snowflake, stored procedures | *(direct invocation)* |
| `snowflake-connector` | Connection setup, data loading/unloading | *(direct invocation)* |

### Commands

| Command | Purpose |
|---|---|
| `/snowflake-connect` | Setup and test Snowflake connection |
| `/snowflake-coldstart` | Full Snowflake ML workflow (connect → deploy) |
| `/snowflake-sql` | Natural language → Snowflake SQL |
| `/snowflake-pipeline` | Build Snowpark transformation pipeline |
| `/snowflake-train` | Train model via Snowpark ML or ML Functions |
| `/snowflake-deploy` | Deploy to Model Registry, Streamlit in Snowflake, or stored procedure |
| `/snowflake-migrate` | Migrate pandas/sklearn code to Snowpark |
| `/snowflake-status` | Check Snowflake resources and usage |

## Getting Started

```bash
# 1. Setup connection
/snowflake-connect

# 2. Run full workflow on a Snowflake table
/snowflake-coldstart MY_DATABASE.MY_SCHEMA.MY_TABLE --target revenue

# Or use individual commands
/snowflake-sql create a feature table with clustering on date
/snowflake-train MY_TABLE --target revenue --mode snowpark-ml
/snowflake-deploy --target streamlit
```

## How It Integrates

When installed alongside the core plugin:

1. **Automatic routing** — Tasks mentioning Snowflake, Snowpark, SQL development are routed to Snowflake agents
2. **Core workflow hooks** — When running `/team-coldstart`:
   - `snowflake-data-engineer` fires at `after-init` to discover Snowflake data sources
   - `snowflake-reviewer` fires at `after-evaluation` to validate Snowflake compatibility
   - `snowflake-ml-engineer` fires at `before-deploy` to offer Snowflake deployment
3. **Core agent reuse** — Commands use eda-analyst, developer, ml-theory-advisor from core

## License

MIT
