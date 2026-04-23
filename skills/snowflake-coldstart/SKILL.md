---
name: snowflake-coldstart
description: "Full Snowflake ML workflow — connect, discover data, build pipeline, train model, deploy to Snowflake. Triggers: sf coldstart, snowflake workflow, snowflake ml pipeline, end-to-end snowflake, snowflake ml project."
aliases: [sf coldstart, snowflake workflow, snowflake ml pipeline]
extends: spark
user_invocable: true
tools: [Read, Write, Bash, sql_execute]
---

# Snowflake Coldstart

End-to-end orchestration for Snowflake ML projects: establishes connection, discovers and profiles available tables, builds a Snowpark transformation pipeline, trains a model using Snowpark ML or Snowflake ML Functions, and deploys the result to the Model Registry or a Streamlit in Snowflake app. Designed to take a project from zero to a live Snowflake-native ML solution with minimal manual steps.

Use this whenever the user wants to build an ML model on data that lives in Snowflake, even if they don't mention "coldstart." Also use it when the user says "end-to-end Snowflake," "Snowflake ML project," or "train a model on my Snowflake table."

## When to Use

- The user has data in Snowflake and wants an ML model trained and deployed entirely inside the warehouse
- A new Snowflake ML project needs to go from zero to a working pipeline in a single session
- The user wants to combine data discovery, SQL development, Snowpark pipeline creation, training, and deployment into one orchestrated run
- The user mentions a Snowflake table or query and asks for predictions, forecasts, or anomaly detection

## Workflow

1. **Ensure Connection** -- verify `ml_utils.py` and `snowflake_utils.py` are present in `src/`, then run `/snowflake-connect --check`
2. **Connect & Discover** -- connect to Snowflake, list databases/schemas/tables, profile the target table or query, load a sample for EDA
3. **SQL Development** -- generate DDL for staging tables, feature tables with clustering keys, and views; show SQL for approval before execution
4. **Snowpark Pipeline** -- build a Snowpark DataFrame transformation pipeline in `src/snowpark_pipeline.py` covering joins, aggregations, and feature engineering
5. **Train Model** -- train via Snowpark ML (sklearn-compatible) or Snowflake ML Functions (FORECAST, ANOMALY_DETECTION); register in Model Registry
6. **Evaluate** -- run model evaluation, write results to Snowflake, invoke ml-theory-advisor for methodology review
7. **Deploy** -- register model, create Streamlit in Snowflake dashboard, create stored procedure for batch inference, optionally schedule a Snowflake Task
8. **Finalize** -- generate comprehensive report documenting all deployed Snowflake resources

**Agents:** snowflake-data-engineer, snowflake-ml-engineer, snowflake-deployer

## Report Bus Integration

Each stage writes a JSON report via the shared report bus so downstream stages can read prior outputs:

```python
save_agent_report("snowflake_discovery_report", {
    "table": table_name,
    "row_count": row_count,
    "columns": column_profiles,
    "snowflake_resources": {"database": db, "schema": sch}
})
```

## Full Specification

See `commands/snowflake-coldstart.md` for the complete workflow with per-stage details.
