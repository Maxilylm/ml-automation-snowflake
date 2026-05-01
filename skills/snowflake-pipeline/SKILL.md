---
name: snowflake-pipeline
description: "Build Snowpark data transformation pipelines with DataFrame API. Triggers: sf pipeline, snowpark pipeline, snowflake transform, snowpark transform, feature engineering in snowflake, snowflake dataframe pipeline."
aliases: [sf pipeline, snowpark pipeline, snowflake transform]
extends: spark
user_invocable: true
tools: [Read, Write, Bash, sql_execute]
---

# Snowflake Pipeline

Generate production-ready Snowpark Python pipelines using the DataFrame API for in-warehouse data transformation. Covers ingestion from stages or tables, column transformations, joins, aggregations, and writing results back to Snowflake -- all without moving data out of the warehouse. Supports both batch and streaming (Dynamic Tables) patterns.

Use this whenever the user wants to transform data inside Snowflake using Python, even if they don't mention "pipeline." Also use it when the user says "Snowpark transform," "feature engineering in Snowflake," or "build a data pipeline on my warehouse."

## When to Use

- The user needs a Snowpark DataFrame pipeline to transform raw tables into feature tables
- Data preparation (joins, aggregations, type casts, null handling) must happen inside the Snowflake warehouse
- The user wants to replace pandas-based ETL with Snowpark for scale
- A Dynamic Table or scheduled pipeline pattern is needed for incremental processing

## Workflow

1. **Ensure Connection** -- verify `ml_utils.py` and `snowflake_utils.py` are in `src/`, run `/snowflake-connect --check`
2. **Profile source table** -- connect and describe the source table (column types, row count, sample data); read EDA report from core if available
3. **Design pipeline** -- identify required transformations (joins, aggregations, type casts, null handling), design Snowpark DataFrame operations with data quality checks
4. **Generate code** -- write `src/snowpark_pipeline.py` with session setup, DataFrame transformations, and output to target table
5. **Test** -- run pipeline on a sample (LIMIT 1000) to verify correctness before full execution
6. **Report** -- log pipeline configuration and results in the report bus

**Agent:** snowflake-data-engineer

## Report Bus Integration

```python
save_agent_report("snowflake_pipeline_report", {
    "source_table": source_table,
    "target_table": target_table,
    "transformations": ["join", "aggregation", "null_fill"],
    "sample_row_count": 1000,
    "status": "tested"
})
```

## Full Specification

See `commands/snowflake-pipeline.md` for the complete workflow.
