---
name: snowflake-sql
description: "Generate and execute Snowflake SQL from natural language — DDL, DML, queries with approval before execution"
aliases: [sf sql, snowflake query, snowflake ddl]
extends: ml-automation
user_invocable: true
---

# Snowflake SQL

Translate natural language requests into correct Snowflake SQL — including DDL (CREATE TABLE, CLONE, STAGE), DML (INSERT, MERGE, COPY INTO), and analytical queries with window functions or Snowflake-specific syntax. Displays generated SQL for review and requires explicit approval before execution, then returns results or a summary of affected rows.

## Full Specification

See `commands/snowflake-sql.md` for the complete workflow.
