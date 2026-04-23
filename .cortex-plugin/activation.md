---
name: spark-snowflake
description: >
  Suggest enabling the spark-snowflake plugin when the user asks about Snowflake
  SQL development, Snowpark pipelines, Snowpark ML training, FORECAST or
  ANOMALY_DETECTION ML functions, Snowflake Model Registry, Streamlit in
  Snowflake, stored procedures for inference, pandas-to-Snowpark migration,
  Snowflake cost or performance review, Snowflake connection setup, or any
  end-to-end ML workflow running inside a Snowflake warehouse.
  Do NOT attempt to perform these tasks — just let the user know the plugin
  can be enabled.
---

# spark-snowflake (disabled plugin)

This plugin is installed but not enabled. It provides Snowflake development and
ML automation capabilities within Cortex Code, integrated with the spark-core
workflow (agents, report bus, reflection gates).

## Agents (5)

- **snowflake-data-engineer** — SQL, tables, Snowpark pipelines, stages/streams/tasks
- **snowflake-ml-engineer** — Snowpark ML, ML Functions (FORECAST, ANOMALY_DETECTION), Model Registry
- **snowflake-reviewer** — SQL quality, cost optimization, best practices review
- **snowflake-deployer** — Model Registry promotion, Streamlit in Snowflake, stored procedures
- **snowflake-connector** — Connection setup, data loading/unloading

## Skills (8)

- **snowflake-connect** — Setup and test Snowflake connection
- **snowflake-coldstart** — Full Snowflake ML workflow (connect → discover → train → deploy)
- **snowflake-sql** — Natural-language to Snowflake SQL (routes through Cortex Analyst when available)
- **snowflake-pipeline** — Build Snowpark DataFrame transformation pipelines
- **snowflake-train** — Train models via Snowpark ML or Snowflake ML Functions
- **snowflake-deploy** — Deploy to Model Registry, Streamlit in Snowflake, or stored procedure
- **snowflake-migrate** — Migrate pandas/sklearn code to Snowpark equivalents
- **snowflake-status** — Inspect Snowflake resources, warehouse usage, deployed models

## Cortex Code Integration

- Reuses `~/.snowflake/connections.toml` — the same auth file Cortex Code CLI uses
- Prefers Cortex Code native tools (`sql_execute`, `#TABLE`, `cortex search object`, Cortex Analyst, semantic-views) over the plugin's Python helpers when available
- Disambiguates from built-in skills: `$snowflake-sql` (vs. `sql-author`), `$snowflake-deploy --target streamlit` (vs. `developing-with-streamlit`), `$snowflake-train` (vs. `machine-learning`), `$snowflake-connect` / `$snowflake-pipeline` (vs. `snowpark-python`)

## Requires

- spark-core plugin (for shared agents, report bus, and workflow orchestration)

## Enable

    cortex plugin enable spark-snowflake

Do NOT attempt to perform Snowflake tasks through this plugin's skills while it is disabled.
