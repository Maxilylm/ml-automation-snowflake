---
name: snowflake-sql
description: "Generate and execute Snowflake SQL from natural language — DDL, DML, queries with approval before execution"
aliases: [sf sql, snowflake query, snowflake ddl]
extends: ml-automation
user_invocable: true
---

# Snowflake SQL

Translate natural language requests into correct Snowflake SQL -- including DDL (CREATE TABLE, CLONE, STAGE), DML (INSERT, MERGE, COPY INTO), and analytical queries with window functions or Snowflake-specific syntax. Displays generated SQL for review and requires explicit approval before execution, then returns results or a summary of affected rows.

Use this whenever the user describes a data operation in plain English and expects SQL, even if they don't say "SQL." Also use it when the user says "create a table," "query my data," "merge these tables," or any Snowflake DDL/DML request.

## When to Use

- The user describes a Snowflake data operation in natural language and wants SQL generated
- A new table, view, stage, or other DDL object needs to be created in Snowflake
- The user wants to run an analytical query with Snowflake-specific syntax (QUALIFY, FLATTEN, LATERAL, etc.)
- Data needs to be loaded, merged, or transformed via DML statements

## Workflow

1. **Ensure Connection** -- verify `ml_utils.py` and `snowflake_utils.py` are in `src/`, run `/snowflake-connect --check`
2. **Generate SQL** -- parse the natural language description, generate Snowflake-optimized SQL with explanatory comments
3. **Show for approval** -- display the generated SQL and ask the user to approve, reject, or edit before execution
4. **Execute** -- run the approved SQL via `snowflake_utils.execute_query()`, display results (SELECT) or confirmation (DDL/DML), optionally save to `sql/` directory
5. **Report** -- log the executed SQL and results in the report bus

**Agent:** snowflake-data-engineer

## Report Bus Integration

```python
save_agent_report("snowflake_sql_report", {
    "query": generated_sql,
    "status": "executed",
    "rows_affected": row_count,
    "output_file": "sql/create_feature_table.sql"
})
```

## Full Specification

See `commands/snowflake-sql.md` for the complete workflow.
