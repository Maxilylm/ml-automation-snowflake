---
name: snowflake-status
description: "Check Snowflake resources — warehouse usage, deployed models, Streamlit apps, stored procedures, recent queries"
aliases: [sf status, snowflake resources, snowflake info]
extends: ml-automation
user_invocable: true
---

# Snowflake Status

Query and summarize the current state of Snowflake resources relevant to the project: virtual warehouse credit consumption, Model Registry versions and their deployment stage, running Streamlit in Snowflake apps, registered stored procedures, and the query history for recent pipeline or inference runs. Presents a unified status table to help quickly spot idle warehouses, stale model versions, or failing jobs.

Use this whenever the user wants to check what is running or deployed in Snowflake, even if they just say "what's in my warehouse" or "show my models." Also use it when the user says "Snowflake resources," "warehouse usage," or "check my deployments."

## When to Use

- The user wants a quick overview of all Snowflake ML resources in the current project
- Warehouse credit usage needs to be checked for cost monitoring
- The user wants to see which model versions are deployed and their production status
- Recent query history should be reviewed to spot failures or slow-running jobs

## Workflow

1. **Ensure Connection** -- verify `ml_utils.py` and `snowflake_utils.py` are in `src/`, run `/snowflake-connect --check`
2. **Query metadata** -- execute `SHOW WAREHOUSES`, query `INFORMATION_SCHEMA.ML_MODEL_VERSIONS`, `SHOW STREAMLITS`, `SHOW PROCEDURES`, and pull recent query history from `INFORMATION_SCHEMA.QUERY_HISTORY`
3. **Format output** -- present results as structured tables: Warehouses (name, size, state, auto-suspend), Deployed Models (name, version, stage), Streamlit Apps (name, URL, status), Stored Procedures (name, language), Recent Queries (ID, text, status, elapsed time)
4. **Detailed mode** -- if `--detailed` flag is set, include credit consumption breakdown, query execution plans, and model metric histories

## Report Bus Integration

```python
save_agent_report("snowflake_status_report", {
    "warehouses": [{"name": "COMPUTE_WH", "size": "X-Small", "state": "SUSPENDED"}],
    "models": [{"name": "churn_model", "version": "v2", "stage": "production"}],
    "streamlit_apps": 1,
    "stored_procedures": 3
})
```

## Full Specification

See `commands/snowflake-status.md` for the complete workflow.
