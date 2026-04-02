---
name: snowflake-deploy
description: "Deploy to Snowflake — Model Registry, Streamlit in Snowflake, or stored procedure inference endpoint"
aliases: [sf deploy, snowflake model deploy, streamlit in snowflake]
extends: spark
user_invocable: true
---

# Snowflake Deploy

Package and deploy ML artifacts to Snowflake-native targets: promote a registered model version to production in the Model Registry, publish an interactive Streamlit in Snowflake app for stakeholder exploration, or wrap model inference in a vectorized stored procedure for SQL-callable batch prediction. Validates deployment health and prints the live endpoint or app URL on completion.

Use this whenever the user wants to deploy a model or app to Snowflake, even if they just say "ship it" or "make it available." Also use it when the user mentions "Streamlit in Snowflake," "stored procedure inference," or "promote model to production."

## When to Use

- A trained model needs to be registered or promoted to production in the Snowflake Model Registry
- The user wants an interactive Streamlit in Snowflake app for stakeholders to explore predictions
- Batch inference should be wrapped in a stored procedure callable from SQL
- A Snowflake Task should be scheduled for recurring inference runs

## Workflow

1. **Ensure Connection** -- verify `ml_utils.py` and `snowflake_utils.py` are in `src/`, run `/snowflake-connect --check`
2. **Select target** -- determine deployment target from `--target` flag: model-registry, streamlit, or stored-procedure
3. **Model Registry** -- find trained model artifacts, register with version/metrics/tags, optionally promote to "production" alias
4. **Streamlit in Snowflake** -- generate Streamlit app code, create a Snowflake stage for app files, deploy via `CREATE STREAMLIT` DDL, report app URL and access permissions
5. **Stored Procedure** -- package model and inference code, create stored procedure with Python handler, optionally create a Snowflake Task for scheduled batch inference
6. **Report** -- write deployment report with all resource details (names, URLs, schedules)

**Agent:** snowflake-deployer

## Report Bus Integration

```python
save_agent_report("snowflake_deploy_report", {
    "target": "streamlit",
    "app_name": "ML_DASHBOARD",
    "app_url": "https://app.snowflake.com/...",
    "model_version": "v1",
    "status": "deployed"
})
```

## Full Specification

See `commands/snowflake-deploy.md` for the complete workflow.
